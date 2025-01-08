"""Screen manager service."""

import pygame
from typing import Dict, Optional
from ..utils.logger import get_logger
from ..screens.base_screen import BaseScreen
from ..screens.ticker_screen import TickerScreen
from ..screens.dashboard_screen import DashboardScreen
from ..screens.settings_screen import SettingsScreen
from ..screens.edit_ticker_screen import EditTickerScreen
from ..screens.add_ticker_screen import AddTickerScreen
from ..screens.news_screen import NewsScreen

logger = get_logger(__name__)

class ScreenManager:
    """Manages different screens in the application."""
    
    def __init__(self, display) -> None:
        """Initialize the screen manager."""
        self.display = display
        self.screens: Dict[str, BaseScreen] = {}
        self.current_screen: Optional[BaseScreen] = None
        self.current_screen_name: Optional[str] = None
        
        # Initialize screens
        self.screens['ticker'] = TickerScreen(display)
        self.screens['dashboard'] = DashboardScreen(display)
        self.screens['settings'] = SettingsScreen(display)
        self.screens['edit_ticker'] = EditTickerScreen(display)
        self.screens['add_ticker'] = AddTickerScreen(display)
        self.screens['news'] = NewsScreen(display)
        
        # Set screen manager reference in each screen
        for screen in self.screens.values():
            screen.screen_manager = self
        
        # Set initial screen
        self.switch_screen('dashboard')
        
        logger.info("ScreenManager initialized")
    
    def switch_screen(self, screen_name: str) -> None:
        """Switch to a different screen."""
        if screen_name not in self.screens:
            logger.error(f"Screen {screen_name} not found")
            return
        
        logger.info(f"Switching to screen: {screen_name}")
        self.current_screen_name = screen_name
        self.current_screen = self.screens[screen_name]
        self.current_screen.on_screen_enter()
    
    def get_screen(self, screen_name: str) -> Optional[BaseScreen]:
        """Get a screen by name."""
        return self.screens.get(screen_name)
    
    def update_screen(self) -> None:
        """Update the current screen."""
        if self.current_screen:
            self.current_screen.draw()
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        if self.current_screen:
            self.current_screen.handle_event(event)