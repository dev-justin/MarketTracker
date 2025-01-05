import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen

logger = get_logger(__name__)

class SettingsScreen(BaseScreen):
    """Screen for displaying and modifying application settings."""
    
    def __init__(self, display) -> None:
        """Initialize the settings screen."""
        super().__init__(display)
        # Colors and effects
        self.background_color = (0, 0, 0)  # Pure black
        self.glow_color = (0, 255, 0)      # Bright green
        logger.info("SettingsScreen initialized")
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        is_double_tap, is_swipe_up = self.gesture_handler.handle_touch_event(event, self.height)
        if is_double_tap or is_swipe_up:  # Either gesture returns to dashboard
            logger.info("Returning to dashboard")
            self.screen_manager.switch_screen('dashboard')
    
    def draw(self) -> None:
        """Draw the settings screen."""
        # Fill background with black
        self.display.surface.fill(self.background_color)
        
        # Draw "Settings" text
        settings_text = self.fonts['title-lg'].render("Settings", True, AppConfig.WHITE)
        settings_rect = settings_text.get_rect(centerx=self.width // 2, top=20)
        self.display.surface.blit(settings_text, settings_rect)
        
        self.update_screen() 