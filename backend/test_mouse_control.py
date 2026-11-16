"""
GestureOS - Phase 3: Safe Mouse Control Integration Test
Combines HandDetector + MouseController

SAFETY CONTROLS:
- Safe Mode by default: Hand moves cursor ONLY after pressing 's' on keyboard.
- Closed Fist: Instantly locks / stops gesture control.
- Open Palm: Temporarily pauses tracking (hand rest).
- Press 's': Toggle Mouse Control ON / OFF.
- Press 'q': Quit safely.
- Emergency Screen Corner: Move mouse to screen corner to force abort.
"""

import cv2
import time
from hand_detector import HandDetector
from mouse_controller import MouseController

def main():
    print("=" * 65)
    print("  GestureOS - Phase 3: Touchless Desktop Control Test")
    print("=" * 65)
    print("[SAFETY] Safe Mode is ACTIVE by default.")
    print("[INFO] Press 's' on your keyboard to ENABLE/DISABLE mouse control.")
    print("[INFO] Press 'q' to QUIT.\n")

    # Camera setup
    cam_w, cam_h = 640, 480
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Camera could not be opened.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_h)

    # Initialize modules
    detector = HandDetector(max_hands=1, detection_con=0.7, track_con=0.6)
    controller = MouseController(smoothing=5, click_cooldown=0.4, frame_margin=100)

    p_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Mirror video
        frame = cv2.flip(frame, 1)

        # 1. Detect Hand
        frame = detector.find_hands(frame, draw=True)
        lm_list = detector.find_positions(frame)

        # Draw Active Tracking Boundary Box (neon purple)
        # Inside this box, hand movements map across your entire computer monitor
        margin = controller.frame_margin
        cv2.rectangle(frame, (margin, margin), (cam_w - margin, cam_h - margin), (255, 0, 200), 2)
        cv2.putText(frame, "Active Tracking Zone", (margin + 10, margin - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 200), 1)

        gesture_text = "Searching Hand..."
        action_text = "Idle"

        if len(lm_list) != 0:
            fingers = detector.fingers_up(lm_list)
            # Coordinates of Index Tip (8)
            ix, iy = lm_list[8][1], lm_list[8][2]
            # Coordinates of Middle Tip (12)
            mx, my = lm_list[12][1], lm_list[12][2]

            # Measure Pinch Distance (Thumb Tip 4 to Index Tip 8)
            dist, center, _ = detector.calculate_distance(4, 8, lm_list)

            # --- GESTURE DECISION LOGIC ---

            # 1. Closed Fist: STOP / DISABLE Control immediately
            if fingers == [0, 0, 0, 0, 0]:
                gesture_text = "Closed Fist"
                action_text = "EMERGENCY PAUSE"
                controller.reset_scroll()

            # 2. Open Palm: PAUSE Tracking (hand rest)
            elif fingers == [1, 1, 1, 1, 1]:
                gesture_text = "Open Palm"
                action_text = "Tracking Paused"
                controller.reset_scroll()

            # 3. Pinch: LEFT CLICK (Thumb and Index close together)
            elif dist < 35:
                gesture_text = "Pinch"
                action_text = "LEFT CLICK!"
                cv2.circle(frame, center, 14, (0, 0, 255), cv2.FILLED)
                controller.left_click()
                controller.reset_scroll()

            # 4. Two Fingers Up: SCROLL MODE (Index + Middle Up)
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
                gesture_text = "Two Fingers"
                action_text = "SCROLLING"
                # Draw line connecting index and middle
                cv2.line(frame, (ix, iy), (mx, my), (0, 255, 255), 3)
                controller.scroll(my)

            # 5. Pointer Mode: MOVE CURSOR (Index Finger Up)
            elif fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                gesture_text = "Index Pointing"
                action_text = "MOVING CURSOR"
                # Glow green dot on index tip
                cv2.circle(frame, (ix, iy), 12, (0, 255, 0), cv2.FILLED)
                controller.move_cursor(ix, iy, cam_w, cam_h)
                controller.reset_scroll()

            else:
                gesture_text = "Neutral"
                action_text = "Ready"
                controller.reset_scroll()
        else:
            controller.reset_scroll()

        # FPS Calculation
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time

        # --- HUD Status Display ---
        # Top Header Bar
        cv2.rectangle(frame, (10, 10), (630, 65), (20, 20, 20), -1)
        
        # Mode Badge (Safe Mode vs ACTIVE)
        if controller.is_active:
            status_color = (0, 255, 0)     # Neon Green
            status_text = "MOUSE: ACTIVE (Press 's' to lock)"
        else:
            status_color = (0, 0, 255)     # Red
            status_text = "SAFE MODE (Press 's' to enable)"

        cv2.putText(frame, status_text, (20, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.65, status_color, 2)
        cv2.putText(frame, f"FPS: {int(fps)}", (520, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 200, 0), 2)

        # Bottom Action Bar
        cv2.rectangle(frame, (10, 425), (630, 470), (20, 20, 20), -1)
        cv2.putText(frame, f"Gesture: {gesture_text} | Action: {action_text}",
                    (20, 452), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

        cv2.imshow("GestureOS - Phase 3: Desktop Control (Press Q to Exit)", frame)

        # Keyboard Event Listener
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("[INFO] Quitting application...")
            break
        elif key == ord('s'):
            controller.toggle()

    cap.release()
    cv2.destroyAllWindows()
    print("[SUCCESS] Application closed safely.")

if __name__ == "__main__":
    main()
