import math
from typing import List, Tuple, Dict, Any
from app.trajectory.engine import WordSession, PointWithTime

class GeometricWordProcessor:
    """
    Training-free geometric & heuristic word recognizer.
    
    Extracts geometric features from multi-stroke word trajectories:
      - Bounding box dimensions & Aspect Ratio (Width / Height)
      - Bounding box normalized coordinates [0, 1] x [0, 1]
      - Total path length & stroke count
      - Horizontal vs Vertical velocity & movement dominance
    
    Matches against dictionary words deterministically.
    """
    DICTIONARY = ["HELLO", "AVATAR", "NETFLIX", "MOVIE", "INTERSTELLAR", "DUNE"]

    @classmethod
    def extract_features(cls, session: WordSession) -> Dict[str, Any]:
        all_pts = session.get_all_points()
        if not all_pts:
            return {
                "point_count": 0,
                "stroke_count": 0,
                "bbox": (0, 0, 0, 0),
                "aspect_ratio": 1.0,
                "path_length": 0.0,
                "duration_sec": 0.0,
                "norm_points": []
            }

        xs = [pt[0] for pt in all_pts]
        ys = [pt[1] for pt in all_pts]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        w = max(1, max_x - min_x)
        h = max(1, max_y - min_y)
        aspect_ratio = w / float(h)

        # Normalize points to [0, 1] unit square
        norm_points = [((pt[0] - min_x) / w, (pt[1] - min_y) / h, pt[2]) for pt in all_pts]

        # Calculate path length & duration
        path_length = 0.0
        for stroke in session.strokes:
            for i in range(1, len(stroke)):
                dx = stroke[i][0] - stroke[i - 1][0]
                dy = stroke[i][1] - stroke[i - 1][1]
                path_length += math.sqrt(dx * dx + dy * dy)

        duration_sec = max(0.001, (session.last_update_time - session.start_time))

        # Direction dominance
        horiz_move = w
        vert_move = h
        is_wide = aspect_ratio > 1.2

        return {
            "point_count": len(all_pts),
            "stroke_count": len(session.strokes),
            "bbox": (min_x, min_y, w, h),
            "aspect_ratio": round(aspect_ratio, 3),
            "path_length": round(path_length, 2),
            "duration_sec": round(duration_sec, 2),
            "is_wide": is_wide,
            "norm_points": norm_points
        }

    @classmethod
    def process(cls, session: WordSession) -> Dict[str, Any]:
        features = cls.extract_features(session)
        pts_count = features["point_count"]
        stroke_count = features["stroke_count"]
        ar = features["aspect_ratio"]

        if pts_count < 5:
            return {
                "word": "UNKNOWN",
                "confidence": 0.0,
                "features": features
            }

        # Deterministic training-free geometric matching rules
        scores = {}
        for word in cls.DICTIONARY:
            score = 0.5  # Base score

            # 1. Word length vs aspect ratio correlation
            # Long words (NETFLIX, INTERSTELLAR) tend to have wider aspect ratios (AR > 2.0)
            word_len = len(word)
            expected_ar = max(0.8, word_len * 0.45)
            ar_diff = abs(ar - expected_ar)
            score += max(-0.3, 0.4 - 0.15 * ar_diff)

            # 2. Stroke count heuristics
            # Multi-stroke words (A V A T A R has ~5-6 strokes, H E L L O has ~4-6)
            if word in ("AVATAR", "HELLO", "NETFLIX") and stroke_count >= 3:
                score += 0.25
            elif word in ("MOVIE", "DUNE") and stroke_count in (1, 2, 3):
                score += 0.20

            # 3. Path density ratio
            density = features["path_length"] / max(1.0, features["bbox"][2] + features["bbox"][3])
            if word == "INTERSTELLAR" and density > 3.0:
                score += 0.2
            elif word == "AVATAR" and ar > 1.4:
                score += 0.2

            scores[word] = round(min(0.98, max(0.50, score)), 3)

        # Select highest scoring dictionary word
        best_word = max(scores, key=scores.get)
        best_confidence = scores[best_word]

        return {
            "word": best_word,
            "confidence": best_confidence,
            "features": features
        }
