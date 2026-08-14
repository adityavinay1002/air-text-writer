import os
import sys
import logging

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.gestures.classifier import PalmAwareGestureClassifier, GestureState
from app.trajectory.engine import WordTrajectoryEngine
from app.trajectory.tracker import TrajectoryTracker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TestActionMapping")

def test_letter_by_letter_workflow():
    print("=" * 75)
    print("TESTING PHASE 7.2.2 END-TO-END LETTER-BY-LETTER ACTION MAPPING")
    print("=" * 75)

    engine = WordTrajectoryEngine()
    tracker = TrajectoryTracker()

    # Step 1: Write Letter 'A'
    res1 = engine.update("WRITE", (100, 100))
    tracker.update("WRITE", (100, 100))
    assert engine.session is not None, "WRITE must start an active session"
    assert engine.session.get_total_point_count() == 1, "Point 1 ('A') recorded"
    print("  [PASS] Step 1: WRITE 'A' recorded point (100, 100)")

    # Step 2: Open Palm (PEN_UP)
    res2 = engine.update("PEN_UP", None)
    tracker.update("PEN_UP", None)
    assert res2["event"] == "PAUSED", "OPEN PALM must trigger PAUSED / PEN_UP"
    assert engine.session is not None, "OPEN PALM MUST NEVER clear or destroy session!"
    assert len(engine.session.strokes) == 1, "Stroke 1 ('A') MUST remain intact in session!"
    assert len(tracker.strokes) == 1, "Stroke 1 ('A') MUST remain visible on tracker!"
    print("  [PASS] Step 2: Open Palm (PEN_UP) paused stroke; 'A' REMAINS VISIBLE")

    # Step 3: Write Letter 'D'
    res3 = engine.update("WRITE", (200, 200))
    tracker.update("WRITE", (200, 200))
    assert len(engine.session.strokes) == 2, "Stroke 2 ('D') appended to active session"
    assert len(tracker.strokes) == 2, "Both strokes ('AD') visible on tracker"
    print("  [PASS] Step 3: WRITE 'D' appended stroke 2; 'AD' accumulated")

    # Step 4: Open Palm (PEN_UP)
    res4 = engine.update("PEN_UP", None)
    tracker.update("PEN_UP", None)
    assert len(engine.session.strokes) == 2, "'AD' MUST remain intact on OPEN PALM"
    print("  [PASS] Step 4: Open Palm (PEN_UP) paused stroke; 'AD' REMAINS VISIBLE")

    # Step 5: Write Letter 'I'
    engine.update("WRITE", (300, 300))
    tracker.update("WRITE", (300, 300))
    engine.update("PEN_UP", None)
    tracker.update("PEN_UP", None)
    assert len(engine.session.strokes) == 3, "'ADI' accumulated"
    print("  [PASS] Step 5: WRITE 'I' + Open Palm; 'ADI' REMAINS VISIBLE")

    # Step 6: Write Letter 'T'
    engine.update("WRITE", (400, 400))
    tracker.update("WRITE", (400, 400))
    engine.update("PEN_UP", None)
    tracker.update("PEN_UP", None)
    assert len(engine.session.strokes) == 4, "'ADIT' accumulated"
    print("  [PASS] Step 6: WRITE 'T' + Open Palm; 'ADIT' REMAINS VISIBLE")

    # Step 7: Fist (CLEAR)
    res7 = engine.update("CLEAR", None)
    tracker.update("CLEAR", None)
    assert res7["event"] == "CLEARED", "FIST must trigger CLEARED event"
    assert engine.session is None, "FIST MUST completely reset word session!"
    assert len(tracker.strokes) == 0, "FIST MUST completely clear all tracker strokes!"
    print("  [PASS] Step 7: Fist (CLEAR) completely reset accumulated session & canvas!")

    # Step 8: Fresh Write After FIST
    engine.update("WRITE", (500, 500))
    tracker.update("WRITE", (500, 500))
    assert engine.session is not None, "Fresh WRITE after FIST starts a new session"
    assert len(engine.session.strokes) == 1, "Fresh session has 1 stroke (no previous contamination)"
    print("  [PASS] Step 8: WRITE after FIST started completely fresh session")

    # Step 9: Confirm (CONFIRM)
    res9 = engine.update("CONFIRM", None)
    assert res9["event"] == "CONFIRMED", "CONFIRM triggered CONFIRMED event"
    assert engine.session is None, "CONFIRM resets session cleanly after confirmation"
    print("  [PASS] Step 9: CONFIRM processed complete word and reset session cleanly")

    print("\n" + "=" * 75)
    print("ALL PHASE 7.2.2 END-TO-END ACTION MAPPING TESTS PASSED SUCCESSFULLY!")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    test_letter_by_letter_workflow()
