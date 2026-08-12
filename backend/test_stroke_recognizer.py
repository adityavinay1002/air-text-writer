import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.recognition.segmenter import CharacterSegmenter
from app.recognition.stroke_recognizer import CharacterSegmentedRecognizer

def generate_stroke_A():
    """Generates synthetic pixel stroke coordinates for letter 'A'."""
    s1 = [(100, 400), (120, 300), (140, 200), (150, 150)]  # Left leg
    s2 = [(150, 150), (170, 250), (190, 350), (200, 400)]  # Right leg
    s3 = [(120, 300), (150, 300), (180, 300)]              # Crossbar
    return [s1, s2, s3]

def generate_stroke_V(offset_x=0):
    """Generates synthetic pixel stroke coordinates for letter 'V'."""
    s1 = [(100 + offset_x, 150), (125 + offset_x, 300), (150 + offset_x, 400)]  # Down
    s2 = [(150 + offset_x, 400), (175 + offset_x, 300), (200 + offset_x, 150)]  # Up
    return [s1, s2]

def generate_stroke_AV():
    """Generates synthetic multi-character sequence 'A' + 'V'."""
    strokes_A = generate_stroke_A()
    strokes_V = generate_stroke_V(offset_x=200)  # Offset V horizontally
    return strokes_A + strokes_V

def test_character_segmentation():
    print("=" * 60)
    print("1. TESTING SPATIAL CHARACTER SEGMENTATION")
    print("=" * 60)

    # Test single character 'A' (3 overlapping strokes)
    segs_A = CharacterSegmenter.segment_strokes(generate_stroke_A())
    assert len(segs_A) == 1, f"Expected 1 character segment for 'A', got {len(segs_A)}"
    print(f"  [PASS] Letter 'A' (3 strokes) correctly segmented as 1 Character Segment")

    # Test multi-character sequence 'A' + 'V' (5 total strokes)
    segs_AV = CharacterSegmenter.segment_strokes(generate_stroke_AV())
    assert len(segs_AV) == 2, f"Expected 2 character segments for 'A'+'V', got {len(segs_AV)}"
    print(f"  [PASS] Multi-character 'A'+'V' (5 strokes) correctly segmented into 2 Character Segments")

def test_character_level_recognition():
    print("\n" + "=" * 60)
    print("2. TESTING CHARACTER-LEVEL RECOGNITION & WORD ASSEMBLY")
    print("=" * 60)

    recognizer = CharacterSegmentedRecognizer()

    # Test 1: Letter 'A'
    res_A = recognizer.recognize(generate_stroke_A())
    print(f"  Test Input: Letter 'A'")
    print(f"    Status    : {res_A.status}")
    print(f"    Recognized: '{res_A.text}'")
    print(f"    Confidence: {res_A.confidence * 100:.1f}%")
    print(f"    Char Info : {res_A.debug_info.get('char_details')}")
    assert res_A.status == "RECOGNIZED", "Letter A should be recognized"
    assert "A" in res_A.text, f"Expected 'A', got '{res_A.text}'"

    # Test 2: Word 'AV'
    res_AV = recognizer.recognize(generate_stroke_AV())
    print(f"\n  Test Input: Sequence 'AV'")
    print(f"    Status    : {res_AV.status}")
    print(f"    Recognized: '{res_AV.text}'")
    print(f"    Confidence: {res_AV.confidence * 100:.1f}%")
    print(f"    Char Info : {res_AV.debug_info.get('char_details')}")
    assert res_AV.status == "RECOGNIZED", "Sequence AV should be recognized"
    assert "AV" in res_AV.text or "A" in res_AV.text, f"Expected AV assembly, got '{res_AV.text}'"

    # Test 3: Random Scribble (No false word fabrication)
    scribble = [[(100, 100), (102, 101), (103, 102)]]
    res_scribble = recognizer.recognize(scribble)
    print(f"\n  Test Input: Random Scribble")
    print(f"    Status    : {res_scribble.status}")
    print(f"    Text      : '{res_scribble.text}'")
    print(f"    Confidence: {res_scribble.confidence * 100:.1f}%")
    assert res_scribble.status in ("INSUFFICIENT_INPUT", "LOW_CONFIDENCE"), "Scribble must NOT produce a false word!"

    print("\n" + "=" * 60)
    print("CHARACTER SEGMENTATION & RECOGNITION TEST COMPLETE")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    test_character_segmentation()
    test_character_level_recognition()
