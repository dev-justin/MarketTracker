import pygame
from datetime import datetime
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen
from ..utils.gesture import handle_touch_event

logger = get_logger(__name__)

class DashboardScreen(BaseScreen):
    """Screen for displaying the current day and time."""

        
    logger.info("DashboardScreen initialized")
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        is_double_tap, is_swipe_up = handle_touch_event(event, self.height)
        if is_double_tap:
            logger.info("Double tap detected, returning to ticker screen")
        elif is_swipe_up:
            logger.info("Swipe up detected, switching to settings")
    
    def draw(self) -> None:
        """Draw the dashboard screen."""

        # Display settings
        padding = 20
                
        # Background gradient colors
        gradient_top = (13, 17, 23)     # Dark navy
        gradient_bottom = (22, 27, 34)  # Slightly lighter navy

        # Draw background gradient
        for y in range(self.height):
            progress = y / self.height
            color = [
                int(gradient_top[i] + (gradient_bottom[i] - gradient_top[i]) * progress)
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