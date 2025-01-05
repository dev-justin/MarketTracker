"""Application configuration settings."""

import os

class AppConfig:
    """Global application configuration."""
    
    # General settings
    TIMEZONE = 'America/New_York'  # Default timezone for timestamps
    
    # Display settings
    DISPLAY_WIDTH = 800
    DISPLAY_HEIGHT = 480
    FPS = 30
    
    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    
    # Button colors
    CANCEL_BUTTON_COLOR = (200, 50, 50)
    DELETE_BUTTON_COLOR = (200, 50, 50)
    DONE_BUTTON_ACTIVE_COLOR = (50, 200, 50)
    DONE_BUTTON_INACTIVE_COLOR = (100, 100, 100)
    FAVORITE_ACTIVE_COLOR = (255, 215, 0)  # Gold
    FAVORITE_INACTIVE_COLOR = (100, 100, 100)
    
    # Input colors
    INPUT_BG_COLOR = (30, 30, 30)
    PLACEHOLDER_COLOR = (128, 128, 128)
    
    # Keyboard colors
    KEY_BG_COLOR = (40, 40, 40)
    KEY_BORDER_COLOR = (60, 60, 60)
    
    # Cell colors
    CELL_BG_COLOR = (30, 30, 30)
    CELL_BORDER_COLOR = (60, 60, 60)
    CELL_HIGHLIGHT_COLOR = (0, 255, 0, 80)
    
    # Button dimensions
    BUTTON_WIDTH = 80
    BUTTON_HEIGHT = 40
    BUTTON_MARGIN = 10
    
    # Asset directories
    ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
    FONT_DIR = os.path.join(ASSETS_DIR, 'fonts')
    ICONS_DIR = os.path.join(ASSETS_DIR, 'icons')
    
    # Data directories
    BASE_DIR = os.path.expanduser("~/.crypto_tracker")
    DATA_DIR = os.path.join(BASE_DIR, "data")
    CACHE_DIR = os.path.join(BASE_DIR, "cache")
    
    # File paths
    TRACKED_COINS_FILE = os.path.join(DATA_DIR, "tracked_coins.json")
    
    # Font paths
    FONT_PATHS = {
        'light': os.path.join(FONT_DIR, 'Ubuntu-Light.ttf'),
        'regular': os.path.join(FONT_DIR, 'Ubuntu-Regular.ttf'),
        'medium': os.path.join(FONT_DIR, 'Ubuntu-Medium.ttf'),
        'bold': os.path.join(FONT_DIR, 'Ubuntu-Bold.ttf'),
        'semibold': os.path.join(FONT_DIR, 'Ubuntu-Medium.ttf')
    }
    
    # Font sizes
    FONT_SIZES = {
        'xs': 12,
        'sm': 14,
        'md': 18,
        'lg': 24,
        'xl': 28,
        'title-sm': 32,
        'title-md': 36,
        'title-lg': 42,
        'title-xl': 48
    }
    
    # Touch settings
    SWIPE_THRESHOLD = 0.15  # 15% of screen width/height for swipe detection
    SWIPE_TIME_THRESHOLD = 500  # Maximum time for swipe detection (ms)
    DOUBLE_TAP_THRESHOLD = 300  # Maximum time between taps (ms)
    TOUCH_MARGIN = 0.05  # 5% touch area margin for hit detection
    SWIPE_VELOCITY_THRESHOLD = 0.3  # Minimum velocity for swipe detection
    
    # Event types
    EVENT_TYPES = {
        'FINGER_DOWN': 1792,
        'FINGER_UP': 1793,
        'FINGER_MOTION': 1794
    }
    
    # Chart settings
    CHART_MARGIN = 20
    CHART_HEIGHT = 200
    CHART_Y_POSITION = DISPLAY_HEIGHT - CHART_HEIGHT - 60
    CHART_BG_COLOR = (30, 30, 30)
    CHART_LINE_COLOR = (0, 255, 0)
    CHART_GRID_COLOR = (40, 40, 40)
    
    # Grid settings
    GRID_ROWS = 4
    GRID_COLS = 4
    CELL_PADDING = 10
    TITLE_HEIGHT = 80
    BUTTON_AREA_HEIGHT = 80
    
    # Icon settings
    ICON_SIZE = 48  # Size for coin icons
    ICON_CACHE_TIME = 24 * 60 * 60  # 24 hours in seconds 