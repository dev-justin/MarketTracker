"""Screen manager service."""

import pygame
from typing import Dict, Optional, Any
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
        self.switching_in_progress = False
        self.transition_start_time = 0
        self.transition_duration = 100  # 100ms transition duration
        
        # Initialize screens
        self._init_screens()
        
        # Set initial screen
        logger.info("Setting initial screen to dashboard")
        self.switch_screen('dashboard')
        
        logger.info("ScreenManager initialized")
    
    def _init_screens(self) -> None:
        """Initialize all screens."""
        screen_classes = {
            'ticker': TickerScreen,
            'dashboard': DashboardScreen,
            'settings': SettingsScreen,
            'edit_ticker': EditTickerScreen,
            'add_ticker': AddTickerScreen,
            'news': NewsScreen
        }
        
        for name, screen_class in screen_classes.items():
            self.screens[name] = screen_class(self.display)
            self.screens[name].screen_manager = self
            logger.debug(f"Initialized {name} screen")
    
    def switch_screen(self, screen_name: str, **kwargs) -> None:
        """Switch to a different screen."""
        current_time = pygame.time.get_ticks()
        
        # Basic validation
        if screen_name not in self.screens:
            logger.error(f"Screen {screen_name} not found")
            return
        
        if screen_name == self.current_screen_name:
            return
        
        # Check if we're still in transition
        if self.switching_in_progress:
            if current_time - self.transition_start_time < self.transition_duration:
                logger.debug("Screen transition in progress")
                return
            else:
                # Force end previous transition if it's taking too long
                self.switching_in_progress = False
        
        try:
            self.switching_in_progress = True
            self.transition_start_time = current_time
            
            logger.info(f"Switching to screen: {screen_name}")
            
            # Exit current screen
            if self.current_screen:
                self.current_screen.on_screen_exit()
            
            # Update screen references
            self.current_screen_name = screen_name
            self.current_screen = self.screens[screen_name]
            
            # Initialize new screen with any kwargs
            self.current_screen.on_screen_enter(**kwargs)
            
            # Force immediate draw
            self.current_screen.needs_redraw = True
            self.update_screen()
            
        except Exception as e:
            logger.error(f"Error switching screen: {e}")
            self.switching_in_progress = False
            raise
        finally:
            # Reset switch flag after transition duration
            if current_time - self.transition_start_time >= self.transition_duration:
                self.switching_in_progress = False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events and return whether screen needs update."""
        if not self.current_screen:
            logger.warning("No current screen to handle event")
            return False
            
        if self.switching_in_progress:
            logger.debug("Ignoring event during screen transition")
            return False
            
        try:
            # Let current screen handle the event
            logger.debug(f"Forwarding event {event.type} to {self.current_screen.__class__.__name__}")
            self.current_screen.handle_event(event)
            return True
        except Exception as e:
            logger.error(f"Error handling event: {e}")
            return False
    
    def update_screen(self) -> None:
        """Update the current screen."""
        if not self.current_screen:
            return
            
        try:
            if self.current_screen.needs_redraw:
                self.current_screen.draw()
                pygame.display.flip()
                self.current_screen.needs_redraw = False
        except Exception as e:
            logger.error(f"Error updating screen: {e}")
    
    def get_screen(self, screen_name: str) -> Optional[BaseScreen]:
        """Get a screen by name."""
        return self.screens.get(screen_name)