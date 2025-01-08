"""Screen for displaying detailed coin information."""

import pygame
import os
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen

logger = get_logger(__name__)

def catmull_rom(p0, p1, p2, p3, t):
    """Calculate point on a Catmull-Rom spline."""
    t2 = t * t
    t3 = t2 * t
    
    # Catmull-Rom matrix coefficients
    a = -0.5 * t3 + t2 - 0.5 * t
    b = 1.5 * t3 - 2.5 * t2 + 1.0
    c = -1.5 * t3 + 2.0 * t2 + 0.5 * t
    d = 0.5 * t3 - 0.5 * t2
    
    # Interpolate x and y separately
    x = a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0]
    y = a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]
    
    return (int(x), int(y))

class TickerScreen(BaseScreen):
    """Screen for displaying detailed coin information."""
    
    def __init__(self, display) -> None:
        """Initialize the ticker screen."""
        super().__init__(display)
        self.background_color = (13, 13, 13)  # Darker black for more contrast
        self.current_index = 0
        self.coins = []
        
        # Sparkline dimensions
        self.sparkline_height = int(self.height * 0.6)  # 60% of screen height
        self.sparkline_padding = 20  # Add padding from bottom
        
        # Ticker selector state
        self.showing_selector = False
        self.selector_start_time = 0
        self.selector_scroll_offset = 0  # Horizontal scroll offset for selector
        
        # Load initial coin data
        self.refresh_coins()
        
        logger.info("TickerScreen initialized")
    
    def refresh_coins(self):
        """Refresh the list of tracked coins with current data."""
        self.coins = self.crypto_manager.get_tracked_coins()
        if self.coins and self.current_index >= len(self.coins):
            self.current_index = 0
    
    def next_coin(self):
        """Switch to next coin."""
        if self.coins:
            self.current_index = (self.current_index + 1) % len(self.coins)
    
    def previous_coin(self):
        """Switch to previous coin."""
        if self.coins:
            self.current_index = (self.current_index - 1) % len(self.coins)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        gestures = self.gesture_handler.handle_touch_event(event)
        
        if event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            x, y = self._scale_touch_input(event)
            
            if self.showing_selector:
                # Define the same layout parameters as in draw_ticker_selector
                logo_size = 60
                spacing = 25
                crypto_section_y = self.height * 0.25
                stock_section_y = self.height * 0.65
                
                # Split coins into sections
                cryptos = [coin for coin in self.coins if coin.get('type', '') != 'stock']
                stocks = [coin for coin in self.coins if coin.get('type', '') == 'stock']
                
                # Check crypto section
                if cryptos:
                    row_width = self.width - 80
                    logos_per_row = max(1, (row_width + spacing) // (logo_size + spacing))
                    
                    for i, coin in enumerate(cryptos):
                        row = i // logos_per_row
                        col = i % logos_per_row
                        
                        logo_x = 40 + col * (logo_size + spacing)
                        logo_y = crypto_section_y + row * (logo_size + spacing)
                        
                        # Include symbol text height in clickable area
                        logo_rect = pygame.Rect(logo_x, logo_y, logo_size, logo_size + 30)
                        
                        if logo_rect.collidepoint(x, y):
                            self.current_index = self.coins.index(coin)
                            self.showing_selector = False
                            self.needs_redraw = True
                            return
                
                # Check stock section
                if stocks:
                    row_width = self.width - 80
                    logos_per_row = max(1, (row_width + spacing) // (logo_size + spacing))
                    
                    for i, coin in enumerate(stocks):
                        row = i // logos_per_row
                        col = i % logos_per_row
                        
                        logo_x = 40 + col * (logo_size + spacing)
                        logo_y = stock_section_y + row * (logo_size + spacing)
                        
                        # Include symbol text height in clickable area
                        logo_rect = pygame.Rect(logo_x, logo_y, logo_size, logo_size + 30)
                        
                        if logo_rect.collidepoint(x, y):
                            self.current_index = self.coins.index(coin)
                            self.showing_selector = False
                            self.needs_redraw = True
                            return
                
                # Hide selector if clicked outside
                self.showing_selector = False
                self.needs_redraw = True
        
        if not self.showing_selector:
            if gestures['swipe_up']:
                logger.info("Swipe up detected, returning to dashboard")
                self.screen_manager.switch_screen('dashboard')
            elif gestures['swipe_left']:
                logger.info("Swipe left detected, showing next coin")
                self.next_coin()
                self.needs_redraw = True
            elif gestures['swipe_right']:
                logger.info("Swipe right detected, showing previous coin")
                self.previous_coin()
                self.needs_redraw = True
            elif gestures['long_press']:
                logger.info("Long press detected, showing selector")
                self.showing_selector = True
                self.needs_redraw = True
    
    def draw_ticker_selector(self):
        """Draw the ticker selector overlay."""
        if not self.showing_selector:
            return
            
        # Create semi-transparent dark overlay for background
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 230))  # Very dark, almost black background
        self.display.surface.blit(overlay, (0, 0))
        
        # Define sizes and spacing
        logo_size = 60
        spacing = 25
        section_spacing = 60
        
        # Split coins into crypto and stocks
        cryptos = [coin for coin in self.coins if coin.get('type', '') != 'stock']
        stocks = [coin for coin in self.coins if coin.get('type', '') == 'stock']
        
        # Calculate layout
        crypto_section_y = self.height * 0.25  # Start crypto section at 25% of screen height
        stock_section_y = self.height * 0.65   # Start stock section at 65% of screen height
        
        # Draw section headers
        header_font = self.display.get_title_font('md', 'bold')
        label_font = self.display.get_text_font('sm', 'regular')
        
        # Crypto section
        if cryptos:
            # Draw "CRYPTO" header
            header_surface = header_font.render("CRYPTO", True, AppConfig.WHITE)
            header_rect = header_surface.get_rect(
                left=40,
                bottom=crypto_section_y - 20
            )
            self.display.surface.blit(header_surface, header_rect)
            
            # Draw crypto count
            count_text = f"{len(cryptos)} {'asset' if len(cryptos) == 1 else 'assets'}"
            count_surface = label_font.render(count_text, True, (128, 128, 128))
            count_rect = count_surface.get_rect(
                left=header_rect.right + 15,
                centery=header_rect.centery
            )
            self.display.surface.blit(count_surface, count_rect)
            
            # Draw crypto logos
            row_width = self.width - 80  # 40px padding on each side
            logos_per_row = max(1, (row_width + spacing) // (logo_size + spacing))
            
            for i, coin in enumerate(cryptos):
                row = i // logos_per_row
                col = i % logos_per_row
                
                x = 40 + col * (logo_size + spacing)
                y = crypto_section_y + row * (logo_size + spacing)
                
                self._draw_selector_item(coin, x, y, logo_size)
        
        # Stock section
        if stocks:
            # Draw "STOCKS" header
            header_surface = header_font.render("STOCKS", True, AppConfig.WHITE)
            header_rect = header_surface.get_rect(
                left=40,
                bottom=stock_section_y - 20
            )
            self.display.surface.blit(header_surface, header_rect)
            
            # Draw stock count
            count_text = f"{len(stocks)} {'asset' if len(stocks) == 1 else 'assets'}"
            count_surface = label_font.render(count_text, True, (128, 128, 128))
            count_rect = count_surface.get_rect(
                left=header_rect.right + 15,
                centery=header_rect.centery
            )
            self.display.surface.blit(count_surface, count_rect)
            
            # Draw stock logos
            row_width = self.width - 80  # 40px padding on each side
            logos_per_row = max(1, (row_width + spacing) // (logo_size + spacing))
            
            for i, coin in enumerate(stocks):
                row = i // logos_per_row
                col = i % logos_per_row
                
                x = 40 + col * (logo_size + spacing)
                y = stock_section_y + row * (logo_size + spacing)
                
                self._draw_selector_item(coin, x, y, logo_size)
    
    def _draw_selector_item(self, coin, x, y, size):
        """Draw a single item in the selector with logo and hover effects."""
        is_current = coin == self.coins[self.current_index]
        logo_path = os.path.join(AppConfig.CACHE_DIR, f"{coin['symbol'].lower()}_logo.png")
        
        if os.path.exists(logo_path):
            try:
                # Create background for logo
                bg_rect = pygame.Rect(x, y, size, size)
                if is_current:
                    # Draw glow effect for current ticker
                    glow_surface = pygame.Surface((size + 20, size + 20), pygame.SRCALPHA)
                    for radius in range(10, 0, -2):
                        alpha = int(60 * (radius / 10))
                        pygame.draw.circle(glow_surface, (255, 255, 255, alpha), 
                                        (size//2 + 10, size//2 + 10), size//2 + radius)
                    self.display.surface.blit(glow_surface, (x - 10, y - 10))
                
                # Draw subtle background for logo
                pygame.draw.rect(self.display.surface, (30, 30, 30), bg_rect, border_radius=15)
                
                # Draw logo
                logo = pygame.image.load(logo_path)
                logo = pygame.transform.scale(logo, (size - 20, size - 20))
                logo_rect = logo.get_rect(center=bg_rect.center)
                self.display.surface.blit(logo, logo_rect)
                
                # Draw symbol below logo
                symbol_font = self.display.get_text_font('sm', 'regular')
                symbol_surface = symbol_font.render(coin['symbol'].upper(), True, (200, 200, 200))
                symbol_rect = symbol_surface.get_rect(
                    centerx=bg_rect.centerx,
                    top=bg_rect.bottom + 8
                )
                self.display.surface.blit(symbol_surface, symbol_rect)
                
            except Exception as e:
                logger.error(f"Error drawing selector item: {e}")
    
    def draw(self) -> None:
        """Draw the ticker screen."""
        if not self.coins:
            return
            
        current_coin = self.coins[self.current_index]
        
        # Fill background
        self.display.surface.fill(self.background_color)
        
        # If selector is showing, only draw it and return
        if self.showing_selector:
            self.draw_ticker_selector()
            self.needs_redraw = False
            return
            
        # Draw regular ticker screen content
        # Draw coin logo in top right
        logo_size = 64  # Large icon size
        logo_path = os.path.join(AppConfig.CACHE_DIR, f"{current_coin['symbol'].lower()}_logo.png")
        if os.path.exists(logo_path):
            try:
                logo = pygame.image.load(logo_path)
                logo = pygame.transform.scale(logo, (logo_size, logo_size))
                logo_rect = logo.get_rect(
                    right=self.width - 20,  # 20px from right edge
                    top=20  # 20px from top
                )
                self.display.surface.blit(logo, logo_rect)
            except Exception as e:
                logger.error(f"Error loading logo: {e}")
        
        # Draw price (larger)
        price_text = f"${current_coin['current_price']:,.2f}"
        price_font = self.display.get_title_font('xl')
        price_surface = price_font.render(price_text, True, AppConfig.WHITE)
        price_rect = price_surface.get_rect(
            left=20,
            top=20
        )
        self.display.surface.blit(price_surface, price_rect)
        
        # Draw 24h change next to price
        change_24h = current_coin['price_change_24h']
        change_color = AppConfig.GREEN if change_24h >= 0 else AppConfig.RED
        change_text = f"{change_24h:+.1f}%"
        change_font = self.display.get_title_font('md')
        change_surface = change_font.render(change_text, True, change_color)
        change_rect = change_surface.get_rect(
            left=price_rect.right + 20,
            centery=price_rect.centery
        )
        self.display.surface.blit(change_surface, change_rect)
        
        # Draw trend icon
        trend_icon = self.assets.get_icon(
            'trending-up' if change_24h >= 0 else 'trending-down',
            size=(32, 32),
            color=change_color
        )
        if trend_icon:
            trend_rect = trend_icon.get_rect(
                left=change_rect.right + 10,
                centery=change_rect.centery
            )
            self.display.surface.blit(trend_icon, trend_rect)
        
        # Draw coin name and symbol below price (larger)
        name_text = f"{current_coin['name']}"
        name_font = self.display.get_title_font('lg', 'bold')
        name_surface = name_font.render(name_text, True, AppConfig.WHITE)
        name_rect = name_surface.get_rect(
            left=20,
            top=price_rect.bottom + 15
        )
        self.display.surface.blit(name_surface, name_rect)
        
        # Draw symbol below name (larger but light weight)
        symbol_text = current_coin['symbol'].upper()
        symbol_font = self.display.get_font('light', 'title-md')
        symbol_surface = symbol_font.render(symbol_text, True, (128, 128, 128))
        symbol_rect = symbol_surface.get_rect(
            left=20,
            top=name_rect.bottom + 8
        )
        self.display.surface.blit(symbol_surface, symbol_rect)
        
        # Draw star if favorited
        if current_coin.get('favorite', False):
            star_icon = self.assets.get_icon('star', size=(24, 24), color=(255, 165, 0))
            if star_icon:
                star_rect = star_icon.get_rect(
                    left=symbol_rect.right + 10,
                    centery=symbol_rect.centery
                )
                self.display.surface.blit(star_icon, star_rect)
        
        # Draw sparkline if price history is available
        if 'sparkline_7d' in current_coin and current_coin['sparkline_7d']:
            prices = current_coin['sparkline_7d']
            if prices and len(prices) > 1:
                # Create a surface for the gradient and sparkline with alpha channel
                sparkline_surface = pygame.Surface((self.width, self.sparkline_height), pygame.SRCALPHA)
                
                # Calculate sparkline dimensions
                sparkline_rect = pygame.Rect(
                    0,
                    0,
                    self.width,
                    self.sparkline_height
                )
                
                # Calculate points for sparkline
                min_price = min(prices)
                max_price = max(prices)
                price_range = max_price - min_price
                
                if price_range > 0:
                    # Calculate base points
                    base_points = []
                    for i, price in enumerate(prices):
                        x = int((i / (len(prices) - 1)) * sparkline_rect.width)
                        y = int(sparkline_rect.height - ((price - min_price) / price_range) * sparkline_rect.height)
                        base_points.append((x, y))
                    
                    # Generate smooth points using Catmull-Rom splines
                    points = []
                    num_segments = 10  # Number of segments between each pair of points
                    
                    # Add extra control points at the ends
                    control_points = [base_points[0]]  # Start with first point
                    control_points.extend(base_points)
                    control_points.append(base_points[-1])  # End with last point
                    
                    # Generate smooth points
                    for i in range(len(base_points) - 1):
                        p0 = control_points[i]
                        p1 = control_points[i + 1]
                        p2 = control_points[i + 2]
                        p3 = control_points[i + 3]
                        
                        for t in range(num_segments):
                            t_normalized = t / num_segments
                            point = catmull_rom(p0, p1, p2, p3, t_normalized)
                            points.append(point)
                    
                    # Add the last point
                    points.append(base_points[-1])
                    
                    # Calculate price change
                    price_change = ((prices[-1] - prices[0]) / prices[0]) * 100
                    # Get base color based on price change
                    base_color = AppConfig.GREEN if price_change >= 0 else AppConfig.RED
                    
                    # Draw fill first (lighter color under the line)
                    fill_points = points + [(sparkline_rect.width, sparkline_rect.height), (0, sparkline_rect.height)]
                    fill_color = (*base_color, 20)  # Very transparent fill
                    pygame.draw.polygon(sparkline_surface, fill_color, fill_points)
                    
                    # Draw neon effect (multiple lines with decreasing alpha)
                    for thickness in range(6, 0, -1):
                        alpha = int(80 * (thickness / 6))  # Alpha decreases with thickness
                        glow_color = (*base_color, alpha)
                        pygame.draw.aalines(sparkline_surface, glow_color, False, points, thickness)
                    
                    # Draw the main line (bright and sharp)
                    main_line_color = (*base_color, 255)  # Full opacity for main line
                    pygame.draw.aalines(sparkline_surface, main_line_color, False, points, 2)
                
                # Position sparkline at bottom of screen with no padding
                sparkline_rect.bottom = self.height
                self.display.surface.blit(sparkline_surface, sparkline_rect)
        
        # Reset needs_redraw flag
        self.needs_redraw = False 