"""Screen for displaying detailed coin information."""

import pygame
import os
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen

logger = get_logger(__name__)

class TickerScreen(BaseScreen):
    """Screen for displaying detailed coin information."""
    
    def __init__(self, display) -> None:
        """Initialize the ticker screen."""
        super().__init__(display)
        self.background_color = (13, 13, 13)  # Darker black for more contrast
        self.current_index = 0
        self.coins = []
        
        # Sparkline dimensions
        self.sparkline_height = int(self.height * 0.7)  # 70% of screen height
        self.sparkline_padding = 0
        
        # Load initial coin data
        self.refresh_coins()
        
        logger.info("TickerScreen initialized")
    
    def refresh_coins(self):
        """Refresh the list of tracked coins with current data."""
        self.coins = self.crypto_manager.get_tracked_coins()
        if self.coins and self.current_index >= len(self.coins):
            self.current_index = 0
    
    def next_coin(self):
        """Switch to next coin."""
        if self.coins:
            self.current_index = (self.current_index + 1) % len(self.coins)
    
    def previous_coin(self):
        """Switch to previous coin."""
        if self.coins:
            self.current_index = (self.current_index - 1) % len(self.coins)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        gestures = self.gesture_handler.handle_touch_event(event)
        
        if gestures['swipe_left']:
            logger.info("Swipe left detected, showing next coin")
            self.next_coin()
        elif gestures['swipe_right']:
            logger.info("Swipe right detected, showing previous coin")
            self.previous_coin()
        elif gestures['swipe_down']:
            logger.info("Swipe down detected, returning to dashboard")
            self.screen_manager.switch_screen('dashboard')
    
    def draw(self) -> None:
        """Draw the ticker screen."""
        if not self.coins:
            return
            
        current_coin = self.coins[self.current_index]
        
        # Fill background
        self.display.surface.fill(self.background_color)
        
        # Draw coin logo in top right
        logo_size = 64  # Large icon size
        logo_path = os.path.join(AppConfig.CACHE_DIR, f"{current_coin['symbol'].lower()}_logo.png")
        if os.path.exists(logo_path):
            try:
                logo = pygame.image.load(logo_path)
                logo = pygame.transform.scale(logo, (logo_size, logo_size))
                logo_rect = logo.get_rect(
                    right=self.width - 20,  # 20px from right edge
                    top=20  # 20px from top
                )
                self.display.surface.blit(logo, logo_rect)
            except Exception as e:
                logger.error(f"Error loading logo: {e}")
        
        # Draw price (larger)
        price_text = f"${current_coin['current_price']:,.2f}"
        price_font = self.display.get_title_font('xl')
        price_surface = price_font.render(price_text, True, AppConfig.WHITE)
        price_rect = price_surface.get_rect(
            left=20,
            top=20
        )
        self.display.surface.blit(price_surface, price_rect)
        
        # Draw 24h change next to price
        change_24h = current_coin['price_change_24h']
        change_color = AppConfig.GREEN if change_24h >= 0 else AppConfig.RED
        change_text = f"{change_24h:+.1f}%"
        change_font = self.display.get_title_font('md')
        change_surface = change_font.render(change_text, True, change_color)
        change_rect = change_surface.get_rect(
            left=price_rect.right + 20,
            centery=price_rect.centery
        )
        self.display.surface.blit(change_surface, change_rect)
        
        # Draw trend icon
        trend_icon = self.assets.get_icon(
            'trending-up' if change_24h >= 0 else 'trending-down',
            size=(32, 32),
            color=change_color
        )
        if trend_icon:
            trend_rect = trend_icon.get_rect(
                left=change_rect.right + 10,
                centery=change_rect.centery
            )
            self.display.surface.blit(trend_icon, trend_rect)
        
        # Draw coin name and symbol below price (larger)
        name_text = f"{current_coin['name']}"
        name_font = self.display.get_title_font('lg', 'bold')
        name_surface = name_font.render(name_text, True, AppConfig.WHITE)
        name_rect = name_surface.get_rect(
            left=20,
            top=price_rect.bottom + 15
        )
        self.display.surface.blit(name_surface, name_rect)
        
        # Draw symbol below name (larger but light weight)
        symbol_text = current_coin['symbol'].upper()
        symbol_font = self.display.get_font('light', 'title-md')
        symbol_surface = symbol_font.render(symbol_text, True, (128, 128, 128))
        symbol_rect = symbol_surface.get_rect(
            left=20,
            top=name_rect.bottom + 8
        )
        self.display.surface.blit(symbol_surface, symbol_rect)
        
        # Draw star if favorited
        if current_coin.get('favorite', False):
            star_icon = self.assets.get_icon('star', size=(24, 24), color=(255, 165, 0))
            if star_icon:
                star_rect = star_icon.get_rect(
                    left=symbol_rect.right + 10,
                    centery=symbol_rect.centery
                )
                self.display.surface.blit(star_icon, star_rect)
        
        # Draw sparkline if price history is available
        if 'sparkline_7d' in current_coin and current_coin['sparkline_7d']:
            prices = current_coin['sparkline_7d']
            if prices:
                # Create a surface for the gradient and sparkline with alpha channel
                sparkline_surface = pygame.Surface((self.width, self.sparkline_height), pygame.SRCALPHA)
                
                # Calculate sparkline dimensions
                sparkline_rect = pygame.Rect(
                    0,
                    0,
                    self.width,
                    self.sparkline_height
                )
                
                # Draw sparkline
                if len(prices) > 1:
                    min_price = min(prices)
                    max_price = max(prices)
                    price_range = max_price - min_price
                    
                    if price_range > 0:
                        points = []
                        for i, price in enumerate(prices):
                            x = int((i / (len(prices) - 1)) * sparkline_rect.width)
                            y = int(sparkline_rect.height - ((price - min_price) / price_range) * sparkline_rect.height)
                            points.append((x, y))
                        
                        if len(points) > 1:
                            # Calculate 7-day price change
                            price_change_7d = ((prices[-1] - prices[0]) / prices[0]) * 100
                            # Draw line with gradient color based on 7-day price change
                            line_color = AppConfig.GREEN if price_change_7d >= 0 else AppConfig.RED
                            pygame.draw.lines(sparkline_surface, line_color, False, points, 2)
                
                # Position sparkline at bottom of screen
                sparkline_rect.bottom = self.height
                self.display.surface.blit(sparkline_surface, sparkline_rect)
        
        self.update_screen() 