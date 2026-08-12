import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.recognition.render import TrajectoryRenderer
from app.recognition.ocr_engine import RapidOCREngine

def generate_stroke_A():
    """Generates synthetic pixel stroke coordinates for letter 'A'."""
    # Stroke 1: Left leg (bottom to top)
    s1 = [(150, 400), (160, 350), (170, 300), (180, 250), (190, 200), (200, 150)]
    # Stroke 2: Right leg (top to bottom)
    s2 = [(200, 150), (210, 200), (220, 250), (230, 300), (240, 350), (250, 400)]
    # Stroke 3: Crossbar
    s3 = [(170, 300), (190, 300), (210, 300), (230, 300)]
    return [s1, s2, s3]

def generate_stroke_I():
    """Generates synthetic pixel stroke coordinates for letter 'I'."""
    # Vertical line
    s1 = [(250, 150), (250, 200), (250, 250), (250, 300), (250, 350), (250, 400)]
    # Top bar
    s2 = [(200, 150), (250, 150), (300, 150)]
    # Bottom bar
    s3 = [(200, 400), (250, 400), (300, 400)]
    return [s1, s2, s3]

def generate_scribble():
    """Generates a tiny ambiguous scribble."""
    s1 = [(200, 200), (202, 201), (203, 202)]
    return [s1]

def test_renderer_and_validation():
    print("=" * 60)
    print("1. TESTING TRAJECTORY RENDERER & VALIDATION LAYER")
    print("=" * 60)

    # Empty test
    valid, info = TrajectoryRenderer.validate_and_get_bbox([])
    assert not valid, "Empty strokes must be invalid"
    print("  [PASS] Empty stroke rejected (INSUFFICIENT_INPUT)")

    # Tiny scribble test
    valid_scribble, info_scribble = TrajectoryRenderer.validate_and_get_bbox(generate_scribble())
    assert not valid_scribble, "Tiny scribble must be invalid"
    print(f"  [PASS] Tiny scribble rejected ({info_scribble['reason']})")

    # Valid letter A render test
    canvas, info_A = TrajectoryRenderer.render_to_canvas(generate_stroke_A())
    assert canvas is not None, "Canvas rendering failed"
    assert canvas.shape == (512, 512, 3), "Canvas shape must be 512x512x3"
    print(f"  [PASS] Letter 'A' rendered successfully to 512x512 canvas (BBox: {info_A['width']}x{info_A['height']}px)")

def test_real_ocr_performance():
    print("\n" + "=" * 60)
    print("2. MEASURING REAL OFF-THE-SHELF RAPIDOCR PERFORMANCE")
    print("=" * 60)

    engine = RapidOCREngine(min_confidence=0.45)
    if not engine.ocr_instance:
        print("  [SKIP] RapidOCR engine not available.")
        return

    test_cases = [
        ("Letter 'A'", generate_stroke_A()),
        ("Letter 'I'", generate_stroke_I()),
        ("Scribble", generate_scribble())
    ]

    for label, strokes in test_cases:
        res = engine.recognize(strokes)
        print(f"\nTest Input: {label}")
        print(f"  Status    : {res.status}")
        print(f"  Text      : '{res.text}'")
        print(f"  Confidence: {res.confidence * 100:.1f}%")
        if res.debug_info.get("raw_ocr_output"):
            print(f"  Raw Output: {res.debug_info['raw_ocr_output']}")

    print("\n" + "=" * 60)
    print("OFF-THE-SHELF OCR VALIDATION TEST COMPLETE")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    test_renderer_and_validation()
    test_real_ocr_performance()
