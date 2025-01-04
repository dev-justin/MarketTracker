import os
import pygame
from pathlib import Path
from typing import Optional
from ..config.settings import AppConfig
from ..constants import ScreenNames
from ..exceptions import ConfigError
from ..utils.logger import get_logger
from .screen_manager import ScreenManager
from ..screens import TickerScreen, SettingsScreen, KeyboardScreen

logger = get_logger(__name__)

class Display:
    """Main display manager for the application."""
    
    def __init__(self, crypto_api) -> None:
        """
        Initialize the display manager.
        
        Args:
            crypto_api: The crypto API service instance
        """
        self.crypto_api = crypto_api
        self._setup_runtime_dir()
        self._init_pygame()
        self._init_display()
        self._init_screen_manager()
        logger.info("Display initialized successfully")

    def _setup_runtime_dir(self) -> None:
        """Set up the runtime directory for the display."""
        try:
            if os.geteuid() == 0:
                uid = int(os.environ.get('SUDO_UID', 1000))
                runtime_dir = f"/run/user/{uid}"
                os.environ['XDG_RUNTIME_DIR'] = runtime_dir
                Path(runtime_dir).mkdir(parents=True, exist_ok=True)
                os.chmod(runtime_dir, 0o700)
                os.chown(runtime_dir, uid, uid)
                logger.info(f"Runtime directory set up: {runtime_dir}")
        except Exception as e:
            raise ConfigError(f"Failed to set up runtime directory: {str(e)}")

    def _init_pygame(self) -> None:
        """Initialize pygame and set display properties."""
        try:
            pygame.init()
            pygame.mouse.set_visible(False)
            os.putenv('SDL_VIDEODRIVER', 'fbcon')
            os.putenv('SDL_FBDEV', '/dev/fb0')
            logger.info("Pygame initialized")
        except Exception as e:
            raise ConfigError(f"Failed to initialize pygame: {str(e)}")

    def _init_display(self) -> None:
        """Initialize the display surface."""
        try:
            self.width = AppConfig.SCREEN_WIDTH
            self.height = AppConfig.SCREEN_HEIGHT
            self.screen = pygame.display.set_mode(
                (self.width, self.height),
                pygame.FULLSCREEN | pygame.NOFRAME | pygame.HWSURFACE
            )
            logger.info(f"Display initialized: {self.width}x{self.height}")
        except Exception as e:
            raise ConfigError(f"Failed to initialize display: {str(e)}")

    def _init_screen_manager(self) -> None:
        """Initialize and set up the screen manager with all screens."""
        try:
            self.screen_manager = ScreenManager(self.screen, self.width, self.height)
            
            # Add screens to manager
            self.screen_manager.add_screen(ScreenNames.TICKER.value, TickerScreen, self.crypto_api)
            ticker_screen = self.screen_manager.screens[ScreenNames.TICKER.value]
            
            self.screen_manager.add_screen(ScreenNames.SETTINGS.value, SettingsScreen, ticker_screen)
            settings_screen = self.screen_manager.screens[ScreenNames.SETTINGS.value]
            
            self.screen_manager.add_screen(ScreenNames.KEYBOARD.value, KeyboardScreen, settings_screen.add_ticker)
            
            # Set initial screen
            self.screen_manager.switch_to(ScreenNames.TICKER.value)
            logger.info("Screen manager initialized")
        except Exception as e:
            raise ConfigError(f"Failed to initialize screen manager: {str(e)}")

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events.
        
        Args:
            event: The pygame event to handle
        """
        self.screen_manager.handle_event(event)

    def update(self, prices: Optional[dict] = None) -> None:
        """
        Update the current screen.
        
        Args:
            prices: Optional dictionary of current prices
        """
        self.screen_manager.update(prices)

    def draw(self) -> None:
        """Draw the current screen."""
        self.screen_manager.draw()

    def cleanup(self) -> None:
        """Clean up pygame resources."""
        try:
            pygame.quit()
            logger.info("Display cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}") 