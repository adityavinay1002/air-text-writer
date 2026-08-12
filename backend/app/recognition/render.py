import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any

class TrajectoryRenderer:
    """
    Renders multi-stroke air-writing trajectories onto a normalized high-contrast
    bitmap canvas suitable for OCR and vision recognition engines.
    """
    
    @staticmethod
    def validate_and_get_bbox(strokes: List[List[Tuple[int, int]]], min_points: int = 10, min_dim: int = 20) -> Tuple[bool, Dict[str, Any]]:
        """
        Validates trajectory quality and calculates bounding box.
        Returns (is_valid, bbox_info_dict).
        """
        all_pts = [pt for stroke in strokes for pt in stroke]
        point_count = len(all_pts)
        stroke_count = len(strokes)

        if point_count < min_points or stroke_count == 0:
            return False, {
                "point_count": point_count,
                "stroke_count": stroke_count,
                "reason": f"Insufficient points ({point_count} < {min_points})"
            }

        xs = [pt[0] for pt in all_pts]
        ys = [pt[1] for pt in all_pts]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        width = max_x - min_x
        height = max_y - min_y

        if width < min_dim or height < min_dim:
            return False, {
                "point_count": point_count,
                "stroke_count": stroke_count,
                "bbox": (min_x, min_y, width, height),
                "reason": f"Bounding box too small ({width}x{height} < {min_dim}px)"
            }

        return True, {
            "point_count": point_count,
            "stroke_count": stroke_count,
            "min_x": min_x,
            "max_x": max_x,
            "min_y": min_y,
            "max_y": max_y,
            "width": width,
            "height": height,
            "aspect_ratio": round(width / float(max(1, height)), 3)
        }

    @classmethod
    def render_to_canvas(
        cls,
        strokes: List[List[Tuple[int, int]]],
        canvas_size: int = 512,
        padding: int = 50,
        stroke_thickness: int = 14
    ) -> Tuple[Optional[np.ndarray], Dict[str, Any]]:
        """
        Renders strokes onto a white canvas (255) with thick black lines (0).
        Strokes are centered and scaled while preserving aspect ratio.
        Returns (image_bgr_or_gray, bbox_info).
        """
        is_valid, info = cls.validate_and_get_bbox(strokes)
        if not is_valid:
            return None, info

        min_x = info["min_x"]
        min_y = info["min_y"]
        w = info["width"]
        h = info["height"]

        # Target drawing area inside padding
        draw_size = canvas_size - (2 * padding)
        scale = draw_size / float(max(w, h))

        # Center offsets
        scaled_w = w * scale
        scaled_h = h * scale
        offset_x = padding + (draw_size - scaled_w) / 2.0
        offset_y = padding + (draw_size - scaled_h) / 2.0

        # Initialize solid white canvas
        canvas = np.full((canvas_size, canvas_size, 3), 255, dtype=np.uint8)

        # Draw normalized strokes
        for stroke in strokes:
            if len(stroke) < 1:
                continue
            
            scaled_pts = []
            for (px, py) in stroke:
                sx = int(offset_x + (px - min_x) * scale)
                sy = int(offset_y + (py - min_y) * scale)
                scaled_pts.append((sx, sy))

            if len(scaled_pts) == 1:
                cv2.circle(canvas, scaled_pts[0], stroke_thickness // 2, (0, 0, 0), -1)
            else:
                for i in range(1, len(scaled_pts)):
                    cv2.line(canvas, scaled_pts[i - 1], scaled_pts[i], (0, 0, 0), stroke_thickness, cv2.LINE_AA)

        info["scale"] = round(scale, 4)
        info["canvas_size"] = canvas_size
        return canvas, info
