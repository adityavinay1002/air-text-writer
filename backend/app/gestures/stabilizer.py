from collections import deque, Counter
from typing import Dict
from app.config.settings import settings
from app.gestures.classifier import GestureState

class SingleHandStabilizer:
    """Stabilizes gesture predictions for a single hand using sliding-window voting."""
    def __init__(self, window_size: int = settings.DEBOUNCE_WINDOW_SIZE, threshold: int = settings.TRANSITION_THRESHOLD):
        self.window_size = window_size
        self.threshold = threshold
        self.history = deque(maxlen=window_size)
        self.current_state = GestureState.NEUTRAL

    def update(self, raw_gesture: str) -> str:
        self.history.append(raw_gesture)
        if len(self.history) < 3:
            return self.current_state

        counts = Counter(self.history)
        most_common_gesture, max_count = counts.most_common(1)[0]

        if max_count >= self.threshold:
            self.current_state = most_common_gesture

        return self.current_state

    def reset(self):
        self.history.clear()
        self.current_state = GestureState.NEUTRAL


class MultiHandStabilizer:
    """Manages independent gesture stabilizers per hand key (e.g., 'Left', 'Right', 'Hand_0', 'Hand_1')."""
    def __init__(self, window_size: int = settings.DEBOUNCE_WINDOW_SIZE, threshold: int = settings.TRANSITION_THRESHOLD):
        self.window_size = window_size
        self.threshold = threshold
        self.stabilizers: Dict[str, SingleHandStabilizer] = {}

    def get_stabilizer(self, hand_key: str) -> SingleHandStabilizer:
        if hand_key not in self.stabilizers:
            self.stabilizers[hand_key] = SingleHandStabilizer(self.window_size, self.threshold)
        return self.stabilizers[hand_key]

    def update(self, hand_key: str, raw_gesture: str) -> str:
        stabilizer = self.get_stabilizer(hand_key)
        return stabilizer.update(raw_gesture)

    def prune_missing(self, active_keys: list):
        """Removes stabilizers for hands no longer present in frame."""
        for key in list(self.stabilizers.keys()):
            if key not in active_keys:
                del self.stabilizers[key]
