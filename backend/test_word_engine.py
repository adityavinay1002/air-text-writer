import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.trajectory.engine import WordTrajectoryEngine
from app.trajectory.processor import GeometricWordProcessor

def test_word_engine():
    print("Running Phase 2 Word Engine Unit Tests...")
    engine = WordTrajectoryEngine()
    processor = GeometricWordProcessor()

    # 1. ☝️ WRITE stroke 1 (Letter 'A' left leg)
    engine.update("WRITE", (100, 300))
    engine.update("WRITE", (150, 100))
    res1 = engine.update("WRITE", (200, 300))

    assert res1["event"] == "WRITING", f"Expected WRITING event, got {res1['event']}"
    assert engine.session is not None, "Session should be active"
    assert len(engine.session.strokes) == 1, f"Expected 1 stroke, got {len(engine.session.strokes)}"
    assert engine.session.get_total_point_count() == 3, "Expected 3 points"
    print("  [PASS] [WRITE] Stroke 1 recorded (3 points)")

    # 2. PEN_UP (hand movement between letters/strokes)
    res2 = engine.update("PEN_UP", None)
    assert res2["event"] == "PAUSED", f"Expected PAUSED event, got {res2['event']}"
    assert res2["word"] is None, "PEN_UP MUST NEVER trigger word recognition!"
    assert engine.session is not None, "Session MUST remain active on PEN_UP"
    assert len(engine.session.strokes) == 1, "Stroke 1 must remain stored"
    print("  [PASS] [PEN_UP] Paused session without triggering recognition or clearing canvas")

    # 3. WRITE stroke 2 (Letter 'A' crossbar)
    engine.update("WRITE", (120, 200))
    res3 = engine.update("WRITE", (180, 200))
    assert res3["event"] == "WRITING", f"Expected WRITING event, got {res3['event']}"
    assert len(engine.session.strokes) == 2, f"Expected 2 separate strokes, got {len(engine.session.strokes)}"
    assert engine.session.get_total_point_count() == 5, "Expected 5 total points across 2 strokes"
    print("  [PASS] [WRITE] Stroke 2 appended to word session (Total strokes: 2, Total points: 5)")

    # 4. CONFIRM (Word confirmation trigger)
    res4 = engine.update("CONFIRM", None, processor=processor)
    assert res4["event"] == "CONFIRMED", f"Expected CONFIRMED event, got {res4['event']}"
    assert res4["word"] in GeometricWordProcessor.DICTIONARY, f"Expected valid dictionary word, got {res4['word']}"
    assert res4["confidence"] > 0.0, "Expected non-zero confidence score"
    print(f"  [PASS] [CONFIRM] Processed complete word: '{res4['word']}' (Confidence: {res4['confidence']*100:.1f}%)")

    # 5. Verify Post-Confirmation State Reset
    assert engine.session is None, "Engine session MUST reset cleanly to None after confirmation!"
    print("  [PASS] Engine auto-reset completely; zero data contamination for next word")

    # 6. Start Next Word (verify clean state)
    engine.update("WRITE", (50, 50))
    assert len(engine.session.strokes) == 1, "New word session started cleanly with 1 stroke"
    assert engine.session.get_total_point_count() == 1, "New session contains only new point"
    print("  [PASS] New word trajectory started cleanly without previous word contamination")

    print("\nALL PHASE 2 WORD ENGINE UNIT TESTS PASSED SUCCESSFULLY!\n")

if __name__ == "__main__":
    test_word_engine()
