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
        self.current_ticker = None
        self.is_favorite = False
        self.tracked_coins = []
        
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
                    data = json.load(f)
                    # Ensure proper data structure
                    self.tracked_coins = []
                    for item in data:
                        if isinstance(item, dict) and 'id' in item and 'symbol' in item:
                            if 'favorite' not in item:
                                item['favorite'] = False
                            self.tracked_coins.append(item)
                        elif isinstance(item, str):
                            # Convert old format to new format
                            self.tracked_coins.append({
                                'id': item.lower(),
                                'symbol': item.upper(),
                                'favorite': False
                            })
                    
                    # Find current ticker
                    self.current_ticker = next(
                        (coin for coin in self.tracked_coins if coin.get('id') == self.ticker_id),
                        None
                    )
                    self.is_favorite = self.current_ticker.get('favorite', False) if self.current_ticker else False
            else:
                self.tracked_coins = []
                self.current_ticker = None
                self.is_favorite = False
                
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
            self.tracked_coins = [coin for coin in self.tracked_coins if coin.get('id') != self.ticker_id]
            self.save_ticker_data()
            logger.info(f"Deleted ticker {self.ticker_id}")
            self.screen_manager.switch_screen('settings')
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        gestures = self.gesture_handler.handle_touch_event(event)
        
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
        if gestures['swipe_right']:
            logger.info("Swipe right detected, returning to settings")
            self.screen_manager.switch_screen('settings')
    
    def draw(self) -> None:
        """Draw the edit ticker screen."""
        # Fill background
        self.display.surface.fill(self.background_color)
        
        if self.current_ticker:
            # Draw ticker symbol
            title_text = f"Edit {self.current_ticker.get('symbol', '').upper()}"
            title_surface = self.fonts['title-md'].render(title_text, True, AppConfig.WHITE)
            title_rect = title_surface.get_rect(centerx=self.width // 2, top=20)
            self.display.surface.blit(title_surface, title_rect)
            
            # Draw buttons
            for button in self.buttons.values():
                pygame.draw.rect(self.display.surface, button['color'], button['rect'])
                text_surface = self.fonts['medium'].render(button['text'], True, AppConfig.WHITE)
                text_rect = text_surface.get_rect(center=button['rect'].center)
                self.display.surface.blit(text_surface, text_rect)
        else:
            # Draw error message if ticker not found
            error_text = "Ticker not found"
            error_surface = self.fonts['title-md'].render(error_text, True, AppConfig.RED)
            error_rect = error_surface.get_rect(center=(self.width // 2, self.height // 2))
            self.display.surface.blit(error_surface, error_rect)
        
        self.update_screen() 