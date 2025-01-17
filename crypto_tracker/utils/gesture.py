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
        self.press_start_time = None
        self.LONG_PRESS_DURATION = 500  # milliseconds
        logger.info("GestureHandler initialized")
    
    def handle_touch_event(self, event: pygame.event.Event) -> dict:
        """Handle touch events and detect gestures."""
        gestures = {
            'swipe_up': False,
            'swipe_down': False,
            'swipe_left': False,
            'swipe_right': False,
            'long_press': False
        }
        
        if event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            self.start_x = event.x
            self.start_y = event.y
            self.press_start_time = pygame.time.get_ticks()
            logger.debug(f"Touch start at ({self.start_x:.2f}, {self.start_y:.2f})")
        
        elif event.type == AppConfig.EVENT_TYPES['FINGER_UP'] and self.start_x is not None and self.start_y is not None:
            dx = event.x - self.start_x
            dy = event.y - self.start_y
            
            # Calculate distance moved
            distance = (dx * dx + dy * dy) ** 0.5
            logger.debug(f"Touch end at ({event.x:.2f}, {event.y:.2f}), distance: {distance:.2f}")
            
            # Check for long press
            if self.press_start_time is not None:
                press_duration = pygame.time.get_ticks() - self.press_start_time
                if press_duration >= self.LONG_PRESS_DURATION and distance < 0.05:
                    gestures['long_press'] = True
                    logger.debug(f"Detected long press (duration={press_duration}ms)")
            
            # Only register as swipe if moved more than 10% of screen
            if distance > 0.1:
                # Determine primary direction
                if abs(dx) > abs(dy):
                    if dx > 0:
                        gestures['swipe_right'] = True
                        logger.debug(f"Detected swipe right (dx={dx:.2f}, dy={dy:.2f})")
                    else:
                        gestures['swipe_left'] = True
                        logger.debug(f"Detected swipe left (dx={dx:.2f}, dy={dy:.2f})")
                else:
                    if dy > 0:
                        gestures['swipe_down'] = True
                        logger.debug(f"Detected swipe down (dx={dx:.2f}, dy={dy:.2f})")
                    else:
                        gestures['swipe_up'] = True
                        logger.debug(f"Detected swipe up (dx={dx:.2f}, dy={dy:.2f})")
            else:
                logger.debug("Touch distance too small for gesture")
            
            # Reset start position and time
            self.start_x = None
            self.start_y = None
            self.press_start_time = None
        
        elif event.type == AppConfig.EVENT_TYPES['FINGER_MOTION']:
            logger.debug(f"Touch motion at ({event.x:.2f}, {event.y:.2f})")
        
        return gestures