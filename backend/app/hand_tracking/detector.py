import cv2
import mediapipe as mp
from typing import List, Dict, Any, Tuple, Optional
from app.config.settings import settings

class HandDetector:
    """Wrapper around MediaPipe Hands solution for multi-hand tracking."""
    def __init__(
        self,
        max_num_hands: int = settings.MAX_NUM_HANDS,
        min_detection_confidence: float = settings.MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence: float = settings.MIN_TRACKING_CONFIDENCE,
        model_complexity: int = settings.MODEL_COMPLEXITY
    ):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def process(self, frame_bgr: cv2.Mat) -> List[Dict[str, Any]]:
        """
        Processes BGR image frame and extracts landmark coordinates for all detected hands.
        Returns a list of dictionaries per hand containing:
          - hand_id: int index (0 or 1)
          - label: "Left" or "Right"
          - landmarks_norm: List of (x, y, z) normalized coordinates (0 to 1)
          - landmarks_pixel: List of (x, y) integer pixel coordinates
          - raw_mp_landmarks: Original mp landmark object for drawing
        """
        h, w, _ = frame_bgr.shape
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        detected_hands = []
        if results.multi_hand_landmarks and results.multi_handedness:
            for idx, (hand_landmarks, handedness) in enumerate(zip(results.multi_hand_landmarks, results.multi_handedness)):
                label = handedness.classification[0].label  # "Left" or "Right"
                score = handedness.classification[0].score

                landmarks_norm = []
                landmarks_pixel = []
                for lm in hand_landmarks.landmark:
                    landmarks_norm.append((lm.x, lm.y, lm.z))
                    px_x = int(lm.x * w)
                    px_y = int(lm.y * h)
                    landmarks_pixel.append((px_x, px_y))

                detected_hands.append({
                    "hand_id": idx,
                    "label": label,
                    "score": score,
                    "landmarks_norm": landmarks_norm,
                    "landmarks_pixel": landmarks_pixel,
                    "raw_mp_landmarks": hand_landmarks
                })

        return detected_hands

    def draw_landmarks(
        self,
        frame: cv2.Mat,
        hand_data: Dict[str, Any],
        is_writing_active: bool = False
    ) -> cv2.Mat:
        """Renders custom hand skeleton with distinct color coding."""
        mp_landmarks = hand_data["raw_mp_landmarks"]
        
        # Define connection colors: Neon Cyan for active writing, Amber/Blue for non-writing hands
        if is_writing_active:
            connection_spec = self.mp_draw.DrawingSpec(color=(255, 230, 0), thickness=3) # Cyan/Yellow glow
            landmark_spec = self.mp_draw.DrawingSpec(color=(0, 255, 255), thickness=4, circle_radius=4)
        else:
            connection_spec = self.mp_draw.DrawingSpec(color=(200, 150, 50), thickness=2)
            landmark_spec = self.mp_draw.DrawingSpec(color=(255, 120, 0), thickness=3, circle_radius=3)

        self.mp_draw.draw_landmarks(
            frame,
            mp_landmarks,
            self.mp_hands.HAND_CONNECTIONS,
            landmark_drawing_spec=landmark_spec,
            connection_drawing_spec=connection_spec
        )
        return frame

    def close(self):
        """Releases MediaPipe resources."""
        self.hands.close()
