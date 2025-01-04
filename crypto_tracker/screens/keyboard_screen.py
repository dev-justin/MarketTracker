import pygame
from ..services.screen_manager import Screen

class KeyboardScreen(Screen):
    def __init__(self, screen_manager, callback):
        super().__init__(screen_manager)
        self.callback = callback
        self.input_text = ""
        self.max_length = 5  # Max ticker length
        
        # Keyboard layout
        self.keys = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '⌫']
        ]
        
        # Calculate key dimensions
        self.key_margin = 10
        usable_width = self.width - (2 * self.key_margin)
        self.key_width = (usable_width - (9 * self.key_margin)) // 10  # 10 keys in longest row
        self.key_height = 60
        
        # Calculate keyboard position
        self.keyboard_y = self.height // 2
        
        # Create key rectangles
        self.key_rects = {}
        self._create_key_rects()

    def _create_key_rects(self):
        for row_idx, row in enumerate(self.keys):
            # Center this row
            row_width = len(row) * self.key_width + (len(row) - 1) * self.key_margin
            start_x = (self.width - row_width) // 2
            y = self.keyboard_y + row_idx * (self.key_height + self.key_margin)
            
            for col_idx, key in enumerate(row):
                x = start_x + col_idx * (self.key_width + self.key_margin)
                self.key_rects[key] = pygame.Rect(x, y, self.key_width, self.key_height)

    def handle_event(self, event):
        if not hasattr(event, 'x') or not hasattr(event, 'y'):
            return

        x = int(event.x * self.width)
        y = int(event.y * self.height)

        if event.type == pygame.FINGERDOWN:
            # Check for key presses
            for key, rect in self.key_rects.items():
                if rect.collidepoint(x, y):
                    if key == '⌫':  # Backspace
                        if self.input_text:
                            self.input_text = self.input_text[:-1]
                    else:
                        if len(self.input_text) < self.max_length:
                            self.input_text += key
                    break
            
            # Check for done button
            if self.done_rect.collidepoint(x, y) and self.input_text:
                self.callback(self.input_text)
                self.manager.switch_to('settings')
            
            # Check for cancel button
            elif self.cancel_rect.collidepoint(x, y):
                self.manager.switch_to('settings')

    def draw(self):
        self.screen.fill(self.manager.BLACK)
        
        # Draw input field
        pygame.draw.rect(self.screen, (30, 30, 30), 
                        (50, 50, self.width - 100, 80), border_radius=10)
        
        if self.input_text:
            input_font = pygame.font.Font(None, 72)
            text_surface = input_font.render(self.input_text, True, self.manager.WHITE)
            text_rect = text_surface.get_rect(center=(self.width // 2, 90))
            self.screen.blit(text_surface, text_rect)
        else:
            # Draw placeholder
            placeholder_font = pygame.font.Font(None, 36)
            placeholder = placeholder_font.render("Enter ticker symbol", True, (100, 100, 100))
            placeholder_rect = placeholder.get_rect(center=(self.width // 2, 90))
            self.screen.blit(placeholder, placeholder_rect)
        
        # Draw keyboard
        for key, rect in self.key_rects.items():
            # Draw key background
            pygame.draw.rect(self.screen, (40, 40, 40), rect, border_radius=5)
            pygame.draw.rect(self.screen, (60, 60, 60), rect, 2, border_radius=5)
            
            # Draw key text
            key_font = pygame.font.Font(None, 36)
            text_surface = key_font.render(key, True, self.manager.WHITE)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
        
        # Draw done button
        self.done_rect = pygame.Rect(self.width - 160, self.height - 100, 120, 50)
        if self.input_text:  # Only show as active if we have input
            pygame.draw.rect(self.screen, (0, 100, 0), self.done_rect, border_radius=25)
        else:
            pygame.draw.rect(self.screen, (40, 40, 40), self.done_rect, border_radius=25)
        done_text = pygame.font.Font(None, 36).render("Done", True, self.manager.WHITE)
        done_rect = done_text.get_rect(center=self.done_rect.center)
        self.screen.blit(done_text, done_rect)
        
        # Draw cancel button
        self.cancel_rect = pygame.Rect(40, self.height - 100, 120, 50)
        pygame.draw.rect(self.screen, (100, 0, 0), self.cancel_rect, border_radius=25)
        cancel_text = pygame.font.Font(None, 36).render("Cancel", True, self.manager.WHITE)
        cancel_rect = cancel_text.get_rect(center=self.cancel_rect.center)
        self.screen.blit(cancel_text, cancel_rect) 