"""Component for displaying top movers in the market."""

import pygame
from typing import List, Dict, Optional
from ..config.settings import AppConfig
from ..utils.logger import get_logger
import os

logger = get_logger(__name__)

class TopMovers:
    """Component for displaying top movers in the market."""
    
    def __init__(self, display, crypto_manager) -> None:
        """Initialize the top movers component."""
        self.display = display
        self.crypto_manager = crypto_manager
        
        # Component dimensions
        self.section_height = 120  # Height for the section
        
        # Calculate card width to span full width with padding
        total_padding = 40  # 20px padding on each side
        spacing_between = 20  # 20px between cards
        total_spacing = total_padding + (spacing_between * 2)  # Total horizontal space used for padding
        self.card_width = (AppConfig.DISPLAY_WIDTH - total_spacing) // 3  # Divide remaining space by 3
        
        # Card dimensions and styling
        self.logo_size = 46  # Logo size
        self.card_height = 120  # Fixed card height
        self.top_padding = 12
        self.element_spacing = 6
        self.card_colors = {
            'positive': (255, 204, 0),  # Yellow for positive
            'negative': (30, 30, 30),   # Dark gray for negative
        }
        
        # State
        self.movers: List[Dict] = []
        
        logger.info("TopMovers component initialized")
    
    def update(self) -> None:
        """Update the list of top movers."""
        tracked_coins = self.crypto_manager.get_tracked_coins()
        self.movers = sorted(
            tracked_coins,
            key=lambda x: abs(float(x.get('price_change_24h', 0))),
            reverse=True
        )[:3]  # Get top 3 movers
    
    def _create_circular_icon(self, surface: pygame.Surface) -> pygame.Surface:
        """Create a circular icon from a square surface."""
        size = surface.get_width()
        circular = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Create a circle mask
        pygame.draw.circle(circular, (255, 255, 255, 255), (size//2, size//2), size//2)
        
        # Apply the mask to the original surface
        circular.blit(surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        return circular

    def _draw_mover_card(self, coin: Dict, x: int, y: int) -> None:
        """Draw a single mover card."""
        # Get price change and determine card color
        change = float(coin.get('price_change_24h', 0))
        card_color = self.card_colors['positive'] if change >= 0 else self.card_colors['negative']
        
        # Create card rectangle
        card_rect = pygame.Rect(x, y, self.card_width, self.card_height)
        
        # Draw card background
        pygame.draw.rect(
            self.display.surface,
            card_color,
            card_rect,
            border_radius=15
        )
        
        # Draw logo
        logo_path = os.path.join(AppConfig.CACHE_DIR, f"{coin['symbol'].lower()}_logo.png")
        logo_x = card_rect.left + (card_rect.width - self.logo_size) // 2  # Center horizontally
        logo_y = card_rect.top + 15  # Top padding
        
        if os.path.exists(logo_path):
            try:
                logo = pygame.image.load(logo_path)
                logo = pygame.transform.scale(logo, (self.logo_size, self.logo_size))
                logo = self._create_circular_icon(logo)
                logo_rect = logo.get_rect(
                    centerx=card_rect.centerx,
                    top=logo_y
                )
                self.display.surface.blit(logo, logo_rect)
            except Exception as e:
                logger.error(f"Error loading logo: {e}")
        
        # Draw symbol (ticker)
        symbol_font = self.display.get_text_font('md', 'bold')
        symbol_surface = symbol_font.render(coin['symbol'].upper(), True, (0, 0, 0) if change >= 0 else AppConfig.WHITE)
        symbol_rect = symbol_surface.get_rect(
            centerx=card_rect.centerx,
            top=logo_y + self.logo_size + 10
        )
        self.display.surface.blit(symbol_surface, symbol_rect)
        
        # Draw percentage change
        change_text = f"{'+' if change >= 0 else ''}{change:.1f}%"
        change_font = self.display.get_text_font('md', 'bold')
        change_surface = change_font.render(change_text, True, (0, 0, 0) if change >= 0 else AppConfig.WHITE)
        change_rect = change_surface.get_rect(
            centerx=card_rect.centerx,
            top=symbol_rect.bottom + 5
        )
        self.display.surface.blit(change_surface, change_rect)
    
    def draw(self, start_y: int) -> None:
        """Draw the top movers section."""
        # Update data
        self.update()
        
        # Draw section title
        title_font = self.display.get_text_font('md', 'bold')
        title_surface = title_font.render("Top Movers", True, AppConfig.WHITE)
        title_rect = title_surface.get_rect(
            left=20,
            top=start_y
        )
        self.display.surface.blit(title_surface, title_rect)
        
        # Draw mover cards
        card_y = title_rect.bottom + 15
        card_x = 20
        spacing = 20  # Space between cards
        
        for coin in self.movers:
            self._draw_mover_card(coin, card_x, card_y)
            card_x += self.card_width + spacing 