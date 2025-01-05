from abc import ABC, abstractmethod
import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from ..utils.gesture import GestureHandler

logger = get_logger(__name__)

class BaseScreen(ABC):
    """Base class for all screens in the application."""
    
    def __init__(self, display) -> None:
        """Initialize the base screen."""
        self.display = display
        self.screen_manager = None
        self.gesture_handler = GestureHandler()
        self.width = AppConfig.DISPLAY_WIDTH
        self.height = AppConfig.DISPLAY_HEIGHT
        self.fonts = display.fonts
        logger.info(f"{self.__class__.__name__} initialized")
    
    def on_screen_enter(self) -> None:
        """Called when entering the screen. Override in subclasses."""
        pass
    
    def on_screen_exit(self) -> None:
        """Called when exiting the screen. Override in subclasses."""
        pass
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        pass
    
    def draw(self) -> None:
        """Draw the screen."""
        pass
    
    def update_screen(self) -> None:
        """Update the display."""
        pygame.display.flip()
    
    def _scale_touch_input(self, event: pygame.event.Event) -> tuple:
        """Scale touch input coordinates to screen dimensions."""
        return (
            int(event.x * self.width),
            int(event.y * self.height)
        )