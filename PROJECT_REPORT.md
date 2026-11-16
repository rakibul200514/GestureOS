# ACADEMIC PROJECT REPORT
## GestureOS: Touchless Desktop Control System Using Computer Vision

**Program:** Bachelor of Computer Applications (BCA)  
**Semester:** 3rd Semester  
**Course:** Summer Project / Minor Project  
**Domain:** Artificial Intelligence, Computer Vision & Human-Computer Interaction (HCI)  

---

## 1. ABSTRACT
Traditional desktop interaction heavily relies on physical peripheral hardware such as mice, trackpads, and physical keyboards. While ubiquitous, physical input devices present ergonomic limitations, wear and tear, and accessibility barriers for individuals with motor disabilities or sterile environments (e.g., medical operating theaters). 

**GestureOS** presents an AI-assisted computer vision framework that transforms a standard consumer-grade webcam into an interactive, touchless human-computer interface. The system captures live video feeds using OpenCV, extracts 21 three-dimensional spatial hand landmarks using Google MediaPipe, and evaluates geometric distances and finger orientations to classify gestures. These gestures translate into OS-level mouse cursor translation, left clicks, scrolling, and emergency state pauses using PyAutoGUI. A modern, dark-neon web dashboard powered by FastAPI and WebSockets delivers real-time telemetry, live visual feedback, and sensitivity calibration. The proposed system demonstrates high accuracy, low latency (>30 FPS), robust cursor smoothing, and comprehensive failsafe mechanisms.

---

## 2. PROBLEM STATEMENT
Current human-computer interaction models suffer from:
1. **Hardware Dependency:** Physical mice and trackpads require clean, flat physical surfaces.
2. **Hygiene & Sterile Constraints:** In medical clinics, laboratories, or public kiosks, physical touch presents contamination risks.
3. **Accessibility Limitations:** Users with temporary or permanent motor restrictions often struggle with physical mice grips.
4. **Cost Barriers:** Specialized gesture-tracking hardware (e.g., Leap Motion, Kinect) is expensive and requires proprietary drivers.

**GestureOS** addresses these challenges by achieving touchless desktop control using existing standard webcams with zero external hardware costs.

---

## 3. OBJECTIVES
- To design a real-time computer vision pipeline utilizing OpenCV and MediaPipe.
- To detect 21 hand landmarks and classify hand gestures without external sensors.
- To map hand movements from camera space to screen resolution with jitter-reducing smoothing algorithms.
- To implement safe desktop automation with click cooldowns, boundary clamps, and fail-safe locks.
- To build a responsive, cyberpunk-themed web dashboard for live monitoring and parameter calibration.
- To maintain an accessible, modular codebase suitable for academic evaluation and viva defense.

---

## 4. SYSTEM REQUIREMENTS

### Hardware Requirements:
- **Processor:** Intel Core i3 / AMD Ryzen 3 or higher.
- **Memory (RAM):** Minimum 4 GB (8 GB recommended).
- **Camera:** Standard 720p / 1080p built-in or USB webcam.
- **Display:** 1366x768 minimum resolution (1920x1080 recommended).

### Software Requirements:
- **Operating System:** Windows 10 / 11 (64-bit).
- **Core Language:** Python 3.12 (CPython).
- **Libraries:**
  - `opencv-python` (v5.0+)
  - `mediapipe` (v0.10.14)
  - `pyautogui` (v0.9.54)
  - `fastapi` (v0.110+)
  - `uvicorn` (v0.28+)
  - `websockets` (v12.0+)
- **Web Browser:** Google Chrome, Microsoft Edge, or Mozilla Firefox.

---

## 5. MATHEMATICAL & ALGORITHMIC FORMULATIONS

### 5.1 Landmark Normalization to Pixel Coordinates
MediaPipe yields normalized 3D landmarks $(x_n, y_n, z_n) \in [0.0, 1.0]$. To map these to pixel positions on an image with width $W$ and height $H$:
$$X_p = \lfloor x_n \times W \rfloor, \quad Y_p = \lfloor y_n \times H \rfloor$$

### 5.2 Euclidean Distance for Pinch (Click) Detection
Let Landmark 4 (Thumb Tip) be $(X_4, Y_4)$ and Landmark 8 (Index Tip) be $(X_8, Y_8)$:
$$d_{\text{pinch}} = \sqrt{(X_8 - X_4)^2 + (Y_8 - Y_4)^2}$$
$$\text{Action} = \begin{cases} \text{Left Click}, & \text{if } d_{\text{pinch}} < \theta_{\text{click}} \text{ and } (\Delta t > t_{\text{cooldown}}) \\ \text{None}, & \text{otherwise} \end{cases}$$
Where $\theta_{\text{click}} = 35\text{px}$ and $t_{\text{cooldown}} = 0.4\text{s}$.

### 5.3 Active Zone Linear Interpolation
To allow full monitor coverage without stretching the hand outside the webcam frame, an active boundary margin $M$ is defined:
$$X_{\text{screen}} = \text{clamp}\left( \frac{X_p - M}{(W - 2M)} \times \text{Screen}_W, 0, \text{Screen}_W \right)$$
$$Y_{\text{screen}} = \text{clamp}\left( \frac{Y_p - M}{(H - 2M)} \times \text{Screen}_H, 0, \text{Screen}_H \right)$$

### 5.4 Exponential Smoothing (Jitter Filter)
To counteract natural hand tremors, an Exponential Moving Average (EMA) is applied:
$$X_t = X_{t-1} + \frac{X_{\text{target}} - X_{t-1}}{S}$$
$$Y_t = Y_{t-1} + \frac{Y_{\text{target}} - Y_{t-1}}{S}$$
Where $S \ge 1$ is the smoothing coefficient (default $S=5$).

---

## 6. PROJECT MODULES & IMPLEMENTATION

### Module 1: `hand_detector.py`
- Encapsulates Google MediaPipe Hands.
- Converts OpenCV BGR frames to RGB for tensor inference.
- Extracts $(x, y, z)$ coordinates of all 21 hand landmarks.
- Computes finger elevation state (UP vs DOWN) by comparing fingertip Y-coordinates with their respective Proximal Interphalangeal (PIP) joints.

### Module 2: `mouse_controller.py`
- Integrates `pyautogui` for desktop automation.
- Implements Safe Mode (`is_active = False` by default).
- Implements linear coordinate interpolation, exponential smoothing, click cooldowns, and vertical delta scroll calculations.
- Enforces safety triggers (PyAutoGUI FailSafe to abort if cursor hits a screen corner).

### Module 3: `main.py` (FastAPI Server & Background Engine)
- Asynchronous FastAPI server serving static frontend files.
- Thread-safe background video worker running camera capture, AI inference, and gesture evaluation.
- MJPEG video streaming route (`/video_feed`).
- Bidirectional WebSocket (`/ws`) streaming telemetry (FPS, gestures, logs) to the browser.
- REST API endpoints for safe mode toggling, emergency stop, and dynamic calibration.

### Module 4: Futuristic Neon Web Dashboard
- Cyberpunk dark aesthetic with neon cyan and purple accents.
- Live video stream HUD with crosshairs and active boundary indicator.
- Interactive gesture dictionary highlighting live gestures.
- Real-time sensitivity sliders and gesture history logs.

---

## 7. Q&A

**Q1: Why did we use MediaPipe instead of training a CNN from scratch?**  
*Answer:* MediaPipe provides a pre-trained, highly optimized pipeline combining a palm detector and a 3D hand landmark model that operates at 30+ FPS on standard CPU hardware without requiring dedicated GPU accelerators.

**Q2: Why is BGR to RGB conversion required?**  
*Answer:* OpenCV reads frames in BGR format by default, whereas MediaPipe’s underlying machine learning model was trained on RGB color spaces. Passing BGR results in inaccurate landmark predictions.

**Q3: How do we prevent accidental multiple clicks?**  
*Answer:* We implemented a software-level **Click Cooldown** timer ($t_{\text{cooldown}} = 0.4\text{s}$). Once a click fires, subsequent clicks within 400 milliseconds are ignored.

**Q4: How does the web browser display live video from Python without video files?**  
*Answer:* Using **MJPEG (Multipart JPEG) streaming**. The FastAPI server yields individual JPEG frames under the `multipart/x-mixed-replace` MIME type over HTTP. The browser renders it as a live video stream inside a standard HTML `<img>` tag.

**Q5: What are the primary safety mechanisms?**  
*Answer:* 
1. Safe Mode by default (no unwanted cursor movements upon launch).
2. Explicit user toggle (via UI switch or keyboard shortcut).
3. Closed-fist gesture locks the system.
4. PyAutoGUI corner failsafe stops control instantly.

---

## 8. CONCLUSION & FUTURE WORK
**GestureOS** provides a reliable, accessible, and responsive touchless computing experience. By combining computer vision, AI, and modern web technologies, the project demonstrates how advanced human-computer interaction can be achieved using ubiquitous consumer hardware.

### Future Enhancements:
- Two-hand gesture recognition (e.g., zoom in / zoom out, window resizing).
- Virtual on-screen gesture keyboard.
- Integration with smart home devices via IoT protocols (MQTT).
- Voice-assisted dual-mode control.

---
**Candidate Signature:** <u>Md Rakibibul Islam</u>
