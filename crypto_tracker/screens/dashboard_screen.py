import pygame
from datetime import datetime
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen
from zoneinfo import ZoneInfo
logger = get_logger(__name__)

class DashboardScreen(BaseScreen):
    """Screen for displaying the current day and time."""
    
    def __init__(self, display) -> None:
        """Initialize the dashboard screen."""
        super().__init__(display)
        self.background_color = (0, 0, 0)  # Pure black
        logger.info("DashboardScreen initialized")
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        # Handle touch events
        gestures = self.gesture_handler.handle_touch_event(event)
        
        if gestures['swipe_up']:
            logger.info("Swipe up detected, switching to settings")
            self.screen_manager.switch_screen('settings')
        elif gestures['swipe_down']:
            logger.info("Swipe down detected, switching to ticker")
            self.screen_manager.switch_screen('ticker')
    
    def draw(self) -> None:
        """Draw the dashboard screen."""
        # Fill background with black
        self.display.surface.fill(self.background_color)
        
        # Get current time 
        now = datetime.now()
        local_time = now.astimezone(ZoneInfo(AppConfig.TIMEZONE))
        
        # Draw date
        date_text = local_time.strftime("%A, %B %d")
        date_surface = self.fonts['light-lg'].render(date_text, True, AppConfig.WHITE)
        date_rect = date_surface.get_rect(centerx=self.width // 2, top=20)
        self.display.surface.blit(date_surface, date_rect)
        
        # Draw time
        time_text = local_time.strftime("%I:%M %p").lstrip("0")
        time_surface = self.fonts['title-xl'].render(time_text, True, AppConfig.WHITE)
        time_rect = time_surface.get_rect(centerx=self.width // 2, top=date_rect.bottom + 5)
        self.display.surface.blit(time_surface, time_rect)
        
        self.update_screen()