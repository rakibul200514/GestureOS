"""
GestureOS - Phase 2: Hand Tracking & 21 Landmarks Visualizer
Tests real-time hand detection, finger counting, and pinch distance.

Press 'q' in the window to quit.
"""

import cv2
import time
from hand_detector import HandDetector

def main():
    print("=" * 60)
    print("  GestureOS - Phase 2: AI Hand Tracking Test")
    print("=" * 60)
    print("[INFO] Initializing MediaPipe Hand Detector...")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open camera.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Initialize our HandDetector class
    detector = HandDetector(max_hands=1, detection_con=0.7, track_con=0.6)
    
    p_time = 0
    print("[SUCCESS] Hand Detector ready!")
    print("[INFO] Show your hand in front of the camera.")
    print("[INFO] Try pointing your Index finger, making a Peace sign, or Pinching.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Mirror view
        frame = cv2.flip(frame, 1)

        # 1. Detect Hand and Draw 21 Landmarks with Neon Connections
        frame = detector.find_hands(frame, draw=True)

        # 2. Get Landmark Coordinates
        lm_list = detector.find_positions(frame)

        # Status text variables
        gesture_name = "No Hand Detected"
        fingers_status = ""

        if len(lm_list) != 0:
            # 3. Check which fingers are up
            # Returns [Thumb, Index, Middle, Ring, Pinky] (1 = UP, 0 = DOWN)
            fingers = detector.fingers_up(lm_list)
            
            finger_names = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
            active_fingers = [finger_names[i] for i in range(5) if fingers[i] == 1]
            fingers_status = ", ".join(active_fingers) if active_fingers else "Fist (All Closed)"

            # 4. Highlight the Index Finger Tip (Landmark 8) - this will control the mouse!
            ix, iy = lm_list[8][1], lm_list[8][2]
            cv2.circle(frame, (ix, iy), 10, (0, 255, 0), cv2.FILLED)  # Green glowing dot

            # 5. Measure Pinch Distance (Thumb Tip 4 to Index Tip 8)
            dist, center, _ = detector.calculate_distance(4, 8, lm_list)
            
            # Simple Gesture Classification preview
            if fingers == [0, 1, 0, 0, 0] or fingers == [1, 1, 0, 0, 0]:
                gesture_name = "Pointer Mode (Move Cursor)"
            elif dist < 35:
                gesture_name = f"PINCH DETECTED! (Click Trigger: {int(dist)}px)"
                cv2.circle(frame, center, 12, (0, 0, 255), cv2.FILLED)  # Red dot when pinched
            elif fingers == [0, 1, 1, 0, 0]:
                gesture_name = "Two Fingers (Scroll Mode)"
            elif fingers == [1, 1, 1, 1, 1]:
                gesture_name = "Open Palm (System Pause)"
            elif fingers == [0, 0, 0, 0, 0]:
                gesture_name = "Closed Fist (Stop Mode)"
            else:
                gesture_name = f"Active: {fingers_status}"

        # Calculate FPS
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time

        # --- Futuristic HUD Overlay on Video ---
        # Top HUD Bar
        cv2.rectangle(frame, (10, 10), (630, 60), (25, 20, 20), -1)
        cv2.putText(frame, f"FPS: {int(fps)}", (25, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 0), 2)
        cv2.putText(frame, f"State: {gesture_name}", (160, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # Bottom HUD Bar (shows active fingers)
        if len(lm_list) != 0:
            cv2.rectangle(frame, (10, 435), (630, 470), (25, 20, 20), -1)
            cv2.putText(frame, f"Fingers UP: {fingers_status}", (20, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 255), 1)

        # Show Output Window
        cv2.imshow("GestureOS - Phase 2: Hand Tracking (Press Q to Exit)", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[SUCCESS] Hand tracking test finished.")

if __name__ == "__main__":
    main()
