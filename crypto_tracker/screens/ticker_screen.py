import pygame
import json
import os
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen
from pycoingecko import CoinGeckoAPI

logger = get_logger(__name__)

class TickerScreen(BaseScreen):
    def __init__(self, display) -> None:
        super().__init__(display)
        self.background_color = AppConfig.BLACK
        self.current_index = 0
        self.chart_height = self.height // 2  # 50% of screen height
        self.chart_y = self.height - self.chart_height
        self.last_touch_x = None
        self.last_touch_time = 0
        self.current_coin = None
        self.tracked_coins = []
        self.coin_data = {}  # Cache for coin data
        self.last_update_time = 0  # Track when we last updated
        self.update_interval = 60  # Update every 60 seconds
        self.coingecko = CoinGeckoAPI()
        
        # Load tracked coins
        self.load_tracked_coins()
        
        logger.info("TickerScreen initialized")
    
    def load_tracked_coins(self) -> None:
        """Load tracked coins from json file."""
        try:
            if os.path.exists(AppConfig.TRACKED_COINS_FILE):
                with open(AppConfig.TRACKED_COINS_FILE, 'r') as f:
                    data = json.load(f)
                    # Ensure proper data structure
                    self.tracked_coins = []
                    for item in data:
                        if isinstance(item, dict) and 'id' in item and 'symbol' in item:
                            if 'favorite' not in item:
                                item['favorite'] = False
                            self.tracked_coins.append(item)
                        elif isinstance(item, str):
                            # Convert old format to new format
                            self.tracked_coins.append({
                                'id': item.lower(),
                                'symbol': item.upper(),
                                'favorite': False
                            })
            else:
                self.tracked_coins = []
        except Exception as e:
            logger.error(f"Error loading tracked coins: {e}")
            self.tracked_coins = []
    
    def update_all_coins(self):
        """Update data for all tracked coins."""
        if not self.tracked_coins:
            return
            
        logger.info("Updating all coins with fresh data")
        try:
            # Update all coins
            for coin in self.tracked_coins:
                coin_id = coin.get('id')
                if coin_id:
                    try:
                        data = self.coingecko.get_coin_by_id(
                            coin_id,
                            localization=False,
                            tickers=False,
                            market_data=True,
                            community_data=False,
                            developer_data=False,
                            sparkline=True
                        )
                        self.coin_data[coin_id] = data
                    except Exception as e:
                        logger.error(f"Error fetching data for {coin_id}: {e}")
            
            # Reset timer after updating all coins
            self.last_update_time = pygame.time.get_ticks() / 1000
        except Exception as e:
            logger.error(f"Error updating coins: {e}")
    
    def update_current_coin(self):
        """Update the current coin data."""
        if not self.tracked_coins:
            self.current_coin = None
            return
            
        current_time = pygame.time.get_ticks() / 1000
        
        # If timer expired, update all coins
        if not self.last_update_time or (current_time - self.last_update_time >= self.update_interval):
            self.update_all_coins()
        
        # Get current coin data
        if 0 <= self.current_index < len(self.tracked_coins):
            coin = self.tracked_coins[self.current_index]
            coin_id = coin.get('id')
            if coin_id in self.coin_data:
                self.current_coin = self.coin_data[coin_id]
            else:
                self.current_coin = None
    
    def next_coin(self):
        """Switch to the next coin."""
        if self.tracked_coins:
            self.current_index = (self.current_index + 1) % len(self.tracked_coins)
            self.update_current_coin()
    
    def previous_coin(self):
        """Switch to the previous coin."""
        if self.tracked_coins:
            self.current_index = (self.current_index - 1) % len(self.tracked_coins)
            self.update_current_coin()
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        gestures = self.gesture_handler.handle_touch_event(event)
        
        if gestures['swipe_up']:
            logger.info("Swipe up detected, switching to dashboard")
            self.screen_manager.switch_screen('dashboard')
        elif gestures['swipe_down']:
            logger.info("Swipe down detected, switching to settings")
            self.screen_manager.switch_screen('settings')
        elif gestures['swipe_left']:
            logger.info("Swipe left detected, showing next coin")
            self.next_coin()
        elif gestures['swipe_right']:
            logger.info("Swipe right detected, showing previous coin")
            self.previous_coin()
    
    def _draw_price_section(self, surface: pygame.Surface):
        """Draw the price and change information."""
        if not self.current_coin:
            return
            
        try:
            # Draw coin symbol
            symbol = self.tracked_coins[self.current_index].get('symbol', '').upper()
            symbol_surface = self.fonts['title-xl'].render(symbol, True, AppConfig.WHITE)
            symbol_rect = symbol_surface.get_rect(
                centerx=self.width // 2,
                top=20
            )
            surface.blit(symbol_surface, symbol_rect)
            
            # Draw current price
            price = self.current_coin['market_data']['current_price'].get('usd', 0)
            price_text = f"${price:,.2f}"
            price_surface = self.fonts['title-lg'].render(price_text, True, AppConfig.WHITE)
            price_rect = price_surface.get_rect(
                centerx=self.width // 2,
                top=symbol_rect.bottom + 10
            )
            surface.blit(price_surface, price_rect)
            
            # Draw 24h change
            change = self.current_coin['market_data']['price_change_percentage_24h']
            change_color = AppConfig.GREEN if change >= 0 else AppConfig.RED
            change_text = f"{change:+.2f}%"
            change_surface = self.fonts['title-sm'].render(change_text, True, change_color)
            change_rect = change_surface.get_rect(
                centerx=self.width // 2,
                top=price_rect.bottom + 10
            )
            surface.blit(change_surface, change_rect)
            
        except Exception as e:
            logger.error(f"Error drawing price section: {e}")
    
    def _draw_chart(self, surface: pygame.Surface):
        """Draw the price chart."""
        if not self.current_coin:
            return
            
        try:
            # Get sparkline data
            prices = self.current_coin['market_data']['sparkline_7d']['price']
            if not prices:
                return
                
            # Calculate chart dimensions
            chart_width = self.width - (2 * AppConfig.CHART_MARGIN)
            chart_height = AppConfig.CHART_HEIGHT
            chart_rect = pygame.Rect(
                AppConfig.CHART_MARGIN,
                AppConfig.CHART_Y_POSITION,
                chart_width,
                chart_height
            )
            
            # Draw chart background
            pygame.draw.rect(surface, AppConfig.CHART_BG_COLOR, chart_rect)
            
            # Calculate price points
            min_price = min(prices)
            max_price = max(prices)
            price_range = max_price - min_price
            
            if price_range > 0:
                points = []
                for i, price in enumerate(prices):
                    x = chart_rect.left + (i * chart_width) // (len(prices) - 1)
                    y = chart_rect.bottom - ((price - min_price) * chart_height) // price_range
                    points.append((x, y))
                
                if len(points) > 1:
                    pygame.draw.lines(surface, AppConfig.CHART_LINE_COLOR, False, points, 2)
            
        except Exception as e:
            logger.error(f"Error drawing chart: {e}")
    
    def _draw_update_countdown(self, surface: pygame.Surface):
        """Draw the time until next update."""
        if self.last_update_time:
            current_time = pygame.time.get_ticks() / 1000
            time_since_update = current_time - self.last_update_time
            time_until_update = max(0, self.update_interval - time_since_update)
            countdown_text = f"Next update in {int(time_until_update)}s"
            countdown_surface = self.fonts['sm'].render(countdown_text, True, AppConfig.GRAY)
            countdown_rect = countdown_surface.get_rect(
                centerx=self.width // 2,
                bottom=self.height - 10
            )
            surface.blit(countdown_surface, countdown_rect)
    
    def draw(self) -> None:
        """Draw the ticker screen."""
        # Fill background
        self.display.surface.fill(self.background_color)
        
        if not self.tracked_coins:
            # Draw "No coins" message
            message = "No coins tracked"
            message_surface = self.fonts['title-md'].render(message, True, AppConfig.WHITE)
            message_rect = message_surface.get_rect(center=(self.width // 2, self.height // 2))
            self.display.surface.blit(message_surface, message_rect)
            
            # Draw help text
            help_text = "Swipe down for settings"
            help_surface = self.fonts['medium'].render(help_text, True, AppConfig.GRAY)
            help_rect = help_surface.get_rect(
                centerx=self.width // 2,
                top=message_rect.bottom + 20
            )
            self.display.surface.blit(help_surface, help_rect)
        else:
            # Check if we need to update data
            self.update_current_coin()
            
            # Draw price section
            self._draw_price_section(self.display.surface)
            
            # Draw chart
            self._draw_chart(self.display.surface)
            
            # Draw update countdown
            self._draw_update_countdown(self.display.surface)
        
        self.update_screen() 