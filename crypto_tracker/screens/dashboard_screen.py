"""Screen for displaying the dashboard with time, top movers, and favorites."""

import pygame
from datetime import datetime
from zoneinfo import ZoneInfo
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen
from ..components.top_movers import TopMovers
from ..components.menu_grid import MenuGrid
import time

logger = get_logger(__name__)

class DashboardScreen(BaseScreen):
    """Screen for displaying the current day and time."""
    
    def __init__(self, display) -> None:
        """Initialize the dashboard screen."""
        super().__init__(display)
        self.background_color = (13, 13, 13)  # Darker black for more contrast
        
        # Initialize components
        self.top_movers = TopMovers(display, self.crypto_manager)
        # Wait to initialize menu_grid until screen_manager is set
        self.menu_grid = None
        
        # Track last click time to prevent rapid screen switches
        self.last_click_time = 0
        
        logger.info("DashboardScreen initialized")
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        gestures = self.gesture_handler.handle_touch_event(event)
        
        if event.type == AppConfig.EVENT_TYPES['FINGER_DOWN'] and self.menu_grid:
            current_time = time.time()
            # Only handle click if enough time has passed since last click (300ms)
            if current_time - self.last_click_time > 0.3:
                x, y = self._scale_touch_input(event)
                self.menu_grid.handle_click(x, y)
                self.last_click_time = current_time
    
    def _draw_datetime(self) -> pygame.Rect:
        """Draw the current date and time."""
        # Get current time 
        now = datetime.now()
        local_time = now.astimezone(ZoneInfo(AppConfig.TIMEZONE))
        
        # Draw date
        date_text = local_time.strftime("%A, %B %d")
        date_font = self.display.get_font('light', 'lg')
        date_surface = date_font.render(date_text, True, AppConfig.WHITE)
        date_rect = date_surface.get_rect(centerx=self.width // 2, top=20)
        self.display.surface.blit(date_surface, date_rect)
        
        # Draw time (larger)
        time_text = local_time.strftime("%I:%M %p").lstrip("0")
        time_font = self.display.get_title_font('xl')  # Use title-xl font
        time_surface = time_font.render(time_text, True, AppConfig.WHITE)
        time_rect = time_surface.get_rect(centerx=self.width // 2, top=date_rect.bottom + 10)
        self.display.surface.blit(time_surface, time_rect)
        
        return time_rect
    
    def draw(self) -> None:
        """Draw the dashboard screen."""
        # Fill background
        self.display.surface.fill(self.background_color)
        
        # Draw date and time
        time_rect = self._draw_datetime()
        
        # Draw top movers section
        self.top_movers.draw()
        
        # Draw menu grid if initialized
        if self.menu_grid:
            menu_start_y = self.height - self.menu_grid.height - 20  # Position from bottom of screen
            self.menu_grid.draw(menu_start_y)
        
        # Update the display
        self.update_screen()

    def refresh_coins(self):
        """Refresh the list of tracked coins."""
        # Update top movers
        self.top_movers.update()
        # Force redraw
        self.draw()

    def on_screen_enter(self) -> None:
        """Called when entering the screen."""
        # Initialize menu grid if not already done
        if not self.menu_grid:
            self.menu_grid = MenuGrid(self.display, self.screen_manager)
        self.draw()