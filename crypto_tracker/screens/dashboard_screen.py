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
        # Colors and effects
        self.background_color = (0, 0, 0)  # Pure black
        self.glow_color = (0, 255, 0)      # Bright green
        self.spots = [
            {'x': 0.2, 'y': 0.3, 'size': 300, 'alpha': 25},   # Top left area
            {'x': 0.8, 'y': 0.7, 'size': 350, 'alpha': 20},   # Bottom right area
            {'x': 0.7, 'y': 0.2, 'size': 280, 'alpha': 30},   # Top right area
            {'x': 0.3, 'y': 0.8, 'size': 320, 'alpha': 22},   # Bottom left area
            {'x': 0.5, 'y': 0.5, 'size': 400, 'alpha': 15},   # Center area (subtle)
        ]
        logger.info("DashboardScreen initialized")
    
    def _draw_glow_spot(self, surface: pygame.Surface, x: int, y: int, size: int, alpha: int) -> None:
        """Draw a single glowing spot with smooth falloff."""
        spot_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        # Create multiple circles with decreasing alpha for smooth glow
        num_layers = 30  # Increased number of layers for smoother gradient
        for i in range(num_layers):
            progress = i / num_layers
            current_size = int(size * (1 - progress))
            # Adjusted falloff for more visible outer glow
            current_alpha = int(alpha * (1 - progress) ** 1.5)  # Reduced power for slower falloff
            
            pygame.draw.circle(
                spot_surface,
                (*self.glow_color, current_alpha),
                (size, size),
                current_size
            )
        
        # Blit the spot onto the main surface
        surface.blit(spot_surface, (x - size, y - size), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        is_double_tap, is_swipe_up = self.gesture_handler.handle_touch_event(event, self.height)
        if is_double_tap:
            logger.info("Double tap detected, returning to ticker screen")
        elif is_swipe_up:
            logger.info("Swipe up detected, switching to settings")
    
    def draw(self) -> None:
        """Draw the dashboard screen."""
        # Fill background with black
        self.display.surface.fill(self.background_color)
        
        # Draw glowing spots
        for spot in self.spots:
            self._draw_glow_spot(
                self.display.surface,
                int(spot['x'] * self.width),
                int(spot['y'] * self.height),
                spot['size'],
                spot['alpha']
            )
        
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