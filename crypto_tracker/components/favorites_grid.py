"""Component for displaying favorite coins in a grid layout."""

import pygame
import os
from ..config.settings import AppConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class FavoritesGrid:
    """Component for displaying favorite coins in a grid layout."""
    
    def __init__(self, display, crypto_manager):
        """Initialize the favorites grid component."""
        self.display = display
        self.crypto_manager = crypto_manager
        
        # Dimensions
        self.box_height = 90
        display_width = self.display.surface.get_width()
        self.box_width = (display_width - 60) // 2  # Two columns with margins
        self.margin = 20
        self.logo_size = 36
    
    def draw(self, start_y: int):
        """Draw the favorites grid starting at the specified y position."""
        # Get favorite coins
        coins = self.crypto_manager.get_tracked_coins()
        favorite_coins = [coin for coin in coins if coin.get('favorite', False)]
        
        if not favorite_coins:
            return
        
        # Draw favorite coins in a grid
        for i, coin in enumerate(favorite_coins):
            row = i // 2
            col = i % 2
            x = self.margin + col * (self.box_width + self.margin)
            y = start_y + row * (self.box_height + self.margin)
            
            self._draw_favorite_box(x, y, coin)
    
    def _draw_favorite_box(self, x: int, y: int, coin: dict):
        """Draw a single favorite coin box."""
        try:
            # Create box rect
            box_rect = pygame.Rect(x, y, self.box_width, self.box_height)
            
            # Load and process logo
            logo_path = os.path.join(AppConfig.CACHE_DIR, f"{coin['symbol'].lower()}_logo.png")
            if os.path.exists(logo_path):
                logo = pygame.image.load(logo_path)
                logo = pygame.transform.scale(logo, (self.logo_size, self.logo_size))
                
                # Get dominant color from logo
                dominant_color = self._get_dominant_color(logo)
                
                # Draw gradient box
                self._draw_gradient_box(box_rect, dominant_color)
                
                # Draw logo
                logo_rect = logo.get_rect(
                    left=box_rect.left + 15,
                    centery=box_rect.centery
                )
                self.display.surface.blit(logo, logo_rect)
                
                # Draw coin symbol
                name_font = self.display.get_font('light', 'lg')
                name_text = coin['symbol'].upper()
                name_surface = name_font.render(name_text, True, AppConfig.WHITE)
                name_rect = name_surface.get_rect(
                    left=logo_rect.right + 15,
                    centery=logo_rect.centery
                )
                self.display.surface.blit(name_surface, name_rect)
                
        except Exception as e:
            logger.error(f"Error drawing favorite box: {e}")
    
    def _get_dominant_color(self, logo_surface):
        """Extract the dominant color from a logo."""
        try:
            # Get surface size
            width, height = logo_surface.get_size()
            
            # Sample points across the image
            sample_size = 10  # Sample every 10th pixel
            r_total, g_total, b_total = 0, 0, 0
            pixel_count = 0
            
            # Lock surface for direct pixel access
            logo_surface.lock()
            
            # Sample pixels
            for x in range(0, width, sample_size):
                for y in range(0, height, sample_size):
                    try:
                        color = logo_surface.get_at((x, y))
                        # Skip transparent or very dark pixels
                        if color.a > 128 and sum(color[:3]) > 60:
                            r_total += color.r
                            g_total += color.g
                            b_total += color.b
                            pixel_count += 1
                    except:
                        continue
            
            # Unlock surface
            logo_surface.unlock()
            
            if pixel_count > 0:
                # Calculate average color
                avg_color = (
                    int(r_total / pixel_count),
                    int(g_total / pixel_count),
                    int(b_total / pixel_count)
                )
                
                # Enhance saturation
                max_component = max(avg_color)
                min_component = min(avg_color)
                if max_component > min_component:
                    # Increase saturation by spreading the color components
                    saturation_factor = 1.5
                    mid_value = sum(avg_color) / 3
                    enhanced_color = tuple(
                        int(min(255, max(0, 
                            mid_value + (c - mid_value) * saturation_factor
                        )))
                        for c in avg_color
                    )
                    return enhanced_color
                
                return avg_color
            
            return (128, 128, 128)  # Default gray if no valid pixels
            
        except Exception as e:
            logger.error(f"Error extracting color: {e}")
            return (128, 128, 128)  # Default gray
    
    def _draw_gradient_box(self, rect, color, alpha_top=40, alpha_bottom=10):
        """Draw a box with a gradient background."""
        gradient_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        # Create gradient
        for y in range(rect.height):
            alpha = int(alpha_top + (alpha_bottom - alpha_top) * (y / rect.height))
            pygame.draw.line(
                gradient_surface,
                (*color, alpha),
                (0, y),
                (rect.width, y)
            )
        
        # Draw rounded rectangle
        pygame.draw.rect(gradient_surface, (*color, 20), (0, 0, rect.width, rect.height), border_radius=15)
        
        # Add subtle border
        pygame.draw.rect(gradient_surface, (*color, 40), (0, 0, rect.width, rect.height), 2, border_radius=15)
        
        self.display.surface.blit(gradient_surface, rect) 