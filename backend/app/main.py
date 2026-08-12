import os
import sys
import asyncio
import json
import time
import logging
import base64
from typing import List, Dict, Any, Optional

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.camera.stream import CameraStream
from app.hand_tracking.detector import HandDetector
from app.gestures.classifier import PalmAwareGestureClassifier, GestureState
from app.gestures.stabilizer import MultiHandStabilizer
from app.trajectory.engine import WordTrajectoryEngine
from app.recognition.trocr_engine import TrOCRHandwritingEngine
from app.services.movie_search import MovieSearchService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AirWrite-FastAPI")

app = FastAPI(
    title="AirWrite TV Search Backend",
    description="Computer vision, live MJPEG video stream, TrOCR recognition, and TV search service",
    version="1.0.0"
)

# Configure CORS for React frontend (Vite dev server http://localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    """Manages active WebSocket connections."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        if not self.active_connections:
            return
        to_remove = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to client: {e}")
                to_remove.append(connection)
        for conn in to_remove:
            self.disconnect(conn)

manager = ConnectionManager()

# Global CV Engine Control State
camera_stream: Optional[CameraStream] = None
cv_task: Optional[asyncio.Task] = None
is_cv_running = False
is_camera_active = False
cv_lock = asyncio.Lock()

# Frame cache for MJPEG stream endpoint
latest_annotated_frame: Optional[np.ndarray] = None

# TrOCR Pretrained Engine Singleton
trocr_engine: Optional[TrOCRHandwritingEngine] = None
word_engine: Optional[WordTrajectoryEngine] = None

def draw_strokes_on_frame(frame: np.ndarray, strokes: List[List[Tuple[int, int]]], line_color=(255, 230, 0), thickness=4):
    """Renders multi-stroke visual handwriting on the preview frame."""
    for stroke in strokes:
        if len(stroke) < 2:
            if len(stroke) == 1:
                cv2.circle(frame, stroke[0], thickness, line_color, -1)
            continue
        for i in range(1, len(stroke)):
            pt1 = stroke[i - 1]
            pt2 = stroke[i]
            cv2.line(frame, pt1, pt2, (0, 180, 255), thickness + 4, cv2.LINE_AA)
            cv2.line(frame, pt1, pt2, line_color, thickness, cv2.LINE_AA)
    return frame

async def cv_processing_loop():
    """Continuous background loop processing camera stream, MediaPipe tracking & TrOCR recognition."""
    global camera_stream, is_cv_running, is_camera_active, trocr_engine, word_engine, latest_annotated_frame

    logger.info("Starting CV Processing Loop...")
    
    if trocr_engine is None:
        logger.info("Pre-loading TrOCR model in background thread...")
        trocr_engine = await asyncio.to_thread(TrOCRHandwritingEngine, 0.38)

    detector = HandDetector(max_num_hands=2)
    stabilizer = MultiHandStabilizer()
    word_engine = WordTrajectoryEngine()

    is_cv_running = True
    is_camera_active = True
    last_broadcast_state = "ready"

    await manager.broadcast({
        "type": "camera_status",
        "camera_active": True,
        "gesture_state": "ready"
    })

    try:
        while is_cv_running and camera_stream and camera_stream.is_opened:
            ret, frame = camera_stream.read_frame()
            if not ret or frame is None:
                await asyncio.sleep(0.01)
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

                classification = PalmAwareGestureClassifier.classify_hand(landmarks_norm)
                raw_gesture = classification["gesture"]
                stable_gesture = stabilizer.update(hand_key, raw_gesture)
                is_write_active = (stable_gesture == GestureState.WRITE)

                if stable_gesture in (GestureState.CONFIRM, GestureState.CLEAR):
                    active_gesture_override = stable_gesture
                elif is_write_active and len(landmarks_pixel) > 8:
                    active_write_point = landmarks_pixel[8]

                # Draw MediaPipe hand landmarks overlay
                frame = detector.draw_landmarks(frame, hand, is_writing_active=is_write_active)

                # Draw index fingertip point
                if is_write_active and len(landmarks_pixel) > 8:
                    idx_x, idx_y = landmarks_pixel[8]
                    cv2.circle(frame, (idx_x, idx_y), 16, (255, 255, 0), 2)
                    cv2.circle(frame, (idx_x, idx_y), 8, (255, 255, 0), -1)
                    cv2.putText(frame, f"WRITE TIP ({idx_x}, {idx_y})", (idx_x + 20, idx_y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

                # Render per-hand wrist status HUD
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

            # Update Word Session Engine State
            current_input_state = active_gesture_override if active_gesture_override else \
                                  (GestureState.WRITE if active_write_point else GestureState.PEN_UP)

            # Get drawable strokes & render on video frame
            drawable_strokes = word_engine.get_strokes_to_draw()
            if drawable_strokes:
                frame = draw_strokes_on_frame(frame, drawable_strokes)

            # Top HUD bar
            cv2.rectangle(frame, (0, 0), (w, 40), (20, 20, 20), -1)
            cv2.putText(frame, "AIRWRITE CV - LIVE BACKEND FEED", (15, 26),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

            latest_annotated_frame = frame.copy()

            # Map gesture state to string
            gesture_state_str = "writing" if active_write_point else \
                                "pen_up" if current_input_state == GestureState.PEN_UP else \
                                "confirm" if current_input_state == GestureState.CONFIRM else \
                                "clear" if current_input_state == GestureState.CLEAR else "ready"

            # Broadcast status & trajectory points to WebSocket
            if gesture_state_str != last_broadcast_state and gesture_state_str != "processing":
                last_broadcast_state = gesture_state_str
                await manager.broadcast({
                    "type": "status",
                    "gesture_state": gesture_state_str,
                    "strokes": drawable_strokes
                })
            elif drawable_strokes:
                await manager.broadcast({
                    "type": "trajectory_update",
                    "strokes": drawable_strokes
                })

            # Run engine update
            engine_res = word_engine.update(current_input_state, active_write_point, processor=trocr_engine)

            if engine_res["event"] == "CONFIRMED":
                status = engine_res.get("status", "LOW_CONFIDENCE")
                word = engine_res.get("word", "")
                conf = engine_res.get("confidence", 0.0)
                cropped_img = engine_res.get("rendered_image")

                img_b64 = ""
                if cropped_img is not None:
                    _, buf = cv2.imencode(".png", cropped_img)
                    img_b64 = base64.b64encode(buf).decode("utf-8")

                rec_msg = {
                    "type": "recognition_result",
                    "text": word,
                    "confidence": conf,
                    "status": status,
                    "cropped_image_base64": img_b64,
                    "event": "CONFIRMED"
                }

                logger.info(f"Broadcasting TrOCR Result -> Text: '{word}' | Status: {status} | Conf: {conf*100:.1f}%")
                await manager.broadcast(rec_msg)

                last_broadcast_state = "recognized" if status == "RECOGNIZED" else "ready"
                await manager.broadcast({"type": "status", "gesture_state": last_broadcast_state})

            await asyncio.sleep(0.01)

    except Exception as e:
        logger.error(f"Error in CV processing loop: {e}", exc_info=True)
    finally:
        detector.close()
        if camera_stream:
            camera_stream.release()
            camera_stream = None
        is_cv_running = False
        is_camera_active = False
        latest_annotated_frame = None
        logger.info("CV Processing loop stopped and camera released.")
        await manager.broadcast({
            "type": "camera_status",
            "camera_active": False,
            "gesture_state": "ready"
        })

def generate_mjpeg_frames():
    """Generator function yielding multipart JPEG frames for live camera streaming."""
    while True:
        if is_camera_active and latest_annotated_frame is not None:
            ret, buffer = cv2.imencode(".jpg", latest_annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            # Standby blank frame
            standby = np.full((360, 640, 3), 20, dtype=np.uint8)
            cv2.putText(standby, "CAMERA STANDBY", (210, 180),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)
            cv2.putText(standby, "Click [ START CAMERA ] in UI", (170, 220),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
            ret, buffer = cv2.imencode(".jpg", standby)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.04)  # ~25 FPS

@app.on_event("startup")
async def startup_event():
    global trocr_engine
    logger.info("Pre-loading Microsoft TrOCR Engine in background thread...")
    try:
        trocr_engine = await asyncio.to_thread(TrOCRHandwritingEngine, 0.38)
        logger.info("Microsoft TrOCR Engine pre-loaded successfully!")
    except Exception as e:
        logger.error(f"Error pre-loading TrOCR engine: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    global is_cv_running, cv_task
    is_cv_running = False
    if cv_task:
        cv_task.cancel()

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "AirWrite TV Search CV Engine",
        "phase": 6.2,
        "camera_active": is_camera_active,
        "trocr_loaded": trocr_engine is not None,
        "max_num_hands": settings.MAX_NUM_HANDS
    }

@app.get("/health")
@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "airwrite-backend",
        "backend_connected": True,
        "camera_active": is_camera_active,
        "cv_running": is_cv_running,
        "trocr_loaded": trocr_engine is not None
    }

@app.get("/api/camera/stream")
async def video_feed():
    """Live MJPEG Video Stream of OpenCV Backend Feed."""
    return StreamingResponse(
        generate_mjpeg_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.post("/api/camera/start")
async def start_camera():
    global camera_stream, cv_task, is_cv_running, is_camera_active
    async with cv_lock:
        if is_camera_active and is_cv_running:
            return {"status": "already_running", "camera_active": True}

        logger.info("Starting Camera Stream via REST request...")
        camera_stream = CameraStream()
        if not camera_stream.start():
            logger.error("Failed to start camera stream.")
            return {"status": "error", "message": "Failed to open camera device", "camera_active": False}

        cv_task = asyncio.create_task(cv_processing_loop())
        return {"status": "started", "camera_active": True}

@app.post("/api/camera/stop")
async def stop_camera():
    global is_cv_running, is_camera_active, camera_stream
    async with cv_lock:
        if not is_camera_active and not is_cv_running:
            return {"status": "already_stopped", "camera_active": False}

        logger.info("Stopping Camera Stream via REST request...")
        is_cv_running = False
        if camera_stream:
            camera_stream.release()
            camera_stream = None
        is_camera_active = False

        await manager.broadcast({
            "type": "camera_status",
            "camera_active": False,
            "gesture_state": "ready"
        })
        return {"status": "stopped", "camera_active": False}

@app.post("/api/session/clear")
async def clear_session():
    global word_engine
    if word_engine and word_engine.session:
        word_engine.session.reset()
    await manager.broadcast({"type": "clear", "gesture_state": "ready"})
    return {"status": "cleared"}

@app.get("/api/search")
async def search_movies(q: str = Query(..., min_length=1, description="Movie/TV search query")):
    logger.info(f"Received search request for: '{q}'")
    results = await asyncio.to_thread(MovieSearchService.search_movies, q)
    return {"query": q, "count": len(results), "movies": results}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    await websocket.send_json({
        "type": "init",
        "backend_connected": True,
        "camera_active": is_camera_active,
        "gesture_state": "ready"
    })
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except Exception:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
