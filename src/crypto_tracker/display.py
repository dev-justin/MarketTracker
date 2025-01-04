import pygame
import os
import platform
from pathlib import Path
from datetime import datetime, timedelta

class Display:
    def __init__(self):
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
        self.chart_color = (100, 149, 237)  # Cornflower blue
        self.chart_data = []
        self.max_data_points = 168  # 7 days worth of hourly points

    def _draw_chart(self, prices):
        if not prices:
            return

        # Draw chart background
        pygame.draw.rect(self.screen, (20, 20, 20), self.chart_rect)
        pygame.draw.rect(self.screen, (40, 40, 40), self.chart_rect, 1)

        # Add new price point
        self.chart_data.append(prices)
        if len(self.chart_data) > self.max_data_points:
            self.chart_data.pop(0)

        if len(self.chart_data) < 2:
            return

        # Calculate min and max for scaling
        min_price = min(self.chart_data)
        max_price = max(self.chart_data)
        price_range = max_price - min_price

        # Draw price labels
        label_font = pygame.font.Font(None, 24)
        for i in range(5):
            price = min_price + (price_range * (i / 4))
            y = self.chart_rect.bottom - (i * self.chart_rect.height / 4)
            label = label_font.render(f"${price:,.2f}", True, self.WHITE)
            self.screen.blit(label, (self.chart_rect.left - 45, y - 10))

        # Draw the chart line
        points = []
        for i, price in enumerate(self.chart_data):
            x = self.chart_rect.left + (i * self.chart_rect.width / (self.max_data_points - 1))
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
            
            # Draw symbol
            symbol_font = pygame.font.Font(None, 72)
            symbol_text = symbol_font.render(symbol, True, self.WHITE)
            symbol_rect = symbol_text.get_rect(centerx=self.width//2, y=40)
            self.screen.blit(symbol_text, symbol_rect)
            
            # Draw price
            price_font = pygame.font.Font(None, 96)
            price_text = price_font.render(f"${price:,.2f}", True, self.GREEN)
            price_rect = price_text.get_rect(centerx=self.width//2, y=100)
            self.screen.blit(price_text, price_rect)
            
            # Draw the chart
            self._draw_chart(price)
        
        # Update the display
        pygame.display.flip()

    def cleanup(self):
        pygame.quit() 