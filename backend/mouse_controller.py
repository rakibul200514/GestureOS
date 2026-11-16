"""
GestureOS - Phase 3: Mouse & System Controller Module
Powered by PyAutoGUI

BCA Viva Key Knowledge:
1. Screen Resolution Mapping (Linear Interpolation):
   Webcam resolution (e.g., 640x480) != Monitor resolution (e.g., 1920x1080).
   We use np.interp() to map hand coordinates inside an active bounding box to full screen.
2. Exponential Smoothing (Jitter Reduction):
   cur_x = prev_x + (target_x - prev_x) / smoothing
   Eliminates natural hand trembling for smooth, professional mouse tracking.
3. Click Cooldown:
   Prevents accidental rapid multi-clicks by enforcing a time gap (e.g., 0.4s).
4. Safety First:
   - Safe Mode enabled by default.
   - PyAutoGUI FAILSAFE enabled (slamming cursor to screen corner triggers emergency stop).
"""

import time
import pyautogui
import numpy as np

class MouseController:
    def __init__(self, smoothing=5, click_cooldown=0.4, frame_margin=100):
        """
        :param smoothing: Higher value = smoother cursor, slightly more latency. (Default 5)
        :param click_cooldown: Minimum seconds between consecutive clicks. (Default 0.4s)
        :param frame_margin: Padding around webcam frame boundary for easy edge reach.
        """
        # Safety Settings
        pyautogui.FAILSAFE = True  # Move mouse to screen corner in emergency to stop
        pyautogui.PAUSE = 0.001    # Minimal delay for responsiveness

        # Screen dimensions
        self.screen_w, self.screen_h = pyautogui.size()
        
        # Calibration & Smoothing variables
        self.frame_margin = frame_margin
        self.smoothing = max(1, smoothing)
        self.prev_x, self.prev_y = self.screen_w // 2, self.screen_h // 2
        self.curr_x, self.curr_y = self.prev_x, self.prev_y

        # State & Cooldowns
        self.is_active = False           # Safe mode: Disabled by default!
        self.click_cooldown = click_cooldown
        self.last_click_time = 0
        self.last_scroll_y = None
        self.scroll_sensitivity = 40

    def enable(self):
        """Explicitly enables mouse control."""
        self.is_active = True
        print("[SAFETY] Mouse Control: ENABLED")

    def disable(self):
        """Disables mouse control (Safe Mode)."""
        self.is_active = False
        print("[SAFETY] Mouse Control: DISABLED (Safe Mode Active)")

    def toggle(self):
        """Toggles between Enabled and Safe Mode."""
        self.is_active = not self.is_active
        return self.is_active

    def move_cursor(self, finger_x, finger_y, cam_w=640, cam_h=480):
        """
        Maps webcam coordinates to computer screen coordinates with smoothing.
        """
        if not self.is_active:
            return self.prev_x, self.prev_y

        # 1. Map camera frame coordinates to screen resolution using active boundary margin
        # This makes it easy to reach screen edges without stretching hand out of camera
        target_x = np.interp(finger_x, (self.frame_margin, cam_w - self.frame_margin), (0, self.screen_w))
        target_y = np.interp(finger_y, (self.frame_margin, cam_h - self.frame_margin), (0, self.screen_h))

        # Clamp values within screen bounds
        target_x = max(0, min(self.screen_w - 1, target_x))
        target_y = max(0, min(self.screen_h - 1, target_y))

        # 2. Smooth the movement using Exponential Moving Average (EMA)
        self.curr_x = self.prev_x + (target_x - self.prev_x) / self.smoothing
        self.curr_y = self.prev_y + (target_y - self.prev_y) / self.smoothing

        # 3. Perform the actual cursor movement
        try:
            pyautogui.moveTo(self.curr_x, self.curr_y)
        except pyautogui.FailSafeException:
            print("[EMERGENCY] PyAutoGUI FailSafe triggered! Disabling control.")
            self.disable()

        # Update previous position for next frame
        self.prev_x, self.prev_y = self.curr_x, self.curr_y
        return int(self.curr_x), int(self.curr_y)

    def left_click(self):
        """
        Simulates left mouse click if cooldown time has passed.
        Returns True if click succeeded, False if blocked by cooldown.
        """
        if not self.is_active:
            return False

        c_time = time.time()
        if (c_time - self.last_click_time) > self.click_cooldown:
            try:
                pyautogui.click()
                self.last_click_time = c_time
                print("[ACTION] Left Click performed!")
                return True
            except pyautogui.FailSafeException:
                self.disable()
        return False

    def scroll(self, middle_y):
        """
        Scrolls up or down based on vertical finger movement.
        """
        if not self.is_active:
            return

        if self.last_scroll_y is None:
            self.last_scroll_y = middle_y
            return

        delta_y = self.last_scroll_y - middle_y

        # Only scroll if movement exceeds deadzone threshold
        if abs(delta_y) > 8:
            scroll_amount = int(delta_y * 3)
            try:
                pyautogui.scroll(scroll_amount)
            except pyautogui.FailSafeException:
                self.disable()

        self.last_scroll_y = middle_y

    def reset_scroll(self):
        """Resets scroll tracker when gesture exits."""
        self.last_scroll_y = None
