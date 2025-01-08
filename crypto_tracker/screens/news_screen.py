"""Screen for displaying crypto and stock news."""

import pygame
import os
from ..config.settings import AppConfig
from ..utils.logger import get_logger
from .base_screen import BaseScreen
from ..services.news_service import NewsService
import time

logger = get_logger(__name__)

class NewsScreen(BaseScreen):
    """Screen for displaying crypto and stock news."""
    
    def __init__(self, display) -> None:
        """Initialize the news screen."""
        super().__init__(display)
        self.background_color = (13, 13, 13)  # Darker black for more contrast
        
        # Initialize news service and get initial news
        self.news_service = NewsService()
        self.news_items = self.news_service.get_combined_news()
        
        # State
        self.scroll_offset = 0
        self.scroll_velocity = 0
        self.last_update_time = time.time()
        self.update_interval = 3600  # 1 hour
        
        # Dimensions
        self.news_item_height = 200  # Increased to accommodate image
        self.news_item_padding = 15
        self.title_height = 80
        self.image_size = (120, 120)  # Size for news images
        
        logger.info("NewsScreen initialized")
    
    def _update_news(self) -> None:
        """Update news items if needed."""
        current_time = time.time()
        if current_time - self.last_update_time > self.update_interval:
            self.news_items = self.news_service.get_combined_news()
            self.last_update_time = current_time
            logger.info("Updated news items")
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        gestures = self.gesture_handler.handle_touch_event(event)
        
        if gestures['swipe_down']:
            logger.info("Swipe down detected, returning to dashboard")
            self.screen_manager.switch_screen('dashboard')
        elif event.type == AppConfig.EVENT_TYPES['FINGER_MOTION']:
            # Handle scrolling
            _, rel_y = event.rel
            self.scroll_velocity = rel_y * 2
    
    def _draw_news_item(self, item: dict, y: int) -> pygame.Rect:
        """Draw a single news item."""
        # Create item rectangle
        item_rect = pygame.Rect(
            self.news_item_padding,
            y,
            self.width - (self.news_item_padding * 2),
            self.news_item_height
        )
        
        # Draw background
        pygame.draw.rect(
            self.display.surface,
            (30, 30, 30),
            item_rect,
            border_radius=15
        )
        
        # Load and draw image if available
        image_rect = None
        if item.get('image_path') and os.path.exists(item['image_path']):
            try:
                image = pygame.image.load(item['image_path'])
                image = pygame.transform.scale(image, self.image_size)
                image_rect = image.get_rect(
                    left=item_rect.left + 20,
                    top=item_rect.top + 20
                )
                self.display.surface.blit(image, image_rect)
            except Exception as e:
                logger.error(f"Error loading news image: {e}")
        
        # Calculate text start position based on image
        text_left = image_rect.right + 20 if image_rect else item_rect.left + 20
        text_width = item_rect.right - text_left - 20
        
        # Draw title
        title_font = self.display.get_text_font('md', 'bold')
        title_words = item['title'].split()
        title_lines = []
        current_line = []
        
        for word in title_words:
            test_line = ' '.join(current_line + [word])
            test_surface = title_font.render(test_line, True, AppConfig.WHITE)
            if test_surface.get_width() <= text_width:
                current_line.append(word)
            else:
                if current_line:
                    title_lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            title_lines.append(' '.join(current_line))
        
        title_y = item_rect.top + 20
        for line in title_lines[:2]:  # Limit to 2 lines
            title_surface = title_font.render(line, True, AppConfig.WHITE)
            title_rect = title_surface.get_rect(
                left=text_left,
                top=title_y
            )
            self.display.surface.blit(title_surface, title_rect)
            title_y += title_font.get_height()
        
        # Draw source
        source_font = self.display.get_text_font('sm', 'regular')
        source_text = f"{item['source']}"
        source_surface = source_font.render(source_text, True, AppConfig.GRAY)
        source_rect = source_surface.get_rect(
            left=text_left,
            top=title_y + 10
        )
        self.display.surface.blit(source_surface, source_rect)
        
        # Draw summary if available
        if 'summary' in item:
            summary_font = self.display.get_text_font('sm', 'regular')
            summary_words = item['summary'].split()
            summary_lines = []
            current_line = []
            
            for word in summary_words:
                test_line = ' '.join(current_line + [word])
                test_surface = summary_font.render(test_line, True, AppConfig.GRAY)
                if test_surface.get_width() <= text_width:
                    current_line.append(word)
                else:
                    if current_line:
                        summary_lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                summary_lines.append(' '.join(current_line))
            
            summary_y = source_rect.bottom + 10
            for line in summary_lines[:2]:  # Limit to 2 lines
                summary_surface = summary_font.render(line, True, AppConfig.GRAY)
                summary_rect = summary_surface.get_rect(
                    left=text_left,
                    top=summary_y
                )
                self.display.surface.blit(summary_surface, summary_rect)
                summary_y += summary_font.get_height()
        
        return item_rect
    
    def draw(self) -> None:
        """Draw the news screen."""
        # Update news if needed
        self._update_news()
        
        # Fill background
        self.display.surface.fill(self.background_color)
        
        # Draw header
        header_font = self.display.get_title_font('md', 'bold')
        header_surface = header_font.render("Market News", True, AppConfig.WHITE)
        header_rect = header_surface.get_rect(
            left=20,
            top=20
        )
        self.display.surface.blit(header_surface, header_rect)
        
        # Apply scrolling physics
        self.scroll_offset += self.scroll_velocity
        self.scroll_velocity *= 0.95  # Damping
        
        # Limit scrolling
        max_scroll = len(self.news_items) * (self.news_item_height + self.news_item_padding) - self.height + self.title_height
        if max_scroll > 0:
            self.scroll_offset = max(min(self.scroll_offset, 0), -max_scroll)
        else:
            self.scroll_offset = 0
        
        # Draw news items
        current_y = self.title_height + self.scroll_offset
        for item in self.news_items:
            # Only draw items that are visible
            if current_y + self.news_item_height > 0 and current_y < self.height:
                self._draw_news_item(item, current_y)
            current_y += self.news_item_height + self.news_item_padding
        
        self.update_screen()
    
    def on_screen_enter(self) -> None:
        """Called when entering the screen."""
        # Force news update
        self.last_update_time = 0
        self._update_news()
        self.draw() 