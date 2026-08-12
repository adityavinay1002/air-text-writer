import sys
import site
import logging
import re
from typing import List, Tuple, Dict, Any, Optional
import numpy as np

# Ensure user site packages are accessible for RapidOCR / EasyOCR
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

from app.recognition.base import BaseRecognitionEngine, RecognitionResult
from app.recognition.render import TrajectoryRenderer

logger = logging.getLogger(__name__)


class RapidOCREngine(BaseRecognitionEngine):
    """
    Off-the-shelf OCR recognition engine powered by RapidOCR (ONNX Runtime).
    Evaluates trajectory images without dataset training or word fabrication.
    """
    def __init__(self, min_confidence: float = 0.45):
        self.min_confidence = min_confidence
        self.ocr_instance = None
        self._init_engine()

    def _init_engine(self):
        try:
            from rapidocr_onnxruntime import RapidOCR
            self.ocr_instance = RapidOCR()
            logger.info("RapidOCR engine initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize RapidOCR engine: {e}")
            self.ocr_instance = None

    def recognize(self, strokes: List[List[Tuple[int, int]]]) -> RecognitionResult:
        # 1. Trajectory rendering & minimum input validation
        canvas, debug_info = TrajectoryRenderer.render_to_canvas(strokes)

        if canvas is None or not self.ocr_instance:
            return RecognitionResult(
                text="INSUFFICIENT INPUT",
                confidence=0.0,
                status="INSUFFICIENT_INPUT",
                alternatives=[],
                rendered_image=None,
                debug_info=debug_info
            )

        # 2. Run off-the-shelf OCR on rendered canvas
        try:
            ocr_result, elapsed_time = self.ocr_instance(canvas)
            debug_info["elapsed_time_sec"] = elapsed_time
            debug_info["raw_ocr_output"] = str(ocr_result)

            if not ocr_result:
                return RecognitionResult(
                    text="LOW CONFIDENCE / NOT RECOGNIZED",
                    confidence=0.0,
                    status="LOW_CONFIDENCE",
                    alternatives=[],
                    rendered_image=canvas,
                    debug_info=debug_info
                )

            # RapidOCR returns list of [bbox, text, score]
            candidates = []
            for item in ocr_result:
                if len(item) >= 3:
                    raw_text = str(item[1]).strip()
                    conf = float(item[2])
                    # Clean text to uppercase alphanumeric
                    cleaned_text = re.sub(r'[^A-Za-z0-9]', '', raw_text).upper()
                    if cleaned_text:
                        candidates.append((cleaned_text, conf))

            if not candidates:
                return RecognitionResult(
                    text="LOW CONFIDENCE / NOT RECOGNIZED",
                    confidence=0.0,
                    status="LOW_CONFIDENCE",
                    alternatives=[],
                    rendered_image=canvas,
                    debug_info=debug_info
                )

            # Sort candidates by confidence
            candidates.sort(key=lambda x: x[1], reverse=True)
            best_text, best_conf = candidates[0]
            alternatives = candidates[1:]

            # 3. Confidence thresholding (NEVER fabricate a word on low confidence)
            if best_conf < self.min_confidence or len(best_text) == 0:
                return RecognitionResult(
                    text="LOW CONFIDENCE / NOT RECOGNIZED",
                    confidence=best_conf,
                    status="LOW_CONFIDENCE",
                    alternatives=alternatives,
                    rendered_image=canvas,
                    debug_info=debug_info
                )

            return RecognitionResult(
                text=best_text,
                confidence=best_conf,
                status="RECOGNIZED",
                alternatives=alternatives,
                rendered_image=canvas,
                debug_info=debug_info
            )

        except Exception as e:
            logger.error(f"Error during RapidOCR inference: {e}", exc_info=True)
            debug_info["error"] = str(e)
            return RecognitionResult(
                text="LOW CONFIDENCE / NOT RECOGNIZED",
                confidence=0.0,
                status="LOW_CONFIDENCE",
                alternatives=[],
                rendered_image=canvas,
                debug_info=debug_info
            )


class EasyOCREngine(BaseRecognitionEngine):
    """
    Optional fallback OCR recognition engine powered by EasyOCR (PyTorch).
    """
    def __init__(self, min_confidence: float = 0.45):
        self.min_confidence = min_confidence
        self.reader = None
        self._init_engine()

    def _init_engine(self):
        try:
            import easyocr
            self.reader = easyocr.Reader(['en'], gpu=False)
            logger.info("EasyOCR engine initialized successfully.")
        except Exception as e:
            logger.warning(f"EasyOCR engine unavailable: {e}")
            self.reader = None

    def recognize(self, strokes: List[List[Tuple[int, int]]]) -> RecognitionResult:
        canvas, debug_info = TrajectoryRenderer.render_to_canvas(strokes)

        if canvas is None or not self.reader:
            return RecognitionResult(
                text="INSUFFICIENT INPUT",
                confidence=0.0,
                status="INSUFFICIENT_INPUT",
                alternatives=[],
                rendered_image=None,
                debug_info=debug_info
            )

        try:
            results = self.reader.readtext(canvas)
            debug_info["raw_ocr_output"] = str(results)

            if not results:
                return RecognitionResult(
                    text="LOW CONFIDENCE / NOT RECOGNIZED",
                    confidence=0.0,
                    status="LOW_CONFIDENCE",
                    alternatives=[],
                    rendered_image=canvas,
                    debug_info=debug_info
                )

            candidates = []
            for item in results:
                if len(item) >= 3:
                    raw_text = str(item[1]).strip()
                    conf = float(item[2])
                    cleaned_text = re.sub(r'[^A-Za-z0-9]', '', raw_text).upper()
                    if cleaned_text:
                        candidates.append((cleaned_text, conf))

            if not candidates:
                return RecognitionResult(
                    text="LOW CONFIDENCE / NOT RECOGNIZED",
                    confidence=0.0,
                    status="LOW_CONFIDENCE",
                    alternatives=[],
                    rendered_image=canvas,
                    debug_info=debug_info
                )

            candidates.sort(key=lambda x: x[1], reverse=True)
            best_text, best_conf = candidates[0]
            alternatives = candidates[1:]

            if best_conf < self.min_confidence:
                return RecognitionResult(
                    text="LOW CONFIDENCE / NOT RECOGNIZED",
                    confidence=best_conf,
                    status="LOW_CONFIDENCE",
                    alternatives=alternatives,
                    rendered_image=canvas,
                    debug_info=debug_info
                )

            return RecognitionResult(
                text=best_text,
                confidence=best_conf,
                status="RECOGNIZED",
                alternatives=alternatives,
                rendered_image=canvas,
                debug_info=debug_info
            )

        except Exception as e:
            logger.error(f"Error during EasyOCR inference: {e}", exc_info=True)
            return RecognitionResult(
                text="LOW CONFIDENCE / NOT RECOGNIZED",
                confidence=0.0,
                status="LOW_CONFIDENCE",
                alternatives=[],
                rendered_image=canvas,
                debug_info=debug_info
            )
