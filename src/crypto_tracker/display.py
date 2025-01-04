import pygame
import os
import platform
from pathlib import Path
import requests
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
        chart_height = 250
        chart_y = 180
        self.chart_rect = pygame.Rect(0, chart_y, self.width, chart_height)  # Full width
        self.chart_color = self.GREEN
        self.chart_data = []
        self.max_data_points = 168  # 7 days worth of hourly points

        # Add logo settings
        self.logo_size = 72  # Size of the logo
        self.logos = {}  # Cache for loaded logos
        self.logo_path = Path("assets/logos")  # Directory to store downloaded logos
        self.logo_path.mkdir(parents=True, exist_ok=True)

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

    def _get_logo(self, symbol):
        """Download and load the coin logo"""
        if symbol in self.logos:
            return self.logos[symbol]

        logo_file = self.logo_path / f"{symbol.lower()}.png"
        
        # Mapping for CoinGecko IDs
        coingecko_ids = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'DOGE': 'dogecoin'
        }
        
        # Download logo if it doesn't exist
        if not logo_file.exists():
            try:
                # Get coin data from CoinGecko
                coin_id = coingecko_ids.get(symbol)
                if not coin_id:
                    return None
                    
                url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                
                # Get the image URL from the response
                image_url = data['image']['large']
                
                # Download the image
                img_response = requests.get(image_url)
                img_response.raise_for_status()
                
                with open(logo_file, 'wb') as f:
                    f.write(img_response.content)
            except Exception as e:
                print(f"Error downloading logo for {symbol}: {e}")
                return None

        try:
            # Load and scale the logo
            logo = pygame.image.load(str(logo_file))
            logo = pygame.transform.scale(logo, (self.logo_size, self.logo_size))
            self.logos[symbol] = logo
            return logo
        except Exception as e:
            print(f"Error loading logo for {symbol}: {e}")
            return None

    def update(self, prices):
        # Clear the screen
        self.screen.fill(self.BLACK)
        
        # Get the first symbol and price
        if prices:
            symbol, price = next(iter(prices.items()))
            
            # Left margin for text
            text_x = 50
            
            # Draw symbol (larger and left-aligned)
            symbol_font = pygame.font.Font(None, 96)
            symbol_text = symbol_font.render(symbol, True, self.WHITE)
            symbol_rect = symbol_text.get_rect(left=text_x, y=40)
            self.screen.blit(symbol_text, symbol_rect)
            
            # Draw price (larger and left-aligned)
            price_font = pygame.font.Font(None, 120)
            price_text = price_font.render(f"${price:,.2f}", True, self.GREEN)
            price_rect = price_text.get_rect(left=text_x, y=100)
            self.screen.blit(price_text, price_rect)
            
            # Load and draw logo on the right
            logo = self._get_logo(symbol)
            if logo:
                # Position logo on the right side, aligned with symbol
                logo_rect = logo.get_rect(
                    right=self.width - 50,  # 50 pixels from right edge
                    centery=symbol_rect.centery  # Centered with symbol
                )
                self.screen.blit(logo, logo_rect)
            
            # Get historical prices and draw the chart
            historical_prices = self.crypto_api.get_historical_prices(symbol)
            if historical_prices:
                self._draw_chart(historical_prices)
        
        # Update the display
        pygame.display.flip()

    def cleanup(self):
        pygame.quit() 