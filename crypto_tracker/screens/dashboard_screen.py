from typing import Dict, Optional, List
import pygame
import os
from datetime import datetime
import pytz
from ..config.settings import AppConfig
from ..constants import EventTypes, ScreenNames
from ..utils.logger import get_logger
from .base import Screen
import time
from ..utils.icon_manager import IconManager

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
        
        # Get local timezone
        self.local_tz = pytz.timezone('America/Vancouver')
        try:
            with open('/etc/timezone') as f:
                system_tz = f.read().strip()
                self.local_tz = pytz.timezone(system_tz)
                logger.info(f"Using system timezone: {system_tz}")
        except:
            logger.warning("Could not detect system timezone, using default: America/Vancouver")
        
        # Display settings
        self.padding = 20
        
        # Load custom fonts
        try:
            # Create fonts using settings
            self.date_font = pygame.font.Font(AppConfig.FONT_PATHS['light'], AppConfig.FONT_SIZES['date'])
            self.time_font = pygame.font.Font(AppConfig.FONT_PATHS['bold'], AppConfig.FONT_SIZES['time'])
            self.coin_font = pygame.font.Font(AppConfig.FONT_PATHS['semibold'], AppConfig.FONT_SIZES['coin_name'])
            self.price_font = pygame.font.Font(AppConfig.FONT_PATHS['bold'], AppConfig.FONT_SIZES['price'])
            self.label_font = pygame.font.Font(AppConfig.FONT_PATHS['regular'], AppConfig.FONT_SIZES['label'])
            
            logger.info("Custom fonts loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load custom fonts, falling back to default: {e}")
            # Fallback to default fonts
            self.date_font = pygame.font.Font(None, AppConfig.FONT_SIZES['date'])
            self.time_font = pygame.font.Font(None, AppConfig.FONT_SIZES['time'])
            self.coin_font = pygame.font.Font(None, AppConfig.FONT_SIZES['coin_name'])
            self.price_font = pygame.font.Font(None, AppConfig.FONT_SIZES['price'])
            self.label_font = pygame.font.Font(None, AppConfig.FONT_SIZES['label'])
        
        # Background gradient colors
        self.gradient_top = (13, 17, 23)     # Dark navy
        self.gradient_bottom = (22, 27, 34)  # Slightly lighter navy
        
        # Touch handling
        self.swipe_start_y = None
        self.swipe_threshold = AppConfig.SWIPE_THRESHOLD
        self.last_tap_time = 0
        self.double_tap_threshold = AppConfig.DOUBLE_TAP_THRESHOLD
        
        # Price data
        self.current_prices = None
        self.price_changes = {}
        self.ticker_items = []
        
        # Initialize icon manager
        self.icon_manager = IconManager()
        
        logger.info("DashboardScreen initialized")
    
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
            self.ticker_items = []
            for symbol in prices:
                historical_prices = self.crypto_api.get_historical_prices(symbol)
                if historical_prices and len(historical_prices) > 4:
                    current_price = historical_prices[-1]
                    price_24h_ago = historical_prices[-4]
                    change_percent = ((current_price - price_24h_ago) / price_24h_ago) * 100
                    
                    # Map symbols to full names
                    full_names = {
                        'BTC': 'Bitcoin',
                        'ETH': 'Ethereum',
                        'LTC': 'Litecoin',
                        'DOGE': 'Dogecoin',
                        'XRP': 'Ripple',
                        'ADA': 'Cardano',
                        'DOT': 'Polkadot',
                        'SOL': 'Solana',
                        'MATIC': 'Polygon',
                        'LINK': 'Chainlink'
                    }
                    
                    self.ticker_items.append({
                        'symbol': symbol,
                        'name': full_names.get(symbol, symbol),
                        'price': f"${prices[symbol]:,.2f}",
                        'change': f"{change_percent:+.2f}%",
                        'color': AppConfig.GREEN if change_percent >= 0 else AppConfig.RED
                    })
    
    def _create_date_text(self, text: str, color: tuple) -> pygame.Surface:
        """Create text surface using the non-bold date font."""
        return self.date_font.render(text, True, color)
    
    def _create_gradient_background(self, surface: pygame.Surface) -> None:
        """Create a vertical gradient background."""
        height = surface.get_height()
        for y in range(height):
            # Calculate color for this line
            factor = y / height
            r = self.gradient_top[0] + (self.gradient_bottom[0] - self.gradient_top[0]) * factor
            g = self.gradient_top[1] + (self.gradient_bottom[1] - self.gradient_top[1]) * factor
            b = self.gradient_top[2] + (self.gradient_bottom[2] - self.gradient_top[2]) * factor
            color = (int(r), int(g), int(b))
            
            # Draw a line of the calculated color
            pygame.draw.line(surface, color, (0, y), (surface.get_width(), y))
    
    def _create_price_text(self, text: str, color: tuple) -> pygame.Surface:
        """Create text surface using the price font."""
        return self.price_font.render(text, True, color)
    
    def _create_coin_text(self, text: str, color: tuple) -> pygame.Surface:
        """Create text surface using the coin font."""
        return self.coin_font.render(text, True, color)
    
    def _create_label_text(self, text: str, color: tuple) -> pygame.Surface:
        """Create text surface using the label font."""
        return self.label_font.render(text, True, color)
    
    def _create_time_text(self, text: str, color: tuple) -> pygame.Surface:
        """Create text surface using the time font."""
        return self.time_font.render(text, True, color)
    
    def draw(self, display: pygame.Surface) -> None:
        """Draw the screen contents."""
        self._create_gradient_background(display)
        
        if not self.ticker_items:
            return
        
        # Draw date and time at top
        current_date = datetime.now(self.local_tz).strftime("%A, %b %-d")
        date_text = self._create_date_text(current_date, AppConfig.WHITE)
        date_rect = date_text.get_rect(centerx=self.width//2, top=self.padding)
        display.blit(date_text, date_rect)
        
        current_time = datetime.now(self.local_tz).strftime("%I:%M %p").lstrip("0")
        time_text = self._create_time_text(current_time, AppConfig.WHITE)
        time_rect = time_text.get_rect(centerx=self.width//2, top=date_rect.bottom + 10)
        display.blit(time_text, time_rect)
        
        # Draw tickers in a grid (2 columns)
        start_y = time_rect.bottom + self.padding * 2
        card_height = 80
        card_spacing = 10
        card_width = (self.width - (self.padding * 3)) // 2  # 3 paddings: left, middle, right
        arrow_size = 12  # Size of the arrow indicator
        
        for i, item in enumerate(self.ticker_items):
            # Calculate grid position
            row = i // 2
            col = i % 2
            
            # Calculate card position
            card_rect = pygame.Rect(
                self.padding + (col * (card_width + self.padding)),
                start_y + (row * (card_height + card_spacing)),
                card_width,
                card_height
            )
            
            # Draw card background
            pygame.draw.rect(display, (30, 35, 42), card_rect, border_radius=15)
            
            # Get and draw coin icon
            icon = self.icon_manager.get_icon(item['symbol'])
            icon_x = card_rect.left + 15
            icon_y = card_rect.top + (card_height - AppConfig.ICON_SIZE) // 2
            
            if icon:
                display.blit(icon, (icon_x, icon_y))
                text_left = icon_x + AppConfig.ICON_SIZE + 10
            else:
                text_left = icon_x
            
            # Draw coin name and symbol
            name_text = self._create_coin_text(item['name'], AppConfig.WHITE)
            symbol_text = self._create_label_text(item['symbol'], (128, 128, 128))
            
            name_rect = name_text.get_rect(
                left=text_left,
                centery=card_rect.centery - 10
            )
            symbol_rect = symbol_text.get_rect(
                left=text_left,
                top=name_rect.bottom + 5
            )
            
            display.blit(name_text, name_rect)
            display.blit(symbol_text, symbol_rect)
            
            # Draw price and change percentage with arrow
            price_text = self._create_price_text(item['price'], AppConfig.WHITE)
            change_text = self._create_label_text(item['change'], item['color'])
            
            # Position price at the right
            price_rect = price_text.get_rect(
                right=card_rect.right - 15,
                centery=card_rect.centery - 10
            )
            
            # Draw arrow and change percentage
            is_positive = item['color'] == AppConfig.GREEN
            arrow_x = price_rect.right - 100  # Position arrow
            arrow_y = price_rect.centery + 25
            
            # Draw arrow
            if is_positive:
                # Draw up arrow
                points = [
                    (arrow_x + arrow_size//2, arrow_y - arrow_size//2),  # Top point
                    (arrow_x, arrow_y + arrow_size//2),  # Bottom left
                    (arrow_x + arrow_size, arrow_y + arrow_size//2)  # Bottom right
                ]
            else:
                # Draw down arrow
                points = [
                    (arrow_x, arrow_y - arrow_size//2),  # Top left
                    (arrow_x + arrow_size, arrow_y - arrow_size//2),  # Top right
                    (arrow_x + arrow_size//2, arrow_y + arrow_size//2)  # Bottom point
                ]
            
            pygame.draw.polygon(display, item['color'], points)
            
            # Position change percentage after arrow
            change_rect = change_text.get_rect(
                left=arrow_x + arrow_size + 10,
                centery=arrow_y
            )
            
            display.blit(price_text, price_rect)
            display.blit(change_text, change_rect) 