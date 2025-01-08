"""Base screen class for all screens in the application."""

import pygame
from typing import Dict, Any, Optional, Tuple
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from ..utils.gesture import GestureHandler
from ..services.service_manager import ServiceManager
from ..services.asset_manager import AssetManager
from datetime import datetime
from zoneinfo import ZoneInfo

logger = get_logger(__name__)

class BaseScreen:
    """Base class for all screens in the application."""
    
    def __init__(self, display) -> None:
        """Initialize the base screen."""
        # Store passed display instance
        self.display = display
        
        # Get service instances
        service_manager = ServiceManager()
        self.crypto_manager = service_manager.get_crypto_manager()
        
        # Get asset manager
        self.assets = AssetManager()
        
        # Initialize screen properties
        self.screen_manager = None
        self.width = AppConfig.DISPLAY_WIDTH
        self.height = AppConfig.DISPLAY_HEIGHT
        self.needs_redraw = True
        self.background_color = AppConfig.BLACK
        
        # Create a surface for double buffering
        self.surface = pygame.Surface((self.width, self.height))
        
        # Initialize gesture handler
        self.gesture_handler = GestureHandler()
        
        logger.info(f"{self.__class__.__name__} initialized with dimensions {self.width}x{self.height}")
    
    def on_screen_enter(self, **kwargs) -> None:
        """Called when entering the screen. Override in subclasses."""
        self.needs_redraw = True
    
    def on_screen_exit(self) -> None:
        """Called when exiting the screen. Override in subclasses."""
        pass
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        logger.debug(f"{self.__class__.__name__} received event type: {event.type}")
        gestures = self.gesture_handler.handle_touch_event(event)
        if any(gestures.values()):
            logger.debug(f"{self.__class__.__name__} detected gestures: {gestures}")
        self._handle_gestures(gestures)
    
    def _handle_gestures(self, gestures: Dict[str, bool]) -> None:
        """Handle gestures. Override in subclasses."""
        pass
    
    def draw(self) -> None:
        """Draw the screen."""
        # Fill background
        self.surface.fill(self.background_color)
    
    def update_screen(self) -> None:
        """Update the display."""
        if self.needs_redraw:
            # Draw to our surface first
            self.draw()
            # Then blit to the display surface
            self.display.surface.blit(self.surface, (0, 0))
            pygame.display.flip()
            self.needs_redraw = False
    
    def _scale_touch_input(self, event: pygame.event.Event) -> Tuple[int, int]:
        """Scale touch input coordinates to screen dimensions."""
        scaled_x = int(event.x * self.width)
        scaled_y = int(event.y * self.height)
        return (scaled_x, scaled_y)
    
    def get_current_time(self) -> str:
        """Get the current time formatted for display."""
        now = datetime.now(ZoneInfo(AppConfig.TIMEZONE))
        return now.strftime("%I:%M %p").lstrip("0")
    
    def get_current_date(self) -> str:
        """Get the current date formatted for display."""
        now = datetime.now(ZoneInfo(AppConfig.TIMEZONE))
        return now.strftime("%A, %B %d")
    
    def refresh_coins(self) -> None:
        """Refresh the list of tracked coins."""
        self.needs_redraw = True