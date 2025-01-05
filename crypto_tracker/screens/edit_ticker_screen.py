import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen
from ..services.crypto.crypto_manager import CryptoManager
import os

logger = get_logger(__name__)

class EditTickerScreen(BaseScreen):
    def __init__(self, display) -> None:
        super().__init__(display)
        self.background_color = AppConfig.BLACK
        self.crypto_manager = CryptoManager()
        self.current_coin = None
        
        # Button dimensions - make them similar to example
        self.button_width = int(self.width * 0.9)  # 90% of screen width
        self.button_height = 50  # Fixed height
        self.button_spacing = 15  # Space between buttons
        
        # Calculate positions for stacked buttons
        bottom_padding = 40
        total_button_height = (self.button_height * 3) + (self.button_spacing * 2)
        start_y = self.height - total_button_height - bottom_padding
        
        # Create buttons with modern layout - stacked vertically
        self.favorite_rect = pygame.Rect(
            (self.width - self.button_width) // 2,
            start_y,
            self.button_width,
            self.button_height
        )
        
        self.delete_rect = pygame.Rect(
            (self.width - self.button_width) // 2,
            start_y + self.button_height + self.button_spacing,
            self.button_width,
            self.button_height
        )
        
        self.back_rect = pygame.Rect(
            (self.width - self.button_width) // 2,
            start_y + (self.button_height + self.button_spacing) * 2,
            self.button_width,
            self.button_height
        )
        
        logger.info("EditTickerScreen initialized")
    
    def load_coin(self, coin_id: str) -> None:
        """Load coin data for editing."""
        self.current_coin = self.crypto_manager.get_coin_data(coin_id)
        if not self.current_coin:
            logger.error(f"Could not load coin: {coin_id}")
            self.screen_manager.switch_screen('settings')
    
    def delete_coin(self) -> None:
        """Delete the current coin."""
        if self.current_coin and self.crypto_manager.remove_coin(self.current_coin['id']):
            logger.info(f"Deleted coin: {self.current_coin['symbol']}")
            self.screen_manager.switch_screen('settings')
    
    def toggle_favorite(self) -> None:
        """Toggle favorite status for current coin."""
        if self.current_coin:
            if self.crypto_manager.toggle_favorite(self.current_coin['id']):
                # Refresh current coin data
                self.current_coin = self.crypto_manager.get_coin_data(self.current_coin['id'])
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        if not self.current_coin:
            return
            
        gestures = self.gesture_handler.handle_touch_event(event)
        
        if gestures['swipe_down']:
            logger.info("Swipe down detected, returning to settings")
            self.screen_manager.switch_screen('settings')
        elif event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            x, y = self._scale_touch_input(event)
            
            if self.back_rect.collidepoint(x, y):
                logger.info("Back button clicked")
                self.screen_manager.switch_screen('settings')
            elif self.delete_rect.collidepoint(x, y):
                logger.info("Delete button clicked")
                self.delete_coin()
            elif self.favorite_rect.collidepoint(x, y):
                logger.info("Favorite button clicked")
                self.toggle_favorite()
    
    def draw(self) -> None:
        """Draw the edit ticker screen."""
        if not self.current_coin:
            return
            
        # Fill background
        self.display.surface.fill(self.background_color)
        
        # Draw coin logo if available
        logo_size = 96  # Smaller logo
        try:
            logo_path = os.path.join(AppConfig.CACHE_DIR, f"{self.current_coin['symbol'].lower()}_logo.png")
            if os.path.exists(logo_path):
                logo = pygame.image.load(logo_path)
                logo = pygame.transform.scale(logo, (logo_size, logo_size))
                logo_rect = logo.get_rect(
                    centerx=self.width // 2,
                    centery=self.height // 4  # Position higher up
                )
                self.display.surface.blit(logo, logo_rect)
        except Exception as e:
            logger.error(f"Error loading logo for {self.current_coin['symbol']}: {e}")
        
        # Draw coin name larger and below logo
        name_text = self.fonts['title-lg'].render(self.current_coin['name'], True, AppConfig.WHITE)
        name_rect = name_text.get_rect(
            centerx=self.width // 2,
            top=logo_rect.bottom + 20  # Position relative to logo
        )
        self.display.surface.blit(name_text, name_rect)
        
        # Draw symbol below name
        symbol_text = self.fonts['title-md'].render(self.current_coin['symbol'].upper(), True, AppConfig.GRAY)
        symbol_rect = symbol_text.get_rect(
            centerx=self.width // 2,
            top=name_rect.bottom + 10  # Reduced spacing
        )
        self.display.surface.blit(symbol_text, symbol_rect)
        
        # Common button style
        button_bg_color = (45, 45, 45)  # Dark gray background
        corner_radius = self.button_height // 2  # Make buttons fully rounded
        
        # Favorite button (top)
        pygame.draw.rect(self.display.surface, button_bg_color, self.favorite_rect, border_radius=corner_radius)
        favorite_text = "★ Favorite" if self.current_coin.get('favorite') else "☆ Favorite"
        favorite_text_surface = self.fonts['medium'].render(favorite_text, True, AppConfig.WHITE)
        favorite_text_rect = favorite_text_surface.get_rect(center=self.favorite_rect.center)
        self.display.surface.blit(favorite_text_surface, favorite_text_rect)
        
        # Delete button (middle)
        pygame.draw.rect(self.display.surface, button_bg_color, self.delete_rect, border_radius=corner_radius)
        delete_text = "🗑 Delete"
        delete_text_surface = self.fonts['medium'].render(delete_text, True, AppConfig.WHITE)
        delete_text_rect = delete_text_surface.get_rect(center=self.delete_rect.center)
        self.display.surface.blit(delete_text_surface, delete_text_rect)
        
        # Back button (bottom)
        pygame.draw.rect(self.display.surface, button_bg_color, self.back_rect, border_radius=corner_radius)
        back_text = "← Back"
        back_text_surface = self.fonts['medium'].render(back_text, True, AppConfig.WHITE)
        back_text_rect = back_text_surface.get_rect(center=self.back_rect.center)
        self.display.surface.blit(back_text_surface, back_text_rect)
        
        self.update_screen() 