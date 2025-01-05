import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen
from ..services.crypto.crypto_manager import CryptoManager
from ..components.keyboard import VirtualKeyboard

logger = get_logger(__name__)

class AddTickerScreen(BaseScreen):
    def __init__(self, display) -> None:
        super().__init__(display)
        self.background_color = AppConfig.BLACK
        self.crypto_manager = CryptoManager()
        self.error_message = None
        
        # Button dimensions
        self.button_width = AppConfig.BUTTON_WIDTH
        self.button_height = AppConfig.BUTTON_HEIGHT
        self.button_spacing = AppConfig.BUTTON_MARGIN
        
        # Create keyboard
        self.keyboard = VirtualKeyboard(self.display.surface, self.fonts)
        self.keyboard.on_change = self._on_text_change
        
        # Create buttons
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
        
        logger.info("AddTickerScreen initialized")
    
    def _on_text_change(self, text: str):
        """Handle keyboard text changes."""
        self.error_message = None
    
    def add_ticker(self) -> None:
        """Add a new ticker."""
        symbol = self.keyboard.get_text().strip().upper()
        if not symbol:
            self.error_message = "Please enter a symbol"
            return
            
        try:
            success = self.crypto_manager.add_coin(symbol)
            if success:
                logger.info(f"Successfully added ticker: {symbol}")
                self.screen_manager.switch_screen('settings')
            else:
                self.error_message = f"Could not find coin: {symbol}"
        except Exception as e:
            logger.error(f"Error adding ticker: {e}")
            self.error_message = "Error adding ticker"
    
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
                if self.keyboard.get_text():
                    self.add_ticker()
                    if not self.error_message:
                        self.screen_manager.switch_screen('settings')
            else:
                # Handle keyboard input
                self.keyboard.handle_input(x, y)
    
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
        
        current_text = self.keyboard.get_text()
        if current_text:
            input_text = self.fonts['medium'].render(current_text, True, AppConfig.WHITE)
        else:
            input_text = self.fonts['medium'].render("Enter Symbol", True, AppConfig.PLACEHOLDER_COLOR)
        
        input_text_rect = input_text.get_rect(center=input_rect.center)
        self.display.surface.blit(input_text, input_text_rect)
        
        # Draw error message if any
        if self.error_message:
            error_surface = self.fonts['medium'].render(self.error_message, True, AppConfig.RED)
            error_rect = error_surface.get_rect(
                centerx=self.width // 2,
                top=input_rect.bottom + 10
            )
            self.display.surface.blit(error_surface, error_rect)
        
        # Draw keyboard
        self.keyboard.draw()
        
        # Draw buttons
        pygame.draw.rect(self.display.surface, AppConfig.CANCEL_BUTTON_COLOR, self.cancel_rect)
        cancel_text = self.fonts['medium'].render("Cancel", True, AppConfig.WHITE)
        cancel_text_rect = cancel_text.get_rect(center=self.cancel_rect.center)
        self.display.surface.blit(cancel_text, cancel_text_rect)
        
        save_color = AppConfig.DONE_BUTTON_ACTIVE_COLOR if self.keyboard.get_text() else AppConfig.DONE_BUTTON_INACTIVE_COLOR
        pygame.draw.rect(self.display.surface, save_color, self.save_rect)
        save_text = self.fonts['medium'].render("Save", True, AppConfig.WHITE)
        save_text_rect = save_text.get_rect(center=self.save_rect.center)
        self.display.surface.blit(save_text, save_text_rect)
        
        self.update_screen() 