import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen
import json
import os

logger = get_logger(__name__)

class EditTickerScreen(BaseScreen):
    """Screen for editing ticker properties like favorite status or deleting it."""
    
    def __init__(self, display, ticker_id: str) -> None:
        """Initialize the edit ticker screen."""
        super().__init__(display)
        self.ticker_id = ticker_id
        self.background_color = AppConfig.BLACK
        
        # Load current ticker data
        self.load_ticker_data()
        
        # Button dimensions and positions
        button_y = self.height - AppConfig.BUTTON_AREA_HEIGHT
        self.buttons = {
            'favorite': {
                'rect': pygame.Rect(
                    self.width // 2 - AppConfig.BUTTON_WIDTH - AppConfig.BUTTON_MARGIN,
                    button_y,
                    AppConfig.BUTTON_WIDTH,
                    AppConfig.BUTTON_HEIGHT
                ),
                'color': AppConfig.EDIT_BUTTON_COLOR,
                'text': 'Unfavorite' if self.is_favorite else 'Favorite'
            },
            'delete': {
                'rect': pygame.Rect(
                    self.width // 2 + AppConfig.BUTTON_MARGIN,
                    button_y,
                    AppConfig.BUTTON_WIDTH,
                    AppConfig.BUTTON_HEIGHT
                ),
                'color': AppConfig.DELETE_BUTTON_COLOR,
                'text': 'Delete'
            }
        }
        
        logger.info(f"EditTickerScreen initialized for ticker {ticker_id}")
    
    def load_ticker_data(self) -> None:
        """Load the current ticker data from tracked_coins.json."""
        try:
            if os.path.exists(AppConfig.TRACKED_COINS_FILE):
                with open(AppConfig.TRACKED_COINS_FILE, 'r') as f:
                    self.tracked_coins = json.load(f)
                    # Initialize favorite status if not present
                    for coin in self.tracked_coins:
                        if 'favorite' not in coin and coin['id'] == self.ticker_id:
                            coin['favorite'] = False
            else:
                self.tracked_coins = []
            
            # Find current ticker
            self.current_ticker = next(
                (coin for coin in self.tracked_coins if coin['id'] == self.ticker_id),
                None
            )
            self.is_favorite = self.current_ticker.get('favorite', False) if self.current_ticker else False
            
        except Exception as e:
            logger.error(f"Error loading ticker data: {e}")
            self.tracked_coins = []
            self.current_ticker = None
            self.is_favorite = False
    
    def save_ticker_data(self) -> None:
        """Save the current ticker data to tracked_coins.json."""
        try:
            os.makedirs(os.path.dirname(AppConfig.TRACKED_COINS_FILE), exist_ok=True)
            with open(AppConfig.TRACKED_COINS_FILE, 'w') as f:
                json.dump(self.tracked_coins, f, indent=2)
            logger.info("Ticker data saved successfully")
        except Exception as e:
            logger.error(f"Error saving ticker data: {e}")
    
    def toggle_favorite(self) -> None:
        """Toggle the favorite status of the current ticker."""
        if self.current_ticker:
            self.current_ticker['favorite'] = not self.current_ticker.get('favorite', False)
            self.is_favorite = self.current_ticker['favorite']
            self.buttons['favorite']['text'] = 'Unfavorite' if self.is_favorite else 'Favorite'
            self.save_ticker_data()
            logger.info(f"Toggled favorite status for {self.ticker_id} to {self.is_favorite}")
    
    def delete_ticker(self) -> None:
        """Delete the current ticker from tracked coins."""
        if self.current_ticker:
            self.tracked_coins = [coin for coin in self.tracked_coins if coin['id'] != self.ticker_id]
            self.save_ticker_data()
            logger.info(f"Deleted ticker {self.ticker_id}")
            self.screen_manager.switch_screen('settings')
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        if event.type == pygame.FINGERDOWN:
            x = event.x * self.width
            y = event.y * self.height
            
            # Check button clicks
            for button_name, button in self.buttons.items():
                if button['rect'].collidepoint(x, y):
                    if button_name == 'favorite':
                        self.toggle_favorite()
                    elif button_name == 'delete':
                        self.delete_ticker()
        
        # Handle swipe to go back
        gestures = self.gesture_handler.handle_touch_event(event)
        if gestures['swipe_right']:
            logger.info("Swipe right detected, returning to settings")
            self.screen_manager.switch_screen('settings')
    
    def draw(self) -> None:
        """Draw the edit ticker screen."""
        # Fill background
        self.display.surface.fill(self.background_color)
        
        # Draw ticker ID
        title_text = f"Edit {self.ticker_id.upper()}"
        title_surface = self.fonts['title-md'].render(title_text, True, AppConfig.WHITE)
        title_rect = title_surface.get_rect(centerx=self.width // 2, top=20)
        self.display.surface.blit(title_surface, title_rect)
        
        # Draw buttons
        for button in self.buttons.values():
            pygame.draw.rect(self.display.surface, button['color'], button['rect'])
            text_surface = self.fonts['medium'].render(button['text'], True, AppConfig.WHITE)
            text_rect = text_surface.get_rect(center=button['rect'].center)
            self.display.surface.blit(text_surface, text_rect)
        
        self.update_screen() 