import pygame
from datetime import datetime
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen
import time

logger = get_logger(__name__)

# Display settings
PADDING = 20
        
# Background gradient colors
GRADIENT_TOP = (13, 17, 23)     # Dark navy
GRADIENT_BOTTOM = (22, 27, 34)  # Slightly lighter navy
        
# Touch handling
SWIPE_START_Y = None
SWIPE_THRESHOLD = AppConfig.SWIPE_THRESHOLD
LAST_TAP_TIME = 0
DOUBLE_TAP_THRESHOLD = AppConfig.DOUBLE_TAP_THRESHOLD

class DashboardScreen(BaseScreen):
    """Screen for displaying the current day and time."""

        
    logger.info("DashboardScreen initialized")
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events.
        
        Args:
            event: The pygame event to handle
        """
        if event.type not in (AppConfig.EVENT_TYPES['FINGER_DOWN'], AppConfig.EVENT_TYPES['FINGER_UP']):
            return
            
        x, y = self._scale_touch_input(event)
        
        # Handle double tap to return to ticker screen
        if event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            current_time = time.time()
            if current_time - self.LAST_TAP_TIME < self.DOUBLE_TAP_THRESHOLD:
                logger.info("Double tap detected, returning to ticker screen")
            self.LAST_TAP_TIME = current_time
        
        # Handle swipe up to settings
        if event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            SWIPE_START_Y = y
            logger.debug(f"Touch start at y={y}")
        elif event.type == AppConfig.EVENT_TYPES['FINGER_UP'] and SWIPE_START_Y is not None:
            swipe_distance = SWIPE_START_Y - y
            swipe_threshold = self.height * self.SWIPE_THRESHOLD
            if swipe_distance > swipe_threshold:
                logger.info("Swipe up detected, switching to settings")
            SWIPE_START_Y = None
    
    def draw(self) -> None:
        """Draw the dashboard screen."""
        # Draw background gradient
        for y in range(self.height):
            progress = y / self.height
            color = [
                int(self.GRADIENT_TOP[i] + (self.GRADIENT_BOTTOM[i] - self.GRADIENT_TOP[i]) * progress)
                for i in range(3)
            ]
            pygame.draw.line(self.display.surface, color, (0, y), (self.width, y))
        
        # Get current time in local timezone
        now = datetime.now()
        
        # Draw time
        time_text = now.strftime("%I:%M %p").lstrip("0")
        time_surface = self.fonts['title-xl'].render(time_text, True, AppConfig.WHITE)
        time_rect = time_surface.get_rect(center=(self.width // 2, self.height // 2))
        self.display.surface.blit(time_surface, time_rect)
        
        # Draw date
        date_text = now.strftime("%A, %B %d")
        date_surface = self.fonts['title-md'].render(date_text, True, AppConfig.WHITE)
        date_rect = date_surface.get_rect(center=(self.width // 2, time_rect.top - 50))
        self.display.surface.blit(date_surface, date_rect) 

        self.update_screen()