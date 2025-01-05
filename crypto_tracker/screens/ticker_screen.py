import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen
from ..services.crypto.crypto_manager import CryptoManager

logger = get_logger(__name__)

class TickerScreen(BaseScreen):
    def __init__(self, display) -> None:
        super().__init__(display)
        self.background_color = AppConfig.BLACK
        self.crypto_manager = CryptoManager()
        self.current_index = 0
        self.coins = []
        
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
        
        if gestures['swipe_left']:
            logger.info("Swipe left detected, showing next coin")
            self.next_coin()
        elif gestures['swipe_right']:
            logger.info("Swipe right detected, showing previous coin")
            self.previous_coin()
        elif gestures['swipe_down']:
            logger.info("Swipe down detected, returning to dashboard")
            self.screen_manager.switch_screen('dashboard')
    
    def draw(self) -> None:
        """Draw the ticker screen."""
        # Fill background
        self.display.surface.fill(self.background_color)
        
        # Refresh coin data
        self.refresh_coins()
        
        if not self.coins:
            # Draw "No coins" message
            text = self.fonts['title-md'].render("No coins tracked", True, AppConfig.WHITE)
            text_rect = text.get_rect(center=(self.width//2, self.height//2))
            self.display.surface.blit(text, text_rect)
            self.update_screen()
            return
        
        current_coin = self.coins[self.current_index]
        
        # Draw coin name and symbol
        title_text = f"{current_coin['name']} ({current_coin['symbol']})"
        title_surface = self.fonts['title-md'].render(title_text, True, AppConfig.WHITE)
        title_rect = title_surface.get_rect(centerx=self.width//2, top=20)
        self.display.surface.blit(title_surface, title_rect)
        
        # Draw price
        price_text = f"${current_coin['current_price']:,.2f}"
        price_surface = self.fonts['title-lg'].render(price_text, True, AppConfig.WHITE)
        price_rect = price_surface.get_rect(centerx=self.width//2, top=title_rect.bottom + 20)
        self.display.surface.blit(price_surface, price_rect)
        
        # Draw 24h change
        change_24h = current_coin['price_change_24h']
        change_color = AppConfig.GREEN if change_24h >= 0 else AppConfig.RED
        change_text = f"{change_24h:+.2f}% (24h)"
        change_surface = self.fonts['medium'].render(change_text, True, change_color)
        change_rect = change_surface.get_rect(centerx=self.width//2, top=price_rect.bottom + 10)
        self.display.surface.blit(change_surface, change_rect)
        
        # Draw navigation hints
        if len(self.coins) > 1:
            nav_text = f"{self.current_index + 1} / {len(self.coins)}"
            nav_surface = self.fonts['sm'].render(nav_text, True, AppConfig.GRAY)
            nav_rect = nav_surface.get_rect(centerx=self.width//2, bottom=self.height - 20)
            self.display.surface.blit(nav_surface, nav_rect)
        
        self.update_screen() 