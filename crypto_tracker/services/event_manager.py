"""Event management service."""

import pygame
from typing import Optional, Dict, Any
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from ..utils.gesture import GestureHandler

logger = get_logger(__name__)

class EventManager:
    """Manages event handling and gesture processing."""
    
    def __init__(self) -> None:
        """Initialize the event manager."""
        self.gesture_handler = GestureHandler()
        self.screen_manager = None
        self.last_event_time = 0
        self.event_cooldown = 50  # 50ms cooldown between events
        self.current_gesture: Dict[str, bool] = {
            'swipe_up': False,
            'swipe_down': False,
            'swipe_left': False,
            'swipe_right': False
        }
        logger.info("EventManager initialized")
    
    def set_screen_manager(self, screen_manager) -> None:
        """Set the screen manager reference."""
        self.screen_manager = screen_manager
    
    def process_event(self, event: pygame.event.Event) -> bool:
        """Process a single event and return whether screen needs update."""
        current_time = pygame.time.get_ticks()
        
        # Basic event filtering
        if event.type not in [
            AppConfig.EVENT_TYPES['FINGER_DOWN'],
            AppConfig.EVENT_TYPES['FINGER_UP'],
            AppConfig.EVENT_TYPES['FINGER_MOTION']
        ]:
            return False
            
        # Apply event cooldown
        if current_time - self.last_event_time < self.event_cooldown:
            return False
            
        self.last_event_time = current_time
        
        # Process gestures
        self.current_gesture = self.gesture_handler.handle_touch_event(event)
        
        # Forward event to screen manager if available
        if self.screen_manager:
            return self.screen_manager.handle_event(event, self.current_gesture)
        
        return False
    
    def get_current_gesture(self) -> Dict[str, bool]:
        """Get the current gesture state."""
        return self.current_gesture.copy()
    
    def reset_gesture_state(self) -> None:
        """Reset the current gesture state."""
        self.current_gesture = {
            'swipe_up': False,
            'swipe_down': False,
            'swipe_left': False,
            'swipe_right': False
        } 