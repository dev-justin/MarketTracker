from typing import Dict, Optional, List
import pygame
from ..config.settings import AppConfig
from ..constants import EventTypes, ScreenNames
from ..utils.logger import get_logger
from .base import Screen
import time

logger = get_logger(__name__)

class WallStreetScreen(Screen):
    """Screen for displaying all cryptocurrency prices in a scrolling ticker format."""
    
    def __init__(self, screen_manager, crypto_api) -> None:
        """
        Initialize the wallstreet screen.
        
        Args:
            screen_manager: The screen manager instance
            crypto_api: The crypto API service instance
        """
        super().__init__(screen_manager)
        self.crypto_api = crypto_api
        
        # Ticker settings
        self.scroll_speed = 3  # pixels per frame
        self.scroll_x = self.width  # Start from right edge
        self.ticker_spacing = 100  # Space between each ticker item
        self.font_size = 72  # Larger text for better visibility
        
        # Touch handling
        self.swipe_start_y: Optional[int] = None
        self.swipe_threshold: float = AppConfig.SWIPE_THRESHOLD
        self.last_tap_time: float = 0
        self.double_tap_threshold: float = AppConfig.DOUBLE_TAP_THRESHOLD
        
        # Price data
        self.current_prices: Optional[Dict[str, float]] = None
        self.price_changes: Dict[str, float] = {}
        self.ticker_items: List[Dict] = []  # List of items to display
        
        logger.info("WallStreetScreen initialized")
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events.
        
        Args:
            event: The pygame event to handle
        """
        if event.type not in (EventTypes.FINGER_DOWN.value, EventTypes.FINGER_UP.value):
            return
            
        x, y = self._scale_touch_input(event)
        
        # Handle double tap to return to ticker screen
        if event.type == EventTypes.FINGER_DOWN.value:
            current_time = time.time()
            if current_time - self.last_tap_time < self.double_tap_threshold:
                logger.info("Double tap detected, returning to ticker screen")
                self.manager.switch_screen(ScreenNames.TICKER.value)
            self.last_tap_time = current_time
        
        # Handle swipe up to settings
        if event.type == EventTypes.FINGER_DOWN.value:
            self.swipe_start_y = y
            logger.debug(f"Touch start at y={y}")
        elif event.type == EventTypes.FINGER_UP.value and self.swipe_start_y is not None:
            swipe_distance = self.swipe_start_y - y
            swipe_threshold = self.height * self.swipe_threshold
            if swipe_distance > swipe_threshold:
                logger.info("Swipe up detected, switching to settings")
                self.manager.switch_screen(ScreenNames.SETTINGS.value)
            self.swipe_start_y = None
    
    def update(self, prices: Optional[Dict[str, float]] = None) -> None:
        """
        Update the screen with new price data.
        
        Args:
            prices: Dictionary of current prices
        """
        self.current_prices = prices
        if prices:
            # Update price changes and prepare ticker items
            self.ticker_items = []
            for symbol in prices:
                historical_prices = self.crypto_api.get_historical_prices(symbol)
                if historical_prices and len(historical_prices) > 4:
                    current_price = historical_prices[-1]
                    price_24h_ago = historical_prices[-4]
                    change_percent = ((current_price - price_24h_ago) / price_24h_ago) * 100
                    
                    # Create ticker item with all necessary text
                    self.ticker_items.append({
                        'symbol': symbol,
                        'price': f"${prices[symbol]:,.2f}",
                        'change': f"{change_percent:+.2f}%" if change_percent >= 0 else f"{change_percent:.2f}%",
                        'color': AppConfig.GREEN if change_percent >= 0 else AppConfig.RED
                    })
        
        # Update scroll position
        self.scroll_x -= self.scroll_speed
        total_width = self._calculate_total_width()
        if self.scroll_x < -total_width:
            self.scroll_x = self.width
    
    def draw(self, display: pygame.Surface) -> None:
        """
        Draw the screen contents.
        
        Args:
            display: The pygame surface to draw on
        """
        display.fill(AppConfig.BLACK)
        
        if not self.ticker_items:
            return
        
        # Draw dividing line
        line_y = self.height // 2
        pygame.draw.line(display, AppConfig.CELL_BORDER_COLOR, 
                        (0, line_y), (self.width, line_y), 2)
        
        # Draw scrolling tickers
        x_pos = self.scroll_x
        for item in self.ticker_items:
            # Draw symbol
            symbol_text = self._create_text_surface(item['symbol'], self.font_size, AppConfig.WHITE)
            symbol_rect = symbol_text.get_rect(left=x_pos, centery=line_y)
            display.blit(symbol_text, symbol_rect)
            
            # Draw price
            price_text = self._create_text_surface(item['price'], self.font_size, AppConfig.WHITE)
            price_rect = price_text.get_rect(left=x_pos + symbol_rect.width + 20, centery=line_y)
            display.blit(price_text, price_rect)
            
            # Draw change percentage
            change_text = self._create_text_surface(item['change'], self.font_size, item['color'])
            change_rect = change_text.get_rect(left=x_pos + symbol_rect.width + price_rect.width + 40, centery=line_y)
            display.blit(change_text, change_rect)
            
            # Move to next ticker position
            x_pos += symbol_rect.width + price_rect.width + change_rect.width + self.ticker_spacing
    
    def _calculate_total_width(self) -> int:
        """Calculate the total width of all ticker items."""
        total_width = 0
        if self.ticker_items:
            for item in self.ticker_items:
                # Create temporary surfaces to calculate widths
                symbol_width = self._create_text_surface(item['symbol'], self.font_size, AppConfig.WHITE).get_width()
                price_width = self._create_text_surface(item['price'], self.font_size, AppConfig.WHITE).get_width()
                change_width = self._create_text_surface(item['change'], self.font_size, item['color']).get_width()
                total_width += symbol_width + price_width + change_width + self.ticker_spacing
        return total_width 