import pygame
from datetime import datetime
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen
from zoneinfo import ZoneInfo
logger = get_logger(__name__)

class DashboardScreen(BaseScreen):
    """Screen for displaying the current day and time."""
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        is_double_tap, is_swipe_up = self.gesture_handler.handle_touch_event(event, self.height)
        if is_double_tap:
            logger.info("Double tap detected, returning to ticker screen")
        elif is_swipe_up:
            logger.info("Swipe up detected, switching to settings")
    
    def draw(self) -> None:
        """Draw the dashboard screen."""

        GRADIENT_TOP = (13, 17, 23)
        GRADIENT_BOTTOM = (22, 27, 34)

        # Draw background gradient
        for y in range(self.height):
            progress = y / self.height
            color = [
                int(GRADIENT_TOP[i] + (GRADIENT_BOTTOM[i] - GRADIENT_TOP[i]) * progress)
                for i in range(3)
            ]
            pygame.draw.line(self.display.surface, color, (0, y), (self.width, y))
        
        # Get current time 
        now = datetime.now()
        local_time = now.astimezone(ZoneInfo(AppConfig.TIMEZONE))
        
        # Draw time
        time_text = local_time.strftime("%I:%M %p").lstrip("0")
        time_surface = self.fonts['title-xl'].render(time_text, True, AppConfig.WHITE)
        time_rect = time_surface.get_rect(centerx=self.width // 2, top=20)
        self.display.surface.blit(time_surface, time_rect)
        
        # Draw date
        date_text = local_time.strftime("%A, %B %d")
        date_surface = self.fonts['light-lg'].render(date_text, True, AppConfig.WHITE)
        date_rect = date_surface.get_rect(centerx=self.width // 2, top=time_rect.bottom + 5)
        self.display.surface.blit(date_surface, date_rect)
        
        self.update_screen()