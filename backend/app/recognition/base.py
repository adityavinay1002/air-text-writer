from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional
import numpy as np

@dataclass
class RecognitionResult:
    """Standardized output structure from recognition engines."""
    text: str
    confidence: float
    status: str  # RECOGNIZED | LOW_CONFIDENCE | INSUFFICIENT_INPUT
    alternatives: List[Tuple[str, float]] = field(default_factory=list)
    rendered_image: Optional[np.ndarray] = None
    debug_info: Dict[str, Any] = field(default_factory=dict)


class BaseRecognitionEngine(ABC):
    """Abstract interface for all handwriting & OCR recognition engines."""
    
    @abstractmethod
    def recognize(self, strokes: List[List[Tuple[int, int]]]) -> RecognitionResult:
        """
        Processes a multi-stroke trajectory list and returns a RecognitionResult.
        Each stroke is a list of (x_pixel, y_pixel) coordinate tuples.
        """
        pass
