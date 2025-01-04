import pygame
from datetime import datetime, timedelta
import time
import math
from ..services.screen_manager import Screen

class TickerScreen(Screen):
    def __init__(self, screen_manager, crypto_api):
        super().__init__(screen_manager)
        self.crypto_api = crypto_api
        
        # Symbol management
        self.symbols = ['BTC', 'ETH']
        self.current_symbol_index = 0
        
        # Double tap detection
        self.last_tap_time = 0
        self.double_tap_threshold = 0.3  # seconds between taps
        
        # Triple tap detection
        self.triple_tap_last_time = 0
        self.triple_tap_second_time = 0
        
        # Chart settings
        self.chart_rect = pygame.Rect(0, 220, self.width, 250)
        self.chart_color = self.manager.GREEN
        self.chart_touch_margin = 10  # pixels
        
        # Touch state
        self.touch_active = False
        self.touch_x = None
        self.touch_price = None
        self.touch_date = None

    def handle_event(self, event):
        if not hasattr(event, 'x') or not hasattr(event, 'y'):
            return

        x = int(event.x * self.width)
        y = int(event.y * self.height)

        # Triple tap to switch to settings screen
        if event.type == pygame.FINGERDOWN:
            current_time = time.time()
            if current_time - self.triple_tap_last_time < self.double_tap_threshold:
                if current_time - self.triple_tap_second_time < self.double_tap_threshold:
                    self.manager.switch_to('settings')
                    self.triple_tap_second_time = 0
                    self.triple_tap_last_time = 0
                else:
                    self.triple_tap_second_time = current_time
            else:
                self.triple_tap_second_time = 0
            self.triple_tap_last_time = current_time

        # Handle double tap for symbol switching
        if event.type == pygame.FINGERDOWN:
            current_time = time.time()
            if current_time - self.last_tap_time < self.double_tap_threshold:
                if x < self.width // 2:
                    self.current_symbol_index = (self.current_symbol_index - 1) % len(self.symbols)
                else:
                    self.current_symbol_index = (self.current_symbol_index + 1) % len(self.symbols)
                self.last_tap_time = current_time
            else:
                self.last_tap_time = current_time

        # Handle chart touches
        if event.type == pygame.FINGERDOWN and self.chart_rect.collidepoint(x, y):
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
                        self.touch_active = True
                        self.touch_x = x
                        self.touch_price, self.touch_date = self._get_price_at_x(x, historical_prices)

        elif event.type == pygame.FINGERUP:
            self.touch_active = False
            self.touch_x = self.touch_price = self.touch_date = None

    def get_current_symbol(self):
        return self.symbols[self.current_symbol_index]

    def update(self, prices):
        self.current_prices = prices

    def draw(self):
        print("Drawing ticker screen")
        self.screen.fill(self.manager.BLACK)
        
        if not self.current_prices:
            print("No prices available")
            return
            
        current_symbol = self.get_current_symbol()
        price = self.current_prices.get(current_symbol)
        
        if price is None:
            print(f"No price for {current_symbol}")
            return

        print(f"Drawing price for {current_symbol}: ${price:,.2f}")
        
        # Draw price
        price_font = pygame.font.Font(None, 120)
        price_text = price_font.render(f"${price:,.2f}", True, self.manager.GREEN)
        price_rect = price_text.get_rect(left=50, y=40)
        self.screen.blit(price_text, price_rect)
        
        # Draw symbol
        symbol_font = pygame.font.Font(None, 96)
        symbol_text = symbol_font.render(current_symbol, True, self.manager.WHITE)
        symbol_rect = symbol_text.get_rect(left=50, y=120)
        self.screen.blit(symbol_text, symbol_rect)
        
        # Calculate and draw 24-hour change
        historical_prices = self.crypto_api.get_historical_prices(current_symbol)
        if historical_prices and len(historical_prices) > 4:
            current_price = historical_prices[-1]
            price_24h_ago = historical_prices[-4]
            change_percent = ((current_price - price_24h_ago) / price_24h_ago) * 100
            
            change_color = self.manager.GREEN if change_percent >= 0 else self.manager.RED
            change_text = (f"{change_percent:.2f}%" if change_percent >= 0 
                         else f"({abs(change_percent):.2f}%)")
            change_font = pygame.font.Font(None, 72)
            change_surface = change_font.render(change_text, True, change_color)
            change_rect = change_surface.get_rect(right=self.width - 50, y=40)
            self.screen.blit(change_surface, change_rect)
        
        # Draw chart
        if historical_prices:
            self._draw_chart(historical_prices)
            if all([self.touch_active, self.touch_x is not None, 
                   self.touch_price is not None, self.touch_date is not None]):
                self._draw_touch_indicator(self.touch_x, self.touch_price, self.touch_date)

    def _get_price_at_x(self, x, prices):
        if not prices:
            return None, None

        chart_x = x - self.chart_rect.left
        data_index = int(chart_x * len(prices) / self.chart_rect.width)
        
        if 0 <= data_index < len(prices):
            price = prices[data_index]
            date = datetime.now().replace(hour=0) - timedelta(days=7) + timedelta(hours=data_index * 6)
            return price, date
        return None, None

    def _draw_chart(self, prices):
        if not prices or len(prices) < 2:
            return

        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price or max_price * 0.1

        points = []
        for i, price in enumerate(prices):
            x = self.chart_rect.left + (i * self.chart_rect.width / (len(prices) - 1))
            y = self.chart_rect.bottom - ((price - min_price) * self.chart_rect.height / price_range)
            points.append((x, y))

        # Draw gradient
        gradient_height = self.height - self.chart_rect.y
        gradient_surface = pygame.Surface(
            (self.chart_rect.width, gradient_height), 
            pygame.SRCALPHA
        )
        
        for y in range(gradient_height):
            alpha = max(0, 25 * (1 - y / gradient_height))
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
        
        pygame.draw.lines(self.screen, self.chart_color, False, points, 2)

    def _draw_touch_indicator(self, x, price, date):
        if x < self.chart_rect.left or x > self.chart_rect.right:
            return

        historical_prices = self.crypto_api.get_historical_prices(self.get_current_symbol())
        if historical_prices:
            chart_x = x - self.chart_rect.left
            data_index = int(chart_x * len(historical_prices) / self.chart_rect.width)
            if 0 <= data_index < len(historical_prices):
                min_price = min(historical_prices)
                max_price = max(historical_prices)
                price_range = max_price - min_price or max_price * 0.1
                line_y = self.chart_rect.bottom - ((price - min_price) * self.chart_rect.height / price_range)

                # Draw dot
                dot_radius = 6
                pygame.draw.circle(
                    self.screen,
                    (255, 255, 255, 128),
                    (x, line_y),
                    dot_radius + 2
                )
                pygame.draw.circle(
                    self.screen,
                    self.manager.GREEN,
                    (x, line_y),
                    dot_radius
                )

        # Create tooltip
        info_font = pygame.font.Font(None, 32)
        price_text = f"${price:,.2f}"
        date_text = date.strftime("%b %-d %-I:%M %p")
        
        price_surface = info_font.render(price_text, True, self.manager.GREEN)
        date_surface = info_font.render(date_text, True, self.manager.WHITE)

        padding = 15
        box_width = max(price_surface.get_width(), date_surface.get_width()) + padding * 2
        box_height = price_surface.get_height() + date_surface.get_height() + padding * 2

        box_x = min(max(x - box_width/2, padding), self.width - box_width - padding)
        box_y = line_y - box_height - 10

        if box_y < 0:
            box_y = line_y + 10

        tooltip_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(
            tooltip_surface,
            (40, 40, 40, 230),
            (0, 0, box_width, box_height),
            border_radius=8
        )

        pygame.draw.rect(
            tooltip_surface,
            (60, 60, 60, 128),
            (0, 0, box_width, box_height),
            width=1,
            border_radius=8
        )

        tooltip_surface.blit(
            price_surface,
            (padding, padding)
        )
        tooltip_surface.blit(
            date_surface,
            (padding, padding + price_surface.get_height() + 5)
        )

        y_offset = abs(math.sin(time.time() * 2)) * 2
        self.screen.blit(tooltip_surface, (box_x, box_y + y_offset)) 