"""
GestureOS - Phase 2: Hand Detector Module
Powered by Google MediaPipe & OpenCV

BCA Viva Key Knowledge:
1. MediaPipe tracks 21 3D hand landmarks (points 0 to 20).
2. Key Landmarks:
   - 0: Wrist
   - 4: Thumb Tip
   - 8: Index Finger Tip (Used for Cursor Movement)
   - 12: Middle Finger Tip
   - 16: Ring Finger Tip
   - 20: Pinky Tip
3. OpenCV reads frames in BGR format, but MediaPipe requires RGB format.
   Therefore: cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) is mandatory.
4. Normalized vs Pixel coordinates:
   MediaPipe returns coordinates as ratios (0.0 to 1.0).
   Pixel X = normalized_x * image_width
   Pixel Y = normalized_y * image_height
"""

import cv2
import mediapipe as mp
import math

class HandDetector:
    def __init__(self, mode=False, max_hands=1, detection_con=0.7, track_con=0.6):
        """
        Initializes the MediaPipe Hands model.
        :param mode: False for stream tracking (faster), True for static images.
        :param max_hands: Maximum hands to detect (1 for mouse control to avoid confusion).
        :param detection_con: Minimum confidence (0.0 - 1.0) to detect a hand initially.
        :param track_con: Minimum confidence to continue tracking frame-to-frame.
        """
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con

        # MediaPipe Hands API
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        # Tip Landmark IDs for: [Thumb, Index, Middle, Ring, Pinky]
        self.tip_ids = [4, 8, 12, 16, 20]
        self.results = None

    def find_hands(self, frame, draw=True):
        """
        Detects hand in the frame and draws landmark connections.
        """
        # Convert BGR to RGB because MediaPipe requires RGB
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame with MediaPipe model
        self.results = self.hands.process(img_rgb)

        # If a hand is found and draw is enabled
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    # Draw elegant neon connections and landmark dots
                    self.mp_draw.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        # Landmark circles (Neon Cyan/Blue)
                        self.mp_draw.DrawingSpec(color=(255, 200, 0), thickness=2, circle_radius=3),
                        # Connection lines (Neon Purple/Magenta)
                        self.mp_draw.DrawingSpec(color=(218, 50, 180), thickness=2, circle_radius=2)
                    )
        return frame

    def find_positions(self, frame, hand_no=0):
        """
        Extracts pixel coordinates of all 21 landmarks for a detected hand.
        Returns a list of [id, x, y, z] tuples.
        """
        landmark_list = []
        h, w, c = frame.shape

        if self.results and self.results.multi_hand_landmarks:
            if len(self.results.multi_hand_landmarks) > hand_no:
                target_hand = self.results.multi_hand_landmarks[hand_no]
                for idx, lm in enumerate(target_hand.landmark):
                    # Convert normalized ratio (0.0 to 1.0) into actual pixel values
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    landmark_list.append([idx, cx, cy, lm.z])

        return landmark_list

    def fingers_up(self, lm_list):
        """
        Determines which fingers are held up (open) vs curled (closed).
        Returns a list of 5 booleans [Thumb, Index, Middle, Ring, Pinky]:
        e.g., [0, 1, 0, 0, 0] means only Index finger is pointing up.
        """
        if len(lm_list) < 21:
            return [0, 0, 0, 0, 0]

        fingers = []

        # 1. Thumb Check: Compare Thumb Tip (4) with Thumb Knuckle IP (3) on X-axis
        # For mirrored right hand in front of webcam:
        if lm_list[self.tip_ids[0]][1] > lm_list[self.tip_ids[0] - 1][1]:
            fingers.append(1)  # Open
        else:
            fingers.append(0)  # Closed

        # 2. Four Fingers Check (Index, Middle, Ring, Pinky):
        # A finger is UP if its Tip Y coordinate is LESS (higher on screen) than its PIP joint (2 points down)
        for idx in range(1, 5):
            tip_id = self.tip_ids[idx]
            pip_id = tip_id - 2
            if lm_list[tip_id][2] < lm_list[pip_id][2]:
                fingers.append(1)  # Finger is pointing up
            else:
                fingers.append(0)  # Finger is curled down

        return fingers

    def calculate_distance(self, p1, p2, lm_list):
        """
        Calculates Euclidean distance between two landmarks (e.g., Thumb tip 4 & Index tip 8).
        Formula: sqrt((x2 - x1)^2 + (y2 - y1)^2)
        """
        if len(lm_list) < 21:
            return 0, 0, 0

        x1, y1 = lm_list[p1][1], lm_list[p1][2]
        x2, y2 = lm_list[p2][1], lm_list[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        distance = math.hypot(x2 - x1, y2 - y1)
        return distance, (cx, cy), (x1, y1, x2, y2)
