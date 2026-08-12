import os
import sys
import site
import re
import math
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


class TrOCRHandwritingEngine(BaseRecognitionEngine):
    """
    Enhanced Phase 5.1 Pretrained Microsoft TrOCR Handwriting Recognition Engine.
    
    Features:
      - Multi-Variant Preprocessing (Standard Padded, CLAHE Contrast, Otsu Binarized)
      - Beam Search Decoding (num_beams=4, num_return_sequences=3)
      - Sequence Log-Likelihood Candidate Selection across Variants
      - Zero Fabrication Thresholding (no hardcoded words)
    """
    def __init__(self, min_confidence: float = 0.38):
        self.min_confidence = min_confidence
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

    def _generate_image_variants(self, cropped_bgr: np.ndarray) -> List[Tuple[str, Image.Image]]:
        """
        Generates 3 clean handwriting image variants for TrOCR:
          1. Standard White Padded RGB
          2. CLAHE Contrast-Enhanced Grayscale RGB
          3. Otsu Binarized Crisp Stroke RGB
        """
        h, w, _ = cropped_bgr.shape
        variants = []

        # 1. Standard White Padded RGB (adds 40px margin around crop to preserve aspect ratio)
        pad_size = 40
        padded_bgr = np.full((h + 2 * pad_size, w + 2 * pad_size, 3), 255, dtype=np.uint8)
        padded_bgr[pad_size:pad_size + h, pad_size:pad_size + w] = cropped_bgr
        
        rgb_padded = cv2.cvtColor(padded_bgr, cv2.COLOR_BGR2RGB)
        variants.append(("Standard Padded", Image.fromarray(rgb_padded)))

        # 2. CLAHE Contrast-Enhanced Grayscale
        gray = cv2.cvtColor(padded_bgr, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_img = clahe.apply(gray)
        clahe_rgb = cv2.cvtColor(clahe_img, cv2.COLOR_GRAY2RGB)
        variants.append(("CLAHE Contrast", Image.fromarray(clahe_rgb)))

        # 3. Otsu Adaptive Binarized Stroke
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        _, otsu_thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        otsu_rgb = cv2.cvtColor(otsu_thresh, cv2.COLOR_GRAY2RGB)
        variants.append(("Otsu Binarized", Image.fromarray(otsu_rgb)))

        return variants

    def recognize(self, strokes: List[List[Tuple[int, int]]]) -> RecognitionResult:
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
            # Generate 3 image variants
            variants = self._generate_image_variants(cropped_img)
            all_candidates = []

            for var_name, pil_img in variants:
                pixel_values = self.processor(images=pil_img, return_tensors="pt").pixel_values

                with torch.no_grad():
                    outputs = self.model.generate(
                        pixel_values,
                        num_beams=4,
                        num_return_sequences=3,
                        return_dict_in_generate=True,
                        output_scores=True,
                        early_stopping=True,
                        max_new_tokens=25
                    )

                sequences = outputs.sequences
                seq_scores = outputs.sequences_scores if hasattr(outputs, "sequences_scores") and outputs.sequences_scores is not None else None

                for seq_idx in range(len(sequences)):
                    raw_text = self.processor.decode(sequences[seq_idx], skip_special_tokens=True).strip()
                    cleaned_text = re.sub(r'[^A-Za-z0-9]', '', raw_text).upper()

                    if seq_scores is not None and seq_idx < len(seq_scores):
                        log_prob = seq_scores[seq_idx].item()
                        conf = min(0.99, max(0.0, math.exp(log_prob)))
                    else:
                        conf = 0.80 if len(cleaned_text) > 0 else 0.0

                    if cleaned_text:
                        all_candidates.append({
                            "text": cleaned_text,
                            "confidence": round(conf, 3),
                            "variant": var_name,
                            "raw_text": raw_text
                        })

            if not all_candidates:
                return RecognitionResult(
                    text="LOW CONFIDENCE / NOT RECOGNIZED",
                    confidence=0.0,
                    status="LOW_CONFIDENCE",
                    alternatives=[],
                    rendered_image=cropped_img,
                    debug_info=debug_info
                )

            # Rank candidates across all variants by confidence score descending
            all_candidates.sort(key=lambda x: x["confidence"], reverse=True)
            top_candidate = all_candidates[0]
            best_text = top_candidate["text"]
            best_conf = top_candidate["confidence"]
            best_variant = top_candidate["variant"]

            # Deduplicate top alternative candidate choices for debug output
            seen_texts = set()
            alternatives = []
            for cand in all_candidates:
                if cand["text"] not in seen_texts:
                    seen_texts.add(cand["text"])
                    alternatives.append((cand["text"], cand["confidence"]))
                if len(alternatives) >= 3:
                    break

            debug_info["model_name"] = "microsoft/trocr-small-handwritten"
            debug_info["selected_variant"] = best_variant
            debug_info["all_candidates"] = all_candidates[:5]
            debug_info["raw_text"] = top_candidate["raw_text"]

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
