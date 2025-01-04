from typing import Dict, Optional, List
import pygame
import os
from datetime import datetime
import requests
from ..config.settings import AppConfig
from ..constants import EventTypes, ScreenNames
from ..utils.logger import get_logger
from .base import Screen
import time
import urllib.request
from io import BytesIO

logger = get_logger(__name__)

class DashboardScreen(Screen):
    """Screen for displaying a dashboard of cryptocurrency prices and market information."""
    
    def __init__(self, screen_manager, crypto_api) -> None:
        """
        Initialize the dashboard screen.
        
        Args:
            screen_manager: The screen manager instance
            crypto_api: The crypto API service instance
        """
        super().__init__(screen_manager)
        self.crypto_api = crypto_api
        
        # Display settings
        self.header_font_size = 48
        self.ticker_font_size = 72
        self.date_font_size = 36
        self.news_font_size = 24
        self.padding = 20
        
        # Touch handling
        self.swipe_start_y: Optional[int] = None
        self.swipe_threshold: float = AppConfig.SWIPE_THRESHOLD
        self.last_tap_time: float = 0
        self.double_tap_threshold: float = AppConfig.DOUBLE_TAP_THRESHOLD
        
        # Price data
        self.current_prices: Optional[Dict[str, float]] = None
        self.price_changes: Dict[str, float] = {}
        self.ticker_items: List[Dict] = []
        
        # News data
        self.news_items: List[Dict] = []
        self.news_images: Dict[str, pygame.Surface] = {}
        self.last_news_update: float = 0
        self.news_update_interval: float = 300  # Update every 5 minutes
        
        logger.info("DashboardScreen initialized")
    
    def _update_news(self) -> None:
        """Fetch latest crypto news from CryptoCompare."""
        current_time = time.time()
        if (current_time - self.last_news_update) >= self.news_update_interval:
            try:
                url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN&sortOrder=popular"
                response = requests.get(url)
                data = response.json()
                
                if 'Data' in data:
                    self.news_items = data['Data'][:3]  # Get top 3 news items
                    logger.info(f"Fetched {len(self.news_items)} news items")
                    
                    # Load images for each news item
                    for item in self.news_items:
                        if item['imageurl'] not in self.news_images:
                            try:
                                image_response = urllib.request.urlopen(item['imageurl'])
                                image_data = BytesIO(image_response.read())
                                image = pygame.image.load(image_data)
                                # Scale image to reasonable size (e.g., 200x120)
                                image = pygame.transform.scale(image, (200, 120))
                                self.news_images[item['imageurl']] = image
                                logger.info(f"Loaded image for news item: {item['title'][:30]}...")
                            except Exception as e:
                                logger.error(f"Error loading news image: {str(e)}")
                    
                    self.last_news_update = current_time
                    logger.info("News data updated successfully")
                else:
                    logger.error(f"Unexpected API response structure: {data.keys()}")
            except Exception as e:
                logger.error(f"Error updating news: {str(e)}")
    
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
        Update the screen with new price and news data.
        
        Args:
            prices: Dictionary of current prices
        """
        self.current_prices = prices
        if prices:
            self.ticker_items = []
            for symbol in prices:
                historical_prices = self.crypto_api.get_historical_prices(symbol)
                if historical_prices and len(historical_prices) > 4:
                    current_price = historical_prices[-1]
                    price_24h_ago = historical_prices[-4]
                    change_percent = ((current_price - price_24h_ago) / price_24h_ago) * 100
                    
                    self.ticker_items.append({
                        'symbol': symbol,
                        'price': f"${prices[symbol]:,.2f}",
                        'change': f"{change_percent:+.2f}%" if change_percent >= 0 else f"{change_percent:.2f}%",
                        'color': AppConfig.GREEN if change_percent >= 0 else AppConfig.RED
                    })
        
        # Update news data
        self._update_news()
    
    def draw(self, display: pygame.Surface) -> None:
        """
        Draw the screen contents.
        
        Args:
            display: The pygame surface to draw on
        """
        display.fill(AppConfig.BLACK)
        
        if not self.ticker_items:
            return
        
        # Draw current date
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        date_text = self._create_text_surface(current_date, self.date_font_size, AppConfig.WHITE)
        date_rect = date_text.get_rect(centerx=self.width//2, top=self.padding)
        display.blit(date_text, date_rect)
        
        # Draw current time (remove leading zero from hour)
        current_time = datetime.now().strftime("%I:%M %p").lstrip("0")
        time_text = self._create_text_surface(current_time, self.date_font_size, AppConfig.WHITE)
        time_rect = time_text.get_rect(centerx=self.width//2, top=date_rect.bottom + 10)
        display.blit(time_text, time_rect)
        
        # Draw dividing line
        line_y = time_rect.bottom + self.padding
        pygame.draw.line(display, AppConfig.CELL_BORDER_COLOR, 
                        (self.padding, line_y), (self.width - self.padding, line_y), 2)
        
        # Draw tickers in a grid
        grid_top = line_y + self.padding
        grid_left = self.padding
        row_height = self.ticker_font_size + self.padding
        col_width = (self.width - (self.padding * 3)) // 2
        
        # Draw ticker items
        for i, item in enumerate(self.ticker_items):
            row = i // 2
            col = i % 2
            x = grid_left + (col * (col_width + self.padding))
            y = grid_top + (row * row_height)
            
            # Draw ticker box
            box_rect = pygame.Rect(x, y, col_width, row_height)
            pygame.draw.rect(display, AppConfig.CELL_BORDER_COLOR, box_rect, 1, border_radius=5)
            
            # Draw symbol and price
            symbol_text = self._create_text_surface(item['symbol'], self.ticker_font_size, AppConfig.WHITE)
            price_text = self._create_text_surface(item['price'], self.ticker_font_size, AppConfig.WHITE)
            change_text = self._create_text_surface(item['change'], self.ticker_font_size//2, item['color'])
            
            # Position texts
            symbol_rect = symbol_text.get_rect(left=x + 10, centery=y + row_height//2)
            price_rect = price_text.get_rect(right=x + col_width - 10, centery=y + row_height//2)
            change_rect = change_text.get_rect(centerx=price_rect.centerx, top=price_rect.bottom + 5)
            
            # Draw texts
            display.blit(symbol_text, symbol_rect)
            display.blit(price_text, price_rect)
            display.blit(change_text, change_rect)
        
        # Draw news section
        news_top = grid_top + ((len(self.ticker_items) + 1) // 2) * row_height + self.padding
        news_left = self.padding
        
        # Draw news header
        news_header = self._create_text_surface("Latest Crypto News", self.header_font_size, AppConfig.WHITE)
        header_rect = news_header.get_rect(left=news_left, top=news_top)
        display.blit(news_header, header_rect)
        
        # Draw news items
        for i, news in enumerate(self.news_items):
            news_y = header_rect.bottom + (i * 140) + self.padding
            
            # Draw news image if available
            if news['imageurl'] in self.news_images:
                image = self.news_images[news['imageurl']]
                display.blit(image, (news_left, news_y))
                text_left = news_left + 220  # Image width + padding
            else:
                text_left = news_left
            
            # Draw news title (wrap text if needed)
            title = news['title']
            title_surface = self._create_text_surface(title, self.news_font_size, AppConfig.WHITE)
            title_rect = title_surface.get_rect(left=text_left, top=news_y)
            display.blit(title_surface, title_rect) 