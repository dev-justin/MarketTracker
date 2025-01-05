import os

class AppConfig:
    # Timezone
    TIMEZONE = 'America/New_York'


    # Display settings
    DISPLAY_WIDTH = 800
    DISPLAY_HEIGHT = 480
    FPS = 30

    # Touch events
    EVENT_TYPES = {
        'FINGER_DOWN': 1792,
        'FINGER_UP': 1793,
        'FINGER_MOVE': 1794,
    }
    
    # Asset directories
    ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
    FONT_DIR = os.path.join(ASSETS_DIR, 'fonts')
    ICONS_DIR = os.path.join(ASSETS_DIR, 'icons')

    # DATA_DIR
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    CACHE_DIR = os.path.join(DATA_DIR, 'cache')
    CRYPTO_STORAGE_FILE = os.path.join(DATA_DIR, 'crypto_storage.json')

    # Icon settings
    ICON_SIZE = 48  # Size for coin icons
    
    # Icon settings
    ICON_SIZE = 48  # Size for coin icons
    ICON_CACHE_TIME = 24 * 60 * 60  # 24 hours in seconds
    ICON_API_URL = "https://api.coingecko.com/api/v3/coins/{id}?localization=false&tickers=false&market_data=false&community_data=false&developer_data=false&sparkline=false"
    
    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    GRAY = (128, 128, 128)
    
    # UI Colors
    CELL_BG_COLOR = (30, 30, 30)
    CELL_BORDER_COLOR = (45, 45, 45)
    CELL_HIGHLIGHT_COLOR = (0, 255, 0, 80)
    PLUS_ICON_COLOR = (60, 60, 60)
    OVERLAY_COLOR = (0, 0, 0, 200)
    POPUP_BG_COLOR = (40, 40, 40)
    POPUP_BORDER_COLOR = (60, 60, 60)
    EDIT_BUTTON_COLOR = (60, 60, 60)
    DELETE_BUTTON_COLOR = (180, 0, 0)
    
    # Input colors
    INPUT_BG_COLOR = (30, 30, 30)
    PLACEHOLDER_COLOR = (100, 100, 100)
    KEY_BG_COLOR = (40, 40, 40)
    KEY_BORDER_COLOR = (60, 60, 60)
    DONE_BUTTON_ACTIVE_COLOR = (0, 100, 0)
    DONE_BUTTON_INACTIVE_COLOR = (40, 40, 40)
    CANCEL_BUTTON_COLOR = (100, 0, 0)
    
    # Font settings
    FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'fonts')
    FONT_PATHS = {
        'light': os.path.join(FONT_DIR, 'Ubuntu-Light.ttf'),
        'regular': os.path.join(FONT_DIR, 'Ubuntu-Regular.ttf'),
        'medium': os.path.join(FONT_DIR, 'Ubuntu-Medium.ttf'),
        'bold': os.path.join(FONT_DIR, 'Ubuntu-Bold.ttf'),
        'semibold': os.path.join(FONT_DIR, 'Ubuntu-Medium.ttf')
    }
    
    # Font sizes
    FONT_SIZES = {
        'xs': 20,
        'sm': 24,
        'md': 28,
        'lg': 32,
        'xl': 40,
        'title-sm': 48,
        'title-md': 56,
        'title-lg': 64,
        'title-xl': 72
    }
    
    # Touch settings
    SWIPE_THRESHOLD = 0.15
    DOUBLE_TAP_THRESHOLD = 0.3
    TOUCH_MARGIN = 10
    
    # Chart settings
    CHART_MARGIN = 60
    CHART_BOTTOM_MARGIN = 40
    CHART_Y_POSITION = 300
    CHART_HEIGHT = 300
    CHART_BG_COLOR = (20, 20, 20)
    CHART_GRID_COLOR = (40, 40, 40)
    CHART_LINE_COLOR = (0, 255, 0)
    CHART_LABEL_COLOR = (128, 128, 128)
    
    # Grid settings
    GRID_ROWS = 4
    GRID_COLS = 4
    CELL_PADDING = 10
    TITLE_HEIGHT = 80
    BUTTON_AREA_HEIGHT = 80
    
    # Button settings
    BUTTON_WIDTH = 120
    BUTTON_HEIGHT = 50
    BUTTON_MARGIN = 40
    
    # Keyboard settings
    KEY_SIZE = 60
    KEY_SPACING = 10
    MAX_TICKER_LENGTH = 5
    KEY_MARGIN = 10
    KEY_HEIGHT = 60
    BUTTON_HEIGHT = 50
    BUTTON_WIDTH = 120
    BUTTON_MARGIN = 40 