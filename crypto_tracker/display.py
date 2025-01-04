import pygame
import os
from pathlib import Path
from datetime import datetime, timedelta
import math
import time

class Display:
    def __init__(self, crypto_api):
        self.crypto_api = crypto_api
        self._setup_runtime_dir()
        self._init_pygame()
        self._init_display()
        self._init_touch()
        
        # Add symbol management
        self.symbols = ['BTC', 'ETH']
        self.current_symbol_index = 0
        
        # Double tap detection
        self.last_tap_time = 0
        self.double_tap_threshold = 0.3  # seconds between taps
        self.tap_area_left = pygame.Rect(0, 0, self.width // 2, 180)  # Left half
        self.tap_area_right = pygame.Rect(self.width // 2, 0, self.width // 2, 180)  # Right half
        
        # Define touch margin for chart line
        self.chart_touch_margin = 10  # pixels

    def _setup_runtime_dir(self):
        if os.geteuid() == 0:
            uid = int(os.environ.get('SUDO_UID', 1000))
            runtime_dir = f"/run/user/{uid}"
            os.environ['XDG_RUNTIME_DIR'] = runtime_dir
            Path(runtime_dir).mkdir(parents=True, exist_ok=True)
            os.chmod(runtime_dir, 0o700)
            os.chown(runtime_dir, uid, uid)

    def _init_pygame(self):
        pygame.init()
        pygame.mouse.set_visible(False)
        os.putenv('SDL_VIDEODRIVER', 'fbcon')
        os.putenv('SDL_FBDEV', '/dev/fb0')

    def _init_display(self):
        self.width = 800
        self.height = 480
        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            pygame.FULLSCREEN | pygame.NOFRAME | pygame.HWSURFACE
        )
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        
        # Chart settings
        self.chart_rect = pygame.Rect(0, 220, self.width, 250)
        self.chart_color = self.GREEN

    def _init_touch(self):
        self.touch_active = False
        self.touch_price = None
        self.touch_date = None
        self.touch_x = None
        
        os.environ['SDL_MOUSE_TOUCH_EVENTS'] = '0'
        os.environ['SDL_TOUCH_EVENTS_ENABLED'] = '1'
        
        self.FINGERDOWN = 1793
        self.FINGERUP = 1794
        self.FINGERMOTION = 1792

    def _draw_chart(self, prices):
        if not prices or len(prices) < 2:
            return

        pygame.draw.rect(self.screen, self.BLACK, self.chart_rect)

        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price or max_price * 0.1

        if price_range == 0:
            price_range = max_price * 0.1
            min_price = max_price - price_range
            max_price = max_price + price_range

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

    def _get_price_at_x(self, x, prices):
        if not prices:
            return None, None

        chart_x = x - self.chart_rect.left
        data_index = int(chart_x * len(prices) / self.chart_rect.width)
        
        if 0 <= data_index < len(prices):
            price = prices[data_index]
            # Calculate local time
            date = datetime.now().replace(hour=0) - timedelta(days=7) + timedelta(hours=data_index * 6)
            return price, date
        return None, None

    def _draw_touch_indicator(self, x, price, date):
        if x < self.chart_rect.left or x > self.chart_rect.right:
            return

        # Draw vertical line with gradient alpha
        line_surface = pygame.Surface((1, self.chart_rect.height), pygame.SRCALPHA)
        for y in range(self.chart_rect.height):
            alpha = 255 * (1 - y / self.chart_rect.height)
            pygame.draw.line(
                line_surface,
                (*self.WHITE[:3], int(alpha)),
                (0, y),
                (0, y)
            )
        self.screen.blit(line_surface, (x, self.chart_rect.top))

        # Create tooltip content
        info_font = pygame.font.Font(None, 32)
        price_text = f"${price:,.2f}"
        date_text = date.strftime("%b %-d %-I:%M %p")
        
        price_surface = info_font.render(price_text, True, self.GREEN)
        date_surface = info_font.render(date_text, True, self.WHITE)

        # Calculate tooltip dimensions
        padding = 15
        box_width = max(price_surface.get_width(), date_surface.get_width()) + padding * 2
        box_height = price_surface.get_height() + date_surface.get_height() + padding * 2

        # Position tooltip
        box_x = min(max(x - box_width/2, padding), self.width - box_width - padding)
        box_y = self.chart_rect.top - box_height - 20

        # Draw tooltip background with rounded corners
        tooltip_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(
            tooltip_surface,
            (40, 40, 40, 230),  # Semi-transparent dark background
            (0, 0, box_width, box_height),
            border_radius=8
        )

        # Add subtle border glow
        pygame.draw.rect(
            tooltip_surface,
            (60, 60, 60, 128),
            (0, 0, box_width, box_height),
            width=1,
            border_radius=8
        )

        # Position and draw text
        tooltip_surface.blit(
            price_surface,
            (padding, padding)
        )
        tooltip_surface.blit(
            date_surface,
            (padding, padding + price_surface.get_height() + 5)
        )

        # Draw tooltip with a slight vertical animation based on touch position
        y_offset = abs(math.sin(time.time() * 2)) * 2  # Subtle float effect
        self.screen.blit(tooltip_surface, (box_x, box_y + y_offset))

    def get_current_symbol(self):
        return self.symbols[self.current_symbol_index]

    def handle_event(self, event):
        if not hasattr(event, 'x') or not hasattr(event, 'y'):
            return

        x = int(event.x * self.width)
        y = int(event.y * self.height)

        # Handle double tap in the top area
        if event.type == self.FINGERDOWN:
            current_time = time.time()
            if current_time - self.last_tap_time < self.double_tap_threshold:
                if self.tap_area_left.collidepoint(x, y):
                    # Double tap on left, switch to previous symbol
                    self.current_symbol_index = (self.current_symbol_index - 1) % len(self.symbols)
                elif self.tap_area_right.collidepoint(x, y):
                    # Double tap on right, switch to next symbol
                    self.current_symbol_index = (self.current_symbol_index + 1) % len(self.symbols)
            self.last_tap_time = current_time

        # Handle chart touches
        if event.type == self.FINGERDOWN and self.chart_rect.collidepoint(x, y):
            historical_prices = self.crypto_api.get_historical_prices(self.get_current_symbol())
            if historical_prices:
                # Calculate the y position of the chart line at the touch x
                chart_x = x - self.chart_rect.left
                data_index = int(chart_x * len(historical_prices) / self.chart_rect.width)
                if 0 <= data_index < len(historical_prices):
                    price = historical_prices[data_index]
                    min_price = min(historical_prices)
                    max_price = max(historical_prices)
                    price_range = max_price - min_price or max_price * 0.1
                    line_y = self.chart_rect.bottom - ((price - min_price) * self.chart_rect.height / price_range)

                    # Check if touch is within margin of the line OR below the line
                    if abs(y - line_y) <= self.chart_touch_margin or y > line_y:
                        self.touch_active = True
                        self.touch_x = x
                        self.touch_price, self.touch_date = self._get_price_at_x(x, historical_prices)

        elif event.type == self.FINGERUP:
            self.touch_active = False
            self.touch_x = self.touch_price = self.touch_date = None

    def update(self, prices):
        self.screen.fill(self.BLACK)
        
        if prices:
            current_symbol = self.get_current_symbol()
            price = prices.get(current_symbol)
            
            if price is None:
                return

            # Draw price (on top)
            price_font = pygame.font.Font(None, 120)
            price_text = price_font.render(f"${price:,.2f}", True, self.GREEN)
            price_rect = price_text.get_rect(left=50, y=40)
            self.screen.blit(price_text, price_rect)
            
            # Draw symbol (below price)
            symbol_font = pygame.font.Font(None, 96)
            symbol_text = symbol_font.render(current_symbol, True, self.WHITE)
            symbol_rect = symbol_text.get_rect(left=50, y=120)
            self.screen.blit(symbol_text, symbol_rect)
            
            # Calculate 24-hour change
            historical_prices = self.crypto_api.get_historical_prices(current_symbol)
            if historical_prices and len(historical_prices) > 4:  # Ensure we have enough data
                current_price = historical_prices[-1]
                # Get the price 24 hours ago (4 intervals of 6 hours = 24 hours)
                price_24h_ago = historical_prices[-4]
                change_percent = ((current_price - price_24h_ago) / price_24h_ago) * 100
                
                # Draw 24-hour change
                change_color = self.GREEN if change_percent >= 0 else self.RED
                # Format: positive without brackets, negative with brackets
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

        pygame.display.flip()

    def cleanup(self):
        pygame.quit() 