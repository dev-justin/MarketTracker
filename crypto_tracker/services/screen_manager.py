import pygame
from typing import Dict, Optional
from ..config.settings import AppConfig
from ..constants import ScreenNames
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ScreenManager:
    """Manages screen transitions and state."""
    
    def __init__(self, display, crypto_api, crypto_store):
        """Initialize the screen manager."""
        self.display = display
        self.crypto_api = crypto_api
        self.crypto_store = crypto_store
        self.current_screen = None
        self.screens: Dict[str, object] = {}
        logger.info("ScreenManager initialized")
    
    def add_screen(self, name: str, screen: object):
        """Add a screen to the manager."""
        self.screens[name] = screen
        logger.debug(f"Added screen: {name}")
    
    def switch_screen(self, screen_name: str):
        """Switch to a different screen."""
        if screen_name in self.screens:
            self.current_screen = self.screens[screen_name]
            logger.info(f"Switched to screen: {screen_name}")
        else:
            raise ValueError(f"Screen '{screen_name}' not found")
    
    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events."""
        if self.current_screen:
            self.current_screen.handle_event(event)
    
    def update(self, prices: Optional[Dict[str, float]] = None):
        """Update the current screen."""
        if self.current_screen:
            self.current_screen.update(prices)
    
    def draw(self):
        """Draw the current screen."""
        if self.current_screen:
            self.display.fill(AppConfig.BLACK)
            self.current_screen.draw(self.display.surface)
            self.display.flip() 