"""Component for displaying scrolling top movers."""

import pygame
import os
from ..config.settings import AppConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class TopMovers:
    """Component for displaying scrolling top movers section."""
    
    def __init__(self, display, crypto_manager):
        """Initialize the top movers component."""
        self.display = display
        self.crypto_manager = crypto_manager
        
        # State
        self.movers = []
        self.scroll_offset = 0
        self.scroll_speed = 1.2
        self.mover_width = 340
        self.mover_spacing = 20  # Add spacing between items
        self.last_update_time = 0
        self.update_interval = 10000  # 10 seconds
        self.circle_color = (45, 45, 45)
        
        # Dimensions
        self.section_height = 100
        self.section_y = 160
        self.logo_size = 50
        
        # Initial data fetch
        self.update()
    
    def update(self):
        """Update the list of top movers."""
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_update_time > self.update_interval:
            coins = self.crypto_manager.get_tracked_coins()
            if coins:
                # Sort by absolute price change
                sorted_coins = sorted(coins, key=lambda x: abs(x.get('price_change_24h', 0)), reverse=True)
                self.movers = sorted_coins[:5]  # Get top 5 movers
            self.last_update_time = current_time
    
    def draw(self):
        """Draw the scrolling top movers section."""
        if not self.movers:
            self.update()
            if not self.movers:
                return
        
        # Draw section header
        header_font = self.display.get_text_font('md', 'bold')
        header_surface = header_font.render("TOP MOVERS", True, (150, 150, 150))
        header_rect = header_surface.get_rect(left=20, bottom=self.section_y - 10)
        self.display.surface.blit(header_surface, header_rect)
        
        # Create clipping rect for smooth scrolling
        display_width = self.display.surface.get_width()
        scroll_area = pygame.Rect(0, self.section_y, display_width, self.section_height)
        self.display.surface.set_clip(scroll_area)
        
        # Update scroll position
        self.scroll_offset -= self.scroll_speed
        item_width = self.mover_width + self.mover_spacing
        
        # Reset scroll when we've scrolled one full item width
        if abs(self.scroll_offset) >= item_width:
            self.scroll_offset += item_width  # Instead of resetting to 0, add item width
            # Rotate the list to create infinite scroll effect
            self.movers.append(self.movers.pop(0))
        
        # Draw items (we need to draw 3 items for smooth transition)
        for i in range(3):
            x = 20 + (i * item_width) + self.scroll_offset
            idx = i % len(self.movers)
            coin = self.movers[idx]
            
            # Always use the original index for ranking (based on 24h change)
            rank = idx + 1  # Rank from 1-5 based on original sort order
            
            # Only draw if it would be visible
            if -item_width <= x <= display_width:
                self._draw_mover_item(x, coin, rank)
        
        # Reset clip
        self.display.surface.set_clip(None)
    
    def _draw_mover_item(self, x, coin, rank):
        """Draw a single mover item."""
        # Draw background
        mover_rect = pygame.Rect(x, self.section_y, self.mover_width, self.section_height)
        pygame.draw.rect(self.display.surface, (25, 25, 25), mover_rect, border_radius=15)
        
        # Draw rank number in circle
        circle_radius = 22
        circle_center = (x + 35, self.section_y + self.section_height//2)
        pygame.draw.circle(self.display.surface, self.circle_color, circle_center, circle_radius)
        
        rank_font = self.display.get_title_font('md', 'bold')
        rank_surface = rank_font.render(str(rank), True, AppConfig.WHITE)
        rank_rect = rank_surface.get_rect(center=circle_center)
        self.display.surface.blit(rank_surface, rank_rect)
        
        # Draw logo
        logo_path = os.path.join(AppConfig.CACHE_DIR, f"{coin['symbol'].lower()}_logo.png")
        if os.path.exists(logo_path):
            try:
                logo = pygame.image.load(logo_path)
                logo = pygame.transform.scale(logo, (self.logo_size, self.logo_size))
                logo_rect = logo.get_rect(
                    left=x + 70,  # Adjusted for circle
                    centery=self.section_y + self.section_height//2
                )
                self.display.surface.blit(logo, logo_rect)
                
                # Draw text content
                self._draw_mover_text(x + 70 + self.logo_size + 20, coin, mover_rect)
                
            except Exception as e:
                logger.error(f"Error drawing mover: {e}")
    
    def _draw_mover_text(self, content_left, coin, mover_rect):
        """Draw the text content of a mover item."""
        # Calculate vertical center for symbol/change stack
        stack_height = 42
        stack_top = self.section_y + (self.section_height - stack_height) // 2
        
        # Draw symbol (smaller/lighter)
        text_font = self.display.get_text_font('md', 'regular')
        symbol_surface = text_font.render(coin['symbol'].upper(), True, (200, 200, 200))
        symbol_rect = symbol_surface.get_rect(
            left=content_left,
            top=stack_top
        )
        self.display.surface.blit(symbol_surface, symbol_rect)
        
        # Draw change percentage below symbol
        change_24h = coin['price_change_24h']
        change_color = AppConfig.GREEN if change_24h >= 0 else AppConfig.RED
        change_text = f"{change_24h:+.1f}%"
        change_surface = text_font.render(change_text, True, change_color)
        change_rect = change_surface.get_rect(
            left=content_left,
            top=symbol_rect.bottom + 1
        )
        self.display.surface.blit(change_surface, change_rect)
        
        # Draw price on the right
        price_text = f"${coin['current_price']:,.2f}"
        price_font = self.display.get_text_font('lg', 'regular')
        price_surface = price_font.render(price_text, True, AppConfig.WHITE)
        price_rect = price_surface.get_rect(
            right=mover_rect.right - 20,
            centery=self.section_y + self.section_height//2
        )
        self.display.surface.blit(price_surface, price_rect) 