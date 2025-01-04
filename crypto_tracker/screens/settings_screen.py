import pygame
import time
from ..services.screen_manager import Screen

class SettingsScreen(Screen):
    def __init__(self, screen_manager, ticker_screen):
        super().__init__(screen_manager)
        self.ticker_screen = ticker_screen
        self.crypto_api = ticker_screen.crypto_api
        
        # Grid settings
        self.grid_size = 3  # 3 columns
        self.cell_padding = 25  # Slightly reduced padding for 3 rows
        
        # Calculate usable space
        self.title_height = 80  # Reduced title height
        self.button_area_height = 80
        usable_height = self.height - self.title_height - self.button_area_height
        
        # Calculate cell dimensions to fill space evenly
        self.num_rows = 3  # Changed to 3 rows
        self.cell_width = (self.width - (self.cell_padding * (self.grid_size + 1))) // self.grid_size
        self.cell_height = (usable_height - (self.cell_padding * (self.num_rows + 1))) // self.num_rows
        
        # Colors
        self.cell_bg_color = (30, 30, 30)  # Very light black/grey
        self.cell_border_color = (45, 45, 45)  # Slightly brighter than background
        self.cell_highlight_color = (0, 255, 0, 80)  # Very transparent green for hover effect
        
        # Store cell rectangles for hit testing
        self.cell_rects = []
        self._create_cell_rects()
        
        # Create back button
        button_width = 120
        button_height = 50
        self.back_button = pygame.Rect(
            (self.width - button_width) // 2,
            self.height - button_height - 20,
            button_width,
            button_height
        )
        
        # Long press detection
        self.press_start_time = 0
        self.long_press_duration = 0.5  # seconds
        self.pressed_cell_index = None
        self.showing_delete_confirm = False
        
        # Delete confirmation buttons
        confirm_width = 120
        confirm_height = 50
        padding = 20
        total_width = (confirm_width * 2) + (padding * 3)
        start_x = (self.width - total_width) // 2
        
        self.delete_confirm_rect = pygame.Rect(
            start_x,
            self.height // 2 - confirm_height - padding,
            confirm_width * 2 + padding,
            confirm_height * 2 + padding
        )
        
        self.confirm_delete_rect = pygame.Rect(
            start_x + padding,
            self.height // 2 - confirm_height // 2,
            confirm_width,
            confirm_height
        )
        
        self.cancel_delete_rect = pygame.Rect(
            start_x + confirm_width + padding * 2,
            self.height // 2 - confirm_height // 2,
            confirm_width,
            confirm_height
        )

    def _create_cell_rects(self):
        start_x = self.cell_padding
        start_y = self.title_height + self.cell_padding  # Start below title
        
        # Create a 3x2 grid of cells
        for row in range(self.num_rows):
            for col in range(self.grid_size):
                x = start_x + col * (self.cell_width + self.cell_padding)
                y = start_y + row * (self.cell_height + self.cell_padding)
                self.cell_rects.append(pygame.Rect(x, y, self.cell_width, self.cell_height))

    def add_ticker(self, symbol):
        """Add a new ticker and update the ticker screen's symbols"""
        if self.crypto_api.add_ticker(symbol):
            self.ticker_screen.symbols = self.crypto_api.get_tracked_symbols()

    def handle_event(self, event):
        if not hasattr(event, 'x') or not hasattr(event, 'y'):
            return

        x = int(event.x * self.width)
        y = int(event.y * self.height)

        if event.type == pygame.FINGERDOWN:
            if self.showing_delete_confirm:
                # Handle delete confirmation
                if self.confirm_delete_rect.collidepoint(x, y):
                    symbol = self.ticker_screen.symbols[self.pressed_cell_index]
                    if self.crypto_api.remove_ticker(symbol):
                        self.ticker_screen.symbols = self.crypto_api.get_tracked_symbols()
                    self.showing_delete_confirm = False
                    self.pressed_cell_index = None
                elif self.cancel_delete_rect.collidepoint(x, y) or not self.delete_confirm_rect.collidepoint(x, y):
                    self.showing_delete_confirm = False
                    self.pressed_cell_index = None
                return
            
            # Check for back button press
            if self.back_button.collidepoint(x, y):
                self.manager.switch_to('ticker')
                return
            
            # Check for cell press
            for i, rect in enumerate(self.cell_rects):
                if rect.collidepoint(x, y):
                    if i < len(self.ticker_screen.symbols):
                        # Start long press detection for existing symbol
                        self.press_start_time = time.time()
                        self.pressed_cell_index = i
                    else:
                        # Add new symbol
                        self.manager.switch_to('keyboard')
                    break
                    
        elif event.type == pygame.FINGERUP:
            # Check if it was a long press
            if self.pressed_cell_index is not None:
                press_duration = time.time() - self.press_start_time
                if press_duration >= self.long_press_duration:
                    self.showing_delete_confirm = True
                self.press_start_time = 0

    def _draw_plus_icon(self, cell_rect):
        # Calculate plus dimensions
        plus_thickness = 2  # Even thinner lines
        plus_size = min(cell_rect.width, cell_rect.height) // 5  # Smaller plus icon
        
        # Calculate center position
        center_x = cell_rect.centerx
        center_y = cell_rect.centery
        
        # Draw plus in a slightly brighter color than the border
        color = (60, 60, 60)
        
        # Draw horizontal line
        horizontal_rect = pygame.Rect(
            center_x - plus_size//2,
            center_y - plus_thickness//2,
            plus_size,
            plus_thickness
        )
        pygame.draw.rect(self.screen, color, horizontal_rect, border_radius=1)
        
        # Draw vertical line
        vertical_rect = pygame.Rect(
            center_x - plus_thickness//2,
            center_y - plus_size//2,
            plus_thickness,
            plus_size
        )
        pygame.draw.rect(self.screen, color, vertical_rect, border_radius=1)

    def draw(self):
        self.screen.fill(self.manager.BLACK)
        
        # Draw title (smaller)
        title_font = pygame.font.Font(None, 48)  # Reduced from 72
        title_text = title_font.render("Tracked Symbols", True, self.manager.WHITE)
        title_rect = title_text.get_rect(centerx=self.width//2, y=self.title_height//2)
        self.screen.blit(title_text, title_rect)
        
        # Draw grid
        for i, cell_rect in enumerate(self.cell_rects):
            # Draw cell background
            pygame.draw.rect(self.screen, self.cell_bg_color, cell_rect, border_radius=10)
            # Draw cell border
            pygame.draw.rect(self.screen, self.cell_border_color, cell_rect, 1, border_radius=10)
            
            # If we have a symbol for this cell, draw it
            if i < len(self.ticker_screen.symbols):
                symbol = self.ticker_screen.symbols[i]
                symbol_font = pygame.font.Font(None, 48)  # Reduced from 72
                symbol_text = symbol_font.render(symbol, True, self.manager.WHITE)
                symbol_rect = symbol_text.get_rect(center=cell_rect.center)
                self.screen.blit(symbol_text, symbol_rect)
                
                # Show visual feedback for long press
                if i == self.pressed_cell_index and not self.showing_delete_confirm:
                    if time.time() - self.press_start_time >= self.long_press_duration:
                        pygame.draw.rect(self.screen, (255, 0, 0, 128), cell_rect, 2, border_radius=10)
            else:
                # Draw plus icon for empty cells
                self._draw_plus_icon(cell_rect)
        
        # Draw back button
        pygame.draw.rect(self.screen, self.cell_bg_color, self.back_button, border_radius=25)
        pygame.draw.rect(self.screen, self.cell_border_color, self.back_button, 1, border_radius=25)
        back_text = pygame.font.Font(None, 36).render("Back", True, self.manager.WHITE)
        back_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_rect)
        
        # Draw delete confirmation overlay
        if self.showing_delete_confirm:
            # Draw semi-transparent background
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            
            # Draw confirmation dialog background
            pygame.draw.rect(self.screen, (40, 40, 40), self.delete_confirm_rect, border_radius=15)
            pygame.draw.rect(self.screen, (60, 60, 60), self.delete_confirm_rect, 1, border_radius=15)
            
            # Draw message
            symbol = self.ticker_screen.symbols[self.pressed_cell_index]
            message_font = pygame.font.Font(None, 36)
            message_text = message_font.render(f"Delete {symbol}?", True, self.manager.WHITE)
            message_rect = message_text.get_rect(centerx=self.width//2, bottom=self.height//2 - 10)
            self.screen.blit(message_text, message_rect)
            
            # Draw confirm button
            pygame.draw.rect(self.screen, (180, 0, 0), self.confirm_delete_rect, border_radius=10)
            confirm_text = pygame.font.Font(None, 36).render("Delete", True, self.manager.WHITE)
            confirm_rect = confirm_text.get_rect(center=self.confirm_delete_rect.center)
            self.screen.blit(confirm_text, confirm_rect)
            
            # Draw cancel button
            pygame.draw.rect(self.screen, self.cell_bg_color, self.cancel_delete_rect, border_radius=10)
            pygame.draw.rect(self.screen, self.cell_border_color, self.cancel_delete_rect, 1, border_radius=10)
            cancel_text = pygame.font.Font(None, 36).render("Cancel", True, self.manager.WHITE)
            cancel_rect = cancel_text.get_rect(center=self.cancel_delete_rect.center)
            self.screen.blit(cancel_text, cancel_rect) 