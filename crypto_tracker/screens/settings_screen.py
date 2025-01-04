import pygame
import time
from ..services.screen_manager import Screen

class SettingsScreen(Screen):
    def __init__(self, screen_manager, ticker_screen):
        super().__init__(screen_manager)
        self.ticker_screen = ticker_screen
        self.crypto_api = ticker_screen.crypto_api
        
        # Grid settings
        self.grid_size = 3
        self.cell_padding = 30
        
        # Calculate usable space (excluding title and button areas)
        title_height = 100
        button_area_height = 80
        usable_height = self.height - title_height - button_area_height
        
        # Calculate cell dimensions to fill space evenly
        self.cell_width = (self.width - (self.cell_padding * (self.grid_size + 1))) // self.grid_size
        self.cell_height = (usable_height - (self.cell_padding * (self.grid_size + 1))) // self.grid_size
        
        # Triple tap detection
        self.triple_tap_last_time = 0
        self.triple_tap_second_time = 0
        self.double_tap_threshold = 0.3
        
        # Store cell rectangles for hit testing
        self.cell_rects = []
        self._create_cell_rects()
        
        # Create back button
        button_width = 120
        button_height = 50
        self.back_button = pygame.Rect(
            (self.width - button_width) // 2,
            self.height - button_height - 20,
            button_width,
            button_height
        )

    def _create_cell_rects(self):
        start_x = self.cell_padding
        start_y = 100  # Below title
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = start_x + col * (self.cell_width + self.cell_padding)
                y = start_y + row * (self.cell_height + self.cell_padding)
                self.cell_rects.append(pygame.Rect(x, y, self.cell_width, self.cell_height))

    def add_ticker(self, symbol):
        """Add a new ticker and update the ticker screen's symbols"""
        if self.crypto_api.add_ticker(symbol):
            self.ticker_screen.symbols = self.crypto_api.get_tracked_symbols()

    def handle_event(self, event):
        if not hasattr(event, 'x') or not hasattr(event, 'y'):
            return

        x = int(event.x * self.width)
        y = int(event.y * self.height)

        if event.type == pygame.FINGERDOWN:
            # Check for back button press
            if self.back_button.collidepoint(x, y):
                self.manager.switch_to('ticker')
                return
            
            # Check for clicks on empty cells
            for i, rect in enumerate(self.cell_rects):
                if rect.collidepoint(x, y) and i >= len(self.ticker_screen.symbols):
                    self.manager.switch_to('keyboard')

    def _draw_plus_icon(self, cell_rect):
        # Calculate plus dimensions
        plus_thickness = 3  # Thinner lines for more modern look
        plus_size = min(cell_rect.width, cell_rect.height) // 4  # Slightly smaller
        
        # Calculate center position
        center_x = cell_rect.centerx
        center_y = cell_rect.centery
        
        # Draw plus in green to match the theme
        color = (0, 255, 0, 128)  # Semi-transparent green
        
        # Draw horizontal line
        horizontal_rect = pygame.Rect(
            center_x - plus_size//2,
            center_y - plus_thickness//2,
            plus_size,
            plus_thickness
        )
        pygame.draw.rect(self.screen, color, horizontal_rect, border_radius=2)
        
        # Draw vertical line
        vertical_rect = pygame.Rect(
            center_x - plus_thickness//2,
            center_y - plus_size//2,
            plus_thickness,
            plus_size
        )
        pygame.draw.rect(self.screen, color, vertical_rect, border_radius=2)

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
                
                # Draw cell border only (no background) with thin green line
                pygame.draw.rect(self.screen, (0, 255, 0, 128), cell_rect, 1, border_radius=10)
                
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
        
        # Draw back button
        pygame.draw.rect(self.screen, (0, 255, 0, 128), self.back_button, 1, border_radius=25)
        back_text = pygame.font.Font(None, 36).render("Back", True, (0, 255, 0))
        back_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_rect) 