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
        
        # Hide the cursor
        pygame.mouse.set_visible(False)
        
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

        # Add touch interaction settings
        self.touch_active = False
        self.touch_price = None
        self.touch_date = None
        self.touch_x = None

        # Add touch event type mapping
        self.FINGERDOWN = 1793
        self.FINGERUP = 1794
        self.FINGERMOTION = 1792

        # Initialize touch input
        os.environ['SDL_MOUSE_TOUCH_EVENTS'] = '0'  # Disable mouse events
        os.environ['SDL_TOUCH_EVENTS_ENABLED'] = '1'  # Enable touch events

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

        # Draw the chart line and collect points for gradient
        points = []
        for i, price in enumerate(prices):
            x = self.chart_rect.left + (i * self.chart_rect.width / (len(prices) - 1))
            y = self.chart_rect.bottom - ((price - min_price) * self.chart_rect.height / price_range)
            points.append((x, y))

        if len(points) > 1:
            # Create gradient surface for the full height
            gradient_height = self.height - self.chart_rect.y
            gradient_surface = pygame.Surface(
                (self.chart_rect.width, gradient_height), 
                pygame.SRCALPHA
            )
            
            # Create gradient effect
            for y in range(gradient_height):
                alpha = max(0, 25 * (1 - y / gradient_height))  # Fade from 25 to 0
                pygame.draw.line(
                    gradient_surface,
                    (0, 255, 0, int(alpha)),
                    (0, y),
                    (self.chart_rect.width, y)
                )
            
            # Create mask surface for the chart area
            mask_surface = pygame.Surface(
                (self.chart_rect.width, gradient_height),
                pygame.SRCALPHA
            )
            
            # Adjust points for mask surface coordinates
            mask_points = [(x - self.chart_rect.left, y - self.chart_rect.y) for x, y in points]
            mask_points = mask_points + [
                (self.chart_rect.width, gradient_height),  # Bottom right
                (0, gradient_height)                       # Bottom left
            ]
            
            # Draw the mask
            pygame.draw.polygon(mask_surface, (255, 255, 255, 255), mask_points)
            
            # Apply mask to gradient
            gradient_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Draw the gradient surface onto the screen
            self.screen.blit(gradient_surface, (self.chart_rect.left, self.chart_rect.y))
            
            # Draw the main line on top
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

    def _get_price_at_x(self, x, prices):
        """Get price and date for the touched x position"""
        if not prices:
            return None, None

        # Convert x position to index in price data
        chart_x = x - self.chart_rect.left
        data_index = int(chart_x * len(prices) / self.chart_rect.width)
        
        # Ensure index is within bounds
        if 0 <= data_index < len(prices):
            price = prices[data_index]
            # Calculate date (7 days ago + index hours)
            date = datetime.now() - timedelta(days=7) + timedelta(hours=data_index)
            return price, date
        return None, None

    def _draw_touch_indicator(self, x, price, date):
        """Draw vertical line and price/date information at touch position"""
        if x < self.chart_rect.left or x > self.chart_rect.right:
            return

        # Draw vertical line
        pygame.draw.line(self.screen, self.WHITE, 
            (x, self.chart_rect.top),
            (x, self.chart_rect.bottom),
            1)

        # Format price and date
        price_text = f"${price:,.2f}"
        date_text = date.strftime("%b %d %H:%M")

        # Create text surfaces
        info_font = pygame.font.Font(None, 36)
        price_surface = info_font.render(price_text, True, self.WHITE)
        date_surface = info_font.render(date_text, True, self.WHITE)

        # Position text boxes
        padding = 10
        box_width = max(price_surface.get_width(), date_surface.get_width()) + padding * 2
        box_height = price_surface.get_height() + date_surface.get_height() + padding * 2

        # Determine box position (avoid going off screen)
        box_x = min(max(x - box_width/2, 0), self.width - box_width)
        box_y = self.chart_rect.top - box_height - padding

        # Draw background box
        pygame.draw.rect(self.screen, (40, 40, 40), 
            (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, self.WHITE, 
            (box_x, box_y, box_width, box_height), 1)

        # Draw text
        self.screen.blit(price_surface, 
            (box_x + padding, box_y + padding))
        self.screen.blit(date_surface, 
            (box_x + padding, box_y + price_surface.get_height() + padding))

    def handle_event(self, event):
        """Handle a single pygame event"""
        print(f"Display handling event: {event.type} ({event.__dict__})")  # More detailed debug
        
        # Convert touch coordinates to screen coordinates
        if hasattr(event, 'x') and hasattr(event, 'y'):
            x = int(event.x * self.width)
            y = int(event.y * self.height)
            print(f"Touch position converted: ({x}, {y})")
        else:
            print("No position data in event")
            return

        if event.type == self.FINGERDOWN:
            print(f"Touch DOWN at position: ({x}, {y})")
            self.touch_active = True
            self.touch_x = x
            historical_prices = self.crypto_api.get_historical_prices('BTC')
            self.touch_price, self.touch_date = self._get_price_at_x(x, historical_prices)
            print(f"Price at touch: ${self.touch_price:,.2f}, Date: {self.touch_date}")
            
        elif event.type == self.FINGERUP:
            print(f"Touch UP at position: ({x}, {y})")
            self.touch_active = False
            self.touch_x = None
            self.touch_price = None
            self.touch_date = None
            
        elif event.type == self.FINGERMOTION and self.touch_active:
            print(f"Touch MOTION at position: ({x}, {y})")
            self.touch_x = x
            historical_prices = self.crypto_api.get_historical_prices('BTC')
            self.touch_price, self.touch_date = self._get_price_at_x(x, historical_prices)
            print(f"Price at touch: ${self.touch_price:,.2f}, Date: {self.touch_date}")

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
                logo_rect = logo.get_rect(
                    right=self.width - 50,
                    centery=symbol_rect.centery
                )
                self.screen.blit(logo, logo_rect)
            
            # Get historical prices and draw the chart
            historical_prices = self.crypto_api.get_historical_prices(symbol)
            if historical_prices:
                self._draw_chart(historical_prices)
                
                # Draw touch indicator if active
                if self.touch_active and self.touch_price and self.touch_date:
                    print(f"Drawing indicator at x={self.touch_x} for price=${self.touch_price:,.2f}")  # Debug print
                    self._draw_touch_indicator(self.touch_x, self.touch_price, self.touch_date)

        # Update the display
        pygame.display.flip()

    def cleanup(self):
        pygame.quit() 