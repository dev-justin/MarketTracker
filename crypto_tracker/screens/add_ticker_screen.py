import pygame
import json
import os
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen

logger = get_logger(__name__)

class AddTickerScreen(BaseScreen):
    def __init__(self, display) -> None:
        super().__init__(display)
        self.background_color = AppConfig.BLACK
        self.new_symbol = ""
        
        # Button dimensions
        self.button_width = AppConfig.BUTTON_WIDTH
        self.button_height = AppConfig.BUTTON_HEIGHT
        self.button_spacing = AppConfig.BUTTON_MARGIN
        
        # Keyboard layout
        self.keys = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'DEL']
        ]
        self.setup_keyboard()
        
        logger.info("AddTickerScreen initialized")
    
    def add_ticker(self, symbol: str) -> None:
        """Add a new ticker to tracked coins."""
        try:
            # Load existing coins
            tracked_coins = []
            if os.path.exists(AppConfig.TRACKED_COINS_FILE):
                with open(AppConfig.TRACKED_COINS_FILE, 'r') as f:
                    tracked_coins = json.load(f)
            
            # Add new coin with proper structure
            new_coin = {
                'id': symbol.lower(),
                'symbol': symbol.upper(),
                'favorite': False
            }
            
            # Check if coin already exists
            if not any(coin.get('id') == new_coin['id'] for coin in tracked_coins):
                tracked_coins.append(new_coin)
                
                # Save updated list
                os.makedirs(os.path.dirname(AppConfig.TRACKED_COINS_FILE), exist_ok=True)
                with open(AppConfig.TRACKED_COINS_FILE, 'w') as f:
                    json.dump(tracked_coins, f, indent=2)
                logger.info(f"Added new ticker: {symbol}")
            else:
                logger.warning(f"Ticker already exists: {symbol}")
                
        except Exception as e:
            logger.error(f"Error adding ticker: {e}")
    
    def setup_keyboard(self):
        """Calculate keyboard layout dimensions."""
        keyboard_height = self.height * 0.5 
        keyboard_top = self.height * 0.35 
        key_padding = 10
        num_rows = len(self.keys)
        
        # Calculate key sizes
        max_keys_in_row = max(len(row) for row in self.keys)
        self.key_width = (self.width - (key_padding * (max_keys_in_row + 1))) // max_keys_in_row
        self.key_height = (keyboard_height - (key_padding * (num_rows + 1))) // num_rows
        
        # Store key rectangles for hit detection
        self.key_rects = []
        y = keyboard_top
        for row in self.keys:
            row_width = len(row) * self.key_width + (len(row) - 1) * key_padding
            x = (self.width - row_width) // 2
            row_rects = []
            for key in row:
                rect = pygame.Rect(x, y, self.key_width, self.key_height)
                row_rects.append((key, rect))
                x += self.key_width + key_padding
            self.key_rects.append(row_rects)
            y += self.key_height + key_padding
        
        # Create save and cancel buttons
        button_y = self.height - self.button_height - 20
        self.cancel_rect = pygame.Rect(
            20,
            button_y,
            self.button_width,
            self.button_height
        )
        self.save_rect = pygame.Rect(
            self.width - self.button_width - 20,
            button_y,
            self.button_width,
            self.button_height
        )
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        gestures = self.gesture_handler.handle_touch_event(event)
        
        if gestures['swipe_down']:
            logger.info("Swipe down detected, returning to settings")
            self.screen_manager.switch_screen('settings')
        elif event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            # Get touch position
            x, y = self._scale_touch_input(event)
            
            # Check for button clicks
            if self.cancel_rect.collidepoint(x, y):
                logger.info("Cancel button clicked")
                self.screen_manager.switch_screen('settings')
            elif self.save_rect.collidepoint(x, y):
                logger.info("Save button clicked")
                if self.new_symbol:
                    self.add_ticker(self.new_symbol)
                    self.screen_manager.switch_screen('settings')
            else:
                # Check for key presses
                for row in self.key_rects:
                    for key, rect in row:
                        if rect.collidepoint(x, y):
                            if key == 'DEL':
                                if self.new_symbol:
                                    self.new_symbol = self.new_symbol[:-1]
                                    logger.debug(f"Backspace pressed, current input: {self.new_symbol}")
                            elif len(self.new_symbol) < 5:
                                self.new_symbol += key
                                logger.debug(f"Key pressed: {key}, current input: {self.new_symbol}")
                            return
    
    def draw(self) -> None:
        """Draw the add ticker screen."""
        # Fill background with black
        self.display.surface.fill(self.background_color)
        
        # Draw "Add New Ticker" text
        title_text = self.fonts['title-md'].render("Add New Ticker", True, AppConfig.WHITE)
        title_rect = title_text.get_rect(centerx=self.width//2, top=20)
        self.display.surface.blit(title_text, title_rect)
        
        # Draw input box
        input_rect = pygame.Rect(
            (self.width - 300) // 2,
            self.height * 0.2,
            300,
            60
        )
        pygame.draw.rect(self.display.surface, AppConfig.INPUT_BG_COLOR, input_rect)
        pygame.draw.rect(self.display.surface, AppConfig.CELL_BORDER_COLOR, input_rect, 1)
        
        if self.new_symbol:
            input_text = self.fonts['medium'].render(self.new_symbol, True, AppConfig.WHITE)
        else:
            input_text = self.fonts['medium'].render("Enter Symbol", True, AppConfig.PLACEHOLDER_COLOR)
        
        input_text_rect = input_text.get_rect(center=input_rect.center)
        self.display.surface.blit(input_text, input_text_rect)
        
        # Draw keyboard
        for row in self.key_rects:
            for key, rect in row:
                pygame.draw.rect(self.display.surface, AppConfig.KEY_BG_COLOR, rect)
                pygame.draw.rect(self.display.surface, AppConfig.KEY_BORDER_COLOR, rect, 1)
                
                key_text = self.fonts['medium'].render(key, True, AppConfig.WHITE)
                key_text_rect = key_text.get_rect(center=rect.center)
                self.display.surface.blit(key_text, key_text_rect)
        
        # Draw buttons
        pygame.draw.rect(self.display.surface, AppConfig.CANCEL_BUTTON_COLOR, self.cancel_rect)
        cancel_text = self.fonts['medium'].render("Cancel", True, AppConfig.WHITE)
        cancel_text_rect = cancel_text.get_rect(center=self.cancel_rect.center)
        self.display.surface.blit(cancel_text, cancel_text_rect)
        
        save_color = AppConfig.DONE_BUTTON_ACTIVE_COLOR if self.new_symbol else AppConfig.DONE_BUTTON_INACTIVE_COLOR
        pygame.draw.rect(self.display.surface, save_color, self.save_rect)
        save_text = self.fonts['medium'].render("Save", True, AppConfig.WHITE)
        save_text_rect = save_text.get_rect(center=self.save_rect.center)
        self.display.surface.blit(save_text, save_text_rect)
        
        self.update_screen() 