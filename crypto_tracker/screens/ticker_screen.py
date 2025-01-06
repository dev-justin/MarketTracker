"""Screen for displaying detailed coin information."""

import pygame
import os
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen

logger = get_logger(__name__)

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
            self.selector_start_time = pygame.time.get_ticks()
            x, y = self._scale_touch_input(event)
            
            # If selector is showing, check for ticker selection
            if self.showing_selector:
                # Calculate ticker positions with scroll offset
                center_y = self.height // 2
                center_x = self.width // 2
                current_logo_size = 80
                other_logo_size = 50
                spacing = 30
                
                # Check if click is in the selector area
                selector_area = pygame.Rect(0, center_y - 60, self.width, 120)
                if selector_area.collidepoint(x, y):
                    # Calculate visible range
                    for i in range(len(self.coins)):
                        # Calculate position relative to center
                        offset_from_current = i - self.current_index
                        
                        if offset_from_current < 0:
                            cumulative_width = sum([other_logo_size + spacing for _ in range(abs(offset_from_current))])
                            logo_x = center_x - (current_logo_size // 2) - spacing - cumulative_width
                        elif offset_from_current > 0:
                            cumulative_width = sum([other_logo_size + spacing for _ in range(offset_from_current)])
                            logo_x = center_x + (current_logo_size // 2) + spacing + cumulative_width - other_logo_size
                        else:
                            logo_x = center_x - (current_logo_size // 2)
                        
                        logo_x += self.selector_scroll_offset
                        logo_size = current_logo_size if i == self.current_index else other_logo_size
                        logo_rect = pygame.Rect(logo_x, center_y - logo_size // 2, logo_size, logo_size)
                        
                        if logo_rect.collidepoint(x, y):
                            self.current_index = i
                            self.showing_selector = False
                            self.selector_scroll_offset = 0
                            return
                else:
                    # Hide selector if clicked outside
                    self.showing_selector = False
                    self.selector_scroll_offset = 0
        
        elif event.type == AppConfig.EVENT_TYPES['FINGER_UP']:
            # Check if this was a long press
            if not self.showing_selector and pygame.time.get_ticks() - self.selector_start_time > 500:  # 500ms for long press
                self.showing_selector = True
                self.selector_scroll_offset = 0
                return
        
        # Handle horizontal scrolling in selector mode
        if self.showing_selector:
            if gestures['swipe_left']:
                self.selector_scroll_offset += 100  # Scroll left
            elif gestures['swipe_right']:
                self.selector_scroll_offset -= 100  # Scroll right
            
            # Limit scrolling
            max_scroll = (len(self.coins) - 5) * (50 + 30)  # (other_logo_size + spacing)
            self.selector_scroll_offset = max(-max_scroll, min(self.selector_scroll_offset, 0))
        elif gestures['swipe_down']:
            logger.info("Swipe down detected, returning to dashboard")
            self.screen_manager.switch_screen('dashboard')
    
    def draw_ticker_selector(self):
        """Draw the ticker selector overlay."""
        if not self.showing_selector:
            return
            
        # Define sizes
        current_logo_size = 80  # Larger size for current ticker
        other_logo_size = 50    # Normal size for other tickers
        spacing = 30
        
        center_y = self.height // 2  # Vertical center of screen
        center_x = self.width // 2   # Horizontal center of screen
        
        # Draw all logos
        for i in range(len(self.coins)):
            # Calculate position and size for this logo
            is_current = (i == self.current_index)
            logo_size = current_logo_size if is_current else other_logo_size
            
            # Calculate position relative to center
            offset_from_current = i - self.current_index
            
            # Position logos with current one in center
            if offset_from_current < 0:
                # Logos to the left of current
                cumulative_width = sum([other_logo_size + spacing for _ in range(abs(offset_from_current))])
                logo_x = center_x - (current_logo_size // 2) - spacing - cumulative_width
            elif offset_from_current > 0:
                # Logos to the right of current
                cumulative_width = sum([other_logo_size + spacing for _ in range(offset_from_current)])
                logo_x = center_x + (current_logo_size // 2) + spacing + cumulative_width - other_logo_size
            else:
                # Current logo (centered)
                logo_x = center_x - (current_logo_size // 2)
            
            # Apply scroll offset
            logo_x += self.selector_scroll_offset
            
            # Only draw if visible on screen
            if -logo_size <= logo_x <= self.width:
                # Calculate y position (center vertically)
                logo_y = center_y - logo_size // 2
                
                logo_path = os.path.join(AppConfig.CACHE_DIR, f"{self.coins[i]['symbol'].lower()}_logo.png")
                
                if os.path.exists(logo_path):
                    try:
                        logo = pygame.image.load(logo_path)
                        logo = pygame.transform.scale(logo, (logo_size, logo_size))
                        logo_rect = logo.get_rect(topleft=(logo_x, logo_y))
                        
                        # Add subtle glow effect for current ticker
                        if is_current:
                            glow_surface = pygame.Surface((logo_size + 20, logo_size + 20), pygame.SRCALPHA)
                            glow_rect = glow_surface.get_rect(center=(logo_size//2 + 10, logo_size//2 + 10))
                            
                            # Draw multiple circles for glow effect
                            for radius in range(10, 0, -2):
                                alpha = int(100 * (radius / 10))
                                pygame.draw.circle(glow_surface, (255, 255, 255, alpha), glow_rect.center, logo_size//2 + radius)
                            
                            # Position and draw glow
                            glow_pos = (logo_x - 10, logo_y - 10)
                            self.display.surface.blit(glow_surface, glow_pos)
                        
                        self.display.surface.blit(logo, logo_rect)
                        
                        # Draw symbol below logo for current ticker
                        if is_current:
                            symbol_font = self.display.get_text_font('md', 'bold')
                            symbol_surface = symbol_font.render(self.coins[i]['symbol'].upper(), True, AppConfig.WHITE)
                            symbol_rect = symbol_surface.get_rect(
                                centerx=logo_rect.centerx,
                                top=logo_rect.bottom + 10
                            )
                            self.display.surface.blit(symbol_surface, symbol_rect)
                            
                    except Exception as e:
                        logger.error(f"Error loading logo for selector: {e}")
    
    def draw(self) -> None:
        """Draw the ticker screen."""
        if not self.coins:
            return
            
        current_coin = self.coins[self.current_index]
        
        # Fill background
        self.display.surface.fill(self.background_color)
        
        # If selector is showing, only draw it
        if self.showing_selector:
            self.draw_ticker_selector()
            self.update_screen()
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
                
                min_price = min(prices)
                max_price = max(prices)
                price_range = max_price - min_price
                
                if price_range > 0:
                    # Generate base points from price data
                    base_points = []
                    for i, price in enumerate(prices):
                        x = int((i / (len(prices) - 1)) * sparkline_rect.width)
                        y = int(sparkline_rect.height - ((price - min_price) / price_range) * sparkline_rect.height * 0.8)
                        base_points.append((x, y))
                    
                    # Generate smooth points using Catmull-Rom spline interpolation
                    points = []
                    num_segments = 32  # Number of segments between each pair of points
                    
                    # Helper function for Catmull-Rom interpolation
                    def catmull_rom(p0, p1, p2, p3, t):
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
        
        # Draw the ticker selector overlay last
        self.draw_ticker_selector()
        
        self.update_screen() 