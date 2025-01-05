import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class VirtualKeyboard:
    """A reusable virtual keyboard component."""
    
    def __init__(self, surface: pygame.Surface, fonts: dict, max_length: int = 5):
        self.surface = surface
        self.fonts = fonts
        self.max_length = max_length
        self.text = ""
        self.on_change = None
        
        # Keyboard layout
        self.keys = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'DEL']
        ]
        
        # Calculate dimensions
        self.width = surface.get_width()
        self.height = surface.get_height()
        self.setup_keyboard()
        
        logger.info("Virtual keyboard initialized")
    
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
    
    def handle_input(self, x: float, y: float) -> bool:
        """
        Handle touch input at the given coordinates.
        Returns True if input was handled, False otherwise.
        """
        for row in self.key_rects:
            for key, rect in row:
                if rect.collidepoint(x, y):
                    if key == 'DEL':
                        if self.text:
                            self.text = self.text[:-1]
                            logger.debug(f"Backspace pressed, current input: {self.text}")
                    elif len(self.text) < self.max_length:
                        self.text += key
                        logger.debug(f"Key pressed: {key}, current input: {self.text}")
                    
                    if self.on_change:
                        self.on_change(self.text)
                    return True
        return False
    
    def draw(self):
        """Draw the keyboard on the surface."""
        # Draw keyboard
        for row in self.key_rects:
            for key, rect in row:
                pygame.draw.rect(self.surface, AppConfig.KEY_BG_COLOR, rect)
                pygame.draw.rect(self.surface, AppConfig.KEY_BORDER_COLOR, rect, 1)
                
                key_text = self.fonts['medium'].render(key, True, AppConfig.WHITE)
                key_text_rect = key_text.get_rect(center=rect.center)
                self.surface.blit(key_text, key_text_rect)
    
    def set_text(self, text: str):
        """Set the current text value."""
        self.text = text[:self.max_length]
        if self.on_change:
            self.on_change(self.text)
    
    def get_text(self) -> str:
        """Get the current text value."""
        return self.text
    
    def clear(self):
        """Clear the current text."""
        self.text = ""
        if self.on_change:
            self.on_change(self.text) 