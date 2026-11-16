"""
GestureOS - Standalone Native Desktop Application
Runs directly on Windows 11 with NO browser required.

Controls:
- 's' key: Toggle Mouse Control ON / OFF (Safe Mode)
- 'q' key or ESC: Exit cleanly
- Corner FailSafe: Push mouse to screen corner to emergency abort
"""

import cv2
import time
from hand_detector import HandDetector
from mouse_controller import MouseController

def main():
    print("=" * 65)
    print("      GestureOS - Standalone Desktop Application")
    print("               (No Browser Required)")
    print("=" * 65)
    print("[INFO] Starting Native Windows Desktop Controller...")
    
    cam_w, cam_h = 640, 480
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("[ERROR] Cannot access webcam.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_h)

    # Initialize modules
    detector = HandDetector(max_hands=1, detection_con=0.7, track_con=0.6)
    controller = MouseController(smoothing=5, click_cooldown=0.4, frame_margin=90)

    p_time = 0
    print("[READY] Press 's' on your keyboard to ENABLE mouse control.")
    print("[READY] Press 'q' or 'ESC' to quit.\n")

    window_name = "GestureOS - Touchless Controller"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Mirror view for natural interaction
        frame = cv2.flip(frame, 1)

        # 1. Detect Hand
        frame = detector.find_hands(frame, draw=True)
        lm_list = detector.find_positions(frame)

        # 2. Draw Active Zone Box (Neon Purple)
        margin = controller.frame_margin
        cv2.rectangle(frame, (margin, margin), (cam_w - margin, cam_h - margin), (255, 0, 200), 2)
        cv2.putText(frame, "ACTIVE DESKTOP ZONE", (margin + 8, margin - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 200), 1)

        gesture_name = "Searching Hand..."
        action_name = "Idle"

        if len(lm_list) != 0:
            fingers = detector.fingers_up(lm_list)
            ix, iy = lm_list[8][1], lm_list[8][2]
            mx, my = lm_list[12][1], lm_list[12][2]
            dist, center, _ = detector.calculate_distance(4, 8, lm_list)

            # Gesture 1: Closed Fist (Emergency Pause)
            if fingers == [0, 0, 0, 0, 0]:
                gesture_name = "Closed Fist"
                action_name = "STOPPED (Safe Mode)"
                controller.disable()
                controller.reset_scroll()

            # Gesture 2: Open Palm (Pause)
            elif fingers == [1, 1, 1, 1, 1]:
                gesture_name = "Open Palm"
                action_name = "Tracking Paused"
                controller.reset_scroll()

            # Gesture 3: Pinch (Left Click)
            elif dist < 35:
                gesture_name = "Pinch"
                action_name = "LEFT CLICK!"
                cv2.circle(frame, center, 14, (0, 0, 255), cv2.FILLED)
                controller.left_click()
                controller.reset_scroll()

            # Gesture 4: Two Fingers (Scroll Mode)
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
                gesture_name = "Two Fingers"
                action_name = "SCROLLING"
                cv2.line(frame, (ix, iy), (mx, my), (0, 255, 255), 3)
                controller.scroll(my)

            # Gesture 5: Index Finger (Move Mouse Cursor)
            elif fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                gesture_name = "Index Finger"
                action_name = "MOVING CURSOR"
                cv2.circle(frame, (ix, iy), 10, (0, 255, 0), cv2.FILLED)
                controller.move_cursor(ix, iy, cam_w, cam_h)
                controller.reset_scroll()

            else:
                gesture_name = "Neutral"
                action_name = "Ready"
                controller.reset_scroll()
        else:
            controller.reset_scroll()

        # FPS
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time

        # --- HUD Elements ---
        # Top Header Bar
        cv2.rectangle(frame, (10, 10), (630, 65), (20, 20, 20), -1)
        if controller.is_active:
            status_text = "MOUSE: ACTIVE (Press 's' to lock)"
            status_color = (0, 255, 0)
        else:
            status_text = "SAFE MODE (Press 's' to enable)"
            status_color = (0, 0, 255)

        cv2.putText(frame, status_text, (20, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.65, status_color, 2)
        cv2.putText(frame, f"FPS: {int(fps)}", (520, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 200, 0), 2)

        # Bottom Bar
        cv2.rectangle(frame, (10, 425), (630, 470), (20, 20, 20), -1)
        cv2.putText(frame, f"State: {gesture_name} | Action: {action_name}",
                    (20, 452), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

        cv2.imshow(window_name, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # 'q' or ESC
            break
        elif key == ord('s'):
            controller.toggle()

    cap.release()
    cv2.destroyAllWindows()
    print("[SUCCESS] Application closed.")

if __name__ == "__main__":
    main()
