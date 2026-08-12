import math
import logging
from typing import List, Tuple, Dict, Any, Optional
import numpy as np

from app.recognition.base import BaseRecognitionEngine, RecognitionResult
from app.recognition.segmenter import CharacterSegmenter, CharacterSegment
from app.recognition.letter_templates import LETTER_TEMPLATES, normalize_point_cloud
from app.recognition.render import TrajectoryRenderer

logger = logging.getLogger(__name__)

class CharacterSegmentedRecognizer(BaseRecognitionEngine):
    """
    Training-free character-segmented air-writing recognition engine.
    
    Pipeline:
      1. Character Segmentation (Spatial X-axis clustering)
      2. P Point-Cloud Letter Recognition against A-Z topologies
      3. Word Assembly & Per-Character Confidence Validation
    """
    def __init__(self, min_char_confidence: float = 0.38, min_word_confidence: float = 0.45):
        self.min_char_confidence = min_char_confidence
        self.min_word_confidence = min_word_confidence

    @staticmethod
    def _point_cloud_distance(pts_a: List[Tuple[float, float]], pts_b: List[Tuple[float, float]]) -> float:
        """Computes average point-to-point Euclidean distance between two 32-point clouds."""
        if not pts_a or not pts_b or len(pts_a) != len(pts_b):
            return 999.0

        total_dist = 0.0
        for p1, p2 in zip(pts_a, pts_b):
            dx = p1[0] - p2[0]
            dy = p1[1] - p2[1]
            total_dist += math.sqrt(dx * dx + dy * dy)

        return total_dist / float(len(pts_a))

    def recognize_single_character(self, char_strokes: CharacterSegment) -> Dict[str, Any]:
        """Recognizes an individual character segment against A-Z templates."""
        flat_pts = [pt for stroke in char_strokes for pt in stroke]
        if len(flat_pts) < 4:
            return {"letter": "?", "confidence": 0.0, "alternatives": []}

        # Normalize point cloud to 32 points
        norm_pts = normalize_point_cloud(flat_pts, target_points=32)

        # Match against A-Z templates
        scores = []
        for letter, tmpl_pts in LETTER_TEMPLATES.items():
            dist = self._point_cloud_distance(norm_pts, tmpl_pts)
            # Map distance (0.0 to ~0.8) to confidence score (1.0 to 0.0)
            confidence = max(0.0, 1.0 - (dist * 1.75))
            scores.append((letter, round(confidence, 3)))

        # Sort by confidence score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        best_letter, best_conf = scores[0]
        alternatives = scores[1:3]

        return {
            "letter": best_letter,
            "confidence": best_conf,
            "alternatives": alternatives
        }

    def recognize(self, strokes: List[List[Tuple[int, int]]]) -> RecognitionResult:
        # 1. Validation & Render bitmap canvas for debug preview
        canvas, debug_info = TrajectoryRenderer.render_to_canvas(strokes)

        all_pts = [pt for s in strokes for pt in s]
        if not strokes or len(all_pts) < 8 or canvas is None:
            return RecognitionResult(
                text="INSUFFICIENT INPUT",
                confidence=0.0,
                status="INSUFFICIENT_INPUT",
                alternatives=[],
                rendered_image=None,
                debug_info={"reason": "Points < 8 or empty stroke"}
            )

        # 2. Character Segmentation
        char_segments = CharacterSegmenter.segment_strokes(strokes)
        if not char_segments:
            return RecognitionResult(
                text="INSUFFICIENT INPUT",
                confidence=0.0,
                status="INSUFFICIENT_INPUT",
                alternatives=[],
                rendered_image=canvas,
                debug_info={"reason": "No valid character segments"}
            )

        # 3. Recognize each character segment independently
        char_results = []
        for idx, seg in enumerate(char_segments):
            res = self.recognize_single_character(seg)
            res["char_index"] = idx + 1
            char_results.append(res)

        # 4. Word Assembly
        predicted_word = "".join([c["letter"] for c in char_results])
        confidences = [c["confidence"] for c in char_results]
        avg_confidence = round(sum(confidences) / float(len(confidences)), 3) if confidences else 0.0

        # Detailed character debug info for OpenCV HUD
        debug_info["character_count"] = len(char_results)
        debug_info["char_details"] = char_results
        debug_info["raw_word"] = predicted_word

        # 5. Validation & Confidence Thresholding (NO FABRICATION)
        min_char_conf = min(confidences) if confidences else 0.0

        if avg_confidence < self.min_word_confidence or min_char_conf < self.min_char_confidence:
            return RecognitionResult(
                text="LOW CONFIDENCE / NOT RECOGNIZED",
                confidence=avg_confidence,
                status="LOW_CONFIDENCE",
                alternatives=[(c["letter"], c["confidence"]) for c in char_results],
                rendered_image=canvas,
                debug_info=debug_info
            )

        return RecognitionResult(
            text=predicted_word,
            confidence=avg_confidence,
            status="RECOGNIZED",
            alternatives=[(c["letter"], c["confidence"]) for c in char_results],
            rendered_image=canvas,
            debug_info=debug_info
        )
