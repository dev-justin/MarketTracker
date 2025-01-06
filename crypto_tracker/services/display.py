"""Service for managing shared display resources."""

import os
import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .asset_manager import AssetManager

logger = get_logger(__name__)

class Display:
    """Service for managing shared display resources."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_display()
        return cls._instance
    
    def _init_display(self):
        """Initialize the display service."""
        if not hasattr(self, 'initialized'):
            self._setup_runtime_dir()
            self._init_pygame()
            self._init_display_surface()
            self.assets = AssetManager()  # Get asset manager instance
            self.initialized = True
            logger.info("Display service initialized")
    
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
    
    def _init_display_surface(self):
        """Initialize the pygame display."""
        self.surface = pygame.display.set_mode((AppConfig.DISPLAY_WIDTH, AppConfig.DISPLAY_HEIGHT))
        pygame.display.set_caption("Crypto Tracker")
        self.clock = pygame.time.Clock()
    
    def get_font(self, style: str, size: str) -> pygame.font.Font:
        """Get a font using the asset manager."""
        return self.assets.get_font(style, size)
    
    def get_title_font(self, size: str = 'md', style: str = 'bold') -> pygame.font.Font:
        """Get a title font using the asset manager."""
        return self.assets.get_title_font(size, style)
    
    def get_text_font(self, size: str = 'md', style: str = 'regular') -> pygame.font.Font:
        """Get a text font using the asset manager."""
        return self.assets.get_text_font(size, style)