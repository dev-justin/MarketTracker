"""Component for displaying top movers in the market."""

import pygame
from typing import List, Dict, Optional
from ..config.settings import AppConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class TopMovers:
    """Component for displaying top movers in the market."""
    
    def __init__(self, display, crypto_manager) -> None:
        """Initialize the top movers component."""
        self.display = display
        self.crypto_manager = crypto_manager
        
        # Component dimensions
        self.section_height = 180
        self.card_width = 140
        self.card_height = 120
        self.padding = 15
        
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
    
    def _draw_mover_card(self, coin: Dict, x: int, y: int) -> None:
        """Draw a single mover card."""
        # Create card rectangle
        card_rect = pygame.Rect(x, y, self.card_width, self.card_height)
        
        # Draw card background
        pygame.draw.rect(
            self.display.surface,
            (30, 30, 30),
            card_rect,
            border_radius=15
        )
        
        # Draw symbol
        symbol_font = self.display.get_text_font('md', 'bold')
        symbol_surface = symbol_font.render(coin['symbol'].upper(), True, AppConfig.WHITE)
        symbol_rect = symbol_surface.get_rect(
            centerx=card_rect.centerx,
            top=card_rect.top + 15
        )
        self.display.surface.blit(symbol_surface, symbol_rect)
        
        # Draw price
        price_font = self.display.get_text_font('sm', 'regular')
        price_text = f"${float(coin['current_price']):,.2f}"
        price_surface = price_font.render(price_text, True, AppConfig.GRAY)
        price_rect = price_surface.get_rect(
            centerx=card_rect.centerx,
            top=symbol_rect.bottom + 10
        )
        self.display.surface.blit(price_surface, price_rect)
        
        # Draw percentage change
        change = float(coin.get('price_change_24h', 0))
        change_color = AppConfig.GREEN if change >= 0 else AppConfig.RED
        change_text = f"{'+' if change >= 0 else ''}{change:.1f}%"
        change_font = self.display.get_text_font('md', 'bold')
        change_surface = change_font.render(change_text, True, change_color)
        change_rect = change_surface.get_rect(
            centerx=card_rect.centerx,
            top=price_rect.bottom + 10
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
            left=self.padding,
            top=start_y
        )
        self.display.surface.blit(title_surface, title_rect)
        
        # Draw mover cards
        card_y = title_rect.bottom + 15
        card_x = self.padding
        
        for coin in self.movers:
            self._draw_mover_card(coin, card_x, card_y)
            card_x += self.card_width + self.padding 