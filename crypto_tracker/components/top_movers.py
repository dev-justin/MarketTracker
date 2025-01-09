"""Component for displaying top movers in the market."""

import pygame
from typing import List, Dict, Optional
from ..config.settings import AppConfig
from ..utils.logger import get_logger
import os
from PIL import Image
import numpy as np

logger = get_logger(__name__)

class TopMovers:
    """Component for displaying top movers in the market."""
    
    def __init__(self, display, crypto_manager) -> None:
        """Initialize the top movers component."""
        self.display = display
        self.crypto_manager = crypto_manager
        
        # Component dimensions
        self.section_height = 120  # Height for the section
        
        # Calculate card width to span full width with padding
        total_padding = 40  # 20px padding on each side
        spacing_between = 20  # 20px between cards
        total_spacing = total_padding + (spacing_between * 2)
        self.card_width = (AppConfig.DISPLAY_WIDTH - total_spacing) // 3
        
        # Card dimensions and styling
        self.logo_size = 52  # Increased logo size
        self.card_height = 150  # Increased from 120 to 150 for better spacing
        self.top_padding = 15
        self.side_padding = 20
        
        # Load trending icons with larger size
        self.trending_up = pygame.image.load(os.path.join(AppConfig.ASSETS_DIR, 'icons', 'trending-up.svg'))
        self.trending_down = pygame.image.load(os.path.join(AppConfig.ASSETS_DIR, 'icons', 'trending-down.svg'))
        self.trending_icon_size = 42  # Increased from 24 to 42
        self.trending_up = pygame.transform.scale(self.trending_up, (self.trending_icon_size, self.trending_icon_size))
        self.trending_down = pygame.transform.scale(self.trending_down, (self.trending_icon_size, self.trending_icon_size))
        
        # Cache for logo colors
        self.logo_colors = {}
        
        # State
        self.movers: List[Dict] = []
        
        logger.info("TopMovers component initialized")
    
    def _get_dominant_color(self, logo_path: str) -> tuple:
        """Extract the dominant color from a logo."""
        if logo_path in self.logo_colors:
            return self.logo_colors[logo_path]
            
        try:
            img = Image.open(logo_path)
            img = img.convert('RGBA')
            img = img.resize((50, 50))  # Reduce size for faster processing
            
            # Convert image to numpy array
            arr = np.array(img)
            
            # Get colors from non-transparent pixels
            valid_pixels = arr[arr[:, :, 3] > 128]  # Only consider mostly opaque pixels
            if len(valid_pixels) == 0:
                return (30, 30, 30)  # Default dark gray
                
            # Calculate average color
            avg_color = np.mean(valid_pixels[:, :3], axis=0)
            
            # Darken the color for better contrast
            darkened_color = tuple(int(c * 0.7) for c in avg_color)
            
            # Cache the result
            self.logo_colors[logo_path] = darkened_color
            return darkened_color
            
        except Exception as e:
            logger.error(f"Error extracting color from logo: {e}")
            return (30, 30, 30)  # Default dark gray
    
    def update(self) -> None:
        """Update the list of top movers."""
        tracked_coins = self.crypto_manager.get_tracked_coins()
        self.movers = sorted(
            tracked_coins,
            key=lambda x: abs(float(x.get('price_change_24h', 0))),
            reverse=True
        )[:3]

    def _create_circular_icon(self, surface: pygame.Surface) -> pygame.Surface:
        """Create a circular icon from a square surface."""
        size = surface.get_width()
        circular = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Create a circle mask
        pygame.draw.circle(circular, (255, 255, 255, 255), (size//2, size//2), size//2)
        
        # Apply the mask to the original surface
        circular.blit(surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        return circular

    def _draw_mover_card(self, coin: Dict, x: int, y: int) -> None:
        """Draw a single mover card."""
        # Create card rectangle
        card_rect = pygame.Rect(x, y, self.card_width, self.card_height)
        
        # Get logo path and extract background color
        logo_path = os.path.join(AppConfig.CACHE_DIR, f"{coin['symbol'].lower()}_logo.png")
        bg_color = self._get_dominant_color(logo_path) if os.path.exists(logo_path) else (30, 30, 30)
        
        # Draw card background
        pygame.draw.rect(
            self.display.surface,
            bg_color,
            card_rect,
            border_radius=15
        )
        
        # Draw logo in top left
        if os.path.exists(logo_path):
            try:
                logo = pygame.image.load(logo_path)
                logo = pygame.transform.scale(logo, (self.logo_size, self.logo_size))
                logo = self._create_circular_icon(logo)
                logo_rect = logo.get_rect(
                    left=card_rect.left + self.side_padding,
                    top=card_rect.top + self.top_padding
                )
                self.display.surface.blit(logo, logo_rect)
                
                # Draw symbol (ticker) to the right of logo
                symbol_font = self.display.get_title_font('md', 'bold')
                symbol_surface = symbol_font.render(coin['symbol'].upper(), True, AppConfig.WHITE)
                symbol_rect = symbol_surface.get_rect(
                    left=logo_rect.right + 15,
                    centery=logo_rect.centery
                )
                self.display.surface.blit(symbol_surface, symbol_rect)
                
                # Draw large percentage change below, ensuring it fits within the card
                change = float(coin.get('price_change_24h', 0))
                change_text = f"{'+' if change >= 0 else ''}{change:.1f}%"
                change_font = self.display.get_title_font('xl', 'bold')
                change_surface = change_font.render(change_text, True, AppConfig.WHITE)
                
                # Calculate maximum width available for percentage
                max_width = card_rect.width - (self.side_padding * 2)
                
                # Scale down font if needed to fit within card
                if change_surface.get_width() > max_width:
                    change_font = self.display.get_title_font('md', 'bold')
                    change_surface = change_font.render(change_text, True, AppConfig.WHITE)
                
                change_rect = change_surface.get_rect(
                    left=card_rect.left + self.side_padding,
                    bottom=card_rect.bottom - self.top_padding
                )
                self.display.surface.blit(change_surface, change_rect)
                
                # Draw trending icon in bottom right
                trending_icon = self.trending_up if change >= 0 else self.trending_down
                icon_rect = trending_icon.get_rect(
                    right=card_rect.right - self.side_padding,
                    bottom=card_rect.bottom - self.top_padding
                )
                self.display.surface.blit(trending_icon, icon_rect)
                
            except Exception as e:
                logger.error(f"Error loading logo: {e}")
    
    def draw(self, start_y: int) -> None:
        """Draw the top movers section."""
        # Update data
        self.update()
        
        # Draw section title
        title_font = self.display.get_text_font('md', 'bold')
        title_surface = title_font.render("Top Movers", True, AppConfig.WHITE)
        title_rect = title_surface.get_rect(
            left=20,
            top=start_y
        )
        self.display.surface.blit(title_surface, title_rect)
        
        # Draw mover cards
        card_y = title_rect.bottom + 15
        card_x = 20
        spacing = 20  # Space between cards
        
        for coin in self.movers:
            self._draw_mover_card(coin, card_x, card_y)
            card_x += self.card_width + spacing 