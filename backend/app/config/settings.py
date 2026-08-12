class Settings:
    # Camera settings
    CAMERA_INDEX: int = 0
    FRAME_WIDTH: int = 1280
    FRAME_HEIGHT: int = 720
    FPS_LIMIT: int = 30

    # MediaPipe Hands settings
    MAX_NUM_HANDS: int = 2
    MIN_DETECTION_CONFIDENCE: float = 0.7
    MIN_TRACKING_CONFIDENCE: float = 0.7
    MODEL_COMPLEXITY: int = 1

    # Stabilizer / Debounce settings
    DEBOUNCE_WINDOW_SIZE: int = 5
    TRANSITION_THRESHOLD: int = 4

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

settings = Settings()
