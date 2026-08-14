import os
import sys
import site
import re
import math
import time
import logging
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import cv2
from PIL import Image

# Ensure backend/libs and user site-packages are accessible
libs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "libs")
if libs_dir not in sys.path:
    sys.path.append(libs_dir)

user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

import torch
from app.recognition.base import BaseRecognitionEngine, RecognitionResult
from app.recognition.canvas import VirtualHandwritingCanvas

logger = logging.getLogger(__name__)

# Directory for debug image exports
DEBUG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "debug_output")


class TrOCRHandwritingEngine(BaseRecognitionEngine):
    """
    Phase 7 — Pretrained Microsoft TrOCR Handwriting Recognition Engine.
    
    Features:
      - Anti-Aliased Canvas & Aspect-Ratio Preserving Normalization
      - Multi-Variant Preprocessing (Centered Standard Padded, CLAHE+Sharpened, Morphological Dilation)
      - Beam Search Generation (num_beams=5, length_penalty=1.0, early_stopping=True)
      - Length-Normalized Log-Likelihood & Multi-Variant Consensus Candidate Ranking
      - Zero Target-Word Hardcoding
      - Optional Debug Artifact Export (backend/debug_output/)
    """
    def __init__(self, min_confidence: float = 0.38, export_debug: bool = False):
        self.min_confidence = min_confidence
        self.export_debug = export_debug
        self.processor = None
        self.model = None
        self.canvas_tracker = VirtualHandwritingCanvas()
        self._init_model()

    def _init_model(self):
        try:
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
            logger.info("Loading pre-trained Microsoft TrOCR Small Handwritten model...")
            self.processor = TrOCRProcessor.from_pretrained('microsoft/trocr-small-handwritten', use_fast=False)
            self.model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-small-handwritten')
            self.model.eval()
            logger.info("Microsoft TrOCR Small Handwritten engine initialized successfully!")
        except Exception as e:
            logger.error(f"Failed to load Microsoft TrOCR model: {e}", exc_info=True)
            self.processor = None
            self.model = None

    def _generate_image_variants(self, cropped_bgr: np.ndarray) -> List[Tuple[str, Image.Image, np.ndarray]]:
        """
        Generates 3 optimized handwriting image variants for TrOCR DeiT patch encoder:
          1. Standard Centered White Padded RGB
          2. CLAHE Contrast-Enhanced + Sharpened RGB
          3. Morphological Dilation Stroke-Enhanced RGB
        """
        h, w, _ = cropped_bgr.shape
        variants = []

        # 1. Standard Centered White Padded RGB (48px margin around crop)
        pad_size = 48
        padded_bgr = np.full((h + 2 * pad_size, w + 2 * pad_size, 3), 255, dtype=np.uint8)
        padded_bgr[pad_size:pad_size + h, pad_size:pad_size + w] = cropped_bgr
        
        rgb_padded = cv2.cvtColor(padded_bgr, cv2.COLOR_BGR2RGB)
        variants.append(("Standard Centered", Image.fromarray(rgb_padded), padded_bgr))

        # 2. CLAHE Contrast-Enhanced + 3x3 Sharpening Kernel
        gray = cv2.cvtColor(padded_bgr, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
        clahe_img = clahe.apply(gray)

        # Apply subtle sharpening filter
        sharpen_kernel = np.array([[0, -0.5, 0], [-0.5, 3.0, -0.5], [0, -0.5, 0]], dtype=np.float32)
        sharpened_gray = cv2.filter2D(clahe_img, -1, sharpen_kernel)
        clahe_rgb = cv2.cvtColor(sharpened_gray, cv2.COLOR_GRAY2RGB)
        variants.append(("CLAHE Sharpened", Image.fromarray(clahe_rgb), cv2.cvtColor(clahe_rgb, cv2.COLOR_RGB2BGR)))

        # 3. Morphological Stroke-Thickening Dilation
        # Invert gray (stroke=white) -> dilate stroke slightly -> invert back
        inverted = cv2.bitwise_not(gray)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        dilated_inv = cv2.dilate(inverted, kernel, iterations=1)
        dilated_gray = cv2.bitwise_not(dilated_inv)
        dilated_rgb = cv2.cvtColor(dilated_gray, cv2.COLOR_GRAY2RGB)
        variants.append(("Stroke Dilated", Image.fromarray(dilated_rgb), cv2.cvtColor(dilated_rgb, cv2.COLOR_RGB2BGR)))

        return variants

    def recognize(self, strokes: List[List[Tuple[int, int]]]) -> RecognitionResult:
        t_start = time.time()

        # Re-populate virtual canvas from strokes for consistent cropping
        self.canvas_tracker.clear()
        for s in strokes:
            if not s:
                continue
            self.canvas_tracker.add_point(s[0])
            for pt in s[1:]:
                self.canvas_tracker.add_point(pt)
            self.canvas_tracker.pause_stroke()

        cropped_img, debug_info = self.canvas_tracker.crop_handwriting()

        if cropped_img is None or not self.model or not self.processor:
            return RecognitionResult(
                text="INSUFFICIENT INPUT",
                confidence=0.0,
                status="INSUFFICIENT_INPUT",
                alternatives=[],
                rendered_image=None,
                debug_info=debug_info
            )

        try:
            # Generate image variants
            variants = self._generate_image_variants(cropped_img)
            all_raw_candidates = []

            for var_name, pil_img, var_bgr in variants:
                pixel_values = self.processor(images=pil_img, return_tensors="pt").pixel_values

                with torch.no_grad():
                    outputs = self.model.generate(
                        pixel_values,
                        num_beams=5,
                        num_return_sequences=3,
                        return_dict_in_generate=True,
                        output_scores=True,
                        early_stopping=True,
                        no_repeat_ngram_size=2,
                        length_penalty=1.0,
                        max_new_tokens=20
                    )

                sequences = outputs.sequences
                seq_scores = outputs.sequences_scores if hasattr(outputs, "sequences_scores") and outputs.sequences_scores is not None else None

                for seq_idx in range(len(sequences)):
                    raw_text = self.processor.decode(sequences[seq_idx], skip_special_tokens=True).strip()
                    cleaned_text = re.sub(r'[^A-Za-z0-9]', '', raw_text).upper()

                    if not cleaned_text:
                        continue

                    if seq_scores is not None and seq_idx < len(seq_scores):
                        raw_log_prob = seq_scores[seq_idx].item()
                        # Length-normalized log likelihood calculation
                        length_penalty_factor = math.pow(len(cleaned_text), 0.8)
                        norm_log_prob = raw_log_prob / max(1.0, length_penalty_factor)
                        base_conf = min(0.99, max(0.0, math.exp(norm_log_prob)))
                    else:
                        base_conf = 0.75

                    all_raw_candidates.append({
                        "text": cleaned_text,
                        "base_confidence": base_conf,
                        "raw_score": seq_scores[seq_idx].item() if seq_scores is not None and seq_idx < len(seq_scores) else 0.0,
                        "variant": var_name,
                        "raw_text": raw_text
                    })

            if not all_raw_candidates:
                return RecognitionResult(
                    text="LOW CONFIDENCE / NOT RECOGNIZED",
                    confidence=0.0,
                    status="LOW_CONFIDENCE",
                    alternatives=[],
                    rendered_image=cropped_img,
                    debug_info=debug_info
                )

            # Calculate Multi-Variant Consensus Frequency
            text_freq = {}
            for cand in all_raw_candidates:
                txt = cand["text"]
                text_freq[txt] = text_freq.get(txt, 0) + 1

            # Compute final ranked candidates with consensus scoring
            scored_candidates = []
            seen_texts = set()

            for cand in all_raw_candidates:
                txt = cand["text"]
                freq = text_freq[txt]
                # Consensus bonus: +0.08 for each additional variant agreement
                consensus_bonus = 0.08 * (freq - 1)
                final_score = min(0.99, cand["base_confidence"] + consensus_bonus)

                scored_candidates.append({
                    "text": txt,
                    "confidence": round(final_score, 3),
                    "base_confidence": round(cand["base_confidence"], 3),
                    "variant": cand["variant"],
                    "consensus_count": freq,
                    "raw_text": cand["raw_text"]
                })

            # Rank by final score descending
            scored_candidates.sort(key=lambda x: x["confidence"], reverse=True)
            top_candidate = scored_candidates[0]
            best_text = top_candidate["text"]
            best_conf = top_candidate["confidence"]
            best_variant = top_candidate["variant"]

            # Deduplicate alternative candidate choices for API output
            alternatives = []
            for cand in scored_candidates:
                if cand["text"] not in seen_texts:
                    seen_texts.add(cand["text"])
                    alternatives.append((cand["text"], cand["confidence"]))
                if len(alternatives) >= 3:
                    break

            latency_ms = int((time.time() - t_start) * 1000)

            debug_info["model_name"] = "microsoft/trocr-small-handwritten"
            debug_info["selected_variant"] = best_variant
            debug_info["all_candidates"] = scored_candidates[:5]
            debug_info["raw_text"] = top_candidate["raw_text"]
            debug_info["latency_ms"] = latency_ms

            # Export debug artifacts if enabled
            if self.export_debug:
                os.makedirs(DEBUG_DIR, exist_ok=True)
                timestamp_str = int(time.time() * 1000)
                cv2.imwrite(os.path.join(DEBUG_DIR, f"crop_{timestamp_str}_{best_text}.png"), cropped_img)

            # Threshold validation (NO FALSE WORD FABRICATION)
            if best_conf < self.min_confidence or len(best_text) == 0:
                return RecognitionResult(
                    text="LOW CONFIDENCE / NOT RECOGNIZED",
                    confidence=best_conf,
                    status="LOW_CONFIDENCE",
                    alternatives=alternatives,
                    rendered_image=cropped_img,
                    debug_info=debug_info
                )

            return RecognitionResult(
                text=best_text,
                confidence=best_conf,
                status="RECOGNIZED",
                alternatives=alternatives,
                rendered_image=cropped_img,
                debug_info=debug_info
            )

        except Exception as e:
            logger.error(f"Error during TrOCR inference: {e}", exc_info=True)
            debug_info["error"] = str(e)
            return RecognitionResult(
                text="LOW CONFIDENCE / NOT RECOGNIZED",
                confidence=0.0,
                status="LOW_CONFIDENCE",
                alternatives=[],
                rendered_image=cropped_img,
                debug_info=debug_info
            )
