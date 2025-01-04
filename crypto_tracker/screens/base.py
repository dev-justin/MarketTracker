from typing import Optional, Tuple
import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class Screen:
    """Base class for all screens in the application."""
    
    def __init__(self, screen_manager) -> None:
        """
        Initialize the base screen.
        
        Args:
            screen_manager: The screen manager instance
        """
        self.manager = screen_manager
        self.width = AppConfig.DISPLAY_WIDTH
        self.height = AppConfig.DISPLAY_HEIGHT
        
        # Initialize fonts for all screens
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
        
        logger.info("Base screen initialized with fonts")
    
    def _create_text(self, text: str, font_key: str, color: tuple) -> pygame.Surface:
        """Create text surface using the specified font."""
        return self.fonts[font_key].render(text, True, color)
    
    def _scale_touch_input(self, event: pygame.event.Event) -> tuple:
        """Scale touch input coordinates to screen coordinates."""
        return (event.x * self.width, event.y * self.height)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events.
        
        Args:
            event: The pygame event to handle
        """
        raise NotImplementedError("Screens must implement handle_event")
        
    def update(self, *args, **kwargs) -> None:
        """Update the screen state."""
        pass
        
    def draw(self, display: pygame.Surface) -> None:
        """
        Draw the screen contents.
        
        Args:
            display: The pygame surface to draw on
        """
        raise NotImplementedError("Screens must implement draw") 