import pygame
import time
from ..config.settings import AppConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class GestureHandler:
    """Handles touch gestures like swipes and taps."""
    
    def __init__(self):
        """Initialize the gesture handler."""
        self.last_tap_time = 0
        self.last_tap_pos = None
        self.start_pos = None  # Track start position for swipes
        logger.info("GestureHandler initialized")
    
    def handle_touch_event(self, event: pygame.event.Event) -> dict:
        """
        Handle touch events and detect gestures.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            Dictionary containing gesture information:
            {
                'double_tap_left': bool,  # Double tap on left half of screen
                'double_tap_right': bool, # Double tap on right half of screen
                'swipe_up': bool,         # Swipe up gesture
                'swipe_down': bool,       # Swipe down gesture
                'swipe_right': bool,      # Swipe right gesture
                'swipe_left': bool        # Swipe left gesture
            }
        """
        current_time = pygame.time.get_ticks() / 1000  # Convert to seconds
        gestures = {
            'double_tap_left': False,
            'double_tap_right': False,
            'swipe_up': False,
            'swipe_down': False,
            'swipe_right': False,
            'swipe_left': False
        }
        
        if event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            # Store start position for swipe detection
            x = event.x * AppConfig.DISPLAY_WIDTH
            y = event.y * AppConfig.DISPLAY_HEIGHT
            self.start_pos = (x, y)
            
            # Check for double tap
            if self.last_tap_pos is not None:
                time_diff = current_time - self.last_tap_time
                if time_diff < AppConfig.DOUBLE_TAP_THRESHOLD:
                    # Check which half of the screen was tapped
                    if x < AppConfig.DISPLAY_WIDTH / 2:
                        gestures['double_tap_left'] = True
                        logger.debug("Double tap detected on left side")
                    else:
                        gestures['double_tap_right'] = True
                        logger.debug("Double tap detected on right side")
            
            self.last_tap_time = current_time
            self.last_tap_pos = (x, y)
            
        elif event.type == AppConfig.EVENT_TYPES['FINGER_UP'] and self.start_pos is not None:
            # Calculate swipe
            end_x = event.x * AppConfig.DISPLAY_WIDTH
            end_y = event.y * AppConfig.DISPLAY_HEIGHT
            dx = end_x - self.start_pos[0]
            dy = end_y - self.start_pos[1]
            
            # Calculate swipe distance as percentage of screen dimensions
            swipe_x = abs(dx) / AppConfig.DISPLAY_WIDTH
            swipe_y = abs(dy) / AppConfig.DISPLAY_HEIGHT
            
            # Detect swipe direction
            if swipe_y > AppConfig.SWIPE_THRESHOLD:
                if dy > 0:
                    gestures['swipe_down'] = True
                    logger.debug("Swipe down detected")
                else:
                    gestures['swipe_up'] = True
                    logger.debug("Swipe up detected")
            elif swipe_x > AppConfig.SWIPE_THRESHOLD:
                if dx > 0:
                    gestures['swipe_right'] = True
                    logger.debug("Swipe right detected")
                else:
                    gestures['swipe_left'] = True
                    logger.debug("Swipe left detected")
            
            self.start_pos = None
        
        return gestures