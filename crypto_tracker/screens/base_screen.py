from abc import ABC, abstractmethod
import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from ..utils.gesture import GestureHandler

logger = get_logger(__name__)

class BaseScreen(ABC):
    """Base class for all screens in the application."""
    
    def __init__(self, display) -> None:
        """
        Initialize the base screen.
        
        Args:
            display: The display instance
        """
        self.display = display
        self.fonts = display.fonts
        self.width = AppConfig.DISPLAY_WIDTH
        self.height = AppConfig.DISPLAY_HEIGHT
        self.gesture_handler = GestureHandler()
        logger.info("Base screen initialized")
            
    def update_screen(self) -> None:
        """Update the screen."""
        pygame.display.flip()

    def set_screen_manager(self, screen_manager: object) -> None:
        """Set the screen manager."""
        self.screen_manager = screen_manager

    @abstractmethod
    def draw(self) -> None:
        """Draw the screen contents."""
        raise NotImplementedError("Screens must implement draw") 
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events.
        
        Args:
            event: The pygame event to handle
        """
        raise NotImplementedError("Screens must implement handle_event")
    
    def _scale_touch_input(self, event: pygame.event.Event) -> tuple:
        """Scale touch input coordinates to screen coordinates."""
        return (event.x * self.width, event.y * self.height)