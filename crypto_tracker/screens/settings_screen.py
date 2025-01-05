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
        self.grid_size = 5  # 5x5 grid
        self.padding = 20
        self.is_adding_coin = False
        self.new_symbol = ""  # For storing symbol being typed
        
        # Calculate grid layout
        usable_width = self.width - (2 * self.padding)
        usable_height = self.height - (2 * self.padding) - 80  # Account for title
        self.cell_size = min(usable_width // self.grid_size, usable_height // self.grid_size)
        self.grid_start_x = (self.width - (self.cell_size * self.grid_size)) // 2
        self.grid_start_y = 80  # Start below title
        
        logger.info("SettingsScreen initialized")
    
    def _draw_coin_cell(self, surface: pygame.Surface, x: int, y: int, symbol: str = None):
        """Draw a single cell in the grid."""
        rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
        
        # Draw cell border
        pygame.draw.rect(surface, self.grid_color, rect, 2, border_radius=10)
        
        if symbol:
            # Draw coin symbol
            text = self.fonts['bold-md'].render(symbol, True, self.grid_color)
            text_rect = text.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
            surface.blit(text, text_rect)
        else:
            # Draw plus sign
            plus_size = min(self.cell_size // 3, 30)
            plus_color = self.grid_color
            center_x = x + self.cell_size // 2
            center_y = y + self.cell_size // 2
            
            # Horizontal line
            pygame.draw.line(surface, plus_color, 
                           (center_x - plus_size//2, center_y),
                           (center_x + plus_size//2, center_y), 2)
            # Vertical line
            pygame.draw.line(surface, plus_color,
                           (center_x, center_y - plus_size//2),
                           (center_x, center_y + plus_size//2), 2)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        if self.is_adding_coin:
            # Handle keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Add the coin and exit keyboard mode
                    if self.new_symbol:
                        self.crypto_service.add_tracked_symbol(self.new_symbol)
                    self.is_adding_coin = False
                    self.new_symbol = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.new_symbol = self.new_symbol[:-1]
                elif event.unicode.isalnum() and len(self.new_symbol) < 5:
                    self.new_symbol += event.unicode.upper()
        else:
            # Handle touch events
            is_double_tap, is_swipe_up = self.gesture_handler.handle_touch_event(event, self.height)
            if is_double_tap or is_swipe_up:  # Either gesture returns to dashboard
                logger.info("Returning to dashboard")
                self.screen_manager.switch_screen('dashboard')
            elif event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
                # Check if plus button was clicked
                x, y = self._scale_touch_input(event)
                cell_x = (x - self.grid_start_x) // self.cell_size
                cell_y = (y - self.grid_start_y) // self.cell_size
                
                if (0 <= cell_x < self.grid_size and 
                    0 <= cell_y < self.grid_size):
                    cell_index = cell_y * self.grid_size + cell_x
                    if cell_index >= len(self.crypto_service.tracked_symbols):
                        logger.info("Add button clicked")
                        self.is_adding_coin = True
    
    def draw(self) -> None:
        """Draw the settings screen."""
        # Fill background with black
        self.display.surface.fill(self.background_color)
        
        # Draw "Settings" text
        settings_text = self.fonts['title-lg'].render("Settings", True, AppConfig.WHITE)
        settings_rect = settings_text.get_rect(centerx=self.width // 2, top=20)
        self.display.surface.blit(settings_text, settings_rect)
        
        # Draw grid
        tracked_symbols = self.crypto_service.tracked_symbols
        for i in range(self.grid_size * self.grid_size):
            row = i // self.grid_size
            col = i % self.grid_size
            x = self.grid_start_x + (col * self.cell_size)
            y = self.grid_start_y + (row * self.cell_size)
            
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
            input_y = (self.height - input_height) // 2
            
            pygame.draw.rect(self.display.surface, self.grid_color,
                           (input_x, input_y, input_width, input_height), 2, border_radius=10)
            
            # Draw entered text
            if self.new_symbol:
                text = self.fonts['bold-lg'].render(self.new_symbol, True, AppConfig.WHITE)
            else:
                text = self.fonts['light-md'].render("Enter Symbol", True, (128, 128, 128))
            text_rect = text.get_rect(center=(self.width // 2, input_y + input_height // 2))
            self.display.surface.blit(text, text_rect)
        
        self.update_screen() 