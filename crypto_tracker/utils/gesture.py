import pygame
import time
from ..config.settings import AppConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class GestureHandler:
    """Handles touch gestures like swipes and taps."""
    
    def __init__(self):
        self.start_pos = None
        self.start_time = None
        self.last_tap_time = 0
        self.last_tap_pos = None
        
        logger.info("GestureHandler initialized")
    
    def handle_touch_event(self, event: pygame.event.Event) -> dict:
        """Handle touch events and detect gestures."""
        gestures = {
            'swipe_up': False,
            'swipe_down': False,
            'swipe_left': False,
            'swipe_right': False,
            'tap': False,
            'double_tap': False
        }
        
        if event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            self.start_pos = (event.x, event.y)
            self.start_time = time.time()
            
        elif event.type == AppConfig.EVENT_TYPES['FINGER_UP']:
            if self.start_pos and self.start_time:
                current_time = time.time()
                dx = event.x - self.start_pos[0]
                dy = event.y - self.start_pos[1]
                dt = current_time - self.start_time
                
                # Check for swipe
                if dt < AppConfig.SWIPE_TIME_THRESHOLD / 1000:  # Convert ms to seconds
                    # Calculate swipe distance as percentage of screen
                    if abs(dx) > abs(dy) and abs(dx) > AppConfig.SWIPE_THRESHOLD:
                        gestures['swipe_right' if dx > 0 else 'swipe_left'] = True
                        logger.debug(f"Horizontal swipe detected: {'right' if dx > 0 else 'left'}")
                    elif abs(dy) > abs(dx) and abs(dy) > AppConfig.SWIPE_THRESHOLD:
                        gestures['swipe_down' if dy > 0 else 'swipe_up'] = True
                        logger.debug(f"Vertical swipe detected: {'down' if dy > 0 else 'up'}")
                else:
                    # Check for tap/double tap
                    if abs(dx) < AppConfig.TOUCH_MARGIN and abs(dy) < AppConfig.TOUCH_MARGIN:
                        current_time_ms = current_time * 1000
                        if (self.last_tap_time and 
                            current_time_ms - self.last_tap_time < AppConfig.DOUBLE_TAP_THRESHOLD):
                            gestures['double_tap'] = True
                            logger.debug("Double tap detected")
                        else:
                            gestures['tap'] = True
                            logger.debug("Tap detected")
                        self.last_tap_time = current_time_ms
                        self.last_tap_pos = (event.x, event.y)
                
                # Reset tracking
                self.start_pos = None
                self.start_time = None
        
        return gestures