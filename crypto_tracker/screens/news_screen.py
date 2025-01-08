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
        self.crypto_news, self.stock_news = self.news_service.get_news()
        
        # State for both sections
        self.crypto_scroll_offset = 0
        self.stock_scroll_offset = 0
        self.crypto_scroll_velocity = 0
        self.stock_scroll_velocity = 0
        self.last_update_time = time.time()
        self.update_interval = 3600  # 1 hour
        
        # Touch tracking
        self.last_touch_y = None
        self.active_section = None  # 'crypto' or 'stock'
        
        # Dimensions
        self.title_height = 60  # Increased header height
        self.section_padding = 20
        self.news_item_padding = 15
        
        # Calculate section heights
        available_height = self.height - (self.title_height * 2) - self.section_padding
        self.section_height = available_height // 2
        
        # Calculate item dimensions for 2x2 grid
        self.news_item_width = (self.width - (self.news_item_padding * 3)) // 2  # 3 paddings: left, middle, right
        self.news_item_height = self.section_height - (self.news_item_padding * 2)  # Full height minus padding
        
        # Calculate section boundaries
        self.crypto_section_rect = pygame.Rect(
            0,
            self.title_height,
            self.width,
            self.section_height
        )
        self.stock_section_rect = pygame.Rect(
            0,
            self.title_height + self.section_height + self.section_padding,
            self.width,
            self.section_height
        )
        
        logger.info("NewsScreen initialized")
    
    def _update_news(self) -> None:
        """Update news items if needed."""
        current_time = time.time()
        if current_time - self.last_update_time > self.update_interval:
            self.crypto_news, self.stock_news = self.news_service.get_news()
            self.last_update_time = current_time
            logger.info("Updated news items")
            logger.info(f"Fetched {len(self.crypto_news)} crypto news and {len(self.stock_news)} stock news items")
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        gestures = self.gesture_handler.handle_touch_event(event)
        
        if gestures['swipe_down']:
            logger.info("Swipe down detected, returning to dashboard")
            self.screen_manager.switch_screen('dashboard')
        elif event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            x, y = self._scale_touch_input(event)
            # Determine which section was touched
            if self.crypto_section_rect.collidepoint(x, y):
                self.active_section = 'crypto'
            elif self.stock_section_rect.collidepoint(x, y):
                self.active_section = 'stock'
            else:
                self.active_section = None
            
            # Start tracking touch
            self.last_touch_y = event.y
            if self.active_section == 'crypto':
                self.crypto_scroll_velocity = 0
            elif self.active_section == 'stock':
                self.stock_scroll_velocity = 0
                
        elif event.type == AppConfig.EVENT_TYPES['FINGER_MOTION'] and self.last_touch_y is not None:
            # Calculate relative movement
            rel_y = event.y - self.last_touch_y
            self.last_touch_y = event.y
            
            # Apply scrolling to active section
            if self.active_section == 'crypto':
                self.crypto_scroll_velocity = rel_y * self.height * 2
            elif self.active_section == 'stock':
                self.stock_scroll_velocity = rel_y * self.height * 2
                
        elif event.type == AppConfig.EVENT_TYPES['FINGER_UP']:
            # Stop tracking touch
            self.last_touch_y = None
            self.active_section = None
    
    def _draw_news_item(self, item: dict, x: int, y: int, section_rect: pygame.Rect) -> pygame.Rect:
        """Draw a single news item."""
        # Create item rectangle within section bounds
        item_rect = pygame.Rect(
            x,
            y,
            self.news_item_width,
            self.news_item_height
        )
        
        # Only draw if item is visible within its section
        if (y + self.news_item_height > section_rect.top and 
            y < section_rect.bottom):
            
            # Draw background with gradient effect
            gradient_colors = [(25, 25, 25), (30, 30, 30)]
            gradient_rects = []
            gradient_height = item_rect.height // len(gradient_colors)
            
            for i, color in enumerate(gradient_colors):
                gradient_rect = pygame.Rect(
                    item_rect.left,
                    item_rect.top + (i * gradient_height),
                    item_rect.width,
                    gradient_height
                )
                pygame.draw.rect(
                    self.display.surface,
                    color,
                    gradient_rect,
                    border_radius=15
                )
                gradient_rects.append(gradient_rect)
            
            # Draw border
            pygame.draw.rect(
                self.display.surface,
                (40, 40, 40),
                item_rect,
                border_radius=15,
                width=1
            )
            
            # Calculate text area
            text_padding = 20
            text_left = item_rect.left + text_padding
            text_width = item_rect.width - (text_padding * 2)
            
            # Draw title
            title_font = self.display.get_text_font('md', 'bold')  # Increased font size
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
            
            title_y = item_rect.top + text_padding
            for line in title_lines[:2]:  # Limit to 2 lines
                title_surface = title_font.render(line, True, AppConfig.WHITE)
                title_rect = title_surface.get_rect(
                    left=text_left,
                    top=title_y
                )
                self.display.surface.blit(title_surface, title_rect)
                title_y += title_font.get_height()
            
            # Draw source with accent color based on type
            source_color = (45, 156, 219) if item['type'] == 'crypto' else (39, 174, 96)
            source_font = self.display.get_text_font('sm', 'bold')  # Increased font size
            source_text = f"{item['source']}"
            source_surface = source_font.render(source_text, True, source_color)
            source_rect = source_surface.get_rect(
                left=text_left,
                top=title_y + 10
            )
            self.display.surface.blit(source_surface, source_rect)
            
            # Draw summary if available
            if 'summary' in item:
                summary_font = self.display.get_text_font('sm', 'regular')  # Increased font size
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
                for line in summary_lines[:2]:  # Show up to 2 lines of summary
                    summary_surface = summary_font.render(line, True, AppConfig.GRAY)
                    summary_rect = summary_surface.get_rect(
                        left=text_left,
                        top=summary_y
                    )
                    self.display.surface.blit(summary_surface, summary_rect)
                    summary_y += summary_font.get_height()
        
        return item_rect
    
    def _draw_news_section(self, news_items: list, section_rect: pygame.Rect, scroll_offset: float) -> None:
        """Draw a section of news items in a 2x2 grid."""
        if not news_items:
            # Draw "No news available" message
            font = self.display.get_text_font('sm', 'regular')
            text = font.render("No news available", True, AppConfig.GRAY)
            text_rect = text.get_rect(center=section_rect.center)
            self.display.surface.blit(text, text_rect)
            return
            
        # Calculate grid positions
        rows = (len(news_items) + 1) // 2  # Number of rows needed
        current_y = section_rect.top + scroll_offset
        
        for row in range(rows):
            for col in range(2):
                idx = row * 2 + col
                if idx < len(news_items):
                    x = self.news_item_padding + col * (self.news_item_width + self.news_item_padding)
                    self._draw_news_item(news_items[idx], x, current_y, section_rect)
            current_y += self.news_item_height + self.news_item_padding
    
    def draw(self) -> None:
        """Draw the news screen."""
        # Update news if needed
        self._update_news()
        
        # Fill background
        self.display.surface.fill(self.background_color)
        
        # Draw section headers with pill/badge design
        header_font = self.display.get_title_font('md', 'bold')  # Increased font size
        
        # Crypto header with pill background
        crypto_header = header_font.render("Crypto News", True, (45, 156, 219))  # Blue accent
        crypto_header_rect = crypto_header.get_rect(
            left=20,
            centery=self.title_height // 2
        )
        # Draw pill background
        pill_padding = 15  # Padding around text
        crypto_pill_rect = pygame.Rect(
            crypto_header_rect.left - pill_padding,
            crypto_header_rect.top - pill_padding,
            crypto_header_rect.width + (pill_padding * 2),
            crypto_header_rect.height + (pill_padding * 2)
        )
        pygame.draw.rect(
            self.display.surface,
            (20, 62, 88),  # Darker blue background
            crypto_pill_rect,
            border_radius=crypto_pill_rect.height // 2  # Fully rounded corners
        )
        self.display.surface.blit(crypto_header, crypto_header_rect)
        
        # Stock header with pill background
        stock_header = header_font.render("Stock News", True, (39, 174, 96))  # Green accent
        stock_header_rect = stock_header.get_rect(
            left=20,
            centery=self.crypto_section_rect.bottom + self.title_height // 2
        )
        # Draw pill background
        stock_pill_rect = pygame.Rect(
            stock_header_rect.left - pill_padding,
            stock_header_rect.top - pill_padding,
            stock_header_rect.width + (pill_padding * 2),
            stock_header_rect.height + (pill_padding * 2)
        )
        pygame.draw.rect(
            self.display.surface,
            (16, 70, 38),  # Darker green background
            stock_pill_rect,
            border_radius=stock_pill_rect.height // 2  # Fully rounded corners
        )
        self.display.surface.blit(stock_header, stock_header_rect)
        
        # Draw section divider with gradient
        divider_y = self.crypto_section_rect.bottom + self.section_padding // 2
        divider_gradient = [(30, 30, 30), (40, 40, 40), (30, 30, 30)]
        divider_width = 2
        
        for i, color in enumerate(divider_gradient):
            y_offset = i - len(divider_gradient) // 2
            pygame.draw.line(
                self.display.surface,
                color,
                (0, divider_y + y_offset),
                (self.width, divider_y + y_offset),
                divider_width
            )
        
        # Apply scrolling physics for both sections
        self.crypto_scroll_offset += self.crypto_scroll_velocity
        self.stock_scroll_offset += self.stock_scroll_velocity
        self.crypto_scroll_velocity *= 0.95  # Damping
        self.stock_scroll_velocity *= 0.95  # Damping
        
        # Draw crypto news section
        max_crypto_scroll = ((len(self.crypto_news) + 1) // 2) * (self.news_item_height + self.news_item_padding) - self.section_height
        if max_crypto_scroll > 0:
            self.crypto_scroll_offset = max(min(self.crypto_scroll_offset, 0), -max_crypto_scroll)
        else:
            self.crypto_scroll_offset = 0
        
        self._draw_news_section(self.crypto_news, self.crypto_section_rect, self.crypto_scroll_offset)
        
        # Draw stock news section
        max_stock_scroll = ((len(self.stock_news) + 1) // 2) * (self.news_item_height + self.news_item_padding) - self.section_height
        if max_stock_scroll > 0:
            self.stock_scroll_offset = max(min(self.stock_scroll_offset, 0), -max_stock_scroll)
        else:
            self.stock_scroll_offset = 0
        
        self._draw_news_section(self.stock_news, self.stock_section_rect, self.stock_scroll_offset)
    
    def on_screen_enter(self) -> None:
        """Called when entering the screen."""
        # Force news update
        self.last_update_time = 0
        self._update_news()
        self.needs_redraw = True  # Let the screen manager handle the redraw 