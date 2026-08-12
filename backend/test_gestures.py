import os
import sys

# Add backend root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.gestures.classifier import PalmAwareGestureClassifier, GestureState
from app.gestures.stabilizer import MultiHandStabilizer

def generate_landmarks(index_up=False, middle_up=False, ring_up=False, pinky_up=False):
    """Generates synthetic 21-point normalized landmark array."""
    # Base wrist at (0.5, 0.8, 0.0)
    landmarks = [(0.5, 0.8, 0.0)] * 21

    # Wrist: 0
    landmarks[0] = (0.5, 0.8, 0.0)

    # MCPs
    landmarks[5] = (0.45, 0.5, 0.0)   # Index MCP
    landmarks[9] = (0.50, 0.5, 0.0)   # Middle MCP
    landmarks[13] = (0.55, 0.5, 0.0)  # Ring MCP
    landmarks[17] = (0.60, 0.5, 0.0)  # Pinky MCP

    # PIPs
    landmarks[6] = (0.45, 0.4, 0.0)   # Index PIP
    landmarks[10] = (0.50, 0.4, 0.0)  # Middle PIP
    landmarks[14] = (0.55, 0.4, 0.0)  # Ring PIP
    landmarks[18] = (0.60, 0.4, 0.0)  # Pinky PIP

    # DIPs
    landmarks[7] = (0.45, 0.35, 0.0)  # Index DIP
    landmarks[11] = (0.50, 0.35, 0.0) # Middle DIP
    landmarks[15] = (0.55, 0.35, 0.0) # Ring DIP
    landmarks[19] = (0.60, 0.35, 0.0) # Pinky DIP

    # Tips
    landmarks[8] = (0.45, 0.2, 0.0) if index_up else (0.45, 0.6, 0.0)    # Index TIP
    landmarks[12] = (0.50, 0.2, 0.0) if middle_up else (0.50, 0.6, 0.0)  # Middle TIP
    landmarks[16] = (0.55, 0.2, 0.0) if ring_up else (0.55, 0.6, 0.0)    # Ring TIP
    landmarks[20] = (0.60, 0.2, 0.0) if pinky_up else (0.60, 0.6, 0.0)   # Pinky TIP

    # Thumb
    landmarks[1] = (0.40, 0.7, 0.0)
    landmarks[2] = (0.38, 0.65, 0.0)
    landmarks[3] = (0.36, 0.60, 0.0)
    landmarks[4] = (0.34, 0.55, 0.0)

    return landmarks

def test_classifier():
    print("Running Classifier Sanity Unit Tests...")

    # Test 1: WRITE (☝️)
    write_lm = generate_landmarks(index_up=True)
    res_write = PalmAwareGestureClassifier.classify_hand(write_lm)
    assert res_write["gesture"] == GestureState.WRITE, f"Expected WRITE, got {res_write['gesture']}"
    print("  [PASS] WRITE detected correctly")

    # Test 2: PEN_UP
    pen_up_lm = generate_landmarks()
    res_pen_up = PalmAwareGestureClassifier.classify_hand(pen_up_lm)
    assert res_pen_up["gesture"] == GestureState.PEN_UP, f"Expected PEN_UP, got {res_pen_up['gesture']}"
    print("  [PASS] PEN_UP detected correctly")

    # Test 3: CONFIRM
    confirm_lm = generate_landmarks(index_up=True, middle_up=True)
    res_confirm = PalmAwareGestureClassifier.classify_hand(confirm_lm)
    assert res_confirm["gesture"] == GestureState.CONFIRM, f"Expected CONFIRM, got {res_confirm['gesture']}"
    print("  [PASS] CONFIRM detected correctly (NOT WRITE)")

    # Test 4: CLEAR
    clear_lm = generate_landmarks(index_up=True, middle_up=True, ring_up=True, pinky_up=True)
    res_clear = PalmAwareGestureClassifier.classify_hand(clear_lm)
    assert res_clear["gesture"] == GestureState.CLEAR, f"Expected CLEAR, got {res_clear['gesture']}"
    print("  [PASS] CLEAR detected correctly (NOT WRITE)")

    # Test 5: Multi-hand Independent Tracking Test
    stabilizer = MultiHandStabilizer()
    for _ in range(5):
        st_right = stabilizer.update("Right_0", GestureState.WRITE)
        st_left = stabilizer.update("Left_1", GestureState.CONFIRM)

    assert st_right == GestureState.WRITE, f"Expected Right_0 to be WRITE, got {st_right}"
    assert st_left == GestureState.CONFIRM, f"Expected Left_1 to be CONFIRM, got {st_left}"
    print("  [PASS] Dual Hand Independent Tracking verified (Left=CONFIRM, Right=WRITE)")

    print("\nALL CLASSIFIER AND STABILIZER UNIT TESTS PASSED SUCCESSFULLY!\n")

if __name__ == "__main__":
    test_classifier()
