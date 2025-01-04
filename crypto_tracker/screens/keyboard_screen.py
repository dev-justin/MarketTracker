from typing import Dict, Callable, Optional
import pygame
from ..config.settings import AppConfig
from ..constants import EventTypes, ScreenNames, KeyboardLayout
from ..utils.logger import get_logger
from .base import Screen

logger = get_logger(__name__)

class KeyboardScreen(Screen):
    """Screen for virtual keyboard input of ticker symbols."""
    
    def __init__(self, screen_manager, callback: Callable[[str], None]) -> None:
        """
        Initialize the keyboard screen.
        
        Args:
            screen_manager: The screen manager instance
            callback: Function to call with the entered text when done
        """
        super().__init__(screen_manager)
        self.callback = callback
        self.input_text: str = ""
        self.max_length: int = AppConfig.MAX_TICKER_LENGTH
        
        # Keyboard layout (removed numbers)
        self.keys: list[list[str]] = KeyboardLayout.ROWS
        
        # Calculate key dimensions
        self.key_margin: int = AppConfig.KEY_MARGIN
        usable_width = self.width - (2 * self.key_margin)
        self.key_width: int = (usable_width - (9 * self.key_margin)) // 10  # 10 keys in longest row
        self.key_height: int = AppConfig.KEY_HEIGHT
        
        # Calculate keyboard position (moved up slightly since we removed a row)
        self.keyboard_y: int = self.height // 3
        
        # Button dimensions
        self.button_height: int = AppConfig.BUTTON_HEIGHT
        self.button_width: int = AppConfig.BUTTON_WIDTH
        self.button_margin: int = AppConfig.BUTTON_MARGIN
        
        # Store key rectangles for hit testing
        self.key_rects: Dict[str, pygame.Rect] = {}
        self._create_key_rects()
        
        # Create button rectangles
        self._create_button_rects()
        
        logger.info("KeyboardScreen initialized")

    def _create_key_rects(self) -> None:
        """Create rectangles for each key in the keyboard layout."""
        for row_idx, row in enumerate(self.keys):
            # Center this row
            row_width = len(row) * self.key_width + (len(row) - 1) * self.key_margin
            start_x = (self.width - row_width) // 2
            y = self.keyboard_y + row_idx * (self.key_height + self.key_margin)
            
            for col_idx, key in enumerate(row):
                x = start_x + col_idx * (self.key_width + self.key_margin)
                self.key_rects[key] = pygame.Rect(x, y, self.key_width, self.key_height)
        
        logger.debug(f"Created {len(self.key_rects)} key rectangles")

    def _create_button_rects(self) -> None:
        """Create rectangles for the Done and Cancel buttons."""
        # Position buttons at the bottom with proper spacing
        buttons_y = self.keyboard_y + (len(self.keys) * (self.key_height + self.key_margin)) + self.button_margin
        
        # Cancel button (left)
        self.cancel_button_rect = pygame.Rect(
            self.button_margin,
            buttons_y,
            self.button_width,
            self.button_height
        )
        
        # Done button (right)
        self.done_button_rect = pygame.Rect(
            self.width - self.button_width - self.button_margin,
            buttons_y,
            self.button_width,
            self.button_height
        )
        
        logger.debug("Created button rectangles")

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events.
        
        Args:
            event: The pygame event to handle
        """
        x, y = self._scale_touch_input(event)
        
        if event.type == EventTypes.FINGER_DOWN.value:
            self._handle_touch(x, y)

    def _handle_touch(self, x: int, y: int) -> None:
        """
        Handle touch events on the keyboard.
        
        Args:
            x: Touch x coordinate
            y: Touch y coordinate
        """
        # Check for key presses
        for key, rect in self.key_rects.items():
            if rect.collidepoint(x, y):
                if key == 'DEL':  # Backspace
                    if self.input_text:
                        logger.debug("Deleting last character")
                        self.input_text = self.input_text[:-1]
                else:
                    if len(self.input_text) < self.max_length:
                        logger.debug(f"Adding character: {key}")
                        self.input_text += key
                break
        
        # Check for done button
        if self.done_button_rect.collidepoint(x, y) and self.input_text:
            logger.info(f"Done pressed with input: {self.input_text}")
            self.callback(self.input_text)
            self.manager.switch_to(ScreenNames.SETTINGS.value)
        
        # Check for cancel button
        elif self.cancel_button_rect.collidepoint(x, y):
            logger.info("Cancel pressed")
            self.manager.switch_to(ScreenNames.SETTINGS.value)

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
        
        self._draw_input_field(display)
        self._draw_keyboard(display)
        self._draw_buttons(display)

    def _draw_input_field(self, display: pygame.Surface) -> None:
        """
        Draw the input field and current text.
        
        Args:
            display: The pygame surface to draw on
        """
        # Draw input field background
        pygame.draw.rect(
            display,
            AppConfig.INPUT_BG_COLOR,
            (50, 50, self.width - 100, 80),
            border_radius=10
        )
        
        if self.input_text:
            text_surface = self._create_text_surface(
                self.input_text,
                72,
                AppConfig.WHITE
            )
            text_rect = text_surface.get_rect(center=(self.width // 2, 90))
            display.blit(text_surface, text_rect)
        else:
            # Draw placeholder
            placeholder = self._create_text_surface(
                "Enter ticker symbol",
                36,
                AppConfig.PLACEHOLDER_COLOR
            )
            placeholder_rect = placeholder.get_rect(center=(self.width // 2, 90))
            display.blit(placeholder, placeholder_rect)

    def _draw_keyboard(self, display: pygame.Surface) -> None:
        """
        Draw the keyboard keys.
        
        Args:
            display: The pygame surface to draw on
        """
        for key, rect in self.key_rects.items():
            # Draw key background
            pygame.draw.rect(display, AppConfig.KEY_BG_COLOR, rect, border_radius=5)
            pygame.draw.rect(display, AppConfig.KEY_BORDER_COLOR, rect, 2, border_radius=5)
            
            # Draw key text
            text_surface = self._create_text_surface(key, 36, AppConfig.WHITE)
            text_rect = text_surface.get_rect(center=rect.center)
            display.blit(text_surface, text_rect)

    def _draw_buttons(self, display: pygame.Surface) -> None:
        """
        Draw the Done and Cancel buttons.
        
        Args:
            display: The pygame surface to draw on
        """
        # Draw Done button
        done_color = (AppConfig.DONE_BUTTON_ACTIVE_COLOR if self.input_text 
                     else AppConfig.DONE_BUTTON_INACTIVE_COLOR)
        pygame.draw.rect(display, done_color, self.done_button_rect, border_radius=10)
        done_text = self._create_text_surface("Done", 36, AppConfig.WHITE)
        done_rect = done_text.get_rect(center=self.done_button_rect.center)
        display.blit(done_text, done_rect)
        
        # Draw Cancel button
        pygame.draw.rect(display, AppConfig.CANCEL_BUTTON_COLOR, self.cancel_button_rect, border_radius=10)
        cancel_text = self._create_text_surface("Cancel", 36, AppConfig.WHITE)
        cancel_rect = cancel_text.get_rect(center=self.cancel_button_rect.center)
        display.blit(cancel_text, cancel_rect) 

    def _handle_done(self) -> None:
        """Handle the Done button press."""
        if self.input_text:
            logger.info(f"Keyboard input confirmed: {self.input_text}")
            self.callback(self.input_text)
            self.input_text = ""
            self.manager.switch_screen(ScreenNames.SETTINGS.value)
    
    def _handle_cancel(self) -> None:
        """Handle the Cancel button press."""
        logger.info("Keyboard input cancelled")
        self.input_text = ""
        self.manager.switch_screen(ScreenNames.SETTINGS.value) 