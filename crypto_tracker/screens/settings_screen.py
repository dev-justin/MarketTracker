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
        self.background_color = AppConfig.BLACK
        
        # Header dimensions
        self.header_height = 80
        self.padding = 20
        
        # Button dimensions
        self.button_width = AppConfig.BUTTON_WIDTH
        self.button_height = AppConfig.BUTTON_HEIGHT
        
        # Coin cell dimensions
        self.cell_height = 70
        self.cell_spacing = 10
        
        logger.info("SettingsScreen initialized")
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        # Handle touch events
        is_double_tap, is_swipe_up = self.gesture_handler.handle_touch_event(event, self.height)
        if is_double_tap or is_swipe_up:  # Either gesture returns to dashboard
            logger.info("Returning to dashboard")
            self.screen_manager.switch_screen('dashboard')
        elif event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            x, y = self._scale_touch_input(event)
            
            # Check if Add Ticker button was clicked
            if self.add_button_rect.collidepoint(x, y):
                logger.info("Add Ticker button clicked")
                self.screen_manager.switch_screen('add_ticker')

    def _draw_coin_cell(self, surface: pygame.Surface, y: int, symbol: str):
        """Draw a single coin cell."""
        # Calculate cell dimensions
        cell_width = self.width - (2 * self.padding)
        rect = pygame.Rect(
            self.padding,
            y,
            cell_width,
            self.cell_height
        )
        
        # Draw cell background and border
        pygame.draw.rect(surface, AppConfig.CELL_BG_COLOR, rect, 0, border_radius=10)
        pygame.draw.rect(surface, AppConfig.CELL_BORDER_COLOR, rect, 2, border_radius=10)
        
        # Draw coin symbol
        text = self.fonts['bold-md'].render(symbol, True, AppConfig.WHITE)
        text_rect = text.get_rect(centery=y + self.cell_height//2, left=self.padding + 20)
        surface.blit(text, text_rect)

    def draw(self) -> None:
        """Draw the settings screen."""
        # Fill background with black
        self.display.surface.fill(self.background_color)
        
        # Draw header background
        header_rect = pygame.Rect(0, 0, self.width, self.header_height)
        pygame.draw.rect(self.display.surface, AppConfig.CELL_BG_COLOR, header_rect)
        
        # Draw "Settings" text (left-aligned)
        settings_text = self.fonts['bold-lg'].render("Settings", True, AppConfig.WHITE)
        settings_rect = settings_text.get_rect(left=self.padding, centery=self.header_height//2)
        self.display.surface.blit(settings_text, settings_rect)
        
        # Draw "Add Ticker" button (right-aligned)
        self.add_button_rect = pygame.Rect(
            self.width - self.button_width - self.padding,
            (self.header_height - self.button_height) // 2,
            self.button_width,
            self.button_height
        )
        pygame.draw.rect(self.display.surface, AppConfig.GREEN, self.add_button_rect, 0, border_radius=10)
        add_text = self.fonts['bold-md'].render("Add Ticker", True, AppConfig.WHITE)
        add_text_rect = add_text.get_rect(center=self.add_button_rect.center)
        self.display.surface.blit(add_text, add_text_rect)
        
        # Draw tracked coins in a vertical stack
        start_y = self.header_height + self.padding
        tracked_symbols = self.crypto_service.tracked_symbols
        
        for symbol in tracked_symbols:
            self._draw_coin_cell(self.display.surface, start_y, symbol)
            start_y += self.cell_height + self.cell_spacing
        
        self.update_screen() 