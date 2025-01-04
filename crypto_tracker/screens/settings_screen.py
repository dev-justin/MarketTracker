from typing import List, Optional, Tuple
import pygame
from ..config.settings import AppConfig
from ..constants import EventTypes, ScreenNames
from ..utils.logger import get_logger
from .base import Screen

logger = get_logger(__name__)

class SettingsScreen(Screen):
    """Screen for managing tracked symbols and application settings."""
    
    def __init__(self, screen_manager, ticker_screen) -> None:
        """Initialize the settings screen."""
        super().__init__(screen_manager)
        self.ticker_screen = ticker_screen
        self.crypto_api = ticker_screen.crypto_api
        
        # Grid settings
        self.grid_rows = AppConfig.GRID_ROWS
        self.grid_cols = AppConfig.GRID_COLS
        self.cell_padding = AppConfig.CELL_PADDING
        self.title_height = AppConfig.TITLE_HEIGHT
        
        # Button tracking
        self.edit_buttons = {}
        self.delete_buttons = {}
        
        # Calculate cell dimensions
        usable_height = self.height - self.title_height - AppConfig.BUTTON_AREA_HEIGHT
        self.cell_width = (self.width - (self.cell_padding * (self.grid_cols + 1))) // self.grid_cols
        self.cell_height = (usable_height - (self.cell_padding * (self.grid_rows + 1))) // self.grid_rows
        
        # Colors
        self.cell_bg_color = AppConfig.CELL_BG_COLOR
        self.cell_border_color = AppConfig.CELL_BORDER_COLOR
        self.cell_highlight_color = AppConfig.CELL_HIGHLIGHT_COLOR
        
        # Store cell rectangles for hit testing
        self.cell_rects: List[pygame.Rect] = []
        self._create_cell_rects()
        
        # Create back button
        button_width = AppConfig.BUTTON_WIDTH
        button_height = AppConfig.BUTTON_HEIGHT
        self.back_button = pygame.Rect(
            (self.width - button_width) // 2,
            self.height - button_height - AppConfig.BUTTON_MARGIN,
            button_width,
            button_height
        )
        
        # Action popup settings
        self.showing_action_popup = False
        self.selected_symbol_index = None
        self.is_editing = False
        
        # Action buttons
        action_width = 250
        action_height = 50
        padding = 30
        symbol_height = 40
        popup_width = action_width + (padding * 2)
        
        # Calculate popup height with more padding
        top_padding = padding * 2
        bottom_padding = padding * 2
        button_spacing = padding
        symbol_button_spacing = padding * 0.7
        
        popup_height = (
            top_padding +  # Top padding
            symbol_height +  # Symbol text
            symbol_button_spacing +  # Reduced space after symbol
            (action_height * 3) +  # Three buttons
            (button_spacing * 2) +  # Spacing between buttons
            bottom_padding  # Bottom padding
        )
        
        # Popup background
        self.action_popup_rect = pygame.Rect(
            (self.width - popup_width) // 2,
            (self.height - popup_height) // 2,
            popup_width,
            popup_height
        )
        
        # Action buttons - adjusted y positions with new spacing
        button_x = (self.width - action_width) // 2
        first_button_y = (
            self.action_popup_rect.top +
            top_padding +
            symbol_height +
            symbol_button_spacing
        )
        
        self.edit_button_rect = pygame.Rect(
            button_x,
            first_button_y,
            action_width,
            action_height
        )
        
        self.delete_button_rect = pygame.Rect(
            button_x,
            first_button_y + action_height + button_spacing,
            action_width,
            action_height
        )
        
        self.cancel_button_rect = pygame.Rect(
            button_x,
            first_button_y + (action_height + button_spacing) * 2,
            action_width,
            action_height
        )
        
        logger.info("SettingsScreen initialized")

    def _create_cell_rects(self) -> None:
        """Create rectangles for each cell in the grid."""
        start_x = self.cell_padding
        start_y = self.title_height + self.cell_padding
        
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                x = start_x + col * (self.cell_width + self.cell_padding)
                y = start_y + row * (self.cell_height + self.cell_padding)
                self.cell_rects.append(pygame.Rect(x, y, self.cell_width, self.cell_height))
        
        logger.debug(f"Created {len(self.cell_rects)} cell rectangles")

    def add_ticker(self, symbol: str) -> None:
        """
        Add a new ticker and update the ticker screen's symbols.
        
        Args:
            symbol: The symbol to add
        """
        if self.is_editing:
            # Remove old symbol first
            old_symbol = self.ticker_screen.symbols[self.selected_symbol_index]
            logger.info(f"Removing old symbol: {old_symbol}")
            self.crypto_api.remove_ticker(old_symbol)
            self.is_editing = False
            
        logger.info(f"Adding new symbol: {symbol}")
        if self.crypto_api.add_ticker(symbol):
            self.ticker_screen.symbols = self.crypto_api.get_tracked_symbols()
            logger.debug(f"Updated symbols: {self.ticker_screen.symbols}")

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events.
        
        Args:
            event: The pygame event to handle
        """
        x, y = self._scale_touch_input(event)
        
        if event.type == EventTypes.FINGER_DOWN.value:
            if self.showing_action_popup:
                self._handle_popup_touch(x, y)
            else:
                self._handle_screen_touch(x, y)

    def _handle_popup_touch(self, x: int, y: int) -> None:
        """
        Handle touch events when the action popup is showing.
        
        Args:
            x: Touch x coordinate
            y: Touch y coordinate
        """
        if self.edit_button_rect.collidepoint(x, y):
            logger.debug("Edit button pressed")
            self.is_editing = True
            self.showing_action_popup = False
            self.manager.switch_screen(ScreenNames.KEYBOARD.value)
        elif self.delete_button_rect.collidepoint(x, y):
            symbol = self.ticker_screen.symbols[self.selected_symbol_index]
            logger.info(f"Deleting symbol: {symbol}")
            if self.crypto_api.remove_ticker(symbol):
                self.ticker_screen.symbols = self.crypto_api.get_tracked_symbols()
            self.showing_action_popup = False
        elif self.cancel_button_rect.collidepoint(x, y) or not self.action_popup_rect.collidepoint(x, y):
            logger.debug("Action popup cancelled")
            self.showing_action_popup = False
            self.is_editing = False

    def _handle_screen_touch(self, x: int, y: int) -> None:
        """
        Handle touch events on the main screen.
        
        Args:
            x: Touch x coordinate
            y: Touch y coordinate
        """
        if self.back_button.collidepoint(x, y):
            logger.info("Back button pressed")
            self.manager.switch_screen(ScreenNames.TICKER.value)
            return
        
        for i, rect in enumerate(self.cell_rects):
            if rect.collidepoint(x, y):
                if i < len(self.ticker_screen.symbols):
                    logger.debug(f"Selected symbol at index {i}")
                    self.selected_symbol_index = i
                    self.showing_action_popup = True
                else:
                    logger.debug("Adding new symbol")
                    self.manager.switch_screen(ScreenNames.KEYBOARD.value)
                break

    def update(self, *args, **kwargs) -> None:
        """Update the screen state."""
        pass

    def draw(self, display: pygame.Surface) -> None:
        """
        Draw the screen contents.
        
        Args:
            display: The pygame surface to draw on
        """
        display.fill(AppConfig.BLACK)
        
        # Draw grid
        self._draw_grid(display)
        
        # Draw back button
        pygame.draw.rect(display, AppConfig.CELL_BG_COLOR, self.back_button, border_radius=10)
        pygame.draw.rect(display, AppConfig.CELL_BORDER_COLOR, self.back_button, 1, border_radius=10)
        back_text = self._create_text("Back", 'md', AppConfig.WHITE)
        back_rect = back_text.get_rect(center=self.back_button.center)
        display.blit(back_text, back_rect)
        
        # Draw action popup if active
        if self.showing_action_popup:
            self._draw_action_popup(display)

    def _draw_grid(self, display: pygame.Surface) -> None:
        """Draw the grid of symbols."""
        # Calculate grid dimensions
        cell_width = (self.width - (AppConfig.CELL_PADDING * (AppConfig.GRID_COLS + 1))) // AppConfig.GRID_COLS
        cell_height = (self.height - AppConfig.TITLE_HEIGHT - AppConfig.BUTTON_AREA_HEIGHT - (AppConfig.CELL_PADDING * (AppConfig.GRID_ROWS + 1))) // AppConfig.GRID_ROWS
        
        # Draw title
        self._draw_title(display)
        
        # Draw grid cells
        for i in range(len(self.ticker_screen.symbols) + 1):
            row = i // AppConfig.GRID_COLS
            col = i % AppConfig.GRID_COLS
            
            cell_rect = pygame.Rect(
                AppConfig.CELL_PADDING + (col * (cell_width + AppConfig.CELL_PADDING)),
                AppConfig.TITLE_HEIGHT + AppConfig.CELL_PADDING + (row * (cell_height + AppConfig.CELL_PADDING)),
                cell_width,
                cell_height
            )
            
            # Draw cell background
            pygame.draw.rect(display, AppConfig.CELL_BG_COLOR, cell_rect, border_radius=10)
            pygame.draw.rect(display, AppConfig.CELL_BORDER_COLOR, cell_rect, width=2, border_radius=10)
            
            if i < len(self.ticker_screen.symbols):
                self._draw_symbol(display, self.ticker_screen.symbols[i], cell_rect)
            else:
                self._draw_plus_icon(display, cell_rect)

    def _draw_symbol(self, display: pygame.Surface, symbol: str, cell_rect: pygame.Rect) -> None:
        """Draw a symbol in a grid cell."""
        # Draw symbol text
        symbol_text = self._create_text(symbol, 'lg', AppConfig.WHITE)
        text_rect = symbol_text.get_rect(center=cell_rect.center)
        display.blit(symbol_text, text_rect)
        
        # Draw edit button
        edit_rect = pygame.Rect(
            cell_rect.right - 30,
            cell_rect.top + 5,
            20,
            20
        )
        pygame.draw.rect(display, AppConfig.EDIT_BUTTON_COLOR, edit_rect)
        
        # Draw delete button
        delete_rect = pygame.Rect(
            cell_rect.right - 30,
            cell_rect.bottom - 25,
            20,
            20
        )
        pygame.draw.rect(display, AppConfig.DELETE_BUTTON_COLOR, delete_rect)
        
        # Store button positions for touch handling
        self.edit_buttons[symbol] = edit_rect
        self.delete_buttons[symbol] = delete_rect
    
    def _draw_title(self, display: pygame.Surface) -> None:
        """Draw the settings title."""
        title_text = self._create_text("Settings", 'title-lg', AppConfig.WHITE)
        title_rect = title_text.get_rect(centerx=self.width//2, top=20)
        display.blit(title_text, title_rect)
    
    def _draw_add_button(self, display: pygame.Surface) -> None:
        """Draw the add symbol button."""
        # Draw plus icon
        plus_text = self._create_text("+", 'title-lg', AppConfig.PLUS_ICON_COLOR)
        plus_rect = plus_text.get_rect(center=self.add_button_rect.center)
        display.blit(plus_text, plus_rect)
    
    def _draw_popup(self, display: pygame.Surface) -> None:
        """Draw the delete confirmation popup."""
        # Draw overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill(AppConfig.OVERLAY_COLOR)
        display.blit(overlay, (0, 0))
        
        # Draw popup background
        pygame.draw.rect(display, AppConfig.POPUP_BG_COLOR, self.popup_rect, border_radius=10)
        pygame.draw.rect(display, AppConfig.POPUP_BORDER_COLOR, self.popup_rect, width=2, border_radius=10)
        
        # Draw message
        message = f"Delete {self.symbol_to_delete}?"
        message_text = self._create_text(message, 'md', AppConfig.WHITE)
        message_rect = message_text.get_rect(centerx=self.popup_rect.centerx, top=self.popup_rect.top + 20)
        display.blit(message_text, message_rect)
        
        # Draw buttons
        confirm_text = self._create_text("Delete", 'md', AppConfig.WHITE)
        confirm_rect = confirm_text.get_rect(center=self.confirm_button_rect.center)
        display.blit(confirm_text, confirm_rect)
        
        cancel_text = self._create_text("Cancel", 'md', AppConfig.WHITE)
        cancel_rect = cancel_text.get_rect(center=self.cancel_button_rect.center)
        display.blit(cancel_text, cancel_rect)

    def _draw_plus_icon(self, display: pygame.Surface, cell_rect: pygame.Rect) -> None:
        """Draw a plus icon in a grid cell."""
        plus_text = self._create_text("+", 'title-lg', AppConfig.PLUS_ICON_COLOR)
        plus_rect = plus_text.get_rect(center=cell_rect.center)
        display.blit(plus_text, plus_rect)
        
        # Store add button position for touch handling
        self.add_button_rect = cell_rect.copy()

    def _draw_action_popup(self, display: pygame.Surface) -> None:
        """Draw the action popup."""
        # Draw semi-transparent background
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill(AppConfig.OVERLAY_COLOR)
        display.blit(overlay, (0, 0))
        
        # Draw popup background
        pygame.draw.rect(display, AppConfig.POPUP_BG_COLOR, self.action_popup_rect, border_radius=15)
        pygame.draw.rect(display, AppConfig.POPUP_BORDER_COLOR, self.action_popup_rect, 1, border_radius=15)
        
        # Draw symbol name
        symbol = self.ticker_screen.symbols[self.selected_symbol_index]
        symbol_text = self._create_text(symbol, 'lg', AppConfig.WHITE)
        symbol_rect = symbol_text.get_rect(centerx=self.width//2, top=self.action_popup_rect.top + 10)
        display.blit(symbol_text, symbol_rect)
        
        # Draw edit button
        pygame.draw.rect(display, AppConfig.EDIT_BUTTON_COLOR, self.edit_button_rect, border_radius=10)
        edit_text = self._create_text("Edit", 'md', AppConfig.WHITE)
        edit_rect = edit_text.get_rect(center=self.edit_button_rect.center)
        display.blit(edit_text, edit_rect)
        
        # Draw delete button
        pygame.draw.rect(display, AppConfig.DELETE_BUTTON_COLOR, self.delete_button_rect, border_radius=10)
        delete_text = self._create_text("Delete", 'md', AppConfig.WHITE)
        delete_rect = delete_text.get_rect(center=self.delete_button_rect.center)
        display.blit(delete_text, delete_rect)
        
        # Draw cancel button
        pygame.draw.rect(display, AppConfig.CELL_BG_COLOR, self.cancel_button_rect, border_radius=10)
        pygame.draw.rect(display, AppConfig.CELL_BORDER_COLOR, self.cancel_button_rect, 1, border_radius=10)
        cancel_text = self._create_text("Cancel", 'md', AppConfig.WHITE)
        cancel_rect = cancel_text.get_rect(center=self.cancel_button_rect.center)
        display.blit(cancel_text, cancel_rect) 