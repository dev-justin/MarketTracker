from typing import Dict, Optional, List
import pygame
from ..config.settings import AppConfig
from ..constants import EventTypes, ScreenNames
from ..utils.logger import get_logger
from .base import Screen

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
        self.scroll_speed = 2  # pixels per frame
        self.ticker_height = 60
        self.ticker_spacing = 20
        self.ticker_padding = 20
        
        # Scroll position
        self.scroll_y = 0
        
        # Touch handling
        self.swipe_start_y: Optional[int] = None
        self.swipe_threshold: float = AppConfig.SWIPE_THRESHOLD
        
        # Price data
        self.current_prices: Optional[Dict[str, float]] = None
        self.price_changes: Dict[str, float] = {}
        
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
            for symbol in prices:
                historical_prices = self.crypto_api.get_historical_prices(symbol)
                if historical_prices and len(historical_prices) > 4:
                    current_price = historical_prices[-1]
                    price_24h_ago = historical_prices[-4]
                    self.price_changes[symbol] = ((current_price - price_24h_ago) / price_24h_ago) * 100
        
        # Update scroll position
        self.scroll_y = (self.scroll_y + self.scroll_speed) % (
            (len(self.crypto_api.get_tracked_symbols()) * (self.ticker_height + self.ticker_spacing)) + self.height
        )
    
    def draw(self, display: pygame.Surface) -> None:
        """
        Draw the screen contents.
        
        Args:
            display: The pygame surface to draw on
        """
        display.fill(AppConfig.BLACK)
        
        if not self.current_prices:
            return
        
        symbols = self.crypto_api.get_tracked_symbols()
        total_height = len(symbols) * (self.ticker_height + self.ticker_spacing)
        
        # Draw each ticker
        for i, symbol in enumerate(symbols):
            y_pos = (i * (self.ticker_height + self.ticker_spacing)) - self.scroll_y
            
            # Wrap around to bottom when scrolled off top
            if y_pos < -self.ticker_height:
                y_pos += total_height + self.height
            
            # Only draw visible tickers
            if -self.ticker_height <= y_pos <= self.height:
                self._draw_ticker(display, symbol, y_pos)
    
    def _draw_ticker(self, display: pygame.Surface, symbol: str, y_pos: float) -> None:
        """
        Draw a single ticker row.
        
        Args:
            display: The pygame surface to draw on
            symbol: The symbol to display
            y_pos: The vertical position to draw at
        """
        # Draw background
        ticker_rect = pygame.Rect(
            self.ticker_padding,
            y_pos,
            self.width - (self.ticker_padding * 2),
            self.ticker_height
        )
        pygame.draw.rect(display, AppConfig.CELL_BG_COLOR, ticker_rect, border_radius=10)
        pygame.draw.rect(display, AppConfig.CELL_BORDER_COLOR, ticker_rect, 1, border_radius=10)
        
        # Draw symbol
        symbol_text = self._create_text_surface(symbol, 36, AppConfig.WHITE)
        symbol_rect = symbol_text.get_rect(left=ticker_rect.left + 20, centery=y_pos + self.ticker_height/2)
        display.blit(symbol_text, symbol_rect)
        
        # Draw price
        if symbol in self.current_prices:
            price = self.current_prices[symbol]
            price_text = self._create_text_surface(f"${price:,.2f}", 36, AppConfig.WHITE)
            price_rect = price_text.get_rect(right=self.width - 150, centery=y_pos + self.ticker_height/2)
            display.blit(price_text, price_rect)
        
        # Draw price change
        if symbol in self.price_changes:
            change = self.price_changes[symbol]
            change_color = AppConfig.GREEN if change >= 0 else AppConfig.RED
            change_text = self._create_text_surface(
                f"{change:+.2f}%" if change >= 0 else f"{change:.2f}%",
                36,
                change_color
            )
            change_rect = change_text.get_rect(right=ticker_rect.right - 20, centery=y_pos + self.ticker_height/2)
            display.blit(change_text, change_rect) 