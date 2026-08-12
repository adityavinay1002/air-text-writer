import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.trajectory.tracker import TrajectoryTracker

def test_trajectory_tracker():
    print("Running Trajectory Tracker Unit Tests...")
    tracker = TrajectoryTracker()

    # 1. Start Stroke 1 (WRITE)
    tracker.update("WRITE", (100, 100))
    tracker.update("WRITE", (105, 110))
    tracker.update("WRITE", (110, 120))

    assert len(tracker.strokes) == 1, f"Expected 1 stroke, got {len(tracker.strokes)}"
    assert len(tracker.strokes[0]) == 3, f"Expected 3 points in stroke 1, got {len(tracker.strokes[0])}"
    print("  [PASS] Stroke 1 trajectory recorded successfully (3 points)")

    # 2. Transition to PEN_UP (Fist)
    tracker.update("PEN_UP", None)
    assert len(tracker.strokes) == 1, "Stroke 1 should remain visible on PEN_UP"
    assert tracker.current_stroke is None, "current_stroke should be reset to None on PEN_UP"
    print("  [PASS] PEN_UP finalized stroke 1 and kept it visible")

    # 3. Start Stroke 2 (WRITE again)
    tracker.update("WRITE", (200, 200))
    tracker.update("WRITE", (210, 210))

    assert len(tracker.strokes) == 2, f"Expected 2 separate strokes, got {len(tracker.strokes)}"
    assert len(tracker.strokes[0]) == 3, "Stroke 1 length should remain 3"
    assert len(tracker.strokes[1]) == 2, "Stroke 2 length should be 2"
    assert tracker.strokes[0][-1] != tracker.strokes[1][0], "Strokes must NOT be connected!"
    print("  [PASS] Stroke 2 created independently without connecting to stroke 1")

    # 4. Transition to CONFIRM (2 fingers) -> Canvas clear
    tracker.update("CONFIRM", None)
    assert len(tracker.strokes) == 0, f"Expected empty strokes on CONFIRM, got {len(tracker.strokes)}"
    assert tracker.get_point_count() == 0, "Point count should be 0 on clear"
    print("  [PASS] CONFIRM successfully cleared trajectory canvas")

    print("\nALL TRAJECTORY TRACKER UNIT TESTS PASSED SUCCESSFULLY!\n")

if __name__ == "__main__":
    test_trajectory_tracker()
