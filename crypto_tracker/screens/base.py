from typing import Optional, Tuple
import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class BaseScreen:
    """Base class for all screens in the application."""
    
    def __init__(self, display) -> None:
        """
        Initialize the base screen.
        
        Args:
            display: The display instance
        """
        self.display = display
        self.width = AppConfig.DISPLAY_WIDTH
        self.height = AppConfig.DISPLAY_HEIGHT
        logger.info("Base screen initialized")
    
    def _create_text(self, text: str, font_key: str, color: tuple) -> pygame.Surface:
        """Create text surface using the specified font."""
        return self.display.create_text(text, font_key, color)
    
    def _scale_touch_input(self, event: pygame.event.Event) -> tuple:
        """Scale touch input coordinates to screen coordinates."""
        return (event.x * self.width, event.y * self.height)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events.
        
        Args:
            event: The pygame event to handle
        """
        raise NotImplementedError("Screens must implement handle_event")
        
    def update(self, *args, **kwargs) -> None:
        """Update the screen state."""
        pass
        
    def draw(self, display: pygame.Surface) -> None:
        """
        Draw the screen contents.
        
        Args:
            display: The pygame surface to draw on
        """
        raise NotImplementedError("Screens must implement draw") 