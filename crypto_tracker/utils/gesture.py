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
    
    def handle_touch_event(self, event: pygame.event.Event, screen_width: int, screen_height: int) -> dict:
        """
        Handle touch events and detect gestures.
        
        Args:
            event: The pygame event to handle
            screen_width: The width of the screen for position calculations
            screen_height: The height of the screen for swipe calculations
            
        Returns:
            Dictionary containing gesture information:
            {
                'double_tap_left': bool,  # Double tap on left half of screen
                'double_tap_right': bool, # Double tap on right half of screen
                'swipe_up': bool,         # Swipe up gesture
                'swipe_down': bool        # Swipe down gesture
            }
        """
        current_time = pygame.time.get_ticks() / 1000  # Convert to seconds
        gestures = {
            'double_tap_left': False,
            'double_tap_right': False,
            'swipe_up': False,
            'swipe_down': False
        }
        
        if event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            # Store start position for swipe detection
            x = event.x * screen_width
            y = event.y * screen_height
            self.start_pos = (x, y)
            
            # Check for double tap
            if self.last_tap_pos is not None:
                time_diff = current_time - self.last_tap_time
                if time_diff < AppConfig.DOUBLE_TAP_THRESHOLD:
                    # Determine which side was tapped
                    if x < screen_width / 2:
                        gestures['double_tap_left'] = True
                        logger.debug("Double tap left detected")
                    else:
                        gestures['double_tap_right'] = True
                        logger.debug("Double tap right detected")
            
            self.last_tap_time = current_time
            self.last_tap_pos = (x, y)
            
        elif event.type == AppConfig.EVENT_TYPES['FINGER_UP']:
            if self.start_pos is not None:
                end_x = event.x * screen_width
                end_y = event.y * screen_height
                start_x, start_y = self.start_pos
                
                # Calculate vertical swipe distance as percentage of screen height
                vertical_swipe = (start_y - end_y) / screen_height
                
                # If swiped up more than threshold
                if vertical_swipe > AppConfig.SWIPE_THRESHOLD:
                    gestures['swipe_up'] = True
                    logger.debug("Swipe up detected")
                # If swiped down more than threshold
                elif vertical_swipe < -AppConfig.SWIPE_THRESHOLD:
                    gestures['swipe_down'] = True
                    logger.debug("Swipe down detected")
                
                self.start_pos = None
        
        return gestures