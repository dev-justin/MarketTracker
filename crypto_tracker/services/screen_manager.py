import pygame
from ..utils.logger import get_logger
from typing import Dict, Any, Optional

logger = get_logger(__name__)

class ScreenManager:
    """Manages screen switching and state."""
    
    def __init__(self, display) -> None:
        """Initialize the screen manager."""
        self.display = display
        self.screens = {}
        self.current_screen = None
        logger.info("ScreenManager initialized")
    
    def add_screen(self, name: str, screen_class: Any) -> None:
        """Add a screen to the manager."""
        screen = screen_class(self.display)
        self.screens[name] = screen
        screen.screen_manager = self
        logger.info(f"Added screen: {name}")
    
    def switch_screen(self, name: str, *args, **kwargs) -> None:
        """Switch to a different screen."""
        if name not in self.screens:
            logger.error(f"Screen not found: {name}")
            return
            
        if self.current_screen:
            self.current_screen.on_screen_exit()
            
        self.current_screen = self.screens[name]
        self.current_screen.on_screen_enter()
        logger.info(f"Switched to screen: {name}")
    
    def get_current_screen(self) -> Optional[Any]:
        """Get the current screen."""
        return self.current_screen