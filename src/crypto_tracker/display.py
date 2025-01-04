import pygame
import os
import platform
from pathlib import Path
import requests
from datetime import datetime, timedelta

class Display:
    def __init__(self, crypto_api):
        self.crypto_api = crypto_api
        self._setup_runtime_dir()
        self._init_pygame()
        self._init_display()
        self._init_touch()

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
        
        # Chart settings
        self.chart_rect = pygame.Rect(0, 180, self.width, 250)
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
            date = datetime.now() - timedelta(days=7) + timedelta(hours=data_index)
            return price, date
        return None, None

    def _draw_touch_indicator(self, x, price, date):
        if x < self.chart_rect.left or x > self.chart_rect.right:
            return

        pygame.draw.line(self.screen, self.WHITE, 
            (x, self.chart_rect.top),
            (x, self.chart_rect.bottom),
            1)

        info_font = pygame.font.Font(None, 36)
        price_surface = info_font.render(f"${price:,.2f}", True, self.WHITE)
        date_surface = info_font.render(date.strftime("%b %d %H:%M"), True, self.WHITE)

        padding = 10
        box_width = max(price_surface.get_width(), date_surface.get_width()) + padding * 2
        box_height = price_surface.get_height() + date_surface.get_height() + padding * 2
        box_x = min(max(x - box_width/2, 0), self.width - box_width)
        box_y = self.chart_rect.top - box_height - padding

        pygame.draw.rect(self.screen, (40, 40, 40), 
            (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, self.WHITE, 
            (box_x, box_y, box_width, box_height), 1)

        self.screen.blit(price_surface, (box_x + padding, box_y + padding))
        self.screen.blit(date_surface, 
            (box_x + padding, box_y + price_surface.get_height() + padding))

    def handle_event(self, event):
        if not hasattr(event, 'x') or not hasattr(event, 'y'):
            return

        x = int(event.x * self.width)
        y = int(event.y * self.height)

        if event.type == self.FINGERDOWN:
            self.touch_active = True
            self.touch_x = x
            historical_prices = self.crypto_api.get_historical_prices('BTC')
            self.touch_price, self.touch_date = self._get_price_at_x(x, historical_prices)
        elif event.type == self.FINGERUP:
            self.touch_active = False
            self.touch_x = self.touch_price = self.touch_date = None
        elif event.type == self.FINGERMOTION and self.touch_active:
            self.touch_x = x
            historical_prices = self.crypto_api.get_historical_prices('BTC')
            self.touch_price, self.touch_date = self._get_price_at_x(x, historical_prices)

    def update(self, prices):
        self.screen.fill(self.BLACK)
        
        if prices:
            symbol, price = next(iter(prices.items()))
            
            # Draw symbol
            symbol_font = pygame.font.Font(None, 96)
            symbol_text = symbol_font.render(symbol, True, self.WHITE)
            symbol_rect = symbol_text.get_rect(left=50, y=40)
            self.screen.blit(symbol_text, symbol_rect)
            
            # Draw price
            price_font = pygame.font.Font(None, 120)
            price_text = price_font.render(f"${price:,.2f}", True, self.GREEN)
            price_rect = price_text.get_rect(left=50, y=100)
            self.screen.blit(price_text, price_rect)
            
            # Draw chart
            historical_prices = self.crypto_api.get_historical_prices(symbol)
            if historical_prices:
                self._draw_chart(historical_prices)
                if self.touch_active and self.touch_price and self.touch_date:
                    self._draw_touch_indicator(self.touch_x, self.touch_price, self.touch_date)

        pygame.display.flip()

    def cleanup(self):
        pygame.quit() 