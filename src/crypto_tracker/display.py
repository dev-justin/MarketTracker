import pygame
import os
import platform
from pathlib import Path
from datetime import datetime, timedelta

class Display:
    def __init__(self, crypto_api):
        self.crypto_api = crypto_api
        # Set up XDG_RUNTIME_DIR if running with sudo
        if os.geteuid() == 0:  # Check if running as root/sudo
            uid = int(os.environ.get('SUDO_UID', 1000))
            runtime_dir = f"/run/user/{uid}"
            os.environ['XDG_RUNTIME_DIR'] = runtime_dir
            
            # Create directory if it doesn't exist
            Path(runtime_dir).mkdir(parents=True, exist_ok=True)
            os.chmod(runtime_dir, 0o700)
            os.chown(runtime_dir, uid, uid)

        # Initialize pygame
        pygame.init()
        
        # Set up the display for Raspberry Pi
        os.putenv('SDL_VIDEODRIVER', 'fbcon')  # Tell SDL to use the framebuffer
        os.putenv('SDL_FBDEV', '/dev/fb0')     # Set the framebuffer device
        
        # Set up the display
        # Using your display's resolution
        self.width = 800
        self.height = 480
        
        # Initialize the display with no window manager
        if platform.machine() == 'armv7l':  # Check if we're on Raspberry Pi
            self.screen = pygame.display.set_mode(
                (self.width, self.height),
                pygame.FULLSCREEN | pygame.NOFRAME | pygame.HWSURFACE
            )
        else:
            self.screen = pygame.display.set_mode((self.width, self.height))
            
        pygame.display.set_caption("Crypto Tracker")
        
        # Set up fonts
        self.font = pygame.font.Font(None, 36)
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)

        # Add chart settings
        self.chart_rect = pygame.Rect(50, 180, 700, 250)  # x, y, width, height
        self.chart_color = self.GREEN  # Changed to green
        self.chart_data = []
        self.max_data_points = 168  # 7 days worth of hourly points

    def _draw_chart(self, prices):
        if not prices:
            return

        # Draw chart background (just black, no grid)
        pygame.draw.rect(self.screen, self.BLACK, self.chart_rect)

        # Calculate min and max for scaling
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price

        # Handle case where all prices are the same
        if price_range == 0:
            price_range = max_price * 0.1
            min_price = max_price - price_range
            max_price = max_price + price_range

        # Draw the chart line
        points = []
        for i, price in enumerate(prices):
            x = self.chart_rect.left + (i * self.chart_rect.width / (len(prices) - 1))
            y = self.chart_rect.bottom - ((price - min_price) * self.chart_rect.height / price_range)
            points.append((x, y))

        if len(points) > 1:
            pygame.draw.lines(self.screen, self.chart_color, False, points, 2)

    def update(self, prices):
        # Clear the screen
        self.screen.fill(self.BLACK)
        
        # Get the first symbol and price
        if prices:
            symbol, price = next(iter(prices.items()))
            
            # Draw symbol (larger and left-aligned)
            symbol_font = pygame.font.Font(None, 96)  # Increased size
            symbol_text = symbol_font.render(symbol, True, self.WHITE)
            symbol_rect = symbol_text.get_rect(left=50, y=40)  # Left aligned
            self.screen.blit(symbol_text, symbol_rect)
            
            # Draw price (larger and left-aligned)
            price_font = pygame.font.Font(None, 120)  # Increased size
            price_text = price_font.render(f"${price:,.2f}", True, self.GREEN)
            price_rect = price_text.get_rect(left=50, y=100)  # Left aligned
            self.screen.blit(price_text, price_rect)
            
            # Get historical prices and draw the chart
            historical_prices = self.crypto_api.get_historical_prices(symbol)
            if historical_prices:
                self._draw_chart(historical_prices)
        
        # Update the display
        pygame.display.flip()

    def cleanup(self):
        pygame.quit() 