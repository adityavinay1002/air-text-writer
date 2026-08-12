import math
from typing import List, Tuple, Dict

Point2D = Tuple[float, float]

def normalize_point_cloud(pts: List[Point2D], target_points: int = 32) -> List[Point2D]:
    """
    Resamples points to exact target_points count, translates centroid to (0,0),
    and scales to unit bounding box [-0.5, 0.5] x [-0.5, 0.5].
    """
    if not pts:
        return []

    # 1. Resample to target_points count
    if len(pts) == 1:
        resampled = [pts[0]] * target_points
    else:
        # Calculate cumulative path length
        lengths = [0.0]
        for i in range(1, len(pts)):
            dx = pts[i][0] - pts[i - 1][0]
            dy = pts[i][1] - pts[i - 1][1]
            lengths.append(lengths[-1] + math.sqrt(dx * dx + dy * dy))

        total_length = lengths[-1]
        if total_length == 0:
            resampled = [pts[0]] * target_points
        else:
            step = total_length / float(target_points - 1)
            resampled = [pts[0]]
            curr_idx = 0

            for i in range(1, target_points - 1):
                target_dist = i * step
                while curr_idx < len(lengths) - 1 and lengths[curr_idx + 1] < target_dist:
                    curr_idx += 1
                
                if curr_idx >= len(lengths) - 1:
                    resampled.append(pts[-1])
                else:
                    seg_len = lengths[curr_idx + 1] - lengths[curr_idx]
                    t = 0.0 if seg_len == 0 else (target_dist - lengths[curr_idx]) / seg_len
                    x = pts[curr_idx][0] + t * (pts[curr_idx + 1][0] - pts[curr_idx][0])
                    y = pts[curr_idx][1] + t * (pts[curr_idx + 1][1] - pts[curr_idx][1])
                    resampled.append((x, y))

            resampled.append(pts[-1])

    # 2. Centroid translation to (0,0)
    cx = sum(p[0] for p in resampled) / float(len(resampled))
    cy = sum(p[1] for p in resampled) / float(len(resampled))
    centered = [(p[0] - cx, p[1] - cy) for p in resampled]

    # 3. Bounding box scale to unit box [-0.5, 0.5]
    xs = [p[0] for p in centered]
    ys = [p[1] for p in centered]
    max_dim = max(1e-6, max(max(xs) - min(xs), max(ys) - min(ys)))

    scaled = [(p[0] / max_dim, p[1] / max_dim) for p in centered]
    return scaled


def _generate_letter_templates() -> Dict[str, List[Point2D]]:
    """Generates canonical point cloud templates for uppercase A-Z."""
    raw_templates = {}

    # A: Left leg, right leg, crossbar
    raw_templates['A'] = [(0, 1), (0.5, 0), (1, 1), (0.25, 0.5), (0.75, 0.5)]
    # B: Vertical, top loop, bottom loop
    raw_templates['B'] = [(0, 0), (0, 1), (0, 0), (0.5, 0.25), (0, 0.5), (0.6, 0.75), (0, 1)]
    # C: Left arc
    raw_templates['C'] = [(1, 0.2), (0.5, 0), (0, 0.5), (0.5, 1), (1, 0.8)]
    # D: Vertical, right arc
    raw_templates['D'] = [(0, 0), (0, 1), (0, 0), (0.7, 0.2), (0.7, 0.8), (0, 1)]
    # E: Vertical, 3 bars
    raw_templates['E'] = [(1, 0), (0, 0), (0, 0.5), (0.7, 0.5), (0, 0.5), (0, 1), (1, 1)]
    # F: Vertical, 2 bars
    raw_templates['F'] = [(1, 0), (0, 0), (0, 0.5), (0.7, 0.5), (0, 0.5), (0, 1)]
    # G: C arc with inner bar
    raw_templates['G'] = [(1, 0.2), (0.5, 0), (0, 0.5), (0.5, 1), (1, 1), (1, 0.5), (0.5, 0.5)]
    # H: Left vertical, crossbar, right vertical
    raw_templates['H'] = [(0, 0), (0, 1), (0, 0.5), (1, 0.5), (1, 0), (1, 1)]
    # I: Top bar, vertical, bottom bar
    raw_templates['I'] = [(0.2, 0), (0.8, 0), (0.5, 0), (0.5, 1), (0.2, 1), (0.8, 1)]
    # J: Top bar, vertical hook
    raw_templates['J'] = [(0.2, 0), (0.8, 0), (0.6, 0), (0.6, 0.8), (0.3, 1), (0, 0.8)]
    # K: Vertical, diagonal up, diagonal down
    raw_templates['K'] = [(0, 0), (0, 1), (0, 0.5), (1, 0), (0, 0.5), (1, 1)]
    # L: Vertical, bottom bar
    raw_templates['L'] = [(0, 0), (0, 1), (1, 1)]
    # M: Left vert, peak down, peak up, right vert
    raw_templates['M'] = [(0, 1), (0, 0), (0.5, 0.5), (1, 0), (1, 1)]
    # N: Left vert, diagonal, right vert
    raw_templates['N'] = [(0, 1), (0, 0), (1, 1), (1, 0)]
    # O: Circle loop
    raw_templates['O'] = [(0.5, 0), (0, 0.5), (0.5, 1), (1, 0.5), (0.5, 0)]
    # P: Vertical, top loop
    raw_templates['P'] = [(0, 1), (0, 0), (0.8, 0.25), (0, 0.5)]
    # Q: Circle loop with tail
    raw_templates['Q'] = [(0.5, 0), (0, 0.5), (0.5, 1), (1, 0.5), (0.5, 0), (0.6, 0.6), (1, 1)]
    # R: Vertical, top loop, diagonal leg
    raw_templates['R'] = [(0, 1), (0, 0), (0.8, 0.25), (0, 0.5), (1, 1)]
    # S: Snake curve
    raw_templates['S'] = [(1, 0.2), (0.5, 0), (0, 0.3), (1, 0.7), (0.5, 1), (0, 0.8)]
    # T: Top bar, vertical stem
    raw_templates['T'] = [(0, 0), (1, 0), (0.5, 0), (0.5, 1)]
    # U: U curve
    raw_templates['U'] = [(0, 0), (0, 0.7), (0.5, 1), (1, 0.7), (1, 0)]
    # V: V diagonal
    raw_templates['V'] = [(0, 0), (0.5, 1), (1, 0)]
    # W: W double V
    raw_templates['W'] = [(0, 0), (0.25, 1), (0.5, 0.5), (0.75, 1), (1, 0)]
    # X: Two crossing diagonals
    raw_templates['X'] = [(0, 0), (1, 1), (0.5, 0.5), (1, 0), (0, 1)]
    # Y: V top, vertical stem
    raw_templates['Y'] = [(0, 0), (0.5, 0.5), (1, 0), (0.5, 0.5), (0.5, 1)]
    # Z: Z shape
    raw_templates['Z'] = [(0, 0), (1, 0), (0, 1), (1, 1)]

    # Normalize all templates to 32 points
    templates = {}
    for letter, pts in raw_templates.items():
        templates[letter] = normalize_point_cloud(pts, target_points=32)

    return templates

LETTER_TEMPLATES = _generate_letter_templates()
