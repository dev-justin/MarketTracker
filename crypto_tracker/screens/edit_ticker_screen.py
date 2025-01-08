"""Screen for editing a tracked coin."""

import pygame
import os
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen

logger = get_logger(__name__)

class EditTickerScreen(BaseScreen):
    """Screen for editing a tracked coin."""
    
    def __init__(self, display) -> None:
        """Initialize the edit ticker screen."""
        super().__init__(display)
        self.background_color = AppConfig.BLACK
        self.current_coin = None
        
        # Button dimensions - narrower for right side
        self.button_width = int(self.width * 0.4)  # 40% of screen width
        self.button_height = 50  # Fixed height
        self.button_spacing = 30  # Increased vertical spacing between buttons
        
        # Calculate positions for stacked buttons on right side
        right_side_center = int(self.width * 0.75)
        button_y = int(self.height * 0.4)  # Start buttons at 40% of screen height
        
        # Create button rects
        self.favorite_rect = pygame.Rect(
            right_side_center - (self.button_width // 2),
            button_y,
            self.button_width,
            self.button_height
        )
        
        self.delete_rect = pygame.Rect(
            right_side_center - (self.button_width // 2),
            button_y + self.button_height + self.button_spacing,
            self.button_width,
            self.button_height
        )
        
        self.back_rect = pygame.Rect(
            right_side_center - (self.button_width // 2),
            button_y + (self.button_height + self.button_spacing) * 2,
            self.button_width,
            self.button_height
        )
        
        logger.info("EditTickerScreen initialized")
    
    def load_coin(self, coin_id: str) -> None:
        """Load coin data for editing."""
        # Try crypto storage first
        self.current_coin = self.crypto_manager.storage.get_coin(coin_id)
        if not self.current_coin:
            # If not found in crypto storage, try stock storage
            self.current_coin = self.crypto_manager.stock_service.storage.get_stock(coin_id)
            if not self.current_coin:
                logger.error(f"Could not load coin: {coin_id}")
                self.screen_manager.switch_screen('settings')
            else:
                logger.info(f"Loaded stock: {coin_id}")
        else:
            logger.info(f"Loaded crypto: {coin_id}")
    
    def delete_coin(self) -> None:
        """Delete the current coin."""
        if self.current_coin and self.crypto_manager.remove_coin(self.current_coin['id']):
            logger.info(f"Deleted coin: {self.current_coin['symbol']}")
            self.screen_manager.switch_screen('settings')
    
    def toggle_favorite(self) -> None:
        """Toggle favorite status for current coin."""
        if self.current_coin:
            if self.crypto_manager.toggle_favorite(self.current_coin['id']):
                # Get updated data from the appropriate storage
                if self.current_coin.get('type') == 'stock':
                    self.current_coin = self.crypto_manager.stock_service.storage.get_stock(self.current_coin['id'])
                else:
                    self.current_coin = self.crypto_manager.storage.get_coin(self.current_coin['id'])
                    
                logger.info(f"Toggled favorite state for {self.current_coin['symbol']}")
                # Force redraw to show updated state
                self.draw()
    
    def draw(self) -> None:
        """Draw the edit ticker screen."""
        if not self.current_coin:
            return
            
        # Fill background
        self.display.surface.fill(self.background_color)
        
        # Draw coin logo
        logo_size = 80  # Smaller logo size
        logo_path = os.path.join(AppConfig.CACHE_DIR, f"{self.current_coin['symbol'].lower()}_logo.png")
        if os.path.exists(logo_path):
            try:
                logo = pygame.image.load(logo_path)
                logo = pygame.transform.scale(logo, (logo_size, logo_size))
                logo_rect = logo.get_rect(
                    centerx=int(self.width * 0.25),  # Center in left half
                    top=int(self.height * 0.2)  # Position at 20% of screen height
                )
                self.display.surface.blit(logo, logo_rect)
            except Exception as e:
                logger.error(f"Error loading logo: {e}")
        
        # Draw coin name
        name_font = self.display.get_title_font('lg', 'bold')
        name_surface = name_font.render(self.current_coin['name'], True, AppConfig.WHITE)
        name_rect = name_surface.get_rect(
            centerx=int(self.width * 0.25),  # Center in left half
            top=int(self.height * 0.2) + logo_size + 20  # Below logo
        )
        self.display.surface.blit(name_surface, name_rect)
        
        # Draw coin symbol
        symbol_font = self.display.get_title_font('md', 'light')
        symbol_surface = symbol_font.render(self.current_coin['symbol'].upper(), True, AppConfig.GRAY)
        symbol_rect = symbol_surface.get_rect(
            centerx=int(self.width * 0.25),  # Center in left half
            top=name_rect.bottom + 10
        )
        self.display.surface.blit(symbol_surface, symbol_rect)
        
        # Draw star icon if favorited
        if self.current_coin.get('favorite', False):
            star_icon = self.assets.get_icon('star', size=(24, 24), color=(255, 165, 0))
            if star_icon:
                star_rect = star_icon.get_rect(
                    left=symbol_rect.right + 10,
                    centery=symbol_rect.centery
                )
                self.display.surface.blit(star_icon, star_rect)
        
        # Draw buttons
        button_color = (45, 45, 45)  # Dark gray
        corner_radius = self.button_height // 2  # Fully rounded corners
        
        # Favorite button
        pygame.draw.rect(
            self.display.surface,
            (255, 165, 0) if self.current_coin.get('favorite', False) else button_color,
            self.favorite_rect,
            border_radius=corner_radius
        )
        favorite_text = "Unfavorite" if self.current_coin.get('favorite', False) else "Favorite"
        favorite_font = self.display.get_text_font('md', 'regular')
        favorite_surface = favorite_font.render(favorite_text, True, AppConfig.WHITE)
        favorite_text_rect = favorite_surface.get_rect(center=self.favorite_rect.center)
        self.display.surface.blit(favorite_surface, favorite_text_rect)
        
        # Delete button
        pygame.draw.rect(
            self.display.surface,
            button_color,
            self.delete_rect,
            border_radius=corner_radius
        )
        delete_font = self.display.get_text_font('md', 'regular')
        delete_surface = delete_font.render("Delete", True, AppConfig.WHITE)
        delete_text_rect = delete_surface.get_rect(center=self.delete_rect.center)
        self.display.surface.blit(delete_surface, delete_text_rect)
        
        # Back button
        pygame.draw.rect(
            self.display.surface,
            button_color,
            self.back_rect,
            border_radius=corner_radius
        )
        back_font = self.display.get_text_font('md', 'regular')
        back_surface = back_font.render("Back", True, AppConfig.WHITE)
        back_text_rect = back_surface.get_rect(center=self.back_rect.center)
        self.display.surface.blit(back_surface, back_text_rect)
        
        # Reset needs_redraw flag
        self.needs_redraw = False
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        if not self.current_coin:
            return
            
        gestures = self.gesture_handler.handle_touch_event(event)
        
        if gestures['swipe_down']:
            logger.info("Swipe down detected, returning to settings")
            self.screen_manager.switch_screen('settings')
        elif event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            x, y = self._scale_touch_input(event)
            
            if self.back_rect.collidepoint(x, y):
                logger.info("Back button clicked")
                self.screen_manager.switch_screen('settings')
            elif self.delete_rect.collidepoint(x, y):
                logger.info("Delete button clicked")
                self.delete_coin()
            elif self.favorite_rect.collidepoint(x, y):
                logger.info("Favorite button clicked")
                self.toggle_favorite() 