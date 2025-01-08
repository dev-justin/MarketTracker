"""Dashboard screen for the crypto tracker application."""

import pygame
from typing import List, Tuple
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen
from ..components.top_movers import TopMovers
from ..components.menu_grid import MenuGrid

logger = get_logger(__name__)

class DashboardScreen(BaseScreen):
    """Dashboard screen showing market overview and navigation menu."""
    
    def __init__(self, display) -> None:
        """Initialize the dashboard screen."""
        super().__init__(display)
        self.background_color = (13, 13, 13)  # Darker black for more contrast
        
        # Initialize components
        self.top_movers = TopMovers(display, self.crypto_manager)
        self.menu_grid = None  # Will be initialized when screen_manager is set
        
        # Menu grid position
        self.menu_start_y = 300
        
        # Store clickable areas
        self.clickable_areas: List[Tuple[pygame.Rect, str]] = []
        
        logger.info("DashboardScreen initialized")
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        gestures = self.gesture_handler.handle_touch_event(event)
        
        if gestures['swipe_up']:
            logger.info("Swipe up detected, switching to settings screen")
            self.screen_manager.switch_screen('settings')
        elif gestures['swipe_down']:
            logger.info("Swipe down detected, switching to ticker screen")
            self.screen_manager.switch_screen('ticker')
        elif event.type == AppConfig.EVENT_TYPES['FINGER_DOWN'] and self.menu_grid:
            # Scale the touch input to screen coordinates
            x, y = self._scale_touch_input(event)
            logger.debug(f"Touch detected at ({x}, {y})")
            self.menu_grid.handle_click((x, y), self.clickable_areas)
    
    def draw(self) -> None:
        """Draw the dashboard screen."""
        # Fill background
        self.display.surface.fill(self.background_color)
        
        # Draw time
        time_font = self.display.get_title_font('lg', 'bold')
        time_surface = time_font.render(self.get_current_time(), True, AppConfig.WHITE)
        time_rect = time_surface.get_rect(
            centerx=self.width // 2,
            top=20
        )
        self.display.surface.blit(time_surface, time_rect)
        
        # Draw date
        date_font = self.display.get_text_font('md', 'regular')
        date_surface = date_font.render(self.get_current_date(), True, AppConfig.GRAY)
        date_rect = date_surface.get_rect(
            centerx=self.width // 2,
            top=time_rect.bottom + 10
        )
        self.display.surface.blit(date_surface, date_rect)
        
        # Draw top movers
        self.top_movers.draw(date_rect.bottom + 20)
        
        # Initialize menu grid if needed
        if not self.menu_grid and self.screen_manager:
            logger.debug("Initializing menu grid")
            self.menu_grid = MenuGrid(self.display, self.screen_manager)
        
        # Draw menu grid
        if self.menu_grid:
            self.clickable_areas = self.menu_grid.draw(self.menu_start_y)
        
        self.update_screen()
    
    def refresh_coins(self) -> None:
        """Refresh the list of tracked coins."""
        self.top_movers.update()
        self.draw()