import pygame
from datetime import datetime
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen
from zoneinfo import ZoneInfo
from ..services.crypto.crypto_manager import CryptoManager
import os

logger = get_logger(__name__)

class DashboardScreen(BaseScreen):
    """Screen for displaying the current day and time."""
    
    def __init__(self, display) -> None:
        """Initialize the dashboard screen."""
        super().__init__(display)
        self.background_color = (0, 0, 0)  # Pure black
        self.crypto_manager = CryptoManager()
        logger.info("DashboardScreen initialized")
    
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
        # Fill background with black
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
        # Create larger font for time
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
            
            # Draw favorite coins
            y_position = favorites_rect.bottom + 20
            for coin in favorite_coins:
                # Draw coin logo if available
                logo_size = 32
                logo_margin = 20
                try:
                    logo_path = os.path.join(AppConfig.CACHE_DIR, f"{coin['symbol'].lower()}_logo.png")
                    if os.path.exists(logo_path):
                        logo = pygame.image.load(logo_path)
                        logo = pygame.transform.scale(logo, (logo_size, logo_size))
                        logo_rect = logo.get_rect(
                            left=20,
                            centery=y_position + logo_size//2
                        )
                        self.display.surface.blit(logo, logo_rect)
                        
                        # Draw coin name and price
                        name_font = pygame.font.Font(AppConfig.FONT_PATHS['light'], AppConfig.FONT_SIZES['lg'])
                        name_text = f"{coin['name']}"
                        name_surface = name_font.render(name_text, True, AppConfig.WHITE)
                        name_rect = name_surface.get_rect(
                            left=logo_rect.right + 15,
                            top=y_position
                        )
                        self.display.surface.blit(name_surface, name_rect)
                        
                        # Draw price and 24h change
                        price_text = f"${coin['current_price']:,.2f}"
                        change_24h = coin['price_change_24h']
                        change_color = AppConfig.GREEN if change_24h >= 0 else AppConfig.RED
                        change_text = f"{change_24h:+.1f}%"
                        
                        # Price
                        price_font = pygame.font.Font(AppConfig.FONT_PATHS['regular'], AppConfig.FONT_SIZES['md'])
                        price_surface = price_font.render(price_text, True, AppConfig.WHITE)
                        price_rect = price_surface.get_rect(
                            right=self.width - 20,
                            top=y_position
                        )
                        self.display.surface.blit(price_surface, price_rect)
                        
                        # Change percentage
                        change_font = pygame.font.Font(AppConfig.FONT_PATHS['regular'], AppConfig.FONT_SIZES['md'])
                        change_surface = change_font.render(change_text, True, change_color)
                        change_rect = change_surface.get_rect(
                            right=self.width - 20,
                            top=price_rect.bottom + 2
                        )
                        self.display.surface.blit(change_surface, change_rect)
                        
                except Exception as e:
                    logger.error(f"Error drawing favorite coin {coin['symbol']}: {e}")
                
                y_position += logo_size + 20  # Space for next coin
        
        self.update_screen()