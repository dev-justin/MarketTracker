from typing import Dict, Type, Any, Optional
import pygame
from ..config.settings import AppConfig
from ..constants import ScreenNames
from ..exceptions import ScreenError
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ScreenManager:
    """Manages screen transitions and state."""
    
    def __init__(self, screen: pygame.Surface, width: int, height: int) -> None:
        """
        Initialize the screen manager.
        
        Args:
            screen: The pygame display surface
            width: Screen width
            height: Screen height
        """
        self.screen = screen
        self.width = width
        self.height = height
        self.screens: Dict[str, Any] = {}
        self.current_screen: Optional[str] = None
        
        # Colors from config
        self.BLACK = AppConfig.BLACK
        self.WHITE = AppConfig.WHITE
        self.GREEN = AppConfig.GREEN
        self.RED = AppConfig.RED
        
    def add_screen(self, name: str, screen_class: Type, *args, **kwargs) -> None:
        """
        Add a new screen to the manager.
        
        Args:
            name: Unique identifier for the screen
            screen_class: The screen class to instantiate
            *args: Positional arguments for the screen class
            **kwargs: Keyword arguments for the screen class
        
        Raises:
            ScreenError: If screen name already exists
        """
        if name in self.screens:
            raise ScreenError(f"Screen '{name}' already exists")
            
        try:
            screen_instance = screen_class(self, *args, **kwargs)
            self.screens[name] = screen_instance
            logger.info(f"Added screen: {name}")
        except Exception as e:
            raise ScreenError(f"Failed to create screen '{name}': {str(e)}")
            
    def switch_to(self, name: str) -> None:
        """
        Switch to a different screen.
        
        Args:
            name: Name of the screen to switch to
            
        Raises:
            ScreenError: If screen name doesn't exist
        """
        if name not in self.screens:
            raise ScreenError(f"Screen '{name}' does not exist")
            
        self.current_screen = name
        logger.info(f"Switched to screen: {name}")
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle events for the current screen.
        
        Args:
            event: The pygame event to handle
        """
        if self.current_screen:
            self.screens[self.current_screen].handle_event(event)
            
    def update(self, *args, **kwargs) -> None:
        """Update the current screen."""
        if self.current_screen:
            self.screens[self.current_screen].update(*args, **kwargs)
            
    def draw(self) -> None:
        """Draw the current screen."""
        if self.current_screen:
            self.screens[self.current_screen].draw()
            pygame.display.flip() 