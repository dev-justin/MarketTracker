"""Screen for displaying the dashboard with time and favorite coins."""

import pygame
from datetime import datetime
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen
from zoneinfo import ZoneInfo
import os

logger = get_logger(__name__)

class DashboardScreen(BaseScreen):
    """Screen for displaying the current day and time."""
    
    def __init__(self, display) -> None:
        """Initialize the dashboard screen."""
        super().__init__(display)
        self.background_color = (13, 13, 13)  # Darker black for more contrast
        self.box_height = 90  # Reduced from 120
        self.box_width = (self.width - 60) // 2  # Two columns with margins
        logger.info("DashboardScreen initialized")
    
    def get_dominant_color(self, logo_surface):
        """Extract the dominant color from a logo using pure pygame."""
        try:
            # Get surface size
            width, height = logo_surface.get_size()
            
            # Sample points across the image
            sample_size = 10  # Sample every 10th pixel
            r_total, g_total, b_total = 0, 0, 0
            pixel_count = 0
            
            # Lock surface for direct pixel access
            logo_surface.lock()
            
            # Sample pixels
            for x in range(0, width, sample_size):
                for y in range(0, height, sample_size):
                    try:
                        color = logo_surface.get_at((x, y))
                        # Skip transparent or very dark pixels
                        if color.a > 128 and sum(color[:3]) > 60:
                            r_total += color.r
                            g_total += color.g
                            b_total += color.b
                            pixel_count += 1
                    except:
                        continue
            
            # Unlock surface
            logo_surface.unlock()
            
            if pixel_count > 0:
                # Calculate average color
                avg_color = (
                    int(r_total / pixel_count),
                    int(g_total / pixel_count),
                    int(b_total / pixel_count)
                )
                
                # Enhance saturation
                max_component = max(avg_color)
                min_component = min(avg_color)
                if max_component > min_component:
                    # Increase saturation by spreading the color components
                    saturation_factor = 1.5
                    mid_value = sum(avg_color) / 3
                    enhanced_color = tuple(
                        int(min(255, max(0, 
                            mid_value + (c - mid_value) * saturation_factor
                        )))
                        for c in avg_color
                    )
                    return enhanced_color
                
                return avg_color
            
            return (128, 128, 128)  # Default gray if no valid pixels
            
        except Exception as e:
            logger.error(f"Error extracting color: {e}")
            return (128, 128, 128)  # Default gray
    
    def draw_gradient_box(self, surface, rect, color, alpha_top=40, alpha_bottom=10):
        """Draw a box with a gradient background."""
        gradient_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        # Create gradient
        for y in range(rect.height):
            alpha = int(alpha_top + (alpha_bottom - alpha_top) * (y / rect.height))
            pygame.draw.line(
                gradient_surface,
                (*color, alpha),
                (0, y),
                (rect.width, y)
            )
        
        # Draw rounded rectangle
        pygame.draw.rect(gradient_surface, (*color, 20), (0, 0, rect.width, rect.height), border_radius=15)
        
        # Add subtle border
        pygame.draw.rect(gradient_surface, (*color, 40), (0, 0, rect.width, rect.height), 2, border_radius=15)
        
        surface.blit(gradient_surface, rect)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        gestures = self.gesture_handler.handle_touch_event(event)
        
        if gestures['swipe_up']:
            logger.info("Swipe up detected, switching to settings")
            self.screen_manager.switch_screen('settings')
        elif gestures['swipe_down']:
            logger.info("Swipe down detected, switching to ticker")
            self.screen_manager.switch_screen('ticker')
    
    def draw(self) -> None:
        """Draw the dashboard screen."""
        # Fill background
        self.display.surface.fill(self.background_color)
        
        # Get current time 
        now = datetime.now()
        local_time = now.astimezone(ZoneInfo(AppConfig.TIMEZONE))
        
        # Draw date
        date_text = local_time.strftime("%A, %B %d")
        date_font = self.display.get_font('light', 'lg')
        date_surface = date_font.render(date_text, True, AppConfig.WHITE)
        date_rect = date_surface.get_rect(centerx=self.width // 2, top=20)
        self.display.surface.blit(date_surface, date_rect)
        
        # Draw time (larger)
        time_text = local_time.strftime("%I:%M %p").lstrip("0")
        time_font = self.display.get_title_font('xl')  # Use title-xl font
        time_surface = time_font.render(time_text, True, AppConfig.WHITE)
        time_rect = time_surface.get_rect(centerx=self.width // 2, top=date_rect.bottom + 10)
        self.display.surface.blit(time_surface, time_rect)
        
        # Get favorite coins
        coins = self.crypto_manager.get_tracked_coins()
        favorite_coins = [coin for coin in coins if coin.get('favorite', False)]
        
        if favorite_coins:
            # Draw "Favorites" header
            favorites_text = "Favorites"
            favorites_font = self.display.get_font('light', 'title-md')
            favorites_surface = favorites_font.render(favorites_text, True, (128, 128, 128))
            favorites_rect = favorites_surface.get_rect(
                left=20,
                top=time_rect.bottom + 40
            )
            self.display.surface.blit(favorites_surface, favorites_rect)
            
            # Calculate grid layout
            margin = 20
            start_y = favorites_rect.bottom + 20
            
            # Draw favorite coins in a grid
            for i, coin in enumerate(favorite_coins):
                row = i // 2
                col = i % 2
                x = margin + col * (self.box_width + margin)
                y = start_y + row * (self.box_height + margin)
                
                try:
                    # Create box rect
                    box_rect = pygame.Rect(x, y, self.box_width, self.box_height)
                    
                    # Load and process logo
                    logo_path = os.path.join(AppConfig.CACHE_DIR, f"{coin['symbol'].lower()}_logo.png")
                    if os.path.exists(logo_path):
                        logo = pygame.image.load(logo_path)
                        logo_size = 36  # Reduced from 48
                        logo = pygame.transform.scale(logo, (logo_size, logo_size))
                        
                        # Get dominant color from logo
                        dominant_color = self.get_dominant_color(logo)
                        
                        # Draw gradient box
                        self.draw_gradient_box(self.display.surface, box_rect, dominant_color)
                        
                        # Draw logo
                        logo_rect = logo.get_rect(
                            left=box_rect.left + 15,
                            centery=box_rect.centery
                        )
                        self.display.surface.blit(logo, logo_rect)
                        
                        # Draw coin symbol instead of name
                        name_font = self.display.get_font('light', 'lg')
                        name_text = coin['symbol'].upper()
                        name_surface = name_font.render(name_text, True, AppConfig.WHITE)
                        name_rect = name_surface.get_rect(
                            left=logo_rect.right + 15,
                            centery=logo_rect.centery
                        )
                        self.display.surface.blit(name_surface, name_rect)
                        
                        # Calculate change percentage first
                        change_24h = coin['price_change_24h']
                        change_color = AppConfig.GREEN if change_24h >= 0 else AppConfig.RED
                        change_text = f"{change_24h:+.1f}%"
                        change_font = self.display.get_text_font('md', 'regular')
                        change_surface = change_font.render(change_text, True, change_color)
                        
                        # Draw price
                        price_text = f"${coin['current_price']:,.2f}"
                        price_font = self.display.get_text_font('lg', 'regular')
                        price_surface = price_font.render(price_text, True, AppConfig.WHITE)
                        
                        # Position change percentage and price on the same line (change first)
                        total_width = change_surface.get_width() + 10 + price_surface.get_width()  # 10px spacing
                        start_x = box_rect.right - 15 - total_width
                        
                        change_rect = change_surface.get_rect(
                            left=start_x,
                            centery=logo_rect.centery
                        )
                        self.display.surface.blit(change_surface, change_rect)
                        
                        price_rect = price_surface.get_rect(
                            left=change_rect.right + 10,
                            centery=logo_rect.centery
                        )
                        self.display.surface.blit(price_surface, price_rect)
                        
                except Exception as e:
                    logger.error(f"Error drawing favorite coin {coin['symbol']}: {e}")
        
        self.update_screen()