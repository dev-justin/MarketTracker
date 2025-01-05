import pygame
from ..utils.logger import get_logger
from typing import Dict, Any, Optional

logger = get_logger(__name__)

class ScreenManager:
    def __init__(self, display):
        self.display = display
        self.screens = {}
        self.screen_classes = {}  # Store screen classes for dynamic creation
        self.current_screen = None
        logger.info("ScreenManager initialized")
    
    def add_screen(self, name: str, screen_class: Any, is_singleton: bool = True) -> None:
        """
        Add a screen to the manager.
        
        Args:
            name: The name of the screen
            screen_class: The screen class to instantiate
            is_singleton: If True, reuse the same instance; if False, create new instance each time
        """
        self.screen_classes[name] = {
            'class': screen_class,
            'is_singleton': is_singleton
        }
        if is_singleton:
            screen = screen_class(self.display)
            self.screens[name] = screen
            screen.screen_manager = self
        logger.info(f"Added screen: {name}")
    
    def switch_screen(self, name: str, *args, **kwargs) -> None:
        """
        Switch to a different screen.
        
        Args:
            name: The name of the screen to switch to
            *args, **kwargs: Additional arguments to pass to the screen constructor
        """
        if name not in self.screen_classes:
            logger.error(f"Screen not found: {name}")
            return
            
        screen_info = self.screen_classes[name]
        
        if screen_info['is_singleton']:
            if name in self.screens:
                self.current_screen = self.screens[name]
            else:
                logger.error(f"Singleton screen not initialized: {name}")
                return
        else:
            # Create new instance with parameters
            try:
                screen = screen_info['class'](self.display, *args, **kwargs)
                screen.screen_manager = self
                self.current_screen = screen
            except Exception as e:
                logger.error(f"Error creating screen {name}: {e}")
                return
        
        logger.info(f"Switched to screen: {name}")
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        if self.current_screen:
            self.current_screen.handle_event(event)
    
    def update_screen(self) -> None:
        """Update the current screen."""
        if self.current_screen:
            self.current_screen.draw()