import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any

Point = Tuple[int, int]
Stroke = List[Point]

class VirtualHandwritingCanvas:
    """
    High-resolution virtual handwriting canvas ($1280 x 720$).
    Phase 7 Accuracy Enhancements:
      - Anti-aliased bold stroke rendering (thickness=14, cv2.LINE_AA)
      - Proportional dynamic padding calculation
      - Standardized aspect-ratio-preserving line crop normalization
    """
    def __init__(self, width: int = 1280, height: int = 720, background_color: int = 255):
        self.width = width
        self.height = height
        self.background_color = background_color
        # 3-channel solid white canvas
        self.canvas = np.full((height, width, 3), background_color, dtype=np.uint8)
        self.current_stroke: Optional[Stroke] = None
        self.strokes: List[Stroke] = []

    def add_point(self, pt: Point, stroke_thickness: int = 14, stroke_color: Tuple[int, int, int] = (0, 0, 0)):
        """Appends a new point and draws smooth anti-aliased line on the high-res canvas."""
        if self.current_stroke is None:
            self.current_stroke = [pt]
            self.strokes.append(self.current_stroke)
            cv2.circle(self.canvas, pt, stroke_thickness // 2, stroke_color, -1, cv2.LINE_AA)
        else:
            prev_pt = self.current_stroke[-1]
            if prev_pt != pt:
                self.current_stroke.append(pt)
                cv2.line(self.canvas, prev_pt, pt, stroke_color, stroke_thickness, cv2.LINE_AA)

    def pause_stroke(self):
        """Ends active stroke (PEN_UP pause). Keeps existing writing intact."""
        self.current_stroke = None

    def clear(self):
        """Resets the canvas completely."""
        self.canvas.fill(self.background_color)
        self.current_stroke = None
        self.strokes.clear()

    def crop_handwriting(self, padding: Optional[int] = None, target_height: int = 128) -> Tuple[Optional[np.ndarray], Dict[str, Any]]:
        """
        Calculates bounding box of non-background handwritten content,
        applies proportional dynamic padding, and scales to target height while preserving aspect ratio.
        """
        all_pts = [pt for stroke in self.strokes for pt in stroke]
        if not all_pts or len(all_pts) < 6:
            return None, {"reason": "Insufficient points (< 6)", "point_count": len(all_pts)}

        xs = [pt[0] for pt in all_pts]
        ys = [pt[1] for pt in all_pts]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        w = max_x - min_x
        h = max_y - min_y

        if w < 15 or h < 15:
            return None, {"reason": f"Bounding box too small ({w}x{h} < 15px)", "point_count": len(all_pts)}

        # Compute dynamic proportional padding if padding is not specified
        if padding is None:
            computed_padding = max(24, int(max(w, h) * 0.15))
        else:
            computed_padding = padding

        # Pad bounding box inside canvas boundaries
        crop_x1 = max(0, min_x - computed_padding)
        crop_y1 = max(0, min_y - computed_padding)
        crop_x2 = min(self.width, max_x + computed_padding)
        crop_y2 = min(self.height, max_y + computed_padding)

        # Extract cropped handwriting region
        cropped = self.canvas[crop_y1:crop_y2, crop_x1:crop_x2].copy()
        crop_h, crop_w, _ = cropped.shape

        # Scale to target height preserving natural aspect ratio
        aspect = crop_w / float(max(1, crop_h))
        new_w = int(target_height * aspect)
        new_w = max(48, min(1200, new_w))

        # Use Lanczos / Inter-Area interpolation for crisp stroke downsampling
        interp = cv2.INTER_LANCZOS4 if new_w > crop_w else cv2.INTER_AREA
        resized = cv2.resize(cropped, (new_w, target_height), interpolation=interp)

        info = {
            "bbox": (min_x, min_y, w, h),
            "crop_box": (crop_x1, crop_y1, crop_x2, crop_y2),
            "padding_applied": computed_padding,
            "aspect_ratio": round(aspect, 3),
            "point_count": len(all_pts),
            "stroke_count": len(self.strokes),
            "resized_shape": resized.shape
        }

        return resized, info
