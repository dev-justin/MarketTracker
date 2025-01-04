from enum import Enum

class ScreenNames(Enum):
    TICKER = 'ticker'
    SETTINGS = 'settings'
    KEYBOARD = 'keyboard'

class EventTypes(Enum):
    FINGER_DOWN = 1792
    FINGER_UP = 1793
    FINGER_MOTION = 1794

class ChartSettings:
    GRADIENT_ALPHA_MAX = 25
    DOT_RADIUS = 6
    LINE_WIDTH = 2
    TOOLTIP_PADDING = 15
    TOOLTIP_BORDER_RADIUS = 8
    TOOLTIP_ALPHA = 230
    TOOLTIP_BORDER_ALPHA = 128
    ANIMATION_SPEED = 2
    ANIMATION_AMPLITUDE = 2

class KeyboardLayout:
    ROWS = [
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'DEL']
    ] 