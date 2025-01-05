import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen
from ..services.crypto.crypto_manager import CryptoManager

logger = get_logger(__name__)

class TickerScreen(BaseScreen):
    def __init__(self, display) -> None:
        super().__init__(display)
        self.background_color = AppConfig.BLACK
        self.crypto_manager = CryptoManager()
        self.current_index = 0
        self.coins = []
        
        # Sparkline dimensions
        self.sparkline_height = self.height // 2  # 50% of screen height
        self.sparkline_padding = 0  # No padding for full width
        
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
        
        # Draw coin name and symbol
        title_text = f"{current_coin['name']} ({current_coin['symbol']})"
        title_surface = self.fonts['title-md'].render(title_text, True, AppConfig.WHITE)
        title_rect = title_surface.get_rect(left=20, top=20)  # Left aligned with 20px padding
        self.display.surface.blit(title_surface, title_rect)
        
        # Draw price (larger)
        price_text = f"${current_coin['current_price']:,.2f}"
        price_surface = self.fonts['title-xl'].render(price_text, True, AppConfig.WHITE)  # Using larger font
        price_rect = price_surface.get_rect(left=20, top=title_rect.bottom + 5)  # Left aligned with small gap
        self.display.surface.blit(price_surface, price_rect)
        
        # Draw 24h change
        change_24h = current_coin['price_change_24h']
        change_color = AppConfig.GREEN if change_24h >= 0 else AppConfig.RED
        change_text = f"{change_24h:+.2f}% (24h)"
        change_surface = self.fonts['medium'].render(change_text, True, change_color)
        change_rect = change_surface.get_rect(left=20, top=price_rect.bottom + 5)  # Left aligned
        self.display.surface.blit(change_surface, change_rect)
        
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
                        fill_color = (0, 255, 0, 40)  # Semi-transparent green
                        line_color = (0, 255, 0, 255)  # Solid green
                    else:
                        fill_color = (255, 0, 0, 40)  # Semi-transparent red
                        line_color = (255, 0, 0, 255)  # Solid red
                    
                    # Create fill polygon points by adding bottom corners
                    fill_points = points + [
                        (self.width, sparkline_rect.height),  # Bottom right
                        (0, sparkline_rect.height)  # Bottom left
                    ]
                    
                    # Draw gradient fill using polygon
                    pygame.draw.polygon(sparkline_surface, fill_color, fill_points)
                    
                    # Draw the actual line on top
                    pygame.draw.lines(sparkline_surface, line_color, False, points, 3)  # Thicker line
                    
                    # Position and draw the sparkline surface
                    self.display.surface.blit(
                        sparkline_surface,
                        (0, self.height - self.sparkline_height)
                    )
        
        # Draw navigation hints
        if len(self.coins) > 1:
            nav_text = f"{self.current_index + 1} / {len(self.coins)}"
            nav_surface = self.fonts['sm'].render(nav_text, True, AppConfig.GRAY)
            nav_rect = nav_surface.get_rect(centerx=self.width//2, bottom=self.height - 20)
            self.display.surface.blit(nav_surface, nav_rect)
        
        self.update_screen() 