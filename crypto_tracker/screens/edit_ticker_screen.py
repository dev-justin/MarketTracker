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
        
        # Button dimensions - make them larger
        self.button_width = int(AppConfig.BUTTON_WIDTH * 1.2)  # 20% wider
        self.button_height = int(AppConfig.BUTTON_HEIGHT * 1.5)  # 50% taller
        self.button_spacing = AppConfig.BUTTON_MARGIN * 2
        
        # Create buttons with increased height and better spacing
        button_y = self.height - (self.button_height + 50)  # More space from bottom
        self.back_rect = pygame.Rect(
            30,  # More padding from left
            button_y,
            self.button_width,
            self.button_height
        )
        self.delete_rect = pygame.Rect(
            self.width - self.button_width - 30,  # More padding from right
            button_y,
            self.button_width,
            self.button_height
        )
        self.favorite_rect = pygame.Rect(
            (self.width - self.button_width) // 2,
            button_y,
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
                    centery=self.height // 3  # Position in upper third
                )
                self.display.surface.blit(logo, logo_rect)
        except Exception as e:
            logger.error(f"Error loading logo for {self.current_coin['symbol']}: {e}")
        
        # Draw coin name larger and below logo
        name_text = self.fonts['title-lg'].render(self.current_coin['name'], True, AppConfig.WHITE)
        name_rect = name_text.get_rect(
            centerx=self.width // 2,
            top=self.height // 2  # Center vertically
        )
        self.display.surface.blit(name_text, name_rect)
        
        # Draw symbol below name
        symbol_text = self.fonts['title-md'].render(self.current_coin['symbol'].upper(), True, AppConfig.GRAY)
        symbol_rect = symbol_text.get_rect(
            centerx=self.width // 2,
            top=name_rect.bottom + 20
        )
        self.display.surface.blit(symbol_text, symbol_rect)
        
        # Draw buttons with more rounded corners
        corner_radius = 20  # Increased corner radius
        
        # Back button
        pygame.draw.rect(self.display.surface, AppConfig.CANCEL_BUTTON_COLOR, self.back_rect, border_radius=corner_radius)
        back_text = self.fonts['title-md'].render("Back", True, AppConfig.WHITE)  # Larger font
        back_text_rect = back_text.get_rect(center=self.back_rect.center)
        self.display.surface.blit(back_text, back_text_rect)
        
        # Delete button
        pygame.draw.rect(self.display.surface, AppConfig.DELETE_BUTTON_COLOR, self.delete_rect, border_radius=corner_radius)
        delete_text = self.fonts['title-md'].render("Delete", True, AppConfig.WHITE)  # Larger font
        delete_text_rect = delete_text.get_rect(center=self.delete_rect.center)
        self.display.surface.blit(delete_text, delete_text_rect)
        
        # Favorite button
        favorite_color = AppConfig.FAVORITE_ACTIVE_COLOR if self.current_coin.get('favorite') else AppConfig.FAVORITE_INACTIVE_COLOR
        pygame.draw.rect(self.display.surface, favorite_color, self.favorite_rect, border_radius=corner_radius)
        
        # Add star icon to favorite button with larger text
        favorite_text = "★ Favorite" if self.current_coin.get('favorite') else "☆ Favorite"
        favorite_text_surface = self.fonts['title-md'].render(favorite_text, True, AppConfig.WHITE)  # Larger font
        favorite_text_rect = favorite_text_surface.get_rect(center=self.favorite_rect.center)
        self.display.surface.blit(favorite_text_surface, favorite_text_rect)
        
        self.update_screen() 