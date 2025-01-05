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
        
        # Sparkline dimensions - make it larger
        self.sparkline_height = int(self.height * 0.6)  # 60% of screen height
        self.sparkline_padding = 40  # Add padding for month labels
        
        # Month labels
        self.months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        
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
        
        # Draw sparkline if price history is available
        if 'sparkline_7d' in current_coin and current_coin['sparkline_7d']:
            prices = current_coin['sparkline_7d']
            if prices:
                # Create a surface for the gradient and sparkline with alpha channel
                sparkline_surface = pygame.Surface((self.width, self.sparkline_height), pygame.SRCALPHA)
                
                # Calculate sparkline dimensions with padding
                chart_width = self.width - (self.sparkline_padding * 2)
                sparkline_rect = pygame.Rect(
                    self.sparkline_padding,
                    0,
                    chart_width,
                    self.sparkline_height - 40  # Space for month labels
                )
                
                # Calculate min and max prices for scaling
                min_price = min(prices)
                max_price = max(prices)
                price_range = max_price - min_price
                
                # Calculate points
                points = []
                for i, price in enumerate(prices):
                    x = sparkline_rect.left + (i * chart_width / (len(prices) - 1))
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
                    
                    # Draw month labels
                    label_y = sparkline_rect.bottom + 20
                    label_width = chart_width / (len(self.months) - 1)
                    for i, month in enumerate(self.months):
                        label_surface = self.fonts['light'].render(month, True, (128, 128, 128))
                        label_rect = label_surface.get_rect(
                            centerx=sparkline_rect.left + (i * label_width),
                            centery=label_y
                        )
                        self.display.surface.blit(label_surface, label_rect)
                    
                    # Draw vertical grid lines (very subtle)
                    for i in range(len(self.months)):
                        x = sparkline_rect.left + (i * label_width)
                        pygame.draw.line(
                            sparkline_surface,
                            (40, 40, 40, 128),  # Very subtle gray
                            (x, 0),
                            (x, sparkline_rect.height),
                            1
                        )
                    
                    # Draw the actual line on top
                    pygame.draw.lines(sparkline_surface, line_color, False, points, 2)
                    
                    # Position and draw the sparkline surface
                    self.display.surface.blit(
                        sparkline_surface,
                        (0, 20)  # Position at top with small margin
                    )
        
        # Draw crypto amount (large, centered)
        amount_text = f"{current_coin['current_price']:.8f} {current_coin['symbol']}"
        amount_surface = self.fonts['title-xl'].render(amount_text, True, AppConfig.WHITE)
        amount_rect = amount_surface.get_rect(
            centerx=self.width//2,
            bottom=self.height - 80
        )
        self.display.surface.blit(amount_surface, amount_rect)
        
        # Draw USD value below
        usd_value = f"(${current_coin['current_price']:,.2f})"
        usd_surface = self.fonts['light'].render(usd_value, True, (128, 128, 128))
        usd_rect = usd_surface.get_rect(
            centerx=self.width//2,
            top=amount_rect.bottom + 5
        )
        self.display.surface.blit(usd_surface, usd_rect)
        
        # Draw percentage change with arrow
        change_24h = current_coin['price_change_24h']
        arrow = "↗" if change_24h >= 0 else "↘"
        change_color = AppConfig.GREEN if change_24h >= 0 else AppConfig.RED
        change_text = f"{arrow} {abs(change_24h):.1f}%"
        change_surface = self.fonts['title-md'].render(change_text, True, change_color)
        change_rect = change_surface.get_rect(
            centerx=self.width//2,
            top=usd_rect.bottom + 10
        )
        self.display.surface.blit(change_surface, change_rect)
        
        self.update_screen() 