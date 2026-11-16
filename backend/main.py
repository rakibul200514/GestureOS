"""
GestureOS - Main Application & Web Server
Powered by FastAPI, OpenCV, MediaPipe & PyAutoGUI

BCA Viva Key Knowledge:
1. Asynchronous Architecture:
   FastAPI handles web requests and WebSockets asynchronously while a background thread
   continuously captures webcam frames and executes AI inference.
2. MJPEG Video Streaming:
   Uses multipart/x-mixed-replace MIME type to deliver real-time JPEG frames directly
   to the browser without needing complex video codecs or plugins.
3. WebSockets (Two-Way Communication):
   Pushes real-time metrics (FPS, gesture, active state, logs) to the browser in under 5ms.
"""

import os
import time
import json
import threading
from typing import Optional
from pathlib import Path

import cv2
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from hand_detector import HandDetector
from mouse_controller import MouseController

# Base Directories
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"

# Initialize FastAPI App
app = FastAPI(title="GestureOS", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


class SystemState:
    """Shared state between computer vision thread and web server."""
    def __init__(self):
        self.lock = threading.Lock()
        self.fps = 0.0
        self.hand_detected = False
        self.current_gesture = "Searching..."
        self.gesture_type = "None"
        self.is_active = False
        self.latest_frame_bytes: Optional[bytes] = None
        self.log_queue = []
        self.connected_clients = set()

    def add_log(self, text: str, level: str = "action"):
        log_item = {"text": text, "level": level, "time": time.time()}
        self.log_queue.append(log_item)
        if len(self.log_queue) > 50:
            self.log_queue.pop(0)


state = SystemState()
detector = HandDetector(max_hands=1, detection_con=0.7, track_con=0.6)
controller = MouseController(smoothing=5, click_cooldown=0.4, frame_margin=100)


def vision_worker():
    """Background worker thread: Captures webcam, runs MediaPipe, and maps gestures."""
    print("[INFO] Starting Vision Worker thread...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam index 0!")
        state.add_log("Failed to open webcam.", "alert")
        return

    cam_w, cam_h = 640, 480
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_h)

    p_time = time.time()
    last_log_gesture = ""

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.01)
            continue

        # Horizontal flip for natural mirror view
        frame = cv2.flip(frame, 1)

        # 1. Detect Hand
        frame = detector.find_hands(frame, draw=True)
        lm_list = detector.find_positions(frame)

        # Active boundary box (neon purple)
        margin = controller.frame_margin
        cv2.rectangle(frame, (margin, margin), (cam_w - margin, cam_h - margin), (255, 0, 200), 2)
        cv2.putText(frame, "ACTIVE ZONE", (margin + 6, margin - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 200), 1)

        hand_found = len(lm_list) != 0
        gesture_str = "No Hand"
        g_type = "None"

        if hand_found:
            fingers = detector.fingers_up(lm_list)
            ix, iy = lm_list[8][1], lm_list[8][2]
            mx, my = lm_list[12][1], lm_list[12][2]
            dist, center, _ = detector.calculate_distance(4, 8, lm_list)

            # Gesture 1: Closed Fist -> Stop / Emergency Lock
            if fingers == [0, 0, 0, 0, 0]:
                gesture_str = "Closed Fist (Stop)"
                g_type = "Stop"
                if controller.is_active:
                    controller.disable()
                    state.add_log("Closed Fist detected: Control Locked.", "alert")
                controller.reset_scroll()

            # Gesture 2: Open Palm -> Pause
            elif fingers == [1, 1, 1, 1, 1]:
                gesture_str = "Open Palm (Pause)"
                g_type = "Pause"
                controller.reset_scroll()

            # Gesture 3: Pinch -> Left Click
            elif dist < 35:
                gesture_str = "Pinch (Click)"
                g_type = "Click"
                cv2.circle(frame, center, 12, (0, 0, 255), cv2.FILLED)
                clicked = controller.left_click()
                if clicked:
                    state.add_log("Pinch Gesture: Left Click executed.", "action")
                controller.reset_scroll()

            # Gesture 4: Two Fingers -> Scroll
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
                gesture_str = "Two Fingers (Scroll)"
                g_type = "Scroll"
                cv2.line(frame, (ix, iy), (mx, my), (0, 255, 255), 3)
                controller.scroll(my)

            # Gesture 5: Index Finger -> Move Cursor
            elif fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                gesture_str = "Index (Pointer)"
                g_type = "Pointer"
                cv2.circle(frame, (ix, iy), 10, (0, 255, 0), cv2.FILLED)
                controller.move_cursor(ix, iy, cam_w, cam_h)
                controller.reset_scroll()

            else:
                gesture_str = "Neutral Hand"
                g_type = "None"
                controller.reset_scroll()
        else:
            controller.reset_scroll()

        # FPS calculation
        c_time = time.time()
        calc_fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time

        # Update Shared State
        with state.lock:
            state.fps = calc_fps
            state.hand_detected = hand_found
            state.current_gesture = gesture_str
            state.gesture_type = g_type
            state.is_active = controller.is_active

        # Encode Frame to JPEG
        ret_enc, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if ret_enc:
            with state.lock:
                state.latest_frame_bytes = buffer.tobytes()

        # Small sleep to yield CPU
        time.sleep(0.005)


# Start Background Thread on server launch
@app.on_event("startup")
def startup_event():
    t = threading.Thread(target=vision_worker, daemon=True)
    t.start()


@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    """Serves the main Futuristic Dashboard HTML."""
    html_path = FRONTEND_DIR / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


def mjpeg_frame_generator():
    """Streams live MJPEG camera frames to web browser."""
    while True:
        with state.lock:
            frame_data = state.latest_frame_bytes

        if frame_data:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
        time.sleep(0.03)  # ~30 FPS delivery to browser


@app.get("/video_feed")
def video_feed():
    """Live Video Streaming Route."""
    return StreamingResponse(
        mjpeg_frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Pushes real-time telemetry to the dashboard frontend."""
    await websocket.accept()
    state.connected_clients.add(websocket)
    try:
        last_sent_log_idx = 0
        while True:
            with state.lock:
                fps = state.fps
                hand = state.hand_detected
                gesture = state.current_gesture
                g_type = state.gesture_type
                is_active = state.is_active
                logs = list(state.log_queue)

            payload = {
                "fps": fps,
                "hand_detected": hand,
                "gesture": gesture,
                "gesture_type": g_type,
                "is_active": is_active
            }

            if len(logs) > last_sent_log_idx:
                payload["new_log"] = logs[-1]
                last_sent_log_idx = len(logs)

            await websocket.send_text(json.dumps(payload))
            await websocket.receive_text() if False else None  # non-blocking keepalive
            import asyncio
            await asyncio.sleep(0.05)  # 20 updates per second
    except WebSocketDisconnect:
        state.connected_clients.remove(websocket)
    except Exception:
        if websocket in state.connected_clients:
            state.connected_clients.remove(websocket)


@app.post("/api/toggle_control")
def toggle_control():
    """Toggles safe mode on/off."""
    active = controller.toggle()
    with state.lock:
        state.is_active = active
    return {"is_active": active}


@app.post("/api/emergency_stop")
def emergency_stop():
    """Immediately halts mouse control and returns to Safe Mode."""
    controller.disable()
    with state.lock:
        state.is_active = False
    state.add_log("EMERGENCY STOP BUTTON CLICKED!", "alert")
    return {"is_active": False}


class SettingsPayload(BaseModel):
    smoothing: Optional[int] = None
    click_cooldown: Optional[float] = None


@app.post("/api/settings")
def update_settings(payload: SettingsPayload):
    """Updates sensitivity and smoothing dynamically."""
    if payload.smoothing is not None:
        controller.smoothing = max(1, min(10, payload.smoothing))
        state.add_log(f"Smoothing updated to {controller.smoothing}", "system")
    if payload.click_cooldown is not None:
        controller.click_cooldown = max(0.1, min(2.0, payload.click_cooldown))
        state.add_log(f"Click cooldown updated to {controller.click_cooldown}s", "system")
    return {"status": "ok", "smoothing": controller.smoothing, "cooldown": controller.click_cooldown}


if __name__ == "__main__":
    print("[INFO] Starting GestureOS Application Server on http://127.0.0.1:8000 ...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
