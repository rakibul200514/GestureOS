"""
GestureOS - Phase 1: Camera & FPS Verification
Purpose: Test webcam access, calculate real-time FPS, and ensure smooth mirror view.
Viva Note:
  - cv2.VideoCapture(0): 0 represents default built-in webcam index.
  - cv2.flip(frame, 1): 1 means horizontal flip (mirror effect so right hand looks right).
  - cap.release(): Frees camera hardware lock so other apps can use it.
"""

import cv2
import time

def main():
    print("=" * 50)
    print("  GestureOS - Phase 1: Webcam Test")
    print("=" * 50)
    print("[INFO] Attempting to open default webcam (Index 0)...")
    
    # Initialize webcam (index 0 = built-in camera)
    cap = cv2.VideoCapture(0)
    
    # Check if camera opened successfully
    if not cap.isOpened():
        print("[ERROR] Could not access webcam. If you have an external webcam, try index 1.")
        return

    # Set camera resolution (640x480 standard for fast AI processing)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("[SUCCESS] Webcam opened successfully!")
    print("[INFO] A camera window will open now.")
    print("[INFO] Press 'q' on your keyboard to close the test.\n")

    p_time = 0  # Previous frame timestamp for FPS calculation

    while True:
        # Read a frame from camera
        # ret = True if frame captured successfully, frame = raw image data
        ret, frame = cap.read()

        if not ret:
            print("[WARNING] Failed to grab frame. Exiting...")
            break

        # Flip horizontally (1) to create natural mirror view
        frame = cv2.flip(frame, 1)

        # Calculate FPS (Frames Per Second)
        # FPS = 1 / time_taken_between_frames
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time

        # Draw a sleek neon status badge and FPS on top-left of video frame
        # cv2.putText parameters: image, text, position (x, y), font, scale, color(B,G,R), thickness
        cv2.rectangle(frame, (10, 10), (220, 50), (20, 20, 20), -1)  # Dark background box
        cv2.putText(
            frame,
            f"FPS: {int(fps)} | GestureOS",
            (20, 38),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 200, 0),  # Cyan/Blue color in BGR format
            2
        )

        # Display window
        cv2.imshow("GestureOS - Camera Test (Press Q to Exit)", frame)

        # Wait 1ms for key press; if 'q' key pressed, break loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] 'q' pressed. Closing camera...")
            break

    # Clean up and release camera hardware
    cap.release()
    cv2.destroyAllWindows()
    print("[SUCCESS] Camera released and windows closed cleanly.")

if __name__ == "__main__":
    main()
