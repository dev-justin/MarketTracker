import pygame
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen

logger = get_logger(__name__)

class SettingsScreen(BaseScreen):
    """Screen for displaying and modifying application settings."""
    
    def __init__(self, display) -> None:
        """Initialize the settings screen."""
        super().__init__(display)
        self.background_color = (0, 0, 0)  # Pure black
        self.grid_color = (0, 255, 0)      # Bright green
        self.grid_cols = 5  # 5 columns
        self.grid_rows = 2  # 2 rows
        self.padding = 40   # Increased padding for better spacing
        
        # Calculate grid layout
        usable_width = self.width - (2 * self.padding)
        usable_height = self.height - (2 * self.padding) - 100  # Account for title
        
        # Calculate cell size to maintain aspect ratio
        self.cell_width = usable_width // self.grid_cols
        self.cell_height = usable_height // self.grid_rows
        
        # Center the grid
        self.grid_start_x = (self.width - (self.cell_width * self.grid_cols)) // 2
        self.grid_start_y = 100  # Start below title
        
        # Input state
        self.is_adding_coin = False
        self.new_symbol = ""
        
        # Button dimensions
        self.button_width = 120
        self.button_height = 50
        self.button_spacing = 20
        
        logger.info("SettingsScreen initialized")
    
    def _draw_buttons(self, surface: pygame.Surface):
        """Draw Cancel and Save buttons."""
        # Calculate button positions
        total_width = (2 * self.button_width) + self.button_spacing
        start_x = (self.width - total_width) // 2
        button_y = self.height - self.button_height - 30  # 30px from bottom
        
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
        """Handle pygame events."""
        if not self.is_adding_coin:
            # Handle touch events
            is_double_tap, is_swipe_up = self.gesture_handler.handle_touch_event(event, self.height)
            if is_double_tap or is_swipe_up:  # Either gesture returns to dashboard
                logger.info("Returning to dashboard")
                self.screen_manager.switch_screen('dashboard')
            elif event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
                # Check if plus button was clicked
                x, y = self._scale_touch_input(event)
                cell_x = (x - self.grid_start_x) // self.cell_width
                cell_y = (y - self.grid_start_y) // self.cell_height
                
                if (0 <= cell_x < self.grid_cols and 
                    0 <= cell_y < self.grid_rows):
                    cell_index = cell_y * self.grid_cols + cell_x
                    if cell_index >= len(self.crypto_service.tracked_symbols):
                        logger.info("Add button clicked, switching to add ticker screen")
                        self.screen_manager.switch_screen('add_ticker')
        else:
            if event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
                x, y = self._scale_touch_input(event)
                
                # Check if save button was pressed
                if self.save_rect.collidepoint(x, y):
                    if self.new_symbol:
                        logger.info(f"Adding new coin: {self.new_symbol}")
                        self.crypto_service.add_tracked_symbol(self.new_symbol)
                    self.is_adding_coin = False
                    self.new_symbol = ""
                # Check if cancel button was pressed
                elif self.cancel_rect.collidepoint(x, y):
                    self.is_adding_coin = False
                    self.new_symbol = ""
                # Handle keyboard input
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.new_symbol = self.new_symbol[:-1]
                    elif event.unicode.isalnum() and len(self.new_symbol) < 5:
                        self.new_symbol += event.unicode.upper()

    def _draw_coin_cell(self, surface: pygame.Surface, x: int, y: int, symbol: str = None):
        """Draw a single cell in the grid."""
        margin = 10  # Space between cells
        cell_rect = pygame.Rect(
            x + margin//2, 
            y + margin//2, 
            self.cell_width - margin, 
            self.cell_height - margin
        )
        
        # Draw cell border
        pygame.draw.rect(surface, self.grid_color, cell_rect, 2, border_radius=10)
        
        if symbol:
            # Draw coin symbol
            text = self.fonts['bold-md'].render(symbol, True, self.grid_color)
            text_rect = text.get_rect(center=(x + self.cell_width//2, y + self.cell_height//2))
            surface.blit(text, text_rect)
        else:
            # Draw plus sign
            plus_size = min(self.cell_width//3, 30)
            plus_color = self.grid_color
            center_x = x + self.cell_width//2
            center_y = y + self.cell_height//2
            
            # Horizontal line
            pygame.draw.line(surface, plus_color, 
                           (center_x - plus_size//2, center_y),
                           (center_x + plus_size//2, center_y), 2)
            # Vertical line
            pygame.draw.line(surface, plus_color,
                           (center_x, center_y - plus_size//2),
                           (center_x, center_y + plus_size//2), 2)

    def draw(self) -> None:
        """Draw the settings screen."""
        # Fill background with black
        self.display.surface.fill(self.background_color)
        
        # Draw "Settings" text
        settings_text = self.fonts['title-lg'].render("Settings", True, AppConfig.WHITE)
        settings_rect = settings_text.get_rect(centerx=self.width//2, top=20)
        self.display.surface.blit(settings_text, settings_rect)
        
        # Draw grid
        tracked_symbols = self.crypto_service.tracked_symbols
        max_cells = self.grid_rows * self.grid_cols
        
        for i in range(max_cells):
            row = i // self.grid_cols
            col = i % self.grid_cols
            x = self.grid_start_x + (col * self.cell_width)
            y = self.grid_start_y + (row * self.cell_height)
            
            if i < len(tracked_symbols):
                self._draw_coin_cell(self.display.surface, x, y, tracked_symbols[i])
            elif i == len(tracked_symbols):
                self._draw_coin_cell(self.display.surface, x, y)  # Draw plus button
        
        # Draw keyboard overlay if adding coin
        if self.is_adding_coin:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.display.surface.blit(overlay, (0, 0))
            
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
            
            # Draw buttons
            self._draw_buttons(self.display.surface)
        
        self.update_screen() 