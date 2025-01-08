"""Component for displaying the main menu grid."""

import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class MenuGrid:
    """Component for displaying the main menu grid."""
    
    def __init__(self, display, screen_manager):
        """Initialize the menu grid component."""
        self.display = display
        self.screen_manager = screen_manager
        
        # Dimensions
        self.width = self.display.surface.get_width()
        self.height = 200  # Reduced from 300
        self.padding = 15
        
        # Calculate card dimensions
        usable_width = self.width - (self.padding * 4)  # 4 paddings (left, between cards, right)
        self.card_width = usable_width // 3
        self.card_height = 140  # Reduced from 220
        
        # Menu items configuration
        self.menu_items = [
            {
                'title': 'Ticker',
                'screen': 'ticker',
                'icon': 'trending-up'
            },
            {
                'title': 'News',
                'screen': None,  # Placeholder for now
                'icon': 'trending-up'  # Use appropriate icon when available
            },
            {
                'title': 'Settings',
                'screen': 'settings',
                'icon': 'edit'
            }
        ]
        
        logger.info("MenuGrid initialized")
    
    def _draw_menu_card(self, x: int, y: int, item: dict) -> pygame.Rect:
        """Draw a single menu card."""
        # Create card rectangle
        card_rect = pygame.Rect(x, y, self.card_width, self.card_height)
        
        # Draw card background with gradient effect
        gradient_surface = pygame.Surface((self.card_width, self.card_height), pygame.SRCALPHA)
        pygame.draw.rect(
            gradient_surface,
            (45, 45, 45, 230),  # Semi-transparent dark gray
            gradient_surface.get_rect(),
            border_radius=15
        )
        self.display.surface.blit(gradient_surface, card_rect)
        
        # Draw icon if available
        if item['icon']:
            icon = self.display.assets.get_icon(item['icon'], size=(36, 36), color=AppConfig.WHITE)
            if icon:
                icon_rect = icon.get_rect(
                    centerx=card_rect.centerx,
                    top=card_rect.top + 25  # Reduced from 30
                )
                self.display.surface.blit(icon, icon_rect)
        
        # Draw title
        title_font = self.display.get_title_font('sm', 'bold')
        title_surface = title_font.render(item['title'], True, AppConfig.WHITE)
        title_rect = title_surface.get_rect(
            centerx=card_rect.centerx,
            top=card_rect.top + 80  # Reduced from 90
        )
        self.display.surface.blit(title_surface, title_rect)
        
        return card_rect
    
    def draw(self, start_y: int) -> None:
        """Draw the menu grid."""
        # Calculate starting x position for first card
        current_x = self.padding
        
        # Store card rects for click detection
        self.card_rects = []
        
        # Draw each menu card
        for item in self.menu_items:
            card_rect = self._draw_menu_card(current_x, start_y, item)
            self.card_rects.append((card_rect, item))
            current_x += self.card_width + self.padding
    
    def handle_click(self, x: int, y: int) -> None:
        """Handle click events on menu cards."""
        for rect, item in self.card_rects:
            if rect.collidepoint(x, y) and item['screen']:
                logger.info(f"Menu item clicked: {item['title']}")
                self.screen_manager.switch_screen(item['screen']) 