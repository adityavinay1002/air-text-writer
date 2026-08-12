import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.recognition.canvas import VirtualHandwritingCanvas
from app.recognition.trocr_engine import TrOCRHandwritingEngine

def generate_handwritten_A():
    """Generates synthetic pixel stroke coordinates for letter 'A'."""
    s1 = [(200, 500), (230, 400), (260, 300), (280, 200)]  # Left leg
    s2 = [(280, 200), (300, 300), (320, 400), (340, 500)]  # Right leg
    s3 = [(230, 380), (280, 380), (310, 380)]              # Crossbar
    return [s1, s2, s3]

def test_virtual_canvas_cropping():
    print("=" * 65)
    print("1. TESTING VIRTUAL HANDWRITING CANVAS & AUTO-CROPPING")
    print("=" * 65)

    canvas = VirtualHandwritingCanvas()
    
    # Test empty canvas
    cropped_empty, info_empty = canvas.crop_handwriting()
    assert cropped_empty is None, "Empty canvas must return None"
    print("  [PASS] Empty canvas auto-crop returned None (INSUFFICIENT_INPUT)")

    # Draw strokes for 'A'
    for s in generate_handwritten_A():
        canvas.add_point(s[0])
        for pt in s[1:]:
            canvas.add_point(pt)
        canvas.pause_stroke()

    cropped_A, info_A = canvas.crop_handwriting(padding=30)
    assert cropped_A is not None, "Cropping valid handwriting failed"
    assert info_A["bbox"][2] > 0 and info_A["bbox"][3] > 0, "BBox must have non-zero width and height"
    print(f"  [PASS] Handwriting auto-cropped successfully (BBox: {info_A['bbox'][2]}x{info_A['bbox'][3]}px, Resized shape: {info_A['resized_shape']})")

def test_trocr_engine_inference():
    print("\n" + "=" * 65)
    print("2. TESTING PRETRAINED Microsoft TrOCR HANDWRITING ENGINE")
    print("=" * 65)

    engine = TrOCRHandwritingEngine(min_confidence=0.40)
    if not engine.model:
        print("  [SKIP] TrOCR model not loaded.")
        return

    # Test 1: Letter 'A'
    res_A = engine.recognize(generate_handwritten_A())
    print(f"  Test Input: Letter 'A'")
    print(f"    Status    : {res_A.status}")
    print(f"    Recognized: '{res_A.text}'")
    print(f"    Confidence: {res_A.confidence * 100:.1f}%")
    print(f"    Raw Text  : '{res_A.debug_info.get('raw_trocr_text')}'")

    # Test 2: Random Scribble (Must NOT fabricate word)
    scribble = [[(200, 200), (202, 201), (203, 202)]]
    res_scribble = engine.recognize(scribble)
    print(f"\n  Test Input: Random Scribble")
    print(f"    Status    : {res_scribble.status}")
    print(f"    Recognized: '{res_scribble.text}'")
    print(f"    Confidence: {res_scribble.confidence * 100:.1f}%")
    assert res_scribble.status in ("INSUFFICIENT_INPUT", "LOW_CONFIDENCE"), "Scribble must NOT produce a false word!"
    print("  [PASS] Scribble correctly rejected (No false word fabrication)")

    print("\n" + "=" * 65)
    print("PHASE 5 TrOCR HANDWRITING ENGINE TEST COMPLETE")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    test_virtual_canvas_cropping()
    test_trocr_engine_inference()
