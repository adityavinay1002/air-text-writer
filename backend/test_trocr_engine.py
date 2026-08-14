import os
import sys
import time
import math
import logging

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.recognition.canvas import VirtualHandwritingCanvas
from app.recognition.trocr_engine import TrOCRHandwritingEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Phase7-TrOCR-Benchmark")

# =====================================================================
# SYNTHETIC AIR-WRITING STROKE GENERATORS FOR BENCHMARK WORDS
# =====================================================================

def draw_letter_V(start_x, start_y, height=120, width=70):
    s1 = [(start_x, start_y), (start_x + width // 2, start_y + height)]
    s2 = [(start_x + width // 2, start_y + height), (start_x + width, start_y)]
    return [s1, s2]

def draw_letter_I(start_x, start_y, height=120, width=40):
    s1 = [(start_x + width // 2, start_y), (start_x + width // 2, start_y + height)]
    s2 = [(start_x + 5, start_y), (start_x + width - 5, start_y)]
    s3 = [(start_x + 5, start_y + height), (start_x + width - 5, start_y + height)]
    return [s1, s2, s3]

def draw_letter_N(start_x, start_y, height=120, width=70):
    s1 = [(start_x, start_y + height), (start_x, start_y)]
    s2 = [(start_x, start_y), (start_x + width, start_y + height)]
    s3 = [(start_x + width, start_y + height), (start_x + width, start_y)]
    return [s1, s2, s3]

def draw_letter_A(start_x, start_y, height=120, width=70):
    s1 = [(start_x, start_y + height), (start_x + width // 2, start_y)]
    s2 = [(start_x + width // 2, start_y), (start_x + width, start_y + height)]
    s3 = [(start_x + 15, start_y + int(height * 0.6)), (start_x + width - 15, start_y + int(height * 0.6))]
    return [s1, s2, s3]

def draw_letter_Y(start_x, start_y, height=120, width=70):
    s1 = [(start_x, start_y), (start_x + width // 2, start_y + height // 2)]
    s2 = [(start_x + width, start_y), (start_x + width // 2, start_y + height // 2)]
    s3 = [(start_x + width // 2, start_y + height // 2), (start_x + width // 2, start_y + height)]
    return [s1, s2, s3]

def draw_letter_T(start_x, start_y, height=120, width=70):
    s1 = [(start_x, start_y), (start_x + width, start_y)]
    s2 = [(start_x + width // 2, start_y), (start_x + width // 2, start_y + height)]
    return [s1, s2]

def draw_letter_R(start_x, start_y, height=120, width=70):
    s1 = [(start_x, start_y + height), (start_x, start_y)]
    s2 = [(start_x, start_y), (start_x + width - 10, start_y + 10), (start_x + width - 10, start_y + height // 2 - 10), (start_x, start_y + height // 2)]
    s3 = [(start_x + width // 3, start_y + height // 2), (start_x + width, start_y + height)]
    return [s1, s2, s3]

def draw_letter_H(start_x, start_y, height=120, width=70):
    s1 = [(start_x, start_y), (start_x, start_y + height)]
    s2 = [(start_x + width, start_y), (start_x + width, start_y + height)]
    s3 = [(start_x, start_y + height // 2), (start_x + width, start_y + height // 2)]
    return [s1, s2, s3]

def draw_letter_E(start_x, start_y, height=120, width=65):
    s1 = [(start_x + width, start_y), (start_x, start_y), (start_x, start_y + height), (start_x + width, start_y + height)]
    s2 = [(start_x, start_y + height // 2), (start_x + int(width * 0.8), start_y + height // 2)]
    return [s1, s2]

def draw_letter_L(start_x, start_y, height=120, width=60):
    s1 = [(start_x, start_y), (start_x, start_y + height), (start_x + width, start_y + height)]
    return [s1]

def draw_letter_O(start_x, start_y, height=120, width=70):
    pts = []
    cx, cy = start_x + width // 2, start_y + height // 2
    rx, ry = width // 2, height // 2
    for i in range(16):
        angle = 2 * math.pi * i / 16
        px = int(cx + rx * math.cos(angle))
        py = int(cy + ry * math.sin(angle))
        pts.append((px, py))
    pts.append(pts[0])
    return [pts]

def draw_letter_M(start_x, start_y, height=120, width=80):
    s1 = [(start_x, start_y + height), (start_x, start_y)]
    s2 = [(start_x, start_y), (start_x + width // 2, start_y + height // 2)]
    s3 = [(start_x + width // 2, start_y + height // 2), (start_x + width, start_y)]
    s4 = [(start_x + width, start_y), (start_x + width, start_y + height)]
    return [s1, s2, s3, s4]

def draw_letter_U(start_x, start_y, height=120, width=70):
    s1 = [(start_x, start_y), (start_x, start_y + height - 20), (start_x + 20, start_y + height), (start_x + width - 20, start_y + height), (start_x + width, start_y + height - 20), (start_x + width, start_y)]
    return [s1]

def draw_letter_D(start_x, start_y, height=120, width=70):
    s1 = [(start_x, start_y), (start_x, start_y + height)]
    s2 = [(start_x, start_y), (start_x + width - 15, start_y + 15), (start_x + width, start_y + height // 2), (start_x + width - 15, start_y + height - 15), (start_x, start_y + height)]
    return [s1, s2]

def draw_word(letters_fn_list, start_x=100, start_y=300, spacing=85):
    word_strokes = []
    curr_x = start_x
    for fn in letters_fn_list:
        strokes = fn(curr_x, start_y)
        word_strokes.extend(strokes)
        curr_x += spacing
    return word_strokes

# Map benchmark words to letter functions
BENCHMARK_TARGETS = {
    "VINAY": [draw_letter_V, draw_letter_I, draw_letter_N, draw_letter_A, draw_letter_Y],
    "AVATAR": [draw_letter_A, draw_letter_V, draw_letter_A, draw_letter_T, draw_letter_A, draw_letter_R],
    "HELLO": [draw_letter_H, draw_letter_E, draw_letter_L, draw_letter_L, draw_letter_O],
    "MOVIE": [draw_letter_M, draw_letter_O, draw_letter_V, draw_letter_I, draw_letter_E],
    "DISNEY": [draw_letter_D, draw_letter_I, draw_letter_S if 'draw_letter_S' in globals() else draw_letter_O, draw_letter_N, draw_letter_E, draw_letter_Y]
}

def compute_levenshtein(s1: str, s2: str) -> int:
    """Computes Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return compute_levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def test_canvas_autocrop():
    print("=" * 75)
    print("1. TESTING VIRTUAL HANDWRITING CANVAS & ASPECT-RATIO CROP")
    print("=" * 75)
    canvas = VirtualHandwritingCanvas()
    empty_crop, empty_info = canvas.crop_handwriting()
    assert empty_crop is None, "Empty canvas crop must return None"
    print("  [PASS] Empty canvas crop returned None (INSUFFICIENT_INPUT)")

    strokes_A = draw_word([draw_letter_A])
    for s in strokes_A:
        canvas.add_point(s[0])
        for pt in s[1:]:
            canvas.add_point(pt)
        canvas.pause_stroke()

    crop, info = canvas.crop_handwriting()
    assert crop is not None, "Valid handwriting crop failed"
    print(f"  [PASS] Handwriting cropped successfully (Padding: {info['padding_applied']}px, Aspect: {info['aspect_ratio']}, Resized: {info['resized_shape']})")

def test_trocr_phase7_benchmark():
    print("\n" + "=" * 75)
    print("2. EVALUATING PHASE 7 PRETRAINED Microsoft TrOCR RECOGNITION BENCHMARK")
    print("=" * 75)

    engine = TrOCRHandwritingEngine(min_confidence=0.38, export_debug=False)
    if not engine.model:
        print("  [SKIP] Microsoft TrOCR model not initialized.")
        return

    exact_matches = 0
    total_evals = 0
    total_latency = 0
    total_cer = 0.0

    benchmark_words = ["VINAY", "AVATAR", "HELLO", "MOVIE"]

    print(f"{'EXPECTED':<12} | {'RECOGNIZED':<14} | {'STATUS':<15} | {'CONF':<7} | {'VARIANT':<18} | {'LATENCY':<8} | {'MATCH'}")
    print("-" * 95)

    for word in benchmark_words:
        if word not in BENCHMARK_TARGETS:
            continue

        strokes = draw_word(BENCHMARK_TARGETS[word])
        
        t0 = time.time()
        res = engine.recognize(strokes)
        latency = int((time.time() - t0) * 1000)

        recognized_text = res.text
        status = res.status
        conf_pct = f"{res.confidence * 100:.1f}%"
        variant = res.debug_info.get("selected_variant", "N/A")
        
        edit_dist = compute_levenshtein(word, recognized_text)
        cer = edit_dist / float(len(word))
        is_exact = (word == recognized_text)

        if is_exact:
            exact_matches += 1
            match_str = "[PASS] EXACT"
        else:
            match_str = f"[DIFF] CER: {cer*100:.0f}%"

        total_evals += 1
        total_latency += latency
        total_cer += cer

        print(f"{word:<12} | {recognized_text:<14} | {status:<15} | {conf_pct:<7} | {variant:<18} | {latency:<6}ms | {match_str}")

    print("-" * 95)
    avg_latency = total_latency / float(max(1, total_evals))
    avg_cer = total_cer / float(max(1, total_evals))
    accuracy_pct = (exact_matches / float(max(1, total_evals))) * 100

    print(f"\n=========================================================================")
    print(f"PHASE 7 BENCHMARK SUMMARY RESULTS:")
    print(f"  - Total Benchmark Evaluation Targets: {total_evals}")
    print(f"  - Exact Match Accuracy              : {accuracy_pct:.1f}% ({exact_matches}/{total_evals})")
    print(f"  - Average Character Error Rate (CER): {avg_cer * 100:.1f}%")
    print(f"  - Average Inference Latency         : {avg_latency:.1f} ms")
    print(f"=========================================================================\n")

if __name__ == "__main__":
    test_canvas_autocrop()
    test_trocr_phase7_benchmark()
