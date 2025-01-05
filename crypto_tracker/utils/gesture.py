import time
from ..config.settings import AppConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class GestureDetector:
    """
    A helper class to detect gestures like double tap and swipe up.
    """

    def __init__(self):
        self.last_tap_time = 0
        self.swipe_start_y = None

    def handle_touch_event(self, event, screen_height):
        """
        Analyze the incoming touch event and return whether a double tap or swipe up occurred.

        Args:
            event: The pygame event to handle.
            screen_height: The current screen height, used for scaling threshold.

        Returns:
            A tuple: (is_double_tap, is_swipe_up)
        """
        double_tap_detected = False
        swipe_up_detected = False

        # Only handle finger down/up
        if event.type not in (
            AppConfig.EVENT_TYPES['FINGER_DOWN'],
            AppConfig.EVENT_TYPES['FINGER_UP']
        ):
            return double_tap_detected, swipe_up_detected

        # Check double tap
        if event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            current_time = time.time()
            if (current_time - self.last_tap_time) < AppConfig.DOUBLE_TAP_THRESHOLD:
                double_tap_detected = True
                logger.info("Double tap detected")
            self.last_tap_time = current_time

            # Track start position for swipe
            self.swipe_start_y = event.y * screen_height

        elif event.type == AppConfig.EVENT_TYPES['FINGER_UP'] and self.swipe_start_y is not None:
            swipe_distance = self.swipe_start_y - (event.y * screen_height)
            threshold_pixels = screen_height * AppConfig.SWIPE_THRESHOLD
            if swipe_distance > threshold_pixels:
                swipe_up_detected = True
                logger.info("Swipe up detected")

            # Reset so next touch starts fresh
            self.swipe_start_y = None

        return double_tap_detected, swipe_up_detected