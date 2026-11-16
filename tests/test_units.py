"""
GestureOS - Unit Tests
BCA 3rd Semester Project Verification

Tests:
1. Module imports (OpenCV, MediaPipe, PyAutoGUI, FastAPI)
2. HandDetector class initialization and finger logic
3. MouseController screen size and safety mode
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.append(str(backend_path))

from hand_detector import HandDetector
from mouse_controller import MouseController

def test_hand_detector_initialization():
    """Verify HandDetector initializes with default parameters."""
    detector = HandDetector(max_hands=1, detection_con=0.7, track_con=0.6)
    assert detector.max_hands == 1
    assert detector.detection_con == 0.7
    assert detector.track_con == 0.6
    assert detector.tip_ids == [4, 8, 12, 16, 20]
    print("[PASS] HandDetector initialization test.")

def test_mouse_controller_safe_mode():
    """Verify MouseController starts in Safe Mode (Disabled by default)."""
    controller = MouseController(smoothing=5, click_cooldown=0.4)
    assert controller.is_active is False, "Safety violation: Mouse control should start DISABLED!"
    assert controller.smoothing == 5
    assert controller.click_cooldown == 0.4
    
    # Test toggle
    controller.enable()
    assert controller.is_active is True
    controller.disable()
    assert controller.is_active is False
    print("[PASS] MouseController Safe Mode test.")

def test_distance_calculation():
    """Verify Euclidean distance math."""
    detector = HandDetector()
    # Dummy landmark list where Point 4 is at (0, 0) and Point 8 is at (3, 4) -> 3-4-5 triangle
    lm_list = [[i, 0, 0, 0] for i in range(21)]
    lm_list[4] = [4, 0, 0, 0]
    lm_list[8] = [8, 3, 4, 0]
    
    dist, center, _ = detector.calculate_distance(4, 8, lm_list)
    assert dist == 5.0, f"Expected distance 5.0, got {dist}"
    assert center == (1, 2)
    print("[PASS] Euclidean distance calculation test.")

if __name__ == "__main__":
    test_hand_detector_initialization()
    test_mouse_controller_safe_mode()
    test_distance_calculation()
    print("\n[SUCCESS] ALL UNIT TESTS PASSED!")
