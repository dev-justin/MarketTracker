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
        
        # Track if redraw is needed
        self.needs_redraw = True
        
        logger.info("DashboardScreen initialized")
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        # Handle gestures first
        gestures = self.gesture_handler.handle_touch_event(event)
        
        if gestures['swipe_up']:
            logger.info("Swipe up detected, switching to settings screen")
            if self.screen_manager:
                self.screen_manager.switch_screen('settings')
            else:
                logger.error("Screen manager not initialized for swipe up")
        elif gestures['swipe_down']:
            logger.info("Swipe down detected, switching to ticker screen")
            if self.screen_manager:
                self.screen_manager.switch_screen('ticker')
            else:
                logger.error("Screen manager not initialized for swipe down")
        
        # Handle direct touch events
        if event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            x, y = self._scale_touch_input(event)
            
            if self.menu_grid:
                self.menu_grid.handle_click((x, y), self.clickable_areas)
            else:
                logger.warning("Menu grid not initialized for touch event")
    
    def draw(self) -> None:
        """Draw the dashboard screen."""
        # Only redraw if needed
        if not self.needs_redraw:
            return
            
        logger.debug("Drawing dashboard screen")
        
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
            logger.info("Initializing menu grid with screen manager")
            self.menu_grid = MenuGrid(self.display, self.screen_manager)
        elif not self.screen_manager:
            logger.warning("Cannot initialize menu grid - screen manager not set")
        
        # Draw menu grid and store clickable areas
        if self.menu_grid:
            self.clickable_areas = self.menu_grid.draw(self.menu_start_y)
        
        self.update_screen()
        self.needs_redraw = False
    
    def refresh_coins(self) -> None:
        """Refresh the list of tracked coins."""
        self.top_movers.update()
        self.needs_redraw = True
        self.draw()
    
    def on_screen_enter(self) -> None:
        """Called when entering the screen."""
        logger.debug("Entering dashboard screen")
        self.needs_redraw = True
        self.draw()
    
    def update_screen(self) -> None:
        """Update the display."""
        pygame.display.flip()
        # Set needs_redraw to True every second to update time
        self.needs_redraw = True