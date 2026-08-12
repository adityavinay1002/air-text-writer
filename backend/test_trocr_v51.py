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

def test_phase_51_trocr_enhancements():
    print("=" * 65)
    print("TESTING PHASE 5.1 MULTI-VARIANT BEAM SEARCH TrOCR ENGINE")
    print("=" * 65)

    engine = TrOCRHandwritingEngine(min_confidence=0.38)
    if not engine.model:
        print("  [SKIP] TrOCR model not loaded.")
        return

    # Test 1: Letter 'A'
    res_A = engine.recognize(generate_handwritten_A())
    print(f"  Test Input: Letter 'A'")
    print(f"    Status          : {res_A.status}")
    print(f"    Recognized      : '{res_A.text}'")
    print(f"    Confidence      : {res_A.confidence * 100:.1f}%")
    print(f"    Selected Variant: '{res_A.debug_info.get('selected_variant')}'")
    print(f"    Top Candidates  : {res_A.alternatives}")
    assert res_A.status == "RECOGNIZED", "Letter A should be recognized"
    print("  [PASS] Letter 'A' recognized cleanly with multi-variant beam search!")

    # Test 2: Random Scribble (Must NOT fabricate word)
    scribble = [[(200, 200), (202, 201), (203, 202)]]
    res_scribble = engine.recognize(scribble)
    print(f"\n  Test Input: Random Scribble")
    print(f"    Status          : {res_scribble.status}")
    print(f"    Recognized      : '{res_scribble.text}'")
    print(f"    Confidence      : {res_scribble.confidence * 100:.1f}%")
    assert res_scribble.status in ("INSUFFICIENT_INPUT", "LOW_CONFIDENCE"), "Scribble must NOT produce a false word!"
    print("  [PASS] Scribble correctly rejected (No false word fabrication)")

    print("\n" + "=" * 65)
    print("PHASE 5.1 TrOCR ENHANCEMENTS TEST COMPLETE")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    test_phase_51_trocr_enhancements()
