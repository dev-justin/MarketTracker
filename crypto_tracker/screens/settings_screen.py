import pygame
import json
import os
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
        self.button_width = 200
        self.button_height = 60
        
        # Initialize tracked coins list
        self.tracked_coins = []
        
        # Load tracked coins
        self.load_tracked_coins()
        
        logger.info("SettingsScreen initialized")
    
    def on_screen_enter(self) -> None:
        """Called when entering the screen."""
        logger.info("Refreshing tracked coins list")
        self.load_tracked_coins()
    
    def load_tracked_coins(self) -> None:
        """Load tracked coins from json file."""
        try:
            if os.path.exists(AppConfig.TRACKED_COINS_FILE):
                with open(AppConfig.TRACKED_COINS_FILE, 'r') as f:
                    data = json.load(f)
                    # Ensure proper data structure
                    self.tracked_coins = []
                    for item in data:
                        if isinstance(item, dict) and 'id' in item and 'symbol' in item:
                            if 'favorite' not in item:
                                item['favorite'] = False
                            self.tracked_coins.append(item)
                        elif isinstance(item, str):
                            # Convert old format to new format
                            self.tracked_coins.append({
                                'id': item.lower(),
                                'symbol': item.upper(),
                                'favorite': False
                            })
            else:
                self.tracked_coins = []
        except Exception as e:
            logger.error(f"Error loading tracked coins: {e}")
            self.tracked_coins = []
    
    def save_tracked_coins(self) -> None:
        """Save tracked coins to json file."""
        try:
            os.makedirs(os.path.dirname(AppConfig.TRACKED_COINS_FILE), exist_ok=True)
            with open(AppConfig.TRACKED_COINS_FILE, 'w') as f:
                json.dump(self.tracked_coins, f, indent=2)
            logger.info("Tracked coins saved successfully")
        except Exception as e:
            logger.error(f"Error saving tracked coins: {e}")
    
    def _draw_coin_cell(self, surface: pygame.Surface, x: int, y: int, coin: dict) -> pygame.Rect:
        """Draw a single coin cell with rounded corners."""
        # Calculate cell dimensions and create rect
        rect = pygame.Rect(x, y, self.cell_width, self.cell_height)
        
        # Draw rounded rectangle background
        pygame.draw.rect(surface, AppConfig.CELL_BG_COLOR, rect, border_radius=self.corner_radius)
        pygame.draw.rect(surface, AppConfig.CELL_BORDER_COLOR, rect, 1, border_radius=self.corner_radius)
        
        # Draw coin logo if available
        logo_size = 40
        logo_margin = 10
        if 'image' in coin and coin['image']:
            try:
                logo_path = os.path.join(AppConfig.CACHE_DIR, f"{coin['id']}_logo.png")
                if os.path.exists(logo_path):
                    logo = pygame.image.load(logo_path)
                    logo = pygame.transform.scale(logo, (logo_size, logo_size))
                    logo_rect = logo.get_rect(
                        left=rect.left + logo_margin,
                        centery=rect.centery
                    )
                    surface.blit(logo, logo_rect)
            except Exception as e:
                logger.error(f"Error loading logo for {coin['id']}: {e}")
        
        # Draw coin name and symbol
        text_start_x = rect.left + logo_size + (logo_margin * 2)
        text_width = rect.right - text_start_x - logo_margin
        
        # Draw coin name
        name_text = coin.get('name', '')
        if len(name_text) > 15:  # Truncate long names
            name_text = name_text[:13] + '...'
        name_surface = self.fonts['sm'].render(name_text, True, AppConfig.WHITE)
        name_rect = name_surface.get_rect(
            left=text_start_x,
            top=rect.top + logo_margin
        )
        surface.blit(name_surface, name_rect)
        
        # Draw coin symbol
        symbol_text = coin.get('symbol', '').upper()
        symbol_surface = self.fonts['bold-sm'].render(symbol_text, True, AppConfig.GRAY)
        symbol_rect = symbol_surface.get_rect(
            left=text_start_x,
            top=name_rect.bottom + 5
        )
        surface.blit(symbol_surface, symbol_rect)
        
        # Draw edit icon (using "⚙" as a placeholder)
        edit_text = "⚙"
        edit_surface = self.fonts['md'].render(edit_text, True, AppConfig.GRAY)
        edit_rect = edit_surface.get_rect(
            right=rect.right - logo_margin,
            centery=rect.centery
        )
        surface.blit(edit_surface, edit_rect)
        
        # Draw favorite star if favorited
        if coin.get('favorite', False):
            star_text = "★"
            star_surface = self.fonts['md'].render(star_text, True, AppConfig.FAVORITE_ACTIVE_COLOR)
            star_rect = star_surface.get_rect(
                right=rect.right - logo_margin,
                top=rect.top + logo_margin
            )
            surface.blit(star_surface, star_rect)
        
        return rect
    
    def draw(self) -> None:
        """Draw the settings screen."""
        # Fill background
        self.display.surface.fill(self.background_color)
        
        # Draw header
        header_text = "Settings"
        header_surface = self.fonts['title-md'].render(header_text, True, AppConfig.WHITE)
        header_rect = header_surface.get_rect(
            centerx=self.width // 2,
            top=self.padding
        )
        self.display.surface.blit(header_surface, header_rect)
        
        # Draw tracked coins in a grid
        current_y = self.header_height + self.padding
        self.coin_rects = []  # Store rects for click detection
        
        for i, coin in enumerate(self.tracked_coins):
            if isinstance(coin, dict):
                column = i % self.columns
                x = self.padding + (column * (self.cell_width + self.padding))
                
                if column == 0 and i > 0:
                    current_y += self.cell_height + self.cell_spacing
                
                rect = self._draw_coin_cell(self.display.surface, x, current_y, coin)
                self.coin_rects.append((rect, coin))
        
        # Draw add button at the bottom
        button_y = self.height - self.button_height - self.padding
        self.add_button_rect = pygame.Rect(
            (self.width - self.button_width) // 2,
            button_y,
            self.button_width,
            self.button_height
        )
        pygame.draw.rect(self.display.surface, AppConfig.CELL_BG_COLOR, self.add_button_rect, border_radius=self.corner_radius)
        pygame.draw.rect(self.display.surface, AppConfig.CELL_BORDER_COLOR, self.add_button_rect, 1, border_radius=self.corner_radius)
        
        button_text = "Add Ticker"
        button_surface = self.fonts['medium'].render(button_text, True, AppConfig.WHITE)
        button_text_rect = button_surface.get_rect(center=self.add_button_rect.center)
        self.display.surface.blit(button_surface, button_text_rect)
        
        self.update_screen()
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        gestures = self.gesture_handler.handle_touch_event(event)
        
        if gestures['swipe_down']:
            logger.info("Swipe down detected, returning to dashboard")
            self.screen_manager.switch_screen('dashboard')
        elif event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            # Get touch position
            x, y = self._scale_touch_input(event)
            
            # Check if add button was clicked
            if self.add_button_rect.collidepoint(x, y):
                logger.info("Add button clicked, switching to add ticker screen")
                self.screen_manager.switch_screen('add_ticker')
            
            # Check if any coin cell was clicked
            for rect, coin in self.coin_rects:
                if rect.collidepoint(x, y):
                    logger.info(f"Coin {coin.get('id', 'unknown')} clicked, switching to edit screen")
                    self.screen_manager.switch_screen('edit_ticker', coin.get('id')) 