import os
import pygame

class AppConfig:
    # Display settings
    DISPLAY_WIDTH = 800
    DISPLAY_HEIGHT = 480
    FPS = 30
    
    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    GRAY = (128, 128, 128)
    CELL_BORDER_COLOR = (40, 44, 52)
    
    # Font settings
    FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'fonts')
    FONT_PATHS = {
        'regular': os.path.join(FONT_DIR, 'SF-Pro-Display-Regular.otf'),
        'medium': os.path.join(FONT_DIR, 'SF-Pro-Display-Medium.otf'),
        'bold': os.path.join(FONT_DIR, 'SF-Pro-Display-Bold.otf'),
        'semibold': os.path.join(FONT_DIR, 'SF-Pro-Display-Semibold.otf')
    }
    
    # Font sizes
    FONT_SIZES = {
        'time': 96,
        'date': 48,
        'coin_name': 36,
        'price': 48,
        'label': 24
    }
    
    # Touch settings
    SWIPE_THRESHOLD = 0.15
    DOUBLE_TAP_THRESHOLD = 0.3
    
    # Grid settings
    GRID_ROWS = 4
    GRID_COLS = 4
    CELL_PADDING = 10
    
    # Keyboard settings
    KEY_SIZE = 60
    KEY_SPACING = 10 