import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cv2
import time
import logging
from app.camera.stream import CameraStream
from app.hand_tracking.detector import HandDetector
from app.gestures.classifier import PalmAwareGestureClassifier, GestureState
from app.gestures.stabilizer import MultiHandStabilizer
from app.trajectory.engine import WordTrajectoryEngine
from app.recognition.trocr_engine import TrOCRHandwritingEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AirWrite-CV-Studio")

def draw_strokes(frame, strokes, line_color=(255, 230, 0), thickness=5):
    """Renders multi-stroke visual handwriting on the preview frame."""
    for stroke in strokes:
        if len(stroke) < 2:
            if len(stroke) == 1:
                cv2.circle(frame, stroke[0], thickness, line_color, -1)
            continue
        for i in range(1, len(stroke)):
            pt1 = stroke[i - 1]
            pt2 = stroke[i]
            # Outer glow
            cv2.line(frame, pt1, pt2, (0, 180, 255), thickness + 4, cv2.LINE_AA)
            # Core bright line
            cv2.line(frame, pt1, pt2, line_color, thickness, cv2.LINE_AA)
    return frame

def main():
    print("=" * 70)
    print("  AIRWRITE TV SEARCH - PHASE 5 IMAGE-BASED HANDWRITING ENGINE STUDIO")
    print("=" * 70)
    print("  PRIMARY ENGINE: Microsoft TrOCR (Pretrained Vision-Transformer for Handwriting)")
    print("  AIR-WRITING WORKFLOW:")
    print("    ☝️  WRITE    : Visually accumulate smooth handwriting strokes on canvas")
    print("    🖐️  PEN_UP   : Open palm to pause stroke recording / complete letter (keeps writing intact)")
    print("    ✌️  CONFIRM  : Freeze canvas -> Auto-crop handwriting -> Run TrOCR model")
    print("    ✊  CLEAR    : Make a fist to reset virtual handwriting canvas")
    print("=" * 70)
    print("  Press 'q' or 'ESC' in the window to quit.\n")

    camera = CameraStream()
    if not camera.start():
        logger.error("Failed to start camera. Exiting.")
        return

    detector = HandDetector(max_num_hands=2)
    stabilizer = MultiHandStabilizer()
    word_engine = WordTrajectoryEngine()
    
    # Initialize Pretrained Microsoft TrOCR Handwriting Engine
    logger.info("Initializing Microsoft TrOCR Handwriting Engine...")
    trocr_engine = TrOCRHandwritingEngine(min_confidence=0.40)

    window_name = "AirWrite CV Studio - Phase 5 Image-Based TrOCR Engine"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)

    last_rec_result = None

    try:
        while True:
            ret, frame = camera.read_frame()
            if not ret or frame is None:
                logger.warning("Blank frame received or camera stream ended.")
                time.sleep(0.01)
                continue

            h, w, _ = frame.shape
            hands_data = detector.process(frame)
            active_keys = []

            active_write_point = None
            active_gesture_override = None

            for hand in hands_data:
                hand_label = hand["label"]
                hand_id = hand["hand_id"]
                hand_key = f"{hand_label}_{hand_id}"
                active_keys.append(hand_key)

                landmarks_norm = hand["landmarks_norm"]
                landmarks_pixel = hand["landmarks_pixel"]

                # 1. Classify raw gesture
                classification = PalmAwareGestureClassifier.classify_hand(landmarks_norm)
                raw_gesture = classification["gesture"]

                # 2. Stabilize gesture per hand
                stable_gesture = stabilizer.update(hand_key, raw_gesture)
                is_write_active = (stable_gesture == GestureState.WRITE)

                if stable_gesture in (GestureState.CONFIRM, GestureState.CLEAR, GestureState.PEN_UP):
                    active_gesture_override = stable_gesture
                elif is_write_active and len(landmarks_pixel) > 8:
                    active_write_point = landmarks_pixel[8]

                # 3. Draw hand skeleton overlay
                frame = detector.draw_landmarks(frame, hand, is_writing_active=is_write_active)

                # 4. If WRITE is active, draw bright glowing index fingertip point
                if is_write_active and len(landmarks_pixel) > 8:
                    idx_x, idx_y = landmarks_pixel[8]
                    cv2.circle(frame, (idx_x, idx_y), 16, (255, 255, 0), 2)
                    cv2.circle(frame, (idx_x, idx_y), 8, (255, 255, 0), -1)
                    cv2.putText(frame, f"WRITE TIP ({idx_x}, {idx_y})", (idx_x + 20, idx_y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

                # 5. Render per-hand status HUD
                wrist_x, wrist_y = landmarks_pixel[0]
                status_color = (0, 255, 0) if stable_gesture == GestureState.WRITE else \
                               (0, 200, 255) if stable_gesture == GestureState.CONFIRM else \
                               (0, 0, 255) if stable_gesture == GestureState.PEN_UP else \
                               (255, 100, 0) if stable_gesture == GestureState.CLEAR else (180, 180, 180)

                badge_text = f"{hand_label}: {stable_gesture}"
                cv2.rectangle(frame, (wrist_x - 10, wrist_y - 40), (wrist_x + 180, wrist_y - 10), (0, 0, 0), -1)
                cv2.putText(frame, badge_text, (wrist_x - 5, wrist_y - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)

            stabilizer.prune_missing(active_keys)

            # 6. Update Word Session Engine State
            current_input_state = active_gesture_override if active_gesture_override else \
                                  (GestureState.WRITE if active_write_point else GestureState.PEN_UP)

            # Keep copy of drawable strokes before engine update (in case CONFIRM resets session)
            drawable_strokes = word_engine.get_strokes_to_draw()
            
            t0 = time.time()
            engine_res = word_engine.update(current_input_state, active_write_point, processor=trocr_engine)
            proc_latency_ms = int((time.time() - t0) * 1000)

            if engine_res["event"] == "CONFIRMED":
                engine_res["latency_ms"] = proc_latency_ms
                last_rec_result = engine_res
                logger.info(f"[TrOCR CONFIRMED RESULT] Text: '{engine_res['word']}' | Status: {engine_res['status']} | Conf: {engine_res['confidence']*100:.1f}% | Latency: {proc_latency_ms}ms")

            # 7. Render Visual Handwriting Strokes on Preview Frame
            if drawable_strokes:
                frame = draw_strokes(frame, drawable_strokes)

            # 8. Global Top HUD Bar
            cv2.rectangle(frame, (0, 0), (w, 55), (20, 20, 20), -1)
            cv2.putText(frame, "AIRWRITE CV - PHASE 5 IMAGE-BASED TrOCR HANDWRITING ENGINE", (20, 32),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 255, 255), 2)

            active_pts = word_engine.session.get_total_point_count() if word_engine.session else 0
            active_strokes = len(word_engine.session.strokes) if word_engine.session else 0
            session_state = word_engine.session.state if word_engine.session else "IDLE"

            stats_str = f"STATE: {session_state} | Strokes: {active_strokes} | Pts: {active_pts} | FPS: {int(camera.fps)}"
            cv2.putText(frame, stats_str, (w - 560, 32),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)

            # 9. Render Phase 5 TrOCR Debug Panel & Cropped Image Preview
            if last_rec_result and last_rec_result.get("status"):
                status = last_rec_result["status"]
                text = last_rec_result["word"]
                conf = last_rec_result["confidence"]
                debug_info = last_rec_result.get("debug_info", {})
                latency = last_rec_result.get("latency_ms", 0)
                cropped_img = last_rec_result.get("rendered_image")

                # Color coding based on recognition status
                card_color = (0, 220, 0) if status == "RECOGNIZED" else \
                             (0, 140, 255) if status == "LOW_CONFIDENCE" else (100, 100, 100)

                cv2.rectangle(frame, (20, h - 110), (560, h - 20), (10, 10, 10), -1)
                cv2.rectangle(frame, (20, h - 110), (560, h - 20), card_color, 2)

                cv2.putText(frame, f"RECOGNIZED TEXT: {text}", (30, h - 75),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.70, card_color, 2)
                
                meta_line = f"Status: {status} | Conf: {int(conf*100)}% | Latency: {latency}ms"
                cv2.putText(frame, meta_line, (30, h - 48),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.50, (200, 200, 200), 1)

                model_info = f"Model: microsoft/trocr-small-handwritten (IAM Pretrained)"
                cv2.putText(frame, model_info, (30, h - 28),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 255), 1)

                # Render Picture-in-Picture (PiP) inset preview of cropped handwriting sent to TrOCR
                if cropped_img is not None:
                    pip_h, pip_w, _ = cropped_img.shape
                    # Scale inset preview for HUD
                    target_w = 200
                    target_h = max(50, int(target_w * (pip_h / float(max(1, pip_w)))))
                    target_h = min(120, target_h)
                    pip_resized = cv2.resize(cropped_img, (target_w, target_h))

                    x_offset = w - target_w - 20
                    y_offset = h - target_h - 20

                    cv2.rectangle(frame, (x_offset - 2, y_offset - 22), (x_offset + target_w + 2, y_offset + target_h + 2), (0, 255, 255), 2)
                    cv2.putText(frame, "CROPPED HANDWRITING IMAGE", (x_offset, y_offset - 6),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 255, 255), 1)
                    frame[y_offset:y_offset + target_h, x_offset:x_offset + target_w] = pip_resized

            cv2.imshow(window_name, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27 or cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                logger.info("Quit requested by user.")
                break

    except Exception as e:
        logger.error(f"Error in execution loop: {e}", exc_info=True)
    finally:
        detector.close()
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
