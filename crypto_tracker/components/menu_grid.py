"""Menu grid component for the dashboard screen."""

import pygame
import time
from typing import List, Dict, Tuple
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from ..services.asset_manager import AssetManager

logger = get_logger(__name__)

class MenuGrid:
    """Menu grid component for the dashboard screen."""
    
    def __init__(self, display, screen_manager) -> None:
        """Initialize the menu grid."""
        self.display = display
        self.screen_manager = screen_manager
        self.assets = AssetManager()
        
        # Menu items
        self.menu_items = [
            {
                'title': 'Ticker',
                'screen': 'ticker',
                'icon': 'stocks'  # Using stocks.svg
            },
            {
                'title': 'News',
                'screen': 'news',
                'icon': 'news'  # Using news.svg
            },
            {
                'title': 'Settings',
                'screen': 'settings',
                'icon': 'settings'  # Using settings.svg
            }
        ]
        
        # Dimensions
        self.grid_height = 160
        self.card_height = 130
        self.padding = 15
        self.icon_size = (32, 32)  # Size for SVG icons
        
        # Calculate card width based on number of items
        display_width = self.display.surface.get_width()
        self.card_width = (display_width - (self.padding * (len(self.menu_items) + 1))) // len(self.menu_items)
        
        # Touch handling
        self.last_touch_time = 0
        self.touch_delay = 0.3  # 300ms
        
        logger.info(f"MenuGrid initialized with card dimensions: {self.card_width}x{self.card_height}")
    
    def _draw_menu_item(self, item: Dict, x: int, y: int) -> pygame.Rect:
        """Draw a single menu item."""
        # Create item rectangle
        item_rect = pygame.Rect(x, y, self.card_width, self.card_height)
        
        # Draw background
        pygame.draw.rect(
            self.display.surface,
            (30, 30, 30),
            item_rect,
            border_radius=15
        )
        
        # Draw icon
        icon = self.assets.get_icon(item['icon'], size=self.icon_size, color=AppConfig.WHITE)
        if icon:
            icon_rect = icon.get_rect(
                centerx=item_rect.centerx,
                centery=item_rect.centery - 10
            )
            self.display.surface.blit(icon, icon_rect)
            logger.debug(f"Drew icon {item['icon']} at {icon_rect}")
        else:
            logger.warning(f"Failed to load icon: {item['icon']}")
        
        # Draw title
        title_font = self.display.get_text_font('sm', 'bold')
        title_surface = title_font.render(item['title'], True, AppConfig.WHITE)
        title_rect = title_surface.get_rect(
            centerx=item_rect.centerx,
            top=item_rect.centery + 20
        )
        self.display.surface.blit(title_surface, title_rect)
        
        return item_rect
    
    def draw(self, start_y: int) -> List[Tuple[pygame.Rect, str]]:
        """Draw the menu grid."""
        clickable_areas = []
        current_x = self.padding
        
        for item in self.menu_items:
            item_rect = self._draw_menu_item(item, current_x, start_y)
            clickable_areas.append((item_rect, item['screen']))
            logger.debug(f"Added clickable area for {item['title']} at {item_rect}")
            current_x += self.card_width + self.padding
        
        return clickable_areas
    
    def handle_click(self, pos: Tuple[int, int], clickable_areas: List[Tuple[pygame.Rect, str]]) -> None:
        """Handle touch events."""
        current_time = time.time()
        if current_time - self.last_touch_time < self.touch_delay:
            logger.debug("Touch ignored due to delay")
            return
        
        x, y = pos
        logger.debug(f"Checking touch at ({x}, {y}) against {len(clickable_areas)} areas")
        
        for rect, screen_name in clickable_areas:
            logger.debug(f"Checking rect {rect} for screen {screen_name}")
            if rect.collidepoint(x, y):
                logger.info(f"Menu item touched: {screen_name}")
                if self.screen_manager:
                    logger.debug(f"Switching to screen: {screen_name}")
                    self.screen_manager.switch_screen(screen_name)
                    self.last_touch_time = current_time
                else:
                    logger.error("Screen manager not initialized")
                break 