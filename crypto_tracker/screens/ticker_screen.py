from typing import Optional, List, Dict, Tuple
import pygame
from datetime import datetime, timedelta
import time
import math
from ..config.settings import AppConfig
from ..constants import EventTypes, ChartSettings
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
        self.symbols: List[str] = self.crypto_api.get_tracked_symbols()
        self.current_symbol_index: int = 0
        self.current_prices: Optional[Dict[str, float]] = None
        
        # Double tap detection
        self.last_tap_time: float = 0
        self.double_tap_threshold: float = AppConfig.DOUBLE_TAP_THRESHOLD
        
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
        self.chart_color = self.manager.GREEN
        self.chart_touch_margin = AppConfig.TOUCH_MARGIN
        
        # Touch state
        self.touch_active: bool = False
        self.touch_x: Optional[int] = None
        self.touch_price: Optional[float] = None
        self.touch_date: Optional[datetime] = None
        
        logger.info("TickerScreen initialized")

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events.
        
        Args:
            event: The pygame event to handle
        """
        x, y = self._scale_touch_input(event)
        logger.debug(f"Event type: {event.type}, x: {x}, y: {y}")

        # Handle swipe up for settings screen
        if event.type == EventTypes.FINGER_DOWN.value:
            logger.debug(f"Finger down at y: {y}")
            self.swipe_start_y = y
        elif event.type == EventTypes.FINGER_UP.value and self.swipe_start_y is not None:
            swipe_distance = self.swipe_start_y - y
            logger.debug(f"Swipe distance: {swipe_distance}, threshold: {self.height * self.swipe_threshold}")
            if swipe_distance > self.height * self.swipe_threshold:
                logger.info("Switching to settings screen")
                self.manager.switch_to('settings')
            self.swipe_start_y = None

        # Handle double tap for symbol switching
        if event.type == EventTypes.FINGER_DOWN.value:
            current_time = time.time()
            if current_time - self.last_tap_time < self.double_tap_threshold:
                logger.debug("Double tap detected")
                if x < self.width // 2:
                    logger.debug("Switching to previous symbol")
                    self.current_symbol_index = (self.current_symbol_index - 1) % len(self.symbols)
                else:
                    logger.debug("Switching to next symbol")
                    self.current_symbol_index = (self.current_symbol_index + 1) % len(self.symbols)
                self.last_tap_time = current_time
            else:
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

    def draw(self) -> None:
        """Draw the screen contents."""
        self.screen.fill(self.manager.BLACK)
        
        if not self.current_prices:
            return
            
        current_symbol = self.get_current_symbol()
        price = self.current_prices.get(current_symbol)
        
        if price is None:
            return

        self._draw_price(price)
        self._draw_symbol(current_symbol)
        self._draw_price_change(current_symbol)
        
        # Draw chart
        historical_prices = self.crypto_api.get_historical_prices(current_symbol)
        if historical_prices:
            self._draw_chart(historical_prices)
            if all([self.touch_active, self.touch_x is not None, 
                   self.touch_price is not None, self.touch_date is not None]):
                self._draw_touch_indicator(self.touch_x, self.touch_price, self.touch_date)

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

    def _draw_price(self, price: float) -> None:
        """
        Draw the current price.
        
        Args:
            price: The current price to display
        """
        price_text = self._create_text_surface(
            f"${price:,.2f}",
            120,
            self.manager.GREEN
        )
        price_rect = price_text.get_rect(left=50, y=40)
        self.screen.blit(price_text, price_rect)

    def _draw_symbol(self, symbol: str) -> None:
        """
        Draw the current symbol.
        
        Args:
            symbol: The symbol to display
        """
        symbol_text = self._create_text_surface(
            symbol,
            96,
            self.manager.WHITE
        )
        symbol_rect = symbol_text.get_rect(left=50, y=120)
        self.screen.blit(symbol_text, symbol_rect)

    def _draw_price_change(self, symbol: str) -> None:
        """
        Draw the 24-hour price change.
        
        Args:
            symbol: The current symbol
        """
        historical_prices = self.crypto_api.get_historical_prices(symbol)
        if historical_prices and len(historical_prices) > 4:
            current_price = historical_prices[-1]
            price_24h_ago = historical_prices[-4]
            change_percent = ((current_price - price_24h_ago) / price_24h_ago) * 100
            
            change_color = self.manager.GREEN if change_percent >= 0 else self.manager.RED
            change_text = (f"{change_percent:.2f}%" if change_percent >= 0 
                         else f"({abs(change_percent):.2f}%)")
            
            change_surface = self._create_text_surface(
                change_text,
                72,
                change_color
            )
            change_rect = change_surface.get_rect(right=self.width - 50, y=40)
            self.screen.blit(change_surface, change_rect)

    def _draw_chart(self, prices: List[float]) -> None:
        """
        Draw the price chart.
        
        Args:
            prices: List of historical prices
        """
        if not prices or len(prices) < 2:
            return

        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price or max_price * 0.1

        points = self._calculate_chart_points(prices, min_price, price_range)
        self._draw_chart_gradient(points)
        pygame.draw.lines(
            self.screen,
            self.chart_color,
            False,
            points,
            ChartSettings.LINE_WIDTH
        )

    def _calculate_chart_points(
        self,
        prices: List[float],
        min_price: float,
        price_range: float
    ) -> List[Tuple[float, float]]:
        """
        Calculate points for the chart line.
        
        Args:
            prices: List of prices
            min_price: Minimum price in the range
            price_range: Price range for scaling
            
        Returns:
            List of (x, y) coordinates for the chart line
        """
        points = []
        for i, price in enumerate(prices):
            x = self.chart_rect.left + (i * self.chart_rect.width / (len(prices) - 1))
            y = self.chart_rect.bottom - ((price - min_price) * self.chart_rect.height / price_range)
            points.append((x, y))
        return points

    def _draw_chart_gradient(self, points: List[Tuple[float, float]]) -> None:
        """
        Draw the gradient under the chart line.
        
        Args:
            points: List of chart line points
        """
        gradient_height = self.height - self.chart_rect.y
        gradient_surface = pygame.Surface(
            (self.chart_rect.width, gradient_height),
            pygame.SRCALPHA
        )
        
        for y in range(gradient_height):
            alpha = max(0, ChartSettings.GRADIENT_ALPHA_MAX * (1 - y / gradient_height))
            pygame.draw.line(
                gradient_surface,
                (0, 255, 0, int(alpha)),
                (0, y),
                (self.chart_rect.width, y)
            )
        
        mask_surface = pygame.Surface(
            (self.chart_rect.width, gradient_height),
            pygame.SRCALPHA
        )
        
        mask_points = [(x - self.chart_rect.left, y - self.chart_rect.y) for x, y in points]
        mask_points += [
            (self.chart_rect.width, gradient_height),
            (0, gradient_height)
        ]
        
        pygame.draw.polygon(mask_surface, (255, 255, 255, 255), mask_points)
        gradient_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.screen.blit(gradient_surface, (self.chart_rect.left, self.chart_rect.y))

    def _draw_touch_indicator(self, x: int, price: float, date: datetime) -> None:
        """
        Draw the touch indicator and tooltip.
        
        Args:
            x: Touch x coordinate
            price: Price at touch point
            date: Date at touch point
        """
        if x < self.chart_rect.left or x > self.chart_rect.right:
            return

        historical_prices = self.crypto_api.get_historical_prices(self.get_current_symbol())
        if historical_prices:
            self._draw_touch_dot(x, price, historical_prices)
            self._draw_touch_tooltip(x, price, date)

    def _draw_touch_dot(self, x: int, price: float, historical_prices: List[float]) -> None:
        """
        Draw the touch indicator dot.
        
        Args:
            x: Touch x coordinate
            price: Price at touch point
            historical_prices: List of historical prices
        """
        min_price = min(historical_prices)
        max_price = max(historical_prices)
        price_range = max_price - min_price or max_price * 0.1
        line_y = self.chart_rect.bottom - ((price - min_price) * self.chart_rect.height / price_range)

        pygame.draw.circle(
            self.screen,
            (255, 255, 255, 128),
            (x, line_y),
            ChartSettings.DOT_RADIUS + 2
        )
        pygame.draw.circle(
            self.screen,
            self.manager.GREEN,
            (x, line_y),
            ChartSettings.DOT_RADIUS
        )

    def _draw_touch_tooltip(self, x: int, price: float, date: datetime) -> None:
        """
        Draw the touch indicator tooltip.
        
        Args:
            x: Touch x coordinate
            price: Price at touch point
            date: Date at touch point
        """
        price_text = f"${price:,.2f}"
        date_text = date.strftime("%b %-d %-I:%M %p")
        
        price_surface = self._create_text_surface(price_text, 32, self.manager.GREEN)
        date_surface = self._create_text_surface(date_text, 32, self.manager.WHITE)

        padding = ChartSettings.TOOLTIP_PADDING
        box_width = max(price_surface.get_width(), date_surface.get_width()) + padding * 2
        box_height = price_surface.get_height() + date_surface.get_height() + padding * 2

        box_x = min(max(x - box_width/2, padding), self.width - box_width - padding)
        box_y = self.chart_rect.y - box_height - 10

        if box_y < 0:
            box_y = self.chart_rect.y + 10

        tooltip_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(
            tooltip_surface,
            (40, 40, 40, ChartSettings.TOOLTIP_ALPHA),
            (0, 0, box_width, box_height),
            border_radius=ChartSettings.TOOLTIP_BORDER_RADIUS
        )

        pygame.draw.rect(
            tooltip_surface,
            (60, 60, 60, ChartSettings.TOOLTIP_BORDER_ALPHA),
            (0, 0, box_width, box_height),
            width=1,
            border_radius=ChartSettings.TOOLTIP_BORDER_RADIUS
        )

        tooltip_surface.blit(price_surface, (padding, padding))
        tooltip_surface.blit(
            date_surface,
            (padding, padding + price_surface.get_height() + 5)
        )

        y_offset = abs(math.sin(time.time() * ChartSettings.ANIMATION_SPEED)) * ChartSettings.ANIMATION_AMPLITUDE
        self.screen.blit(tooltip_surface, (box_x, box_y + y_offset))

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