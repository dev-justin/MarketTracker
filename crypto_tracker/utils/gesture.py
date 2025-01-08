"""Gesture handling utilities."""

import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class GestureHandler:
    """Handles touch gestures."""
    
    def __init__(self) -> None:
        """Initialize the gesture handler."""
        self.start_x = None
        self.start_y = None
        self.last_gesture_time = 0
        self.gesture_cooldown = 500  # 500ms cooldown between gestures
        logger.info("GestureHandler initialized")
    
    def handle_touch_event(self, event: pygame.event.Event) -> dict:
        """Handle touch events and detect gestures."""
        gestures = {
            'swipe_up': False,
            'swipe_down': False,
            'swipe_left': False,
            'swipe_right': False
        }
        
        current_time = pygame.time.get_ticks()
        
        # Return early if we're still in cooldown
        if current_time - self.last_gesture_time < self.gesture_cooldown:
            return gestures
        
        if event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            self.start_x = event.x
            self.start_y = event.y
        
        elif event.type == AppConfig.EVENT_TYPES['FINGER_UP'] and self.start_x is not None and self.start_y is not None:
            dx = event.x - self.start_x
            dy = event.y - self.start_y
            
            # Calculate distance moved
            distance = (dx * dx + dy * dy) ** 0.5
            
            # Only register as swipe if moved more than 10% of screen
            if distance > 0.1:
                # Determine primary direction
                if abs(dx) > abs(dy):
                    if dx > 0:
                        gestures['swipe_right'] = True
                    else:
                        gestures['swipe_left'] = True
                else:
                    if dy > 0:
                        gestures['swipe_down'] = True
                    else:
                        gestures['swipe_up'] = True
                
                # Update last gesture time
                self.last_gesture_time = current_time
            
            # Reset start position
            self.start_x = None
            self.start_y = None
        
        return gestures