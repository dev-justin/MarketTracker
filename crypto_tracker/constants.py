from enum import Enum

class ScreenNames(Enum):
    TICKER = 'ticker'
    SETTINGS = 'settings'
    KEYBOARD = 'keyboard'
    WALLSTREET = 'wallstreet'

class EventTypes(Enum):
    FINGER_DOWN = 1792
    FINGER_UP = 1793
    FINGER_MOTION = 1794

class ChartSettings:
    LINE_WIDTH = 2
    DOT_RADIUS = 5
    GRADIENT_ALPHA_MAX = 50
    TOOLTIP_PADDING = 10
    TOOLTIP_ALPHA = 230
    TOOLTIP_BORDER_ALPHA = 128
    TOOLTIP_BORDER_RADIUS = 10
    ANIMATION_SPEED = 4
    ANIMATION_AMPLITUDE = 3

class KeyboardLayout:
    ROWS = [
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'DEL']
    ] 