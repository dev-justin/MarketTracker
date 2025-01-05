import os
import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

"""Service for managing shared display resources."""
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
            self._init_fonts()
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
    
    def _init_fonts(self):
        """Initialize shared fonts."""
        self.fonts = {}
        self._load_default_fonts()
    
    def _load_default_fonts(self):
        """Load the default set of fonts."""
        # Title fonts
        for size in ['title-xl', 'title-lg', 'title-md', 'title-sm']:
            self.get_font('bold', size)
        
        # Regular fonts
        for size in ['xl', 'lg', 'md', 'sm', 'xs']:
            self.get_font('regular', size)
            self.get_font('bold', size)
            self.get_font('light', size)
    
    def get_font(self, style: str, size: str) -> pygame.font.Font:
        """
        Get a font with specific style and size.
        
        Args:
            style: Font style ('light', 'regular', 'medium', 'bold', 'semibold')
            size: Font size ('xs', 'sm', 'md', 'lg', 'xl', 'title-sm', 'title-md', 'title-lg', 'title-xl')
        """
        key = f"{style}-{size}"
        if key not in self.fonts:
            try:
                if style not in AppConfig.FONT_PATHS:
                    logger.error(f"Font style not found: {style}")
                    style = 'regular'  # Fallback to regular
                
                if size not in AppConfig.FONT_SIZES:
                    logger.error(f"Font size not found: {size}")
                    size = 'md'  # Fallback to medium
                
                self.fonts[key] = pygame.font.Font(
                    AppConfig.FONT_PATHS[style],
                    AppConfig.FONT_SIZES[size]
                )
                logger.debug(f"Created font: {key}")
            except Exception as e:
                logger.error(f"Error creating font {key}: {e}")
                # Return a fallback font
                return pygame.font.Font(None, AppConfig.FONT_SIZES['md'])
        
        return self.fonts[key]