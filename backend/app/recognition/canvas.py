import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any

Point = Tuple[int, int]
Stroke = List[Point]

class VirtualHandwritingCanvas:
    """
    High-resolution virtual handwriting canvas ($1280 x 720$).
    Visually accumulates smooth air-writing strokes and auto-crops the handwriting
    region on ✌️ CONFIRM for pre-trained handwriting image recognition.
    """
    def __init__(self, width: int = 1280, height: int = 720, background_color: int = 255):
        self.width = width
        self.height = height
        self.background_color = background_color
        # 3-channel solid white canvas
        self.canvas = np.full((height, width, 3), background_color, dtype=np.uint8)
        self.current_stroke: Optional[Stroke] = None
        self.strokes: List[Stroke] = []

    def add_point(self, pt: Point, stroke_thickness: int = 10, stroke_color: Tuple[int, int, int] = (0, 0, 0)):
        """Appends a new point and draws smooth line on the high-res canvas."""
        if self.current_stroke is None:
            self.current_stroke = [pt]
            self.strokes.append(self.current_stroke)
            cv2.circle(self.canvas, pt, stroke_thickness // 2, stroke_color, -1)
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

    def crop_handwriting(self, padding: int = 30, target_height: int = 128) -> Tuple[Optional[np.ndarray], Dict[str, Any]]:
        """
        Calculates bounding box of non-background handwritten content,
        crops with padding, and resizes while preserving aspect ratio.
        """
        all_pts = [pt for stroke in self.strokes for pt in stroke]
        if not all_pts or len(all_pts) < 8:
            return None, {"reason": "Insufficient points (< 8)", "point_count": len(all_pts)}

        xs = [pt[0] for pt in all_pts]
        ys = [pt[1] for pt in all_pts]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        w = max_x - min_x
        h = max_y - min_y

        if w < 20 or h < 20:
            return None, {"reason": f"Bounding box too small ({w}x{h} < 20px)", "point_count": len(all_pts)}

        # Pad bounding box inside canvas boundaries
        crop_x1 = max(0, min_x - padding)
        crop_y1 = max(0, min_y - padding)
        crop_x2 = min(self.width, max_x + padding)
        crop_y2 = min(self.height, max_y + padding)

        # Extract cropped handwriting region
        cropped = self.canvas[crop_y1:crop_y2, crop_x1:crop_x2].copy()
        crop_h, crop_w, _ = cropped.shape

        # Scale to target height preserving aspect ratio
        aspect = crop_w / float(crop_h)
        new_w = int(target_height * aspect)
        new_w = max(32, min(800, new_w))
        resized = cv2.resize(cropped, (new_w, target_height), interpolation=cv2.INTER_AREA)

        info = {
            "bbox": (min_x, min_y, w, h),
            "crop_box": (crop_x1, crop_y1, crop_x2, crop_y2),
            "aspect_ratio": round(aspect, 3),
            "point_count": len(all_pts),
            "stroke_count": len(self.strokes),
            "resized_shape": resized.shape
        }

        return resized, info
