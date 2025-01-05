from abc import ABC, abstractmethod
import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger

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
        logger.info("Base screen initialized")
            
    def update_screen(self) -> None:
        """Update the screen."""
        pygame.display.flip()

    @abstractmethod
    def draw(self, display: pygame.Surface) -> None:
        """
        Draw the screen contents.
        
        Args:
            display: The pygame surface to draw on
        """
        raise NotImplementedError("Screens must implement draw") 
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events.
        
        Args:
            event: The pygame event to handle
        """
        raise NotImplementedError("Screens must implement handle_event")