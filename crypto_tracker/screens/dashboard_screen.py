import pygame
from datetime import datetime
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen
import time

logger = get_logger(__name__)

class DashboardScreen(BaseScreen):
    """Screen for displaying the current day and time."""
    
    def __init__(self) -> None:
        """Initialize the dashboard screen."""

        # Display settings
        self.padding = 20
        
        # Background gradient colors
        self.gradient_top = (13, 17, 23)     # Dark navy
        self.gradient_bottom = (22, 27, 34)  # Slightly lighter navy
        
        # Touch handling
        self.swipe_start_y = None
        self.swipe_threshold = AppConfig.SWIPE_THRESHOLD
        self.last_tap_time = 0
        self.double_tap_threshold = AppConfig.DOUBLE_TAP_THRESHOLD
        
        logger.info("DashboardScreen initialized")
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events.
        
        Args:
            event: The pygame event to handle
        """
        if event.type not in (AppConfig.EVENT_TYPES.FINGER_DOWN, AppConfig.EVENT_TYPES.FINGER_UP):
            return
            
        x, y = self._scale_touch_input(event)
        
        # Handle double tap to return to ticker screen
        if event.type == AppConfig.EVENT_TYPES.FINGER_DOWN:
            current_time = time.time()
            if current_time - self.last_tap_time < self.double_tap_threshold:
                logger.info("Double tap detected, returning to ticker screen")
            self.last_tap_time = current_time
        
        # Handle swipe up to settings
        if event.type == AppConfig.EVENT_TYPES.FINGER_DOWN:
            self.swipe_start_y = y
            logger.debug(f"Touch start at y={y}")
        elif event.type == AppConfig.EVENT_TYPES.FINGER_UP and self.swipe_start_y is not None:
            swipe_distance = self.swipe_start_y - y
            swipe_threshold = self.height * self.swipe_threshold
            if swipe_distance > swipe_threshold:
                logger.info("Swipe up detected, switching to settings")
            self.swipe_start_y = None
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the dashboard screen."""
        # Draw background gradient
        for y in range(self.height):
            progress = y / self.height
            color = [
                int(self.gradient_top[i] + (self.gradient_bottom[i] - self.gradient_top[i]) * progress)
                for i in range(3)
            ]
            pygame.draw.line(surface, color, (0, y), (self.width, y))
        
        # Get current time in local timezone
        now = datetime.now(self.local_tz)
        
        # Draw time
        time_text = now.strftime("%I:%M %p").lstrip("0")
        time_surface = self.fonts['title-xl'].render(time_text, True, AppConfig.WHITE)
        time_rect = time_surface.get_rect(center=(self.width // 2, self.height // 2))
        surface.blit(time_surface, time_rect)
        
        # Draw date
        date_text = now.strftime("%A, %B %d")
        date_surface = self.fonts['title-md'].render(date_text, True, AppConfig.WHITE)
        date_rect = date_surface.get_rect(center=(self.width // 2, time_rect.top - 50))
        surface.blit(date_surface, date_rect) 