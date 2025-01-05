import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen

logger = get_logger(__name__)

class AddTickerScreen(BaseScreen):
    def __init__(self, display) -> None:
        super().__init__(display)
        self.background_color = (0, 0, 0)  # Pure black
        self.grid_color = (0, 255, 0)      # Bright green
        self.new_symbol = ""
        
        # Button dimensions
        self.button_width = 120
        self.button_height = 50
        self.button_spacing = 20
        
        # Keyboard layout
        self.keys = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '⌫']
        ]
        self.setup_keyboard()
        
        logger.info("AddTickerScreen initialized")
    
    def setup_keyboard(self):
        """Calculate keyboard layout dimensions."""
        keyboard_height = self.height // 2  # Take up bottom half of screen
        key_padding = 5
        num_rows = len(self.keys)
        
        # Calculate key sizes
        max_keys_in_row = max(len(row) for row in self.keys)
        self.key_width = (self.width - (key_padding * (max_keys_in_row + 1))) // max_keys_in_row
        self.key_height = (keyboard_height - (key_padding * (num_rows + 1))) // num_rows
        
        # Store key rectangles for hit detection
        self.key_rects = []
        y = self.height - keyboard_height + key_padding
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
    
    def _draw_keyboard(self, surface: pygame.Surface):
        """Draw the on-screen keyboard."""
        # Draw each key
        for row in self.key_rects:
            for key, rect in row:
                # Draw key background
                pygame.draw.rect(surface, self.grid_color, rect, 2, border_radius=5)
                
                # Draw key text
                text = self.fonts['bold-sm'].render(key, True, self.grid_color)
                text_rect = text.get_rect(center=rect.center)
                surface.blit(text, text_rect)
    
    def _draw_buttons(self, surface: pygame.Surface):
        """Draw Cancel and Save buttons."""
        # Calculate button positions
        total_width = (2 * self.button_width) + self.button_spacing
        start_x = (self.width - total_width) // 2
        button_y = self.key_rects[-1][0][1].bottom + 20  # Below keyboard
        
        # Cancel button (left)
        self.cancel_rect = pygame.Rect(
            start_x,
            button_y,
            self.button_width,
            self.button_height
        )
        pygame.draw.rect(surface, (255, 0, 0), self.cancel_rect, 2, border_radius=10)
        cancel_text = self.fonts['bold-md'].render("Cancel", True, (255, 0, 0))
        cancel_text_rect = cancel_text.get_rect(center=self.cancel_rect.center)
        surface.blit(cancel_text, cancel_text_rect)
        
        # Save button (right)
        self.save_rect = pygame.Rect(
            start_x + self.button_width + self.button_spacing,
            button_y,
            self.button_width,
            self.button_height
        )
        pygame.draw.rect(surface, self.grid_color, self.save_rect, 2, border_radius=10)
        save_text = self.fonts['bold-md'].render("Save", True, self.grid_color)
        save_text_rect = save_text.get_rect(center=self.save_rect.center)
        surface.blit(save_text, save_text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            x, y = self._scale_touch_input(event)
            
            # Check for key presses
            for row in self.key_rects:
                for key, rect in row:
                    if rect.collidepoint(x, y):
                        if key == '⌫':
                            if self.new_symbol:
                                self.new_symbol = self.new_symbol[:-1]
                        elif len(self.new_symbol) < 5:
                            self.new_symbol += key
                        logger.debug(f"Key pressed: {key}, current input: {self.new_symbol}")
                        return
            
            # Check if save button was pressed
            if self.save_rect.collidepoint(x, y):
                if self.new_symbol:
                    logger.info(f"Adding new coin: {self.new_symbol}")
                    self.crypto_service.add_tracked_symbol(self.new_symbol)
                self.screen_manager.switch_screen('settings')
            # Check if cancel button was pressed
            elif self.cancel_rect.collidepoint(x, y):
                self.screen_manager.switch_screen('settings')
    
    def draw(self) -> None:
        # Fill background with black
        self.display.surface.fill(self.background_color)
        
        # Draw "Enter Ticker" text
        title_text = self.fonts['title-lg'].render("Enter Ticker", True, AppConfig.WHITE)
        title_rect = title_text.get_rect(centerx=self.width//2, top=20)
        self.display.surface.blit(title_text, title_rect)
        
        # Draw input box
        input_width = 200
        input_height = 50
        input_x = (self.width - input_width) // 2
        input_y = self.height // 4  # Position in top quarter
        
        pygame.draw.rect(self.display.surface, self.grid_color,
                        (input_x, input_y, input_width, input_height), 2, border_radius=10)
        
        # Draw entered text or placeholder
        if self.new_symbol:
            text = self.fonts['bold-lg'].render(self.new_symbol, True, AppConfig.WHITE)
        else:
            text = self.fonts['light-md'].render("Enter Symbol", True, (128, 128, 128))
        text_rect = text.get_rect(center=(self.width//2, input_y + input_height//2))
        self.display.surface.blit(text, text_rect)
        
        # Draw keyboard and buttons
        self._draw_keyboard(self.display.surface)
        self._draw_buttons(self.display.surface)
        
        self.update_screen() 