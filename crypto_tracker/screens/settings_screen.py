"""Screen for displaying and modifying application settings."""

import pygame
import os
import json
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
        
        # Grid settings
        self.columns = 2
        self.cell_width = (self.width - (self.padding * 3)) // 2  # 3 paddings: left, middle, right
        self.cell_height = 100
        self.cell_spacing = 15
        self.corner_radius = 10
        
        # Button dimensions
        self.button_width = 120  # Smaller width for Add Coin button
        self.button_height = 40
        
        # Pagination
        self.coins_per_page = 6
        self.current_page = 0
        
        # Initialize tracked coins list and click areas
        self.tracked_coins = []
        self.edit_icon_areas = []  # Store edit icon rects and associated coins
        
        # Load tracked coins
        self.load_tracked_coins()
        
        logger.info("SettingsScreen initialized")
    
    def on_screen_enter(self) -> None:
        """Called when entering the screen."""
        logger.info("Refreshing tracked coins list")
        self.load_tracked_coins()
        self.needs_redraw = True  # Let the screen manager handle the redraw
    
    def update(self) -> None:
        """Update screen state."""
        # Refresh tracked coins periodically
        self.load_tracked_coins()
        self.needs_redraw = True
    
    def load_tracked_coins(self) -> None:
        """Load tracked coins using crypto manager."""
        self.tracked_coins = self.crypto_manager.get_tracked_coins()
    
    def _draw_coin_cell(self, surface: pygame.Surface, x: int, y: int, coin: dict) -> tuple:
        """Draw a coin cell and return its rect and edit icon rect."""
        # Draw cell background
        rect = pygame.Rect(x, y, self.cell_width, self.cell_height)
        pygame.draw.rect(surface, (30, 30, 30), rect, border_radius=self.corner_radius)
        
        # Load coin logo if available
        logo = None
        logo_path = os.path.join(AppConfig.CACHE_DIR, f"{coin['symbol'].lower()}_logo.png")
        if os.path.exists(logo_path):
            try:
                logo = pygame.image.load(logo_path)
                logo = pygame.transform.scale(logo, (32, 32))
            except Exception as e:
                logger.error(f"Error loading logo for {coin['symbol']}: {e}")
        
        # Calculate text start position
        text_start_x = x + 15
        if logo:
            surface.blit(logo, (x + 15, y + (self.cell_height - 32) // 2))
            text_start_x = x + 60
        
        # Calculate total height of name + symbol for centering
        name_text = coin.get('name', '')
        if len(name_text) > 15:  # Truncate long names
            name_text = name_text[:13] + '...'
        name_font = self.display.get_text_font('md', 'regular')
        name_surface = name_font.render(name_text, True, AppConfig.WHITE)
        
        symbol_text = coin.get('symbol', '').upper()
        symbol_font = self.display.get_text_font('sm', 'regular')
        symbol_surface = symbol_font.render(symbol_text, True, AppConfig.GRAY)
        
        total_text_height = name_surface.get_height() + symbol_surface.get_height() + 5
        text_start_y = rect.centery - (total_text_height // 2)
        
        # Draw coin name
        name_rect = name_surface.get_rect(
            left=text_start_x,
            top=text_start_y
        )
        surface.blit(name_surface, name_rect)
        
        # Draw star if favorited
        if coin.get('favorite', False):
            star_icon = self.assets.get_icon('star', size=(24, 24), color=(255, 165, 0))
            if star_icon:
                star_rect = star_icon.get_rect(
                    left=name_rect.right + 10,
                    centery=name_rect.centery
                )
                surface.blit(star_icon, star_rect)
        
        # Draw symbol
        symbol_rect = symbol_surface.get_rect(
            left=text_start_x,
            top=name_rect.bottom + 5
        )
        surface.blit(symbol_surface, symbol_rect)
        
        # Draw edit icon (larger)
        edit_icon = self.assets.get_icon('edit', size=(48, 48))  # Increased from 32 to 48
        if edit_icon:
            # Create a larger touch area for the edit icon
            edit_touch_size = 60  # Even larger touch area
            edit_icon_rect = pygame.Rect(
                rect.right - edit_touch_size - 10,  # 10px from right edge
                rect.centery - edit_touch_size // 2,
                edit_touch_size,
                edit_touch_size
            )
            
            # Center the icon within its touch area
            icon_x = edit_icon_rect.centerx - edit_icon.get_width() // 2
            icon_y = edit_icon_rect.centery - edit_icon.get_height() // 2
            surface.blit(edit_icon, (icon_x, icon_y))
        else:
            edit_icon_rect = None
        
        return rect, edit_icon_rect, coin
    
    def next_page(self):
        """Move to next page of coins."""
        total_pages = (len(self.tracked_coins) + self.coins_per_page - 1) // self.coins_per_page
        if total_pages > 0:
            self.current_page = (self.current_page + 1) % total_pages
            logger.info(f"Moved to page {self.current_page + 1} of {total_pages}")
    
    def previous_page(self):
        """Move to previous page of coins."""
        total_pages = (len(self.tracked_coins) + self.coins_per_page - 1) // self.coins_per_page
        if total_pages > 0:
            self.current_page = (self.current_page - 1) % total_pages
            logger.info(f"Moved to page {self.current_page + 1} of {total_pages}")
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        gestures = self.gesture_handler.handle_touch_event(event)
        
        if gestures['swipe_down']:
            logger.info("Swipe down detected, returning to dashboard")
            self.screen_manager.switch_screen('dashboard')
        elif gestures['swipe_left']:
            logger.info("Swipe left detected, showing next page")
            self.next_page()
        elif gestures['swipe_right']:
            logger.info("Swipe right detected, showing previous page")
            self.previous_page()
        elif event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            x, y = self._scale_touch_input(event)
            
            # Check add button first
            if self.add_button_rect.collidepoint(x, y):
                logger.info("Add button clicked")
                self.screen_manager.switch_screen('add_ticker')
                return
            
            # Check edit icons
            for edit_rect, coin in self.edit_icon_areas:
                if edit_rect.collidepoint(x, y):
                    logger.info(f"Edit icon clicked for {coin['symbol']}")
                    self.screen_manager.switch_screen('edit_ticker', coin_id=coin['id'])
                    return
    
    def draw(self) -> None:
        """Draw the settings screen."""
        # Fill background
        self.display.surface.fill(self.background_color)
        
        # Draw header
        header_text = "My Settings"
        header_font = self.display.get_title_font('md')
        header_surface = header_font.render(header_text, True, AppConfig.WHITE)
        header_rect = header_surface.get_rect(
            left=self.padding,
            top=self.padding
        )
        self.display.surface.blit(header_surface, header_rect)
        
        # Draw add button in top right
        self.add_button_rect = pygame.Rect(
            self.width - self.button_width - self.padding,
            self.padding,
            self.button_width,
            self.button_height
        )
        
        pygame.draw.rect(
            self.display.surface,
            (45, 45, 45),
            self.add_button_rect,
            border_radius=10
        )
        
        add_text = "Add Coin"
        add_font = self.display.get_text_font('md', 'regular')
        add_surface = add_font.render(add_text, True, AppConfig.WHITE)
        add_rect = add_surface.get_rect(center=self.add_button_rect.center)
        self.display.surface.blit(add_surface, add_rect)
        
        # Draw tracked coins in a grid with pagination
        start_index = self.current_page * self.coins_per_page
        end_index = min(start_index + self.coins_per_page, len(self.tracked_coins))
        current_y = self.header_height + self.padding
        
        self.coin_rects = []  # Store rects for click detection
        self.edit_icon_areas = []  # Reset edit icon areas
        
        for i, coin in enumerate(self.tracked_coins[start_index:end_index]):
            if isinstance(coin, dict):
                column = i % self.columns
                x = self.padding + (column * (self.cell_width + self.padding))
                
                if column == 0 and i > 0:
                    current_y += self.cell_height + self.cell_spacing
                
                rect, edit_icon_rect, coin = self._draw_coin_cell(self.display.surface, x, current_y, coin)
                self.coin_rects.append((rect, coin))
                if edit_icon_rect:
                    self.edit_icon_areas.append((edit_icon_rect, coin))
        
        # Draw page indicator
        total_pages = (len(self.tracked_coins) + self.coins_per_page - 1) // self.coins_per_page
        if total_pages > 1:
            page_text = f"Page {self.current_page + 1} of {total_pages}"
            page_font = self.display.get_text_font('md', 'regular')
            page_surface = page_font.render(page_text, True, AppConfig.GRAY)
            page_rect = page_surface.get_rect(
                centerx=self.width // 2,
                bottom=self.height - self.padding
            )
            self.display.surface.blit(page_surface, page_rect) 