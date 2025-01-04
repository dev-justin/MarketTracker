import pygame
import time
from ..services.screen_manager import Screen

class SettingsScreen(Screen):
    def __init__(self, screen_manager, ticker_screen):
        super().__init__(screen_manager)
        self.ticker_screen = ticker_screen
        
        # Grid settings
        self.grid_size = 3
        self.cell_padding = 30
        
        # Calculate usable space (excluding title area)
        title_height = 100
        usable_height = self.height - title_height
        
        # Calculate cell dimensions to fill space evenly
        self.cell_width = (self.width - (self.cell_padding * (self.grid_size + 1))) // self.grid_size
        self.cell_height = (usable_height - (self.cell_padding * (self.grid_size + 1))) // self.grid_size
        
        # Triple tap detection
        self.triple_tap_last_time = 0
        self.triple_tap_second_time = 0
        self.double_tap_threshold = 0.3

    def handle_event(self, event):
        if not hasattr(event, 'x') or not hasattr(event, 'y'):
            return

        x = int(event.x * self.width)
        y = int(event.y * self.height)

        # Triple tap to return to ticker screen
        if event.type == pygame.FINGERDOWN:
            current_time = time.time()
            if current_time - self.triple_tap_last_time < self.double_tap_threshold:
                if current_time - self.triple_tap_second_time < self.double_tap_threshold:
                    self.manager.switch_to('ticker')
                    self.triple_tap_second_time = 0
                    self.triple_tap_last_time = 0
                else:
                    self.triple_tap_second_time = current_time
            else:
                self.triple_tap_second_time = 0
            self.triple_tap_last_time = current_time

    def _draw_plus_icon(self, cell_rect):
        # Calculate plus dimensions
        plus_thickness = 6
        plus_size = min(cell_rect.width, cell_rect.height) // 3
        
        # Calculate center position
        center_x = cell_rect.centerx
        center_y = cell_rect.centery
        
        # Draw horizontal line
        horizontal_rect = pygame.Rect(
            center_x - plus_size//2,
            center_y - plus_thickness//2,
            plus_size,
            plus_thickness
        )
        pygame.draw.rect(self.screen, (60, 60, 60), horizontal_rect, border_radius=2)
        
        # Draw vertical line
        vertical_rect = pygame.Rect(
            center_x - plus_thickness//2,
            center_y - plus_size//2,
            plus_thickness,
            plus_size
        )
        pygame.draw.rect(self.screen, (60, 60, 60), vertical_rect, border_radius=2)

    def draw(self):
        self.screen.fill(self.manager.BLACK)
        
        # Draw title
        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("Tracked Symbols", True, self.manager.WHITE)
        title_rect = title_text.get_rect(centerx=self.width//2, y=20)
        self.screen.blit(title_text, title_rect)
        
        # Calculate starting position for grid (below title)
        start_x = self.cell_padding
        start_y = 100  # Below title
        
        # Draw grid
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                # Calculate cell position
                x = start_x + col * (self.cell_width + self.cell_padding)
                y = start_y + row * (self.cell_height + self.cell_padding)
                
                # Create cell rect
                cell_rect = pygame.Rect(x, y, self.cell_width, self.cell_height)
                
                # Calculate index in symbols list
                index = row * self.grid_size + col
                
                # Draw cell background with rounded corners
                pygame.draw.rect(self.screen, (20, 20, 20), cell_rect, border_radius=10)
                # Draw cell border with rounded corners
                pygame.draw.rect(self.screen, (40, 40, 40), cell_rect, 2, border_radius=10)
                
                # If we have a symbol for this cell, draw it
                if index < len(self.ticker_screen.symbols):
                    symbol = self.ticker_screen.symbols[index]
                    symbol_font = pygame.font.Font(None, 72)
                    symbol_text = symbol_font.render(symbol, True, self.manager.WHITE)
                    symbol_rect = symbol_text.get_rect(center=cell_rect.center)
                    self.screen.blit(symbol_text, symbol_rect)
                else:
                    # Draw plus icon for empty cells
                    self._draw_plus_icon(cell_rect) 