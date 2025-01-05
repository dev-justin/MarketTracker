import os
import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

"""Service for managing shared display resources."""
class Display:
    def __init__(self):
        """Initialize the display service."""
        self._setup_runtime_dir()
        self._init_pygame()
        self._init_display()
        self._init_fonts()
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
    
    def _init_display(self):
        """Initialize the pygame display."""
        self.surface = pygame.display.set_mode((AppConfig.DISPLAY_WIDTH, AppConfig.DISPLAY_HEIGHT))
        pygame.display.set_caption("Crypto Tracker")
        self.clock = pygame.time.Clock()
    
    def _init_fonts(self):
        """Initialize shared fonts."""
        self.fonts = {
            'title-xl': pygame.font.Font(AppConfig.FONT_PATHS['bold'], AppConfig.FONT_SIZES['title-xl']),
            'title-lg': pygame.font.Font(AppConfig.FONT_PATHS['bold'], AppConfig.FONT_SIZES['title-lg']),
            'title-md': pygame.font.Font(AppConfig.FONT_PATHS['bold'], AppConfig.FONT_SIZES['title-md']),
            'title-sm': pygame.font.Font(AppConfig.FONT_PATHS['bold'], AppConfig.FONT_SIZES['title-sm']),
            'xl': pygame.font.Font(AppConfig.FONT_PATHS['regular'], AppConfig.FONT_SIZES['xl']),
            'lg': pygame.font.Font(AppConfig.FONT_PATHS['regular'], AppConfig.FONT_SIZES['lg']),
            'md': pygame.font.Font(AppConfig.FONT_PATHS['regular'], AppConfig.FONT_SIZES['md']),
            'sm': pygame.font.Font(AppConfig.FONT_PATHS['regular'], AppConfig.FONT_SIZES['sm']),
            'xs': pygame.font.Font(AppConfig.FONT_PATHS['regular'], AppConfig.FONT_SIZES['xs']),
            'bold-xl': pygame.font.Font(AppConfig.FONT_PATHS['bold'], AppConfig.FONT_SIZES['xl']),
            'bold-lg': pygame.font.Font(AppConfig.FONT_PATHS['bold'], AppConfig.FONT_SIZES['lg']),
            'bold-md': pygame.font.Font(AppConfig.FONT_PATHS['bold'], AppConfig.FONT_SIZES['md']),
            'bold-sm': pygame.font.Font(AppConfig.FONT_PATHS['bold'], AppConfig.FONT_SIZES['sm']),
            'bold-xs': pygame.font.Font(AppConfig.FONT_PATHS['bold'], AppConfig.FONT_SIZES['xs']),
            'light-xl': pygame.font.Font(AppConfig.FONT_PATHS['light'], AppConfig.FONT_SIZES['xl']),
            'light-lg': pygame.font.Font(AppConfig.FONT_PATHS['light'], AppConfig.FONT_SIZES['lg']),
            'light-md': pygame.font.Font(AppConfig.FONT_PATHS['light'], AppConfig.FONT_SIZES['md']),
            'light-sm': pygame.font.Font(AppConfig.FONT_PATHS['light'], AppConfig.FONT_SIZES['sm']),
            'light-xs': pygame.font.Font(AppConfig.FONT_PATHS['light'], AppConfig.FONT_SIZES['xs'])
        }