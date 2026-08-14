import time
from typing import List, Tuple, Optional, Dict, Any

PointWithTime = Tuple[int, int, float]  # (x_px, y_px, timestamp_ms)
Stroke = List[PointWithTime]

class WordSession:
    """Represents a continuous multi-stroke word writing session."""
    def __init__(self):
        self.strokes: List[Stroke] = []
        self.current_stroke: Optional[Stroke] = None
        self.start_time: float = time.time()
        self.last_update_time: float = time.time()
        self.state: str = "IDLE"  # IDLE | WRITING | PAUSED | CONFIRMED

    def add_point(self, pt_px: Tuple[int, int]):
        now_ms = time.time() * 1000.0
        self.last_update_time = time.time()

        if self.current_stroke is None:
            self.current_stroke = []
            self.strokes.append(self.current_stroke)

        # Avoid storing identical consecutive coordinates
        if not self.current_stroke or (self.current_stroke[-1][0], self.current_stroke[-1][1]) != pt_px:
            self.current_stroke.append((pt_px[0], pt_px[1], now_ms))

    def pause_stroke(self):
        """Pauses recording (PEN_UP) without clearing strokes or finishing the session."""
        self.current_stroke = None
        self.state = "PAUSED"

    def get_all_points(self) -> List[PointWithTime]:
        all_pts = []
        for s in self.strokes:
            all_pts.extend(s)
        return all_pts

    def get_total_point_count(self) -> int:
        return sum(len(s) for s in self.strokes)


class WordTrajectoryEngine:
    """
    Manages continuous multi-stroke word writing sessions.
    
    Guarantees:
      1. ✊ PEN_UP pauses current stroke, NEVER triggers recognition.
      2. ☝️ WRITE resumes/continues word writing across multiple strokes.
      3. ✌️ CONFIRM freezes trajectory, triggers recognition exactly once, and resets engine.
    """
    def __init__(self):
        self.session: Optional[WordSession] = None
        self.last_recognized_word: Optional[str] = None
        self.last_confidence: float = 0.0
        self.last_features: Dict[str, Any] = {}
        self.last_strokes: List[List[Tuple[int, int]]] = []
        self.last_rendered_image = None
        self.last_status = "IDLE"

    def _extract_strokes(self, session: WordSession) -> List[List[Tuple[int, int]]]:
        drawable_strokes = []
        for stroke in session.strokes:
            drawable_strokes.append([(pt[0], pt[1]) for pt in stroke])
        return drawable_strokes

    def update(
        self,
        gesture_state: str,
        fingertip_px: Optional[Tuple[int, int]],
        processor: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Updates word session state based on gesture input.
        Returns status report dict for UI & debug logging.
        """
        result_event = {"event": "IDLE", "word": None, "confidence": 0.0}

        if gesture_state == "WRITE" and fingertip_px is not None:
            if self.session is None or self.session.state == "CONFIRMED":
                self.session = WordSession()
                self.last_strokes = []
            
            self.session.state = "WRITING"
            self.session.add_point(fingertip_px)
            self.last_strokes = self._extract_strokes(self.session)
            result_event["event"] = "WRITING"

        elif gesture_state == "CONFIRM":
            if self.session is not None and self.session.get_total_point_count() > 0:
                self.session.state = "CONFIRMED"
                drawable_strokes = self.get_strokes_to_draw()
                self.last_strokes = list(drawable_strokes)
                
                # Execute recognition engine if provided
                if processor is not None:
                    if hasattr(processor, "recognize"):
                        rec_res = processor.recognize(drawable_strokes)
                        self.last_recognized_word = rec_res.text
                        self.last_confidence = rec_res.confidence
                        self.last_status = rec_res.status
                        self.last_rendered_image = rec_res.rendered_image
                        self.last_debug_info = rec_res.debug_info
                    elif hasattr(processor, "process"):
                        proc_res = processor.process(self.session)
                        self.last_recognized_word = proc_res["word"]
                        self.last_confidence = proc_res["confidence"]
                        self.last_status = "RECOGNIZED"
                        self.last_rendered_image = None
                        self.last_debug_info = proc_res.get("features", {})
                else:
                    self.last_recognized_word = "WORD_CAPTURED"
                    self.last_confidence = 1.0
                    self.last_status = "RECOGNIZED"
                    self.last_rendered_image = None
                    self.last_debug_info = {}

                result_event = {
                    "event": "CONFIRMED",
                    "word": self.last_recognized_word,
                    "confidence": self.last_confidence,
                    "status": getattr(self, "last_status", "RECOGNIZED"),
                    "rendered_image": getattr(self, "last_rendered_image", None),
                    "debug_info": getattr(self, "last_debug_info", {})
                }

                # Reset active session cleanly after confirmation to prevent cross-word contamination,
                # while retaining last_strokes for visual display until next write
                self.session = None
            else:
                result_event["event"] = "CONFIRM_EMPTY"

        elif gesture_state == "CLEAR":
            self.clear()
            result_event["event"] = "CLEARED"

        else:
            # PEN_UP or NEUTRAL gesture
            if self.session is not None:
                self.session.pause_stroke()
                self.last_strokes = self._extract_strokes(self.session)
                result_event["event"] = "PAUSED"

        return result_event

    def clear(self):
        """Completely resets active session and recognition memory."""
        self.session = None
        self.last_recognized_word = None
        self.last_confidence = 0.0
        self.last_features = {}
        self.last_strokes = []
        self.last_rendered_image = None

    def get_strokes_to_draw(self) -> List[List[Tuple[int, int]]]:
        """Returns simplified (x, y) stroke tuples for rendering."""
        if self.session is not None:
            return self._extract_strokes(self.session)
        return self.last_strokes
