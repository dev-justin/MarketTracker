"""Asset manager for centralizing asset loading and caching."""

import os
import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class AssetManager:
    """Centralized manager for all application assets."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_assets()
        return cls._instance
    
    def _init_assets(self):
        """Initialize all application assets."""
        if not hasattr(self, 'initialized'):
            self.icons = {}
            self.fonts = {}
            self._load_icons()
            self._load_fonts()
            self.initialized = True
            logger.info("AssetManager initialized")
    
    def _load_icons(self):
        """Load all application icons."""
        icon_names = ['star', 'edit', 'trending-up', 'trending-down', 'settings', 'news', 'stocks']
        for name in icon_names:
            self.icons[name] = self._load_and_process_icon(name)
    
    def _load_fonts(self):
        """Load all application fonts."""
        # Define all available styles and sizes
        styles = ['light', 'regular', 'medium', 'bold', 'semibold']
        sizes = {
            'title': ['title-xl', 'title-lg', 'title-md', 'title-sm'],
            'regular': ['xl', 'lg', 'md', 'sm', 'xs']
        }
        
        # Load all combinations
        for style in styles:
            # Load title fonts
            for size in sizes['title']:
                self._load_font(style, size)
            
            # Load regular fonts
            for size in sizes['regular']:
                self._load_font(style, size)
        
        logger.info("All fonts loaded")
    
    def _load_font(self, style: str, size: str) -> pygame.font.Font:
        """Load a specific font style and size."""
        key = f"{style}-{size}"
        try:
            if style not in AppConfig.FONT_PATHS:
                logger.warning(f"Font style not found: {style}, falling back to regular")
                style = 'regular'
            
            if size not in AppConfig.FONT_SIZES:
                logger.warning(f"Font size not found: {size}, falling back to md")
                size = 'md'
            
            font_path = AppConfig.FONT_PATHS[style]
            font_size = AppConfig.FONT_SIZES[size]
            
            self.fonts[key] = pygame.font.Font(font_path, font_size)
            logger.debug(f"Loaded font: {key}")
            return self.fonts[key]
            
        except Exception as e:
            logger.error(f"Error loading font {key}: {e}")
            # Return a fallback font
            return pygame.font.Font(None, AppConfig.FONT_SIZES['md'])
    
    def _load_and_process_icon(self, name: str, size: tuple = (24, 24)):
        """Load and process an individual icon."""
        try:
            icon_path = os.path.join(AppConfig.ASSETS_DIR, 'icons', f'{name}.svg')
            icon = pygame.image.load(icon_path)
            icon = icon.convert_alpha()
            icon = pygame.transform.scale(icon, size)
            
            # Remove white background if present
            white = (255, 255, 255, 255)
            for x in range(icon.get_width()):
                for y in range(icon.get_height()):
                    if icon.get_at((x, y)) == white:
                        icon.set_at((x, y), (0, 0, 0, 0))
            
            logger.debug(f"Loaded icon: {name}")
            return icon
        except Exception as e:
            logger.error(f"Error loading icon {name}: {e}")
            return None
    
    def get_icon(self, name: str, size: tuple = None, color: tuple = None):
        """
        Get an icon with optional size and color modifications.
        
        Args:
            name: Name of the icon
            size: Optional tuple of (width, height) to resize the icon
            color: Optional tuple of (r,g,b) to recolor the icon
        """
        if name not in self.icons:
            return None
            
        icon = self.icons[name]
        if not icon:
            return None
        
        # Create a copy for modifications
        icon = icon.copy()
        
        # Resize if needed
        if size and size != icon.get_size():
            icon = pygame.transform.scale(icon, size)
        
        # Recolor if needed
        if color:
            for x in range(icon.get_width()):
                for y in range(icon.get_height()):
                    current_color = icon.get_at((x, y))
                    if current_color.a > 0:  # If pixel is not transparent
                        icon.set_at((x, y), (*color, current_color.a))
        
        return icon
    
    def get_font(self, style: str, size: str) -> pygame.font.Font:
        """
        Get a font with specific style and size.
        
        Args:
            style: Font style ('light', 'regular', 'medium', 'bold', 'semibold')
            size: Font size ('xs', 'sm', 'md', 'lg', 'xl', 'title-sm', 'title-md', 'title-lg', 'title-xl')
        """
        key = f"{style}-{size}"
        if key not in self.fonts:
            return self._load_font(style, size)
        return self.fonts[key]
    
    def get_title_font(self, size: str = 'md', style: str = 'bold') -> pygame.font.Font:
        """Convenience method for getting title fonts."""
        return self.get_font(style, f"title-{size}")
    
    def get_text_font(self, size: str = 'md', style: str = 'regular') -> pygame.font.Font:
        """Convenience method for getting regular text fonts."""
        return self.get_font(style, size) 