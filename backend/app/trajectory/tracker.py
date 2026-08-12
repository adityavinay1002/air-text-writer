import cv2
from typing import List, Tuple, Optional

Point = Tuple[int, int]
Stroke = List[Point]

class TrajectoryTracker:
    """
    Tracks and stores multi-stroke air-writing trajectories.
    Allows independent strokes created across multiple WRITE sessions,
    retaining visible strokes during PEN_UP, and clearing on CONFIRM or CLEAR.
    """
    def __init__(self, max_strokes: int = 50):
        self.strokes: List[Stroke] = []
        self.current_stroke: Optional[Stroke] = None
        self.max_strokes = max_strokes

    def update(self, gesture_state: str, fingertip_px: Optional[Point]):
        """
        Updates stroke records based on current gesture state:
          - WRITE: Appends index fingertip pixel coordinates to active stroke.
          - PEN_UP / NEUTRAL: Finalizes active stroke (pen up).
          - CONFIRM / CLEAR: Clears all strokes from canvas.
        """
        if gesture_state == "WRITE" and fingertip_px is not None:
            if self.current_stroke is None:
                self.current_stroke = []
                self.strokes.append(self.current_stroke)

            # Prevent storing identical static points consecutively
            if not self.current_stroke or self.current_stroke[-1] != fingertip_px:
                self.current_stroke.append(fingertip_px)

        elif gesture_state in ("CONFIRM", "CLEAR"):
            self.clear()
        else:
            # PEN_UP or NEUTRAL state: End current stroke segment
            self.current_stroke = None

    def clear(self):
        """Clears all captured strokes."""
        self.strokes.clear()
        self.current_stroke = None

    def get_point_count(self) -> int:
        """Returns total number of points captured across all strokes."""
        return sum(len(s) for s in self.strokes)

    def draw_trajectory(self, frame: cv2.Mat, line_color: Tuple[int, int, int] = (255, 230, 0), thickness: int = 5) -> cv2.Mat:
        """
        Renders all strokes onto frame with smooth anti-aliased lines and glow effect.
        """
        for stroke in self.strokes:
            if len(stroke) < 2:
                if len(stroke) == 1:
                    cv2.circle(frame, stroke[0], thickness, line_color, -1)
                continue

            for i in range(1, len(stroke)):
                pt1 = stroke[i - 1]
                pt2 = stroke[i]
                # Outer glow
                cv2.line(frame, pt1, pt2, (0, 180, 255), thickness + 4, cv2.LINE_AA)
                # Core bright line
                cv2.line(frame, pt1, pt2, line_color, thickness, cv2.LINE_AA)

        return frame
