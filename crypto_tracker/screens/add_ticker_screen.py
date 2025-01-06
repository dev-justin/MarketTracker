"""Screen for adding a new ticker."""

import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen
from ..components.keyboard import VirtualKeyboard

logger = get_logger(__name__)

class AddTickerScreen(BaseScreen):
    """Screen for adding a new ticker."""
    
    def __init__(self, display) -> None:
        """Initialize the add ticker screen."""
        super().__init__(display)
        self.background_color = AppConfig.BLACK
        self.error_message = None
        
        # Button dimensions
        self.button_width = AppConfig.BUTTON_WIDTH
        self.button_height = AppConfig.BUTTON_HEIGHT
        self.button_spacing = AppConfig.BUTTON_MARGIN
        
        # Create keyboard
        self.keyboard = VirtualKeyboard(self.display.surface, self.display)
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
                self.error_message = f"Could not find {symbol}"
        except Exception as e:
            logger.error(f"Error adding ticker: {e}")
            self.error_message = "Error adding ticker"
    
    def draw(self) -> None:
        """Draw the add ticker screen."""
        # Fill background
        self.display.surface.fill(self.background_color)
        
        # Draw header
        header_text = "Add Coin"
        header_font = self.display.get_title_font('md', 'bold')
        header_surface = header_font.render(header_text, True, AppConfig.WHITE)
        header_rect = header_surface.get_rect(
            centerx=self.width // 2,
            top=20
        )
        self.display.surface.blit(header_surface, header_rect)
        
        # Draw input box
        input_box_height = 50
        input_box_width = self.width - 40  # 20px padding on each side
        input_box_rect = pygame.Rect(
            20,
            header_rect.bottom + 30,
            input_box_width,
            input_box_height
        )
        
        # Draw input box background
        pygame.draw.rect(
            self.display.surface,
            (45, 45, 45),  # Dark gray background
            input_box_rect,
            border_radius=10
        )
        
        # Draw current input text
        input_text = self.keyboard.get_text().upper()
        if not input_text:
            # Draw placeholder
            input_text = "Enter coin symbol"
            text_color = (128, 128, 128)  # Gray for placeholder
        else:
            text_color = AppConfig.WHITE
        
        input_font = self.display.get_text_font('lg', 'regular')
        input_surface = input_font.render(input_text, True, text_color)
        input_text_rect = input_surface.get_rect(
            center=input_box_rect.center
        )
        self.display.surface.blit(input_surface, input_text_rect)
        
        # Draw keyboard
        self.keyboard.draw()
        
        # Draw error message if any
        if self.error_message:
            error_font = self.display.get_text_font('md', 'bold')
            error_surface = error_font.render(self.error_message, True, AppConfig.RED)
            error_rect = error_surface.get_rect(
                centerx=self.width // 2,
                centery=self.save_rect.centery
            )
            self.display.surface.blit(error_surface, error_rect)
        
        # Draw buttons
        button_color = (45, 45, 45)  # Dark gray
        corner_radius = self.button_height // 2  # Fully rounded corners
        
        # Cancel button
        pygame.draw.rect(
            self.display.surface,
            button_color,
            self.cancel_rect,
            border_radius=corner_radius
        )
        cancel_text = "Cancel"
        cancel_font = self.display.get_text_font('md', 'regular')
        cancel_surface = cancel_font.render(cancel_text, True, AppConfig.WHITE)
        cancel_text_rect = cancel_surface.get_rect(center=self.cancel_rect.center)
        self.display.surface.blit(cancel_surface, cancel_text_rect)
        
        # Save button
        pygame.draw.rect(
            self.display.surface,
            button_color,
            self.save_rect,
            border_radius=corner_radius
        )
        save_text = "Save"
        save_font = self.display.get_text_font('md', 'regular')
        save_surface = save_font.render(save_text, True, AppConfig.WHITE)
        save_text_rect = save_surface.get_rect(center=self.save_rect.center)
        self.display.surface.blit(save_surface, save_text_rect)
        
        self.update_screen()
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        gestures = self.gesture_handler.handle_touch_event(event)
        
        if gestures['swipe_down']:
            logger.info("Swipe down detected, returning to settings")
            self.screen_manager.switch_screen('settings')
        elif event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            x, y = self._scale_touch_input(event)
            
            # Check keyboard input first
            if self.keyboard.handle_input(x, y):
                return
            
            if self.cancel_rect.collidepoint(x, y):
                logger.info("Cancel button clicked")
                self.screen_manager.switch_screen('settings')
            elif self.save_rect.collidepoint(x, y):
                logger.info("Save button clicked")
                self.add_ticker() 