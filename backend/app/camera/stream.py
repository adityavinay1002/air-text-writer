import cv2
import time
import logging
from typing import Optional, Tuple
from app.config.settings import settings

logger = logging.getLogger(__name__)

class CameraStream:
    """Manages OpenCV webcam VideoCapture device."""
    def __init__(self, camera_index: int = settings.CAMERA_INDEX, width: int = settings.FRAME_WIDTH, height: int = settings.FRAME_HEIGHT):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap: Optional[cv2.VideoCapture] = None
        self.prev_frame_time = time.time()
        self.fps = 0.0

    def start(self) -> bool:
        """Initializes and opens the camera stream using DirectShow."""
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            logger.error(f"Unable to open camera index {self.camera_index} with CAP_DSHOW")
            return False

        # Try requesting requested resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        # Query actual resolution granted by the driver
        actual_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if actual_w > 0 and actual_h > 0:
            self.width = actual_w
            self.height = actual_h

        logger.info(f"Camera opened on index {self.camera_index} using CAP_DSHOW ({self.width}x{self.height})")
        return True

    def read_frame(self) -> Tuple[bool, Optional[cv2.Mat]]:
        """Reads a single frame and updates FPS calculation."""
        if self.cap is None or not self.cap.isOpened():
            return False, None

        ret, frame = self.cap.read()
        if not ret or frame is None:
            return False, None

        # Flip horizontally for natural mirror preview
        frame = cv2.flip(frame, 1)

        # Update FPS calculation
        curr_time = time.time()
        time_diff = curr_time - self.prev_frame_time
        if time_diff > 0:
            self.fps = 0.9 * self.fps + 0.1 * (1.0 / time_diff)
        self.prev_frame_time = curr_time

        return True, frame

    def release(self):
        """Safely closes the camera capture."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            logger.info("Camera capture released.")
