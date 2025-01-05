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
        
        logger.info("TickerScreen initialized")
    
    def update_current_coin(self):
        """Update the current coin data."""
        if not self.crypto_service or not self.crypto_service.tracked_symbols:
            self.current_coin = None
            return
            
        symbol = self.crypto_service.tracked_symbols[self.current_index]
        self.current_coin = self.crypto_service.get_coin_data(symbol)
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
        if event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            x, y = self._scale_touch_input(event)
            current_time = pygame.time.get_ticks() / 1000  # Convert to seconds
            
            # Check for double tap
            if self.last_touch_x is not None:
                time_diff = current_time - self.last_touch_time
                if time_diff < AppConfig.DOUBLE_TAP_THRESHOLD:
                    # Double tap on left side
                    if x < self.width // 2:
                        self.previous_coin()
                    # Double tap on right side
                    else:
                        self.next_coin()
            
            self.last_touch_x = x
            self.last_touch_time = current_time
            
        elif event.type == AppConfig.EVENT_TYPES['FINGER_UP']:
            self.last_touch_x = None
    
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
        price_text = f"${self.current_coin['price']:,.2f}"
        price = self.fonts['title-lg'].render(price_text, True, AppConfig.WHITE)
        price_rect = price.get_rect(left=40, top=40)
        surface.blit(price, price_rect)
        
        # Draw coin name
        name = self.fonts['light-lg'].render(self.current_coin['name'], True, AppConfig.GRAY)
        name_rect = name.get_rect(left=40, top=price_rect.bottom + 10)
        surface.blit(name, name_rect)
    
    def _draw_chart(self, surface: pygame.Surface):
        """Draw the 7-day price chart."""
        if not self.current_coin:
            return
            
        # Draw chart background
        chart_rect = pygame.Rect(0, self.chart_y, self.width, self.chart_height)
        pygame.draw.rect(surface, AppConfig.CHART_BG_COLOR, chart_rect)
        
        # Draw chart grid lines
        for i in range(6):  # 5 horizontal lines
            y = self.chart_y + (i * self.chart_height // 5)
            pygame.draw.line(surface, AppConfig.CHART_GRID_COLOR,
                           (0, y), (self.width, y), 1)
        
        for i in range(8):  # 7 vertical lines
            x = i * self.width // 7
            pygame.draw.line(surface, AppConfig.CHART_GRID_COLOR,
                           (x, self.chart_y), (x, self.height), 1)
    
    def draw(self) -> None:
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
        
        self.update_screen() 