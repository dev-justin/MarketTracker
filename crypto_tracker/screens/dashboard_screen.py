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
        # Colors for gradient
        self.gradient_top = (0, 0, 0)         # Pure black at top
        self.gradient_middle = (0, 20, 0)     # Very slight green in middle
        self.gradient_bottom = (0, 40, 0)     # Stronger green at bottom
        self.glow_color = (0, 255, 0, 25)     # Transparent green for glow
        logger.info("DashboardScreen initialized")
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        is_double_tap, is_swipe_up = self.gesture_handler.handle_touch_event(event, self.height)
        if is_double_tap:
            logger.info("Double tap detected, returning to ticker screen")
        elif is_swipe_up:
            logger.info("Swipe up detected, switching to settings")
    
    def draw(self) -> None:
        """Draw the dashboard screen."""
        # Draw main gradient background
        for y in range(self.height):
            progress = y / self.height
            
            # Use different color transitions for top and bottom half
            if progress < 0.5:
                # Top half: black to slight green
                p = progress * 2  # Normalize to 0-1 for top half
                color = [
                    int(self.gradient_top[i] + (self.gradient_middle[i] - self.gradient_top[i]) * p)
                    for i in range(3)
                ]
            else:
                # Bottom half: slight green to stronger green
                p = (progress - 0.5) * 2  # Normalize to 0-1 for bottom half
                color = [
                    int(self.gradient_middle[i] + (self.gradient_bottom[i] - self.gradient_middle[i]) * p)
                    for i in range(3)
                ]
            
            pygame.draw.line(self.display.surface, color, (0, y), (self.width, y))
        
        # Add glow effect at bottom
        glow_height = 100
        glow_surface = pygame.Surface((self.width, glow_height), pygame.SRCALPHA)
        for y in range(glow_height):
            alpha = int(255 * (1 - y / glow_height))  # Fade from bottom up
            color = (*self.glow_color[:3], int(self.glow_color[3] * (1 - y / glow_height)))
            pygame.draw.line(glow_surface, color, (0, y), (self.width, y))
        
        self.display.surface.blit(glow_surface, (0, self.height - glow_height), special_flags=pygame.BLEND_ALPHA_SDL2)
        
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