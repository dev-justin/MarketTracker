from typing import Optional, List, Dict, Tuple
import pygame
from datetime import datetime, timedelta
import time
import math
from ..config.settings import AppConfig
from ..constants import EventTypes, ChartSettings, ScreenNames
from ..utils.logger import get_logger
from .base import Screen

logger = get_logger(__name__)

class TickerScreen(Screen):
    """Screen for displaying cryptocurrency price information and charts."""

    def __init__(self, screen_manager, crypto_api) -> None:
        """
        Initialize the ticker screen.
        
        Args:
            screen_manager: The screen manager instance
            crypto_api: The crypto API service instance
        """
        super().__init__(screen_manager)
        self.crypto_api = crypto_api
        
        # Symbol management
        self.symbols: List[str] = crypto_api.get_tracked_symbols()
        self.current_symbol_index: int = 0
        self.current_prices: Optional[Dict[str, float]] = None
        self.price_changes: Dict[str, float] = {}
        
        # Double tap detection
        self.last_tap_time: float = 0
        self.double_tap_threshold: float = AppConfig.DOUBLE_TAP_THRESHOLD
        
        # Touch tracking
        self.last_touch_x: Optional[int] = None
        
        # Swipe detection
        self.swipe_start_y: Optional[int] = None
        self.swipe_threshold: float = AppConfig.SWIPE_THRESHOLD
        
        # Chart settings
        self.chart_rect = pygame.Rect(
            0,
            AppConfig.CHART_Y_POSITION,
            self.width,
            AppConfig.CHART_HEIGHT
        )
        self.chart_color = AppConfig.GREEN
        self.chart_touch_margin = AppConfig.TOUCH_MARGIN
        
        # Touch state
        self.touch_active: bool = False
        self.touch_x: Optional[int] = None
        self.touch_price: Optional[float] = None
        self.touch_date: Optional[datetime] = None
        
        # Initialize icon manager
        from ..utils.icon_manager import IconManager
        self.icon_manager = IconManager()

        logger.info("TickerScreen initialized")

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events.
        
        Args:
            event: The pygame event to handle
        """
        if event.type not in (EventTypes.FINGER_DOWN.value, EventTypes.FINGER_UP.value):
            return
            
        x, y = self._scale_touch_input(event)
        self.last_touch_x = x  # Store last touch position
        
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
        
        # Handle double tap to switch symbols or view
        if event.type == EventTypes.FINGER_DOWN.value:
            current_time = time.time()
            if current_time - self.last_tap_time < self.double_tap_threshold:
                logger.debug("Double tap detected")
                if y < self.height // 3:  # Top third of screen switches to dashboard view
                    logger.info("Switching to dashboard view")
                    self.manager.switch_screen(ScreenNames.DASHBOARD.value)
                else:  # Bottom two-thirds switches symbols
                    self._switch_symbol()
            self.last_tap_time = current_time
        
        # Handle chart touches
        if event.type == EventTypes.FINGER_DOWN.value and self.chart_rect.collidepoint(x, y):
            self._handle_chart_touch(x, y)
        elif event.type == EventTypes.FINGER_UP.value:
            self._handle_chart_touch_end()

    def update(self, prices: Optional[Dict[str, float]] = None) -> None:
        """
        Update the screen with new price data.
        
        Args:
            prices: Dictionary of current prices
        """
        self.current_prices = prices

    def draw(self, display: pygame.Surface) -> None:
        """
        Draw the screen contents.
        
        Args:
            display: The pygame surface to draw on
        """
        display.fill(AppConfig.BLACK)
        
        if not self.current_prices:
            return
            
        current_symbol = self.get_current_symbol()
        price = self.current_prices.get(current_symbol)
        
        if price is None:
            return

        self._draw_price(display, price)
        
        # Draw chart
        historical_prices = self.crypto_api.get_historical_prices(current_symbol)
        if historical_prices:
            self._draw_chart(display, historical_prices)
            if all([self.touch_active, self.touch_x is not None, 
                   self.touch_price is not None, self.touch_date is not None]):
                self._draw_touch_indicator(display, self.touch_x, self.touch_price, self.touch_date)

    def get_current_symbol(self) -> str:
        """Get the currently selected symbol."""
        return self.symbols[self.current_symbol_index]

    def _handle_chart_touch(self, x: int, y: int) -> None:
        """
        Handle touch events on the chart.
        
        Args:
            x: Touch x coordinate
            y: Touch y coordinate
        """
        logger.debug(f"Chart touch at x: {x}, y: {y}")
        historical_prices = self.crypto_api.get_historical_prices(self.get_current_symbol())
        if historical_prices:
            chart_x = x - self.chart_rect.left
            data_index = int(chart_x * len(historical_prices) / self.chart_rect.width)
            if 0 <= data_index < len(historical_prices):
                price = historical_prices[data_index]
                min_price = min(historical_prices)
                max_price = max(historical_prices)
                price_range = max_price - min_price or max_price * 0.1
                line_y = self.chart_rect.bottom - ((price - min_price) * self.chart_rect.height / price_range)

                if abs(y - line_y) <= self.chart_touch_margin or y > line_y:
                    logger.debug(f"Touch indicator activated at price: {price}")
                    self.touch_active = True
                    self.touch_x = x
                    self.touch_price, self.touch_date = self._get_price_at_x(x, historical_prices)

    def _handle_chart_touch_end(self) -> None:
        """Handle the end of a chart touch event."""
        if self.touch_active:
            logger.debug("Touch indicator deactivated")
        self.touch_active = False
        self.touch_x = self.touch_price = self.touch_date = None

    def _draw_price(self, display: pygame.Surface, price: float, change_24h: Optional[float] = None) -> None:
        """Draw the current price and 24h change."""
        # Draw price
        price_text = f"${price:,.2f}"
        price_surface = self._create_text(price_text, 'title-lg', AppConfig.WHITE)
        price_rect = price_surface.get_rect(left=40, top=40)
        display.blit(price_surface, price_rect)
        
        # Draw coin name
        coin_name = self.crypto_api.get_coin_name(self.symbols[self.current_symbol_index])
        if coin_name:
            name_surface = self._create_text(coin_name, 'lg', AppConfig.GRAY)
            name_rect = name_surface.get_rect(left=40, top=price_rect.bottom + 10)
            display.blit(name_surface, name_rect)
        
        # Draw 24h change if available
        if change_24h is not None:
            change_color = AppConfig.GREEN if change_24h >= 0 else AppConfig.RED
            change_text = f"{'+' if change_24h >= 0 else ''}{change_24h:.1f}%"
            change_surface = self._create_text(change_text, 'md', change_color)
            change_rect = change_surface.get_rect(left=40, top=name_rect.bottom + 10)
            display.blit(change_surface, change_rect)

    def _draw_chart(self, display: pygame.Surface, prices: List[float]) -> None:
        """Draw the price chart."""
        if not prices:
            return
            
        # Calculate chart dimensions
        chart_height = self.height - self.chart_rect.top - AppConfig.CHART_BOTTOM_MARGIN
        self.chart_rect = pygame.Rect(
            AppConfig.CHART_MARGIN,
            self.chart_rect.top,
            self.width - (AppConfig.CHART_MARGIN * 2),
            chart_height
        )
        
        # Draw chart background
        pygame.draw.rect(display, AppConfig.CHART_BG_COLOR, self.chart_rect)
        
        # Calculate price range
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        # Add 10% padding to price range
        padding = price_range * 0.1
        min_price -= padding
        max_price += padding
        price_range = max_price - min_price
        
        # Draw price axis labels
        label_margin = 10
        for i in range(5):
            price = min_price + (price_range * (i / 4))
            y = self.chart_rect.bottom - (self.chart_rect.height * (i / 4))
            
            # Draw horizontal grid line
            pygame.draw.line(
                display,
                AppConfig.CHART_GRID_COLOR,
                (self.chart_rect.left, y),
                (self.chart_rect.right, y),
                1
            )
            
            # Draw price label
            price_text = self._create_text(
                f"${price:,.0f}",
                'sm',
                AppConfig.CHART_LABEL_COLOR
            )
            text_rect = price_text.get_rect(
                right=self.chart_rect.left - label_margin,
                centery=y
            )
            display.blit(price_text, text_rect)
        
        # Draw time axis labels
        time_labels = ["1w", "6d", "5d", "4d", "3d", "2d", "1d", "Now"]
        label_width = self.chart_rect.width / (len(time_labels) - 1)
        
        for i, label in enumerate(time_labels):
            x = self.chart_rect.right - (i * label_width)
            
            # Draw vertical grid line
            pygame.draw.line(
                display,
                AppConfig.CHART_GRID_COLOR,
                (x, self.chart_rect.top),
                (x, self.chart_rect.bottom),
                1
            )
            
            # Draw time label
            time_text = self._create_text(
                label,
                'sm',
                AppConfig.CHART_LABEL_COLOR
            )
            text_rect = time_text.get_rect(
                centerx=x,
                top=self.chart_rect.bottom + label_margin
            )
            display.blit(time_text, text_rect)
        
        # Draw price line
        if len(prices) > 1:
            points = []
            for i, price in enumerate(reversed(prices)):
                x = self.chart_rect.right - (i * (self.chart_rect.width / (len(prices) - 1)))
                y = self.chart_rect.bottom - ((price - min_price) / price_range * self.chart_rect.height)
                points.append((x, y))
            
            # Draw line with anti-aliasing
            pygame.draw.aalines(
                display,
                AppConfig.CHART_LINE_COLOR,
                False,
                points
            )

    def _draw_touch_indicator(self, display: pygame.Surface, x: int, price: float, date: datetime) -> None:
        """
        Draw the touch indicator and tooltip.
        
        Args:
            display: The pygame surface to draw on
            x: Touch x coordinate
            price: Price at touch point
            date: Date at touch point
        """
        if x < self.chart_rect.left or x > self.chart_rect.right:
            return

        historical_prices = self.crypto_api.get_historical_prices(self.get_current_symbol())
        if historical_prices:
            self._draw_touch_dot(display, x, price, historical_prices)
            self._draw_touch_tooltip(display, x, price, date)

    def _draw_touch_dot(self, display: pygame.Surface, x: int, price: float, historical_prices: List[float]) -> None:
        """
        Draw the touch indicator dot.
        
        Args:
            display: The pygame surface to draw on
            x: Touch x coordinate
            price: Price at touch point
            historical_prices: List of historical prices
        """
        min_price = min(historical_prices)
        max_price = max(historical_prices)
        price_range = max_price - min_price or max_price * 0.1
        line_y = self.chart_rect.bottom - ((price - min_price) * self.chart_rect.height / price_range)

        pygame.draw.circle(
            display,
            (255, 255, 255, 128),
            (x, line_y),
            ChartSettings.DOT_RADIUS + 2
        )
        pygame.draw.circle(
            display,
            AppConfig.GREEN,
            (x, line_y),
            ChartSettings.DOT_RADIUS
        )

    def _draw_touch_tooltip(self, display: pygame.Surface, x: int, price: float, date: str) -> None:
        """Draw the tooltip that appears when touching the chart."""
        # Format price with commas and 2 decimal places
        price_text = f"${price:,.2f}"
        
        # Create text surfaces
        price_surface = self._create_text(price_text, 'md', AppConfig.GREEN)
        date_surface = self._create_text(date, 'sm', AppConfig.GRAY)
        
        # Calculate tooltip dimensions
        padding = 10
        margin = 5
        tooltip_width = max(price_surface.get_width(), date_surface.get_width()) + (padding * 2)
        tooltip_height = price_surface.get_height() + date_surface.get_height() + (padding * 2) + margin
        
        # Position tooltip above touch point
        tooltip_x = min(max(x - tooltip_width // 2, 0), self.width - tooltip_width)
        tooltip_y = self.chart_rect.top - tooltip_height - 10
        
        # Draw tooltip background
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(display, AppConfig.TOOLTIP_BG_COLOR, tooltip_rect, border_radius=5)
        pygame.draw.rect(display, AppConfig.TOOLTIP_BORDER_COLOR, tooltip_rect, 1, border_radius=5)
        
        # Draw text
        price_rect = price_surface.get_rect(
            centerx=tooltip_rect.centerx,
            top=tooltip_rect.top + padding
        )
        display.blit(price_surface, price_rect)
        
        date_rect = date_surface.get_rect(
            centerx=tooltip_rect.centerx,
            top=price_rect.bottom + margin
        )
        display.blit(date_surface, date_rect)

    def _get_price_at_x(self, x: int, prices: List[float]) -> Tuple[Optional[float], Optional[datetime]]:
        """
        Get the price and date at a specific x coordinate.
        
        Args:
            x: X coordinate
            prices: List of historical prices
            
        Returns:
            Tuple of (price, date) at the given x coordinate
        """
        if not prices:
            return None, None

        chart_x = x - self.chart_rect.left
        data_index = int(chart_x * len(prices) / self.chart_rect.width)
        
        if 0 <= data_index < len(prices):
            price = prices[data_index]
            date = datetime.now().replace(hour=0) - timedelta(days=7) + timedelta(hours=data_index * 6)
            return price, date
        return None, None 

    def _switch_symbol(self) -> None:
        """Switch to the next or previous symbol based on touch position."""
        if not self.symbols or self.last_touch_x is None:
            return
            
        if self.last_touch_x < self.width // 2:
            logger.debug("Switching to previous symbol")
            self.current_symbol_index = (self.current_symbol_index - 1) % len(self.symbols)
        else:
            logger.debug("Switching to next symbol")
            self.current_symbol_index = (self.current_symbol_index + 1) % len(self.symbols)
            
        logger.info(f"Switched to symbol: {self.symbols[self.current_symbol_index]}")

    def _draw_touch_indicators(self, display: pygame.Surface) -> None:
        """Draw touch indicators on the sides."""
        # Draw left arrow if not first symbol
        if self.current_symbol_index > 0:
            text = self._create_text("<", 'title-lg', AppConfig.GRAY)
            rect = text.get_rect(
                left=20,
                centery=self.height//2
            )
            display.blit(text, rect)
        
        # Draw right arrow if not last symbol
        if self.current_symbol_index < len(self.symbols) - 1:
            text = self._create_text(">", 'title-lg', AppConfig.GRAY)
            rect = text.get_rect(
                right=self.width - 20,
                centery=self.height//2
            )
            display.blit(text, rect)
        
        # Draw up arrow for dashboard view
        text = self._create_text("^", 'title-lg', AppConfig.GRAY)
        rect = text.get_rect(
            centerx=self.width//2,
            top=20
        )
        display.blit(text, rect) 