import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen

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
        self.crypto_service = None  # Will be set by main app
        self.last_update_time = 0  # Track when we last updated
        self.update_interval = 60  # Update every 60 seconds
        
        logger.info("TickerScreen initialized")
    
    def update_current_coin(self):
        """Update the current coin data."""
        if not self.crypto_service or not self.crypto_service.tracked_symbols:
            self.current_coin = None
            return
            
        symbol = self.crypto_service.tracked_symbols[self.current_index]
        self.current_coin = self.crypto_service.get_coin_data(symbol)
        self.last_update_time = pygame.time.get_ticks() / 1000  # Convert to seconds
        logger.info(f"Updated current coin: {symbol}")
    
    def set_crypto_service(self, service):
        """Set the crypto service and initialize first coin."""
        self.crypto_service = service
        self.update_current_coin()
    
    def next_coin(self):
        """Switch to next coin."""
        if not self.crypto_service.tracked_symbols:
            return
            
        self.current_index = (self.current_index + 1) % len(self.crypto_service.tracked_symbols)
        self.update_current_coin()
        logger.info(f"Switched to next coin: {self.current_index}")
    
    def previous_coin(self):
        """Switch to previous coin."""
        if not self.crypto_service.tracked_symbols:
            return
            
        self.current_index = (self.current_index - 1) % len(self.crypto_service.tracked_symbols)
        self.update_current_coin()
        logger.info(f"Switched to previous coin: {self.current_index}")
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        gestures = self.gesture_handler.handle_touch_event(event)
        
        if gestures['swipe_up']:
            logger.info("Swipe up detected, returning to settings")
            self.screen_manager.switch_screen('settings')
        elif gestures['swipe_down']:
            logger.info("Swipe down detected, returning to dashboard")
            self.screen_manager.switch_screen('dashboard')
        elif gestures['double_tap_left']:
            logger.info("Double tap left detected, switching to previous coin")
            self.previous_coin()
        elif gestures['double_tap_right']:
            logger.info("Double tap right detected, switching to next coin")
            self.next_coin()
    
    def _draw_price_section(self, surface: pygame.Surface):
        """Draw the price and coin info section."""
        if not self.current_coin:
            return
            
        # Load and draw coin logo
        try:
            logo_surface = pygame.image.load(self.current_coin['logo_path'])
            logo_size = 80
            logo_surface = pygame.transform.scale(logo_surface, (logo_size, logo_size))
            logo_rect = logo_surface.get_rect(
                right=self.width - 40,
                top=40
            )
            surface.blit(logo_surface, logo_rect)
        except Exception as e:
            logger.error(f"Error loading logo: {e}")
        
        # Draw price
        price_text = f"${self.current_coin['price']:.2f}"
        price = self.fonts['title-lg'].render(price_text, True, AppConfig.WHITE)
        price_rect = price.get_rect(left=40, top=40)
        surface.blit(price, price_rect)
        
        # Draw coin name
        name = self.fonts['light-lg'].render(self.current_coin['name'], True, AppConfig.GRAY)
        name_rect = name.get_rect(left=40, top=price_rect.bottom + 10)
        surface.blit(name, name_rect)
    
    def _draw_chart(self, surface: pygame.Surface):
        """Draw the 7-day price chart."""
        if not self.current_coin or not self.current_coin.get('sparkline_7d'):
            return
            
        # Get sparkline data
        prices = self.current_coin['sparkline_7d']
        
        # Calculate min and max for scaling
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        # Calculate points for the line
        points = []
        for i, price in enumerate(prices):
            # X coordinate: spread points across chart width
            x = int(i * self.width / (len(prices) - 1))
            
            # Y coordinate: scale price to chart height
            # Subtract from chart_height to flip the Y axis (pygame Y increases downward)
            normalized_price = (price - min_price) / price_range if price_range > 0 else 0.5
            y = self.chart_y + self.chart_height - int(normalized_price * self.chart_height)
            
            points.append((x, y))
        
        # Draw the line
        if len(points) > 1:
            pygame.draw.lines(surface, AppConfig.GREEN, False, points, 2)
    
    def _draw_update_countdown(self, surface: pygame.Surface):
        """Draw the countdown until next update."""
        if not self.last_update_time:
            return
            
        current_time = pygame.time.get_ticks() / 1000
        time_since_update = current_time - self.last_update_time
        seconds_until_update = max(0, int(self.update_interval - time_since_update))
        
        countdown_text = f"Next update in {seconds_until_update}s"
        countdown_surface = self.fonts['light-sm'].render(countdown_text, True, AppConfig.GRAY)
        countdown_rect = countdown_surface.get_rect(
            bottom=self.height - 20,
            right=self.width - 20
        )
        surface.blit(countdown_surface, countdown_rect)
    
    def draw(self) -> None:
        # Check if we need to update data
        current_time = pygame.time.get_ticks() / 1000
        if current_time - self.last_update_time >= self.update_interval:
            logger.debug("Auto-updating coin data")
            self.update_current_coin()
        
        # Fill background
        self.display.surface.fill(self.background_color)
        
        if not self.crypto_service.tracked_symbols:
            # Draw "No coins tracked" message
            text = self.fonts['bold-lg'].render("No coins tracked", True, AppConfig.WHITE)
            text_rect = text.get_rect(center=(self.width//2, self.height//2))
            self.display.surface.blit(text, text_rect)
        else:
            # Draw price section and chart
            self._draw_price_section(self.display.surface)
            self._draw_chart(self.display.surface)
            self._draw_update_countdown(self.display.surface)
        
        self.update_screen() 