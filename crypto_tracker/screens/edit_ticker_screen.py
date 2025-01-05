import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen
from ..services.crypto.crypto_manager import CryptoManager

logger = get_logger(__name__)

class EditTickerScreen(BaseScreen):
    def __init__(self, display) -> None:
        super().__init__(display)
        self.background_color = AppConfig.BLACK
        self.crypto_manager = CryptoManager()
        self.current_coin = None
        
        # Button dimensions
        self.button_width = AppConfig.BUTTON_WIDTH
        self.button_height = AppConfig.BUTTON_HEIGHT
        self.button_spacing = AppConfig.BUTTON_MARGIN
        
        # Create buttons
        button_y = self.height - self.button_height - 20
        self.back_rect = pygame.Rect(
            20,
            button_y,
            self.button_width,
            self.button_height
        )
        self.delete_rect = pygame.Rect(
            self.width - self.button_width - 20,
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
        
        # Draw coin info
        title_text = self.fonts['title-md'].render(f"Edit {self.current_coin['symbol']}", True, AppConfig.WHITE)
        title_rect = title_text.get_rect(centerx=self.width//2, top=20)
        self.display.surface.blit(title_text, title_rect)
        
        name_text = self.fonts['medium'].render(self.current_coin['name'], True, AppConfig.WHITE)
        name_rect = name_text.get_rect(centerx=self.width//2, top=title_rect.bottom + 20)
        self.display.surface.blit(name_text, name_rect)
        
        # Draw buttons
        pygame.draw.rect(self.display.surface, AppConfig.CANCEL_BUTTON_COLOR, self.back_rect)
        back_text = self.fonts['medium'].render("Back", True, AppConfig.WHITE)
        back_text_rect = back_text.get_rect(center=self.back_rect.center)
        self.display.surface.blit(back_text, back_text_rect)
        
        pygame.draw.rect(self.display.surface, AppConfig.DELETE_BUTTON_COLOR, self.delete_rect)
        delete_text = self.fonts['medium'].render("Delete", True, AppConfig.WHITE)
        delete_text_rect = delete_text.get_rect(center=self.delete_rect.center)
        self.display.surface.blit(delete_text, delete_text_rect)
        
        favorite_color = AppConfig.FAVORITE_ACTIVE_COLOR if self.current_coin.get('favorite') else AppConfig.FAVORITE_INACTIVE_COLOR
        pygame.draw.rect(self.display.surface, favorite_color, self.favorite_rect)
        favorite_text = self.fonts['medium'].render("Favorite", True, AppConfig.WHITE)
        favorite_text_rect = favorite_text.get_rect(center=self.favorite_rect.center)
        self.display.surface.blit(favorite_text, favorite_text_rect)
        
        self.update_screen() 