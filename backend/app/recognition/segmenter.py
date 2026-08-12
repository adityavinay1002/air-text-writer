from typing import List, Tuple, Dict, Any

Point = Tuple[int, int]
Stroke = List[Point]
CharacterSegment = List[Stroke]

class CharacterSegmenter:
    """
    Segments multi-stroke word trajectories into individual character candidates
    using spatial X-axis bounding box overlap and gap thresholds.
    """
    @staticmethod
    def segment_strokes(strokes: List[Stroke], max_gap_px: int = 40) -> List[CharacterSegment]:
        if not strokes:
            return []

        # Filter out empty or single-point noise strokes
        valid_strokes = [s for s in strokes if len(s) >= 2]
        if not valid_strokes:
            return []

        # Compute bounding boxes for each stroke: (min_x, max_x, min_y, max_y, stroke)
        stroke_info = []
        for s in valid_strokes:
            xs = [pt[0] for pt in s]
            ys = [pt[1] for pt in s]
            stroke_info.append({
                "min_x": min(xs),
                "max_x": max(xs),
                "min_y": min(ys),
                "max_y": max(ys),
                "stroke": s
            })

        # Calculate word-level bounding width to dynamically scale gap threshold if needed
        all_xs = [pt[0] for s in valid_strokes for pt in s]
        total_width = max(all_xs) - min(all_xs)
        dynamic_gap = max(max_gap_px, int(total_width * 0.12))

        character_segments: List[CharacterSegment] = []
        current_cluster: List[Dict[str, Any]] = []

        for info in stroke_info:
            if not current_cluster:
                current_cluster.append(info)
            else:
                # Calculate cluster X-span bounds
                cluster_min_x = min(item["min_x"] for item in current_cluster)
                cluster_max_x = max(item["max_x"] for item in current_cluster)

                # Check if new stroke overlaps with cluster X-span or is within gap threshold
                stroke_min_x = info["min_x"]
                stroke_max_x = info["max_x"]

                # Overlap condition or close spatial proximity
                is_overlapping = not (stroke_min_x > cluster_max_x or stroke_max_x < cluster_min_x)
                is_close_gap = (stroke_min_x - cluster_max_x) <= dynamic_gap

                if is_overlapping or is_close_gap:
                    current_cluster.append(info)
                else:
                    # Finalize previous character segment
                    character_segments.append([item["stroke"] for item in current_cluster])
                    current_cluster = [info]

        if current_cluster:
            character_segments.append([item["stroke"] for item in current_cluster])

        return character_segments
