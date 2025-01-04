from typing import Optional, Tuple
import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class Screen:
    """Base class for all screens in the application."""
    
    def __init__(self, screen_manager) -> None:
        """
        Initialize the base screen.
        
        Args:
            screen_manager: The screen manager instance
        """
        self.manager = screen_manager
        self.width = AppConfig.DISPLAY_WIDTH
        self.height = AppConfig.DISPLAY_HEIGHT
        
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
        
    def _scale_touch_input(self, event: pygame.event.Event) -> Tuple[int, int]:
        """
        Scale touch input coordinates to screen dimensions.
        
        Args:
            event: The touch event
            
        Returns:
            Tuple of scaled x, y coordinates
        """
        if not hasattr(event, 'x') or not hasattr(event, 'y'):
            return (0, 0)
        return (int(event.x * self.width), int(event.y * self.height))
        
    def _create_text_surface(
        self,
        text: str,
        font_size: int,
        color: Tuple[int, int, int],
        antialias: bool = True
    ) -> pygame.Surface:
        """
        Create a text surface with the given parameters.
        
        Args:
            text: The text to render
            font_size: Size of the font
            color: RGB color tuple
            antialias: Whether to use antialiasing
            
        Returns:
            A pygame Surface with the rendered text
        """
        font = pygame.font.Font(None, font_size)
        return font.render(text, antialias, color) 