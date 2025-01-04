class AppConfig:
    # Display settings
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 480
    FPS = 60
    
    # Base colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    
    # Settings screen colors
    CELL_BG_COLOR = (30, 30, 30)
    CELL_BORDER_COLOR = (45, 45, 45)
    CELL_HIGHLIGHT_COLOR = (0, 255, 0, 80)
    PLUS_ICON_COLOR = (60, 60, 60)
    OVERLAY_COLOR = (0, 0, 0, 200)
    POPUP_BG_COLOR = (40, 40, 40)
    POPUP_BORDER_COLOR = (60, 60, 60)
    EDIT_BUTTON_COLOR = (60, 60, 60)
    DELETE_BUTTON_COLOR = (180, 0, 0)
    
    # Keyboard screen colors
    INPUT_BG_COLOR = (30, 30, 30)
    PLACEHOLDER_COLOR = (100, 100, 100)
    KEY_BG_COLOR = (40, 40, 40)
    KEY_BORDER_COLOR = (60, 60, 60)
    DONE_BUTTON_ACTIVE_COLOR = (0, 100, 0)
    DONE_BUTTON_INACTIVE_COLOR = (40, 40, 40)
    CANCEL_BUTTON_COLOR = (100, 0, 0)
    
    # Touch settings
    DOUBLE_TAP_THRESHOLD = 0.3
    SWIPE_THRESHOLD = 0.15
    
    # Chart settings
    CHART_HEIGHT = 250
    CHART_Y_POSITION = 220
    TOUCH_MARGIN = 10
    
    # Grid settings
    GRID_SIZE = 3
    CELL_PADDING = 25
    TITLE_HEIGHT = 80
    BUTTON_AREA_HEIGHT = 80
    
    # Keyboard settings
    KEY_MARGIN = 10
    KEY_HEIGHT = 60
    BUTTON_HEIGHT = 50
    BUTTON_WIDTH = 120
    BUTTON_MARGIN = 40
    MAX_TICKER_LENGTH = 5 