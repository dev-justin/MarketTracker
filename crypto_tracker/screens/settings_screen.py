import pygame
import json
import os
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen

logger = get_logger(__name__)

class SettingsScreen(BaseScreen):
    """Screen for displaying and modifying application settings."""
    
    def __init__(self, display) -> None:
        """Initialize the settings screen."""
        super().__init__(display)
        self.background_color = AppConfig.BLACK
        
        # Header dimensions
        self.header_height = 80
        self.padding = 20
        
        # Button dimensions
        self.button_width = 200
        self.button_height = 60
        
        # Coin cell dimensions
        self.cell_height = 70
        self.cell_spacing = 10
        
        # Load tracked coins
        self.load_tracked_coins()
        
        logger.info("SettingsScreen initialized")
    
    def load_tracked_coins(self) -> None:
        """Load tracked coins from json file."""
        try:
            if os.path.exists(AppConfig.TRACKED_COINS_FILE):
                with open(AppConfig.TRACKED_COINS_FILE, 'r') as f:
                    self.tracked_coins = json.load(f)
                    # Initialize favorite status if not present
                    for coin in self.tracked_coins:
                        if 'favorite' not in coin:
                            coin['favorite'] = False
            else:
                self.tracked_coins = []
        except Exception as e:
            logger.error(f"Error loading tracked coins: {e}")
            self.tracked_coins = []
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        gestures = self.gesture_handler.handle_touch_event(event)
        
        if gestures['swipe_down']:
            logger.info("Swipe down detected, returning to dashboard")
            self.screen_manager.switch_screen('dashboard')
        elif event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            # Get touch position
            x, y = self._scale_touch_input(event)
            
            # Check if add button was clicked
            if self.add_button_rect.collidepoint(x, y):
                logger.info("Add button clicked, switching to add ticker screen")
                self.screen_manager.switch_screen('add_ticker')
            
            # Check if any coin cell was clicked
            cell_y = self.header_height + self.padding
            for coin in self.tracked_coins:
                cell_rect = pygame.Rect(
                    self.padding,
                    cell_y,
                    self.width - (2 * self.padding),
                    self.cell_height
                )
                if cell_rect.collidepoint(x, y):
                    logger.info(f"Coin {coin['id']} clicked, switching to edit screen")
                    self.screen_manager.switch_screen('edit_ticker', coin['id'])
                cell_y += self.cell_height + self.cell_spacing

    def _draw_coin_cell(self, surface: pygame.Surface, y: int, coin: dict) -> None:
        """Draw a single coin cell."""
        # Calculate cell dimensions
        cell_width = self.width - (2 * self.padding)
        rect = pygame.Rect(self.padding, y, cell_width, self.cell_height)
        
        # Draw cell background
        pygame.draw.rect(surface, AppConfig.CELL_BG_COLOR, rect)
        pygame.draw.rect(surface, AppConfig.CELL_BORDER_COLOR, rect, 1)
        
        # Draw coin symbol
        symbol_text = coin['symbol'].upper()
        symbol_surface = self.fonts['medium'].render(symbol_text, True, AppConfig.WHITE)
        symbol_rect = symbol_surface.get_rect(
            centery=rect.centery,
            left=rect.left + self.padding
        )
        surface.blit(symbol_surface, symbol_rect)
        
        # Draw favorite star if favorited
        if coin.get('favorite', False):
            star_text = "★"  # Filled star for favorites
            star_surface = self.fonts['medium'].render(star_text, True, AppConfig.GREEN)
            star_rect = star_surface.get_rect(
                centery=rect.centery,
                right=rect.right - self.padding
            )
            surface.blit(star_surface, star_rect)
    
    def draw(self) -> None:
        """Draw the settings screen."""
        # Fill background
        self.display.surface.fill(self.background_color)
        
        # Draw header
        header_text = "Settings"
        header_surface = self.fonts['title-md'].render(header_text, True, AppConfig.WHITE)
        header_rect = header_surface.get_rect(
            centerx=self.width // 2,
            top=self.padding
        )
        self.display.surface.blit(header_surface, header_rect)
        
        # Draw tracked coins
        current_y = self.header_height + self.padding
        for coin in self.tracked_coins:
            self._draw_coin_cell(self.display.surface, current_y, coin)
            current_y += self.cell_height + self.cell_spacing
        
        # Draw add button at the bottom
        self.add_button_rect = pygame.Rect(
            (self.width - self.button_width) // 2,
            self.height - self.button_height - self.padding,
            self.button_width,
            self.button_height
        )
        pygame.draw.rect(self.display.surface, AppConfig.CELL_BG_COLOR, self.add_button_rect)
        pygame.draw.rect(self.display.surface, AppConfig.CELL_BORDER_COLOR, self.add_button_rect, 1)
        
        button_text = "Add Ticker"
        button_surface = self.fonts['medium'].render(button_text, True, AppConfig.WHITE)
        button_text_rect = button_surface.get_rect(center=self.add_button_rect.center)
        self.display.surface.blit(button_surface, button_text_rect)
        
        self.update_screen() 