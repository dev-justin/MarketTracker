import pygame
import time
from ..config.settings import AppConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class GestureHandler:
    """Handles touch gestures like swipes and taps."""
    
    def __init__(self):
        """Initialize the gesture handler."""
        self.swipe_start_y = None
        self.last_tap_time = 0
        self.swipe_threshold = AppConfig.SWIPE_THRESHOLD
        self.double_tap_threshold = AppConfig.DOUBLE_TAP_THRESHOLD
        logger.info("GestureHandler initialized")
    
    def handle_touch_event(self, event: pygame.event.Event, screen_height: int) -> tuple[bool, bool]:
        """
        Handle touch events and detect gestures.
        
        Args:
            event: The pygame event to handle
            screen_height: The height of the screen for swipe calculations
            
        Returns:
            Tuple of (is_double_tap, is_swipe_up)
        """
        if event.type not in (AppConfig.EVENT_TYPES['FINGER_DOWN'], AppConfig.EVENT_TYPES['FINGER_UP']):
            return False, False
            
        is_double_tap = False
        is_swipe_up = False
        
        # Handle double tap
        if event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            current_time = time.time()
            if current_time - self.last_tap_time < self.double_tap_threshold:
                is_double_tap = True
                logger.debug("Double tap detected")
            self.last_tap_time = current_time
        
        # Handle swipe up
        if event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            self.swipe_start_y = event.y
        elif event.type == AppConfig.EVENT_TYPES['FINGER_UP'] and self.swipe_start_y is not None:
            swipe_distance = self.swipe_start_y - event.y
            swipe_threshold = screen_height * self.swipe_threshold
            if swipe_distance > swipe_threshold:
                is_swipe_up = True
                logger.debug("Swipe up detected")
            self.swipe_start_y = None
        
        return is_double_tap, is_swipe_up