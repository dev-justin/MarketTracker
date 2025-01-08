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
        self.height = 400  # Fixed height for menu section
        self.padding = 20
        
        # Calculate card dimensions
        usable_width = self.width - (self.padding * 4)  # 4 paddings (left, between cards, right)
        self.card_width = usable_width // 3
        self.card_height = 300
        
        # Menu items configuration
        self.menu_items = [
            {
                'title': 'Ticker',
                'subtitle': 'Track your favorite coins and stocks',
                'screen': 'ticker',
                'icon': 'trending-up'
            },
            {
                'title': 'News',
                'subtitle': 'Latest market updates and analysis',
                'screen': None,  # Placeholder for now
                'icon': 'trending-up'  # Use appropriate icon when available
            },
            {
                'title': 'Settings',
                'subtitle': 'Customize your experience',
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
            border_radius=20
        )
        self.display.surface.blit(gradient_surface, card_rect)
        
        # Draw icon if available
        if item['icon']:
            icon = self.display.assets.get_icon(item['icon'], size=(48, 48), color=AppConfig.WHITE)
            if icon:
                icon_rect = icon.get_rect(
                    centerx=card_rect.centerx,
                    top=card_rect.top + 40
                )
                self.display.surface.blit(icon, icon_rect)
        
        # Draw title
        title_font = self.display.get_title_font('md', 'bold')
        title_surface = title_font.render(item['title'], True, AppConfig.WHITE)
        title_rect = title_surface.get_rect(
            centerx=card_rect.centerx,
            top=card_rect.top + 120
        )
        self.display.surface.blit(title_surface, title_rect)
        
        # Draw subtitle (wrapped to fit card width)
        subtitle_font = self.display.get_text_font('md', 'regular')
        subtitle_words = item['subtitle'].split()
        subtitle_lines = []
        current_line = []
        
        for word in subtitle_words:
            test_line = ' '.join(current_line + [word])
            test_surface = subtitle_font.render(test_line, True, AppConfig.GRAY)
            if test_surface.get_width() <= self.card_width - 40:  # 20px padding on each side
                current_line.append(word)
            else:
                if current_line:
                    subtitle_lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            subtitle_lines.append(' '.join(current_line))
        
        subtitle_y = title_rect.bottom + 20
        for line in subtitle_lines:
            subtitle_surface = subtitle_font.render(line, True, AppConfig.GRAY)
            subtitle_rect = subtitle_surface.get_rect(
                centerx=card_rect.centerx,
                top=subtitle_y
            )
            self.display.surface.blit(subtitle_surface, subtitle_rect)
            subtitle_y += subtitle_font.get_height() + 5
        
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