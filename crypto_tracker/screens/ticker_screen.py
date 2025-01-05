import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen
from ..services.crypto.crypto_manager import CryptoManager
import os

logger = get_logger(__name__)

class TickerScreen(BaseScreen):
    def __init__(self, display) -> None:
        super().__init__(display)
        self.background_color = (13, 13, 13)  # Darker black for more contrast
        self.crypto_manager = CryptoManager()
        self.current_index = 0
        self.coins = []
        
        # Sparkline dimensions
        self.sparkline_height = int(self.height * 0.7)  # 70% of screen height
        self.sparkline_padding = 0
        
        # Load trend icons
        try:
            self.trend_up_icon = pygame.image.load(os.path.join(AppConfig.ASSETS_DIR, 'icons', 'trending-up.svg'))
            self.trend_down_icon = pygame.image.load(os.path.join(AppConfig.ASSETS_DIR, 'icons', 'trending-down.svg'))
            # Scale icons to match text height
            icon_size = 32
            self.trend_up_icon = pygame.transform.scale(self.trend_up_icon, (icon_size, icon_size))
            self.trend_down_icon = pygame.transform.scale(self.trend_down_icon, (icon_size, icon_size))
        except Exception as e:
            logger.error(f"Error loading trend icons: {e}")
            self.trend_up_icon = None
            self.trend_down_icon = None
        
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
        # Fill background
        self.display.surface.fill(self.background_color)
        
        # Refresh coin data
        self.refresh_coins()
        
        if not self.coins:
            # Draw "No coins" message
            text = self.fonts['title-md'].render("No coins tracked", True, AppConfig.WHITE)
            text_rect = text.get_rect(center=(self.width//2, self.height//2))
            self.display.surface.blit(text, text_rect)
            self.update_screen()
            return
        
        current_coin = self.coins[self.current_index]
        
        # Draw coin logo in top right if available
        logo_size = 64
        logo_margin = 20
        logo_rect = None
        try:
            logo_path = os.path.join(AppConfig.CACHE_DIR, f"{current_coin['symbol'].lower()}_logo.png")
            if os.path.exists(logo_path):
                logo = pygame.image.load(logo_path)
                logo = pygame.transform.scale(logo, (logo_size, logo_size))
                logo_rect = logo.get_rect(
                    right=self.width - logo_margin,
                    top=logo_margin
                )
                self.display.surface.blit(logo, logo_rect)
        except Exception as e:
            logger.error(f"Error loading logo for {current_coin['symbol']}: {e}")
        
        # Draw price in top left (large)
        price_text = f"${current_coin['current_price']:,.2f}"
        price_surface = self.fonts['title-xl'].render(price_text, True, AppConfig.WHITE)
        # Scale up the price text
        scaled_price_surface = pygame.transform.scale(
            price_surface,
            (int(price_surface.get_width() * 1.2), int(price_surface.get_height() * 1.2))
        )
        price_rect = scaled_price_surface.get_rect(
            left=20,
            top=20
        )
        self.display.surface.blit(scaled_price_surface, price_rect)
        
        # Draw percentage change with trend icon (next to price)
        change_24h = current_coin['price_change_24h']
        change_color = AppConfig.GREEN if change_24h >= 0 else AppConfig.RED
        
        # Draw trend icon
        trend_icon = self.trend_up_icon if change_24h >= 0 else self.trend_down_icon
        if trend_icon:
            # Color the trend icon
            colored_icon = trend_icon.copy()
            for x in range(colored_icon.get_width()):
                for y in range(colored_icon.get_height()):
                    color = colored_icon.get_at((x, y))
                    if color.a > 0:  # If pixel is not transparent
                        colored_icon.set_at((x, y), change_color)
            
            trend_rect = colored_icon.get_rect(
                left=price_rect.right + 20,
                centery=price_rect.centery
            )
            self.display.surface.blit(colored_icon, trend_rect)
            
            # Draw percentage next to icon
            change_text = f"{abs(change_24h):.1f}%"
            change_surface = self.fonts['title-lg'].render(change_text, True, change_color)
            change_rect = change_surface.get_rect(
                left=trend_rect.right + 5,
                centery=trend_rect.centery
            )
            self.display.surface.blit(change_surface, change_rect)
        
        # Draw coin name and symbol below price (larger)
        name_text = f"{current_coin['name']}"
        name_surface = self.fonts['title-lg'].render(name_text, True, AppConfig.WHITE)  # Increased to title-lg
        name_rect = name_surface.get_rect(
            left=20,
            top=price_rect.bottom + 15  # Increased spacing
        )
        self.display.surface.blit(name_surface, name_rect)
        
        # Draw symbol below name (larger but light weight)
        symbol_text = current_coin['symbol'].upper()
        symbol_surface = self.fonts['light'].render(symbol_text, True, (128, 128, 128))  # Changed to light font
        symbol_rect = symbol_surface.get_rect(
            left=20,
            top=name_rect.bottom + 8
        )
        self.display.surface.blit(symbol_surface, symbol_rect)
        
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
                
                # Calculate min and max prices for scaling
                min_price = min(prices)
                max_price = max(prices)
                price_range = max_price - min_price
                
                # Calculate points
                points = []
                for i, price in enumerate(prices):
                    x = i * self.width / (len(prices) - 1)
                    # Normalize price to sparkline height, starting from bottom
                    normalized_price = (price - min_price) / price_range if price_range > 0 else 0.5
                    y = sparkline_rect.height - (normalized_price * sparkline_rect.height)
                    points.append((x, y))
                
                # Draw sparkline with gradient
                if len(points) > 1:
                    # Calculate 7d performance
                    price_change_7d = (prices[-1] - prices[0]) / prices[0] * 100
                    is_positive = price_change_7d >= 0
                    
                    # Create gradient colors
                    if is_positive:
                        fill_color = (0, 255, 0, 15)  # Very subtle green
                        line_color = (0, 255, 0, 255)  # Solid green
                    else:
                        fill_color = (255, 0, 0, 15)  # Very subtle red
                        line_color = (255, 0, 0, 255)  # Solid red
                    
                    # Create fill polygon points by adding bottom corners
                    fill_points = points + [
                        (sparkline_rect.right, sparkline_rect.height),  # Bottom right
                        (sparkline_rect.left, sparkline_rect.height)  # Bottom left
                    ]
                    
                    # Draw gradient fill using polygon
                    pygame.draw.polygon(sparkline_surface, fill_color, fill_points)
                    
                    # Draw the actual line on top
                    pygame.draw.lines(sparkline_surface, line_color, False, points, 2)
                    
                    # Position and draw the sparkline surface at the bottom
                    self.display.surface.blit(
                        sparkline_surface,
                        (0, self.height - self.sparkline_height)
                    )
        
        self.update_screen() 