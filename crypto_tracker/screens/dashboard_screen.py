import pygame
from datetime import datetime
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen
from zoneinfo import ZoneInfo
from ..services.crypto.crypto_manager import CryptoManager
import os
from pygame import gfxdraw

logger = get_logger(__name__)

class DashboardScreen(BaseScreen):
    """Screen for displaying the current day and time."""
    
    def __init__(self, display) -> None:
        """Initialize the dashboard screen."""
        super().__init__(display)
        self.background_color = (13, 13, 13)  # Darker black for more contrast
        self.crypto_manager = CryptoManager()
        self.box_height = 120  # Height of each coin box
        self.box_width = (self.width - 60) // 2  # Two columns with margins
        logger.info("DashboardScreen initialized")
    
    def get_dominant_color(self, logo_surface):
        """Extract the dominant color from a logo."""
        try:
            # Get surface data
            width, height = logo_surface.get_size()
            pixels = pygame.surfarray.pixels3d(logo_surface)
            
            # Calculate average color of non-black pixels
            r_total, g_total, b_total = 0, 0, 0
            pixel_count = 0
            
            for x in range(width):
                for y in range(height):
                    r, g, b = pixels[x][y]
                    # Skip black/very dark pixels
                    if r + g + b > 60:  # Threshold for considering a pixel
                        r_total += r
                        g_total += g
                        b_total += b
                        pixel_count += 1
            
            if pixel_count > 0:
                return (
                    int(r_total / pixel_count),
                    int(g_total / pixel_count),
                    int(b_total / pixel_count)
                )
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
        # Handle touch events
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
        date_surface = self.fonts['light-lg'].render(date_text, True, AppConfig.WHITE)
        date_rect = date_surface.get_rect(centerx=self.width // 2, top=20)
        self.display.surface.blit(date_surface, date_rect)
        
        # Draw time (larger)
        time_text = local_time.strftime("%I:%M %p").lstrip("0")
        time_font = pygame.font.Font(AppConfig.FONT_PATHS['regular'], int(AppConfig.FONT_SIZES['title-xl'] * 1.5))
        time_surface = time_font.render(time_text, True, AppConfig.WHITE)
        time_rect = time_surface.get_rect(centerx=self.width // 2, top=date_rect.bottom + 10)
        self.display.surface.blit(time_surface, time_rect)
        
        # Get favorite coins
        coins = self.crypto_manager.get_tracked_coins()
        favorite_coins = [coin for coin in coins if coin.get('favorite', False)]
        
        if favorite_coins:
            # Draw "Favorites" header
            favorites_text = "Favorites"
            favorites_font = pygame.font.Font(AppConfig.FONT_PATHS['light'], AppConfig.FONT_SIZES['title-md'])
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
                        logo_size = 48
                        logo = pygame.transform.scale(logo, (logo_size, logo_size))
                        
                        # Get dominant color from logo
                        dominant_color = self.get_dominant_color(logo)
                        
                        # Draw gradient box
                        self.draw_gradient_box(self.display.surface, box_rect, dominant_color)
                        
                        # Draw logo
                        logo_rect = logo.get_rect(
                            left=box_rect.left + 15,
                            top=box_rect.top + 15
                        )
                        self.display.surface.blit(logo, logo_rect)
                        
                        # Draw coin name
                        name_font = pygame.font.Font(AppConfig.FONT_PATHS['light'], AppConfig.FONT_SIZES['lg'])
                        name_text = coin['name']
                        name_surface = name_font.render(name_text, True, AppConfig.WHITE)
                        name_rect = name_surface.get_rect(
                            left=logo_rect.right + 15,
                            top=logo_rect.top + 5
                        )
                        self.display.surface.blit(name_surface, name_rect)
                        
                        # Draw price and change
                        price_text = f"${coin['current_price']:,.2f}"
                        change_24h = coin['price_change_24h']
                        change_color = AppConfig.GREEN if change_24h >= 0 else AppConfig.RED
                        
                        # Price
                        price_font = pygame.font.Font(AppConfig.FONT_PATHS['regular'], AppConfig.FONT_SIZES['md'])
                        price_surface = price_font.render(price_text, True, AppConfig.WHITE)
                        price_rect = price_surface.get_rect(
                            left=box_rect.left + 15,
                            bottom=box_rect.bottom - 15
                        )
                        self.display.surface.blit(price_surface, price_rect)
                        
                        # Change percentage
                        change_text = f"{change_24h:+.1f}%"
                        change_font = pygame.font.Font(AppConfig.FONT_PATHS['regular'], AppConfig.FONT_SIZES['md'])
                        change_surface = change_font.render(change_text, True, change_color)
                        change_rect = change_surface.get_rect(
                            right=box_rect.right - 15,
                            centery=price_rect.centery
                        )
                        self.display.surface.blit(change_surface, change_rect)
                        
                except Exception as e:
                    logger.error(f"Error drawing favorite coin {coin['symbol']}: {e}")
        
        self.update_screen()