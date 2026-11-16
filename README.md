# GestureOS 🚀
> **Control Your Computer With Your Hands**  
> *An AI-assisted computer vision and touchless desktop control system.*  
> **Academic Level:** BCA 3rd Semester Summer Project | Human-Computer Interaction (HCI)

---

## 📌 Project Overview
**GestureOS** is a zero-hardware, AI-assisted computer vision application that transforms any standard laptop or desktop webcam into a touchless mouse and gesture-based desktop controller. 

By leveraging **Google MediaPipe** for 21 3D hand landmarks tracking, **OpenCV** for real-time video stream processing, and **PyAutoGUI** for safe system-level desktop automation, GestureOS enables users to interact with their operating system seamlessly through hand gestures in the air.

---

## 🌟 Key Features
- **Real-Time 21 Hand Landmarks Tracking:** High-speed 3D spatial joint tracking powered by MediaPipe Hands.
- **Natural Mirror Video Stream:** Automatically flipped video feed for intuitive, mirror-like interaction.
- **Smooth Cursor Movement:** Exponential Moving Average (EMA) algorithm eliminates hand jitter and trembling.
- **Pinch-to-Click:** Euclidean distance calculation between Thumb Tip (Landmark 4) and Index Tip (Landmark 8) triggers left clicks.
- **Two-Finger Scroll:** Vertical tracking of Index and Middle fingers provides smooth up/down scrolling.
- **Safety First (Safe Mode by Default):**
  - Mouse control is disabled on startup to prevent accidental cursor jumps.
  - Requires explicit user permission (Master Switch or Keyboard shortcut).
  - Built-in gesture cooldown prevents runaway multi-clicking.
  - FailSafe boundary stop: moving cursor to screen corner triggers immediate halt.
- **Emergency Stop & Rest Gestures:**
  - **Open Palm:** Temporarily pauses tracking (rest mode).
  - **Closed Fist:** Emergency stop gesture that instantly disengages desktop control.
- **Futuristic Cyberpunk Dashboard:**
  - Real-time video HUD with glowing neon overlays.
  - Live FPS counter, active gesture cards, and event history log.
  - Interactive sensitivity and smoothing calibration sliders.

---

## 🏗️ System Architecture
```
                               +-----------------------------+
                               |     Webcam Hardware (0)     |
                               +--------------+--------------+
                                              |
                                              v (BGR Video Frames)
                               +-----------------------------+
                               |     OpenCV Video Engine     |
                               |  - Frame Mirroring (Flip)   |
                               |  - Resolution Normalization |
                               +--------------+--------------+
                                              |
                                              v (RGB Video Frames)
                               +-----------------------------+
                               |     Google MediaPipe AI     |
                               |  - Hand Presence Detection  |
                               |  - 21 3D Joint Landmarks    |
                               +--------------+--------------+
                                              |
                                              v (Landmark Coordinates)
                               +-----------------------------+
                               |       Gesture Engine        |
                               |  - Finger Counting Logic    |
                               |  - Euclidean Distance Math  |
                               +--------------+--------------+
                                              |
                       +----------------------+----------------------+
                       |                                             |
                       v                                             v
        +-----------------------------+               +-----------------------------+
        |   Safety & Mouse Engine     |               |    FastAPI & WebSockets     |
        |  - Coordinate Interpolation |               |  - MJPEG Live Video Feed    |
        |  - Exponential Smoothing    |               |  - Real-Time JSON Telemetry |
        |  - PyAutoGUI Desktop Action |               |  - Futuristic Neon Web UI   |
        +-----------------------------+               +-----------------------------+
```

---

## 🖐️ Gesture Reference Card

| Gesture | Finger State | Action |
| :--- | :--- | :--- |
| **Pointer Mode** | Index Finger UP | Moves mouse cursor smoothly across screen |
| **Pinch Click** | Thumb + Index Tip touch ($\text{dist} < 35\text{px}$) | Triggers Single Left Click |
| **Scroll Mode** | Index + Middle Fingers UP | Scrolls page Up / Down based on vertical delta |
| **Rest / Pause** | Open Palm (All 5 Fingers UP) | Freezes cursor movement to rest hand |
| **Emergency Lock** | Closed Fist (All Fingers DOWN) | Instantly locks mouse control into Safe Mode |

---

## 📐 Mathematical Formulations (BCA Viva Ready)

### 1. Euclidean Distance for Pinch Detection:
$$\text{Distance} = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$$
Where $(x_1, y_1)$ is Thumb Tip (Landmark 4) and $(x_2, y_2)$ is Index Tip (Landmark 8).

### 2. Coordinate Interpolation (Active Box to Full Screen):
$$X_{\text{screen}} = \text{interp}(X_{\text{finger}}, [M, W - M], [0, \text{Screen}_W])$$
$$Y_{\text{screen}} = \text{interp}(Y_{\text{finger}}, [M, H - M], [0, \text{Screen}_H])$$
Where $M$ is the comfort boundary margin, $W, H$ are camera dimensions, and $\text{Screen}_W, \text{Screen}_H$ are monitor dimensions.

### 3. Exponential Moving Average Cursor Smoothing:
$$X_{\text{curr}} = X_{\text{prev}} + \frac{X_{\text{target}} - X_{\text{prev}}}{\alpha}$$
Where $\alpha \ge 1$ is the smoothing factor (default: 5).

---

## 🛠️ Technology Stack
- **Language:** Python 3.12
- **Computer Vision:** OpenCV (`opencv-python 5.0+`)
- **AI Hand Tracking:** Google MediaPipe (`mediapipe 0.10.14`)
- **Desktop Automation:** PyAutoGUI (`pyautogui 0.9.54`)
- **Backend API & WebSockets:** FastAPI (`0.110+`), Uvicorn (`0.28+`)
- **Frontend Dashboard:** Modern HTML5, CSS3 (Cyberpunk Neon Theme), Vanilla JavaScript (WebSockets)

---

## ⚡ Quick Start Guide

### 1. Prerequisites:
- Windows 11 (or 10)
- Python 3.12 installed
- Standard laptop or USB webcam

### 2. Installation:
```powershell
# Navigate to project folder
cd GestureOS

# Create and activate virtual environment
py -3.12 -m venv venv
venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Running Unit Tests:
```powershell
python tests/test_units.py
```

### 4. Launching GestureOS:
```powershell
python backend/main.py
```
Open your browser and navigate to: **`http://127.0.0.1:8000`**

---

## 🛡️ Safety & Ethics
- **Non-Destructive:** Does not modify OS files, run terminal scripts, or execute destructive commands.
- **FailSafe Built-in:** Shoving the mouse to any corner of your monitor immediately aborts PyAutoGUI control.
- **Offline & Private:** Video processing runs 100% locally on your machine. No frames are stored or uploaded to external servers.

---

## 📜 License
This project is licensed under the **MIT License**. Created as a BCA 3rd Semester Summer Project.
