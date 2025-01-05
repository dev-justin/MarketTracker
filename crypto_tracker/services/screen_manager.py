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
    
    def add_screen(self, name: str, screen_class: Any, is_singleton: bool = True) -> None:
        """
        Add a screen to the manager.
        
        Args:
            name: The name of the screen
            screen_class: The screen class to instantiate
            is_singleton: Kept for backward compatibility, no longer used
        """
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
        
        # Special handling for edit_ticker screen
        if name == 'edit_ticker' and args:
            self.current_screen.load_coin(args[0])
        
        self.current_screen.on_screen_enter()
        logger.info(f"Switched to screen: {name}")
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events by passing them to the current screen."""
        if self.current_screen:
            self.current_screen.handle_event(event)
    
    def update_screen(self) -> None:
        """Update the current screen."""
        if self.current_screen:
            self.current_screen.draw()
    
    def get_current_screen(self) -> Optional[Any]:
        """Get the current screen."""
        return self.current_screen