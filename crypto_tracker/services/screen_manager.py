import os
import pygame
from pathlib import Path
from typing import Dict, Type, Any, Optional
from ..config.settings import AppConfig
from ..constants import ScreenNames
from ..exceptions import ScreenError, ConfigError
from ..utils.logger import get_logger
from ..screens import TickerScreen, SettingsScreen, KeyboardScreen

logger = get_logger(__name__)

class ScreenManager:
    """Manages screen transitions, display initialization, and state."""
    
    def __init__(self, crypto_api) -> None:
        """
        Initialize the screen manager.
        
        Args:
            crypto_api: The crypto API service instance
        """
        self.crypto_api = crypto_api
        self.screens: Dict[str, Any] = {}
        self.current_screen: Optional[str] = None
        
        # Initialize display
        self._setup_runtime_dir()
        self._init_pygame()
        self._init_display()
        self._init_screens()
        
        # Colors from config
        self.BLACK = AppConfig.BLACK
        self.WHITE = AppConfig.WHITE
        self.GREEN = AppConfig.GREEN
        self.RED = AppConfig.RED
        
        logger.info("ScreenManager initialized successfully")
        
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

    def _init_screens(self) -> None:
        """Initialize and set up all application screens."""
        try:
            # Add screens to manager
            self.add_screen(ScreenNames.TICKER.value, TickerScreen, self.crypto_api)
            ticker_screen = self.screens[ScreenNames.TICKER.value]
            
            self.add_screen(ScreenNames.SETTINGS.value, SettingsScreen, ticker_screen)
            settings_screen = self.screens[ScreenNames.SETTINGS.value]
            
            self.add_screen(ScreenNames.KEYBOARD.value, KeyboardScreen, settings_screen.add_ticker)
            
            # Set initial screen
            self.switch_to(ScreenNames.TICKER.value)
            logger.info("Screens initialized")
        except Exception as e:
            raise ConfigError(f"Failed to initialize screens: {str(e)}")

    def add_screen(self, name: str, screen_class: Type, *args, **kwargs) -> None:
        """
        Add a new screen to the manager.
        
        Args:
            name: Unique identifier for the screen
            screen_class: The screen class to instantiate
            *args: Positional arguments for the screen class
            **kwargs: Keyword arguments for the screen class
        
        Raises:
            ScreenError: If screen name already exists
        """
        if name in self.screens:
            raise ScreenError(f"Screen '{name}' already exists")
            
        try:
            screen_instance = screen_class(self, *args, **kwargs)
            self.screens[name] = screen_instance
            logger.info(f"Added screen: {name}")
        except Exception as e:
            raise ScreenError(f"Failed to create screen '{name}': {str(e)}")

    def switch_to(self, name: str) -> None:
        """
        Switch to a different screen.
        
        Args:
            name: Name of the screen to switch to
            
        Raises:
            ScreenError: If screen name doesn't exist
        """
        if name not in self.screens:
            raise ScreenError(f"Screen '{name}' does not exist")
            
        self.current_screen = name
        logger.info(f"Switched to screen: {name}")
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle events for the current screen.
        
        Args:
            event: The pygame event to handle
        """
        if self.current_screen:
            self.screens[self.current_screen].handle_event(event)
            
    def update(self, *args, **kwargs) -> None:
        """Update the current screen."""
        if self.current_screen:
            self.screens[self.current_screen].update(*args, **kwargs)
            
    def draw(self) -> None:
        """Draw the current screen."""
        if self.current_screen:
            self.screens[self.current_screen].draw()
            pygame.display.flip()

    def cleanup(self) -> None:
        """Clean up pygame resources."""
        try:
            pygame.quit()
            logger.info("Display cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}") 