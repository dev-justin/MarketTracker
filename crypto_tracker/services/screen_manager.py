import pygame
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ScreenManager:
    def __init__(self):
        """Initialize the screen manager."""
        self.screens = {}
        self.current_screen = None
        logger.info("ScreenManager initialized")
    
    def add_screen(self, name: str, screen: object):
        """Add a screen to the manager."""
        self.screens[name] = screen
        logger.debug(f"Added screen: {name}")
    
    def switch_screen(self, screen_name: str):
        """Switch to a different screen."""
        if screen_name not in self.screens:
            raise ValueError(f"Screen '{screen_name}' not found")
        self.current_screen = self.screens[screen_name]
        logger.info(f"Switched to screen: {screen_name}")
    
    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events."""
        if self.current_screen:
            self.current_screen.handle_event(event)
        
    def update_screen(self):
        """Draw the current screen."""
        if self.current_screen:
            self.current_screen.draw()