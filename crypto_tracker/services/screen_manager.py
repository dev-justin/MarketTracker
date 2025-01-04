import os
import pygame
from typing import Dict, Optional

from crypto_tracker.config.settings import AppConfig
from crypto_tracker.constants import ScreenNames
from crypto_tracker.screens.ticker_screen import TickerScreen
from crypto_tracker.screens.settings_screen import SettingsScreen
from crypto_tracker.screens.keyboard_screen import KeyboardScreen
from crypto_tracker.screens.dashboard_screen import DashboardScreen
from crypto_tracker.services.crypto_api import CryptoAPI

class ScreenManager:
    def __init__(self, crypto_api: CryptoAPI):
        """Initialize the screen manager with the crypto API service."""
        self.crypto_api = crypto_api
        self.current_screen = None
        self.screens: Dict[str, object] = {}
        
        # Initialize pygame and display
        self._setup_runtime_dir()
        self._init_pygame()
        self._init_display()
        
        # Initialize screens
        self._init_screens()
        
        # Set initial screen
        self.switch_screen(ScreenNames.TICKER.value)
    
    def _setup_runtime_dir(self):
        """Set up the runtime directory for pygame."""
        runtime_dir = os.path.expanduser('~/.local/share/crypto_tracker')
        os.makedirs(runtime_dir, exist_ok=True)
        os.environ['SDL_RUNTIME_PATH'] = runtime_dir
    
    def _init_pygame(self):
        """Initialize pygame and its modules."""
        pygame.init()
        pygame.font.init()
        pygame.mouse.set_visible(False)
    
    def _init_display(self) -> None:
        """Initialize the pygame display."""
        pygame.init()
        pygame.display.init()
        
        # Set up the display
        self.display = pygame.display.set_mode((AppConfig.DISPLAY_WIDTH, AppConfig.DISPLAY_HEIGHT))
        pygame.display.set_caption("Crypto Tracker")
        
        # Initialize the clock
        self.clock = pygame.time.Clock()
        
        # Set up screens
        self._init_screens()
    
    def _init_screens(self):
        """Initialize all application screens."""
        ticker_screen = TickerScreen(self, self.crypto_api)
        settings_screen = SettingsScreen(self, ticker_screen)        
        keyboard_screen = KeyboardScreen(self, settings_screen.add_ticker)
        dashboard_screen = DashboardScreen(self, self.crypto_api)
        
        self.screens = {
            ScreenNames.TICKER.value: ticker_screen,
            ScreenNames.SETTINGS.value: settings_screen,
            ScreenNames.KEYBOARD.value: keyboard_screen,
            ScreenNames.DASHBOARD.value: dashboard_screen
        }
    
    def switch_screen(self, screen_name: str):
        """Switch to a different screen."""
        if screen_name in self.screens:
            self.current_screen = self.screens[screen_name]
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
            self.current_screen.draw(self.display)
            pygame.display.flip()
    
    def cleanup(self):
        """Clean up pygame resources."""
        pygame.quit() 