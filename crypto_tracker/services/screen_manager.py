import pygame
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ScreenManager:
    def __init__(self, display):
        self.display = display
        self.screens = {}
        self.current_screen = None
        logger.info("ScreenManager initialized")
    
    def add_screen(self, name: str, screen) -> None:
        """Add a screen to the manager."""
        self.screens[name] = screen
        screen.screen_manager = self
        logger.info(f"Added screen: {name}")
    
    def switch_screen(self, name: str) -> None:
        """Switch to a different screen."""
        if name in self.screens:
            self.current_screen = self.screens[name]
            logger.info(f"Switched to screen: {name}")
        else:
            logger.error(f"Screen not found: {name}")
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        if self.current_screen:
            self.current_screen.handle_event(event)
    
    def update_screen(self) -> None:
        """Update the current screen."""
        if self.current_screen:
            self.current_screen.draw()