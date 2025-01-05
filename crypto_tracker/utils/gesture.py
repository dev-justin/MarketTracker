import time
from ..config.settings import AppConfig

class GestureHandler:
    """Handles touch gestures like swipes and taps."""
    
    def __init__(self):
        self.last_touch = None
        self.last_touch_time = 0
        self.current_touch = None
        self.current_touch_time = 0
    
    def handle_touch_event(self, event) -> dict:
        """
        Handle touch events and detect gestures.
        Returns a dictionary of detected gestures.
        """
        gestures = {
            'swipe_up': False,
            'swipe_down': False,
            'swipe_left': False,
            'swipe_right': False,
            'tap': False,
            'double_tap': False
        }
        
        # Handle touch events
        if event.type == AppConfig.EVENT_TYPES['FINGER_DOWN']:
            self._handle_touch_down(event)
        elif event.type == AppConfig.EVENT_TYPES['FINGER_UP']:
            gestures.update(self._handle_touch_up(event))
        elif event.type == AppConfig.EVENT_TYPES['FINGER_MOTION']:
            gestures.update(self._handle_touch_motion(event))
        
        return gestures
    
    def _handle_touch_down(self, event):
        """Handle touch down event."""
        current_time = time.time() * 1000  # Convert to milliseconds
        
        # Store previous touch
        if self.current_touch:
            self.last_touch = self.current_touch
            self.last_touch_time = self.current_touch_time
        
        # Store current touch
        self.current_touch = (event.x, event.y)
        self.current_touch_time = current_time
    
    def _handle_touch_up(self, event) -> dict:
        """Handle touch up event and detect taps."""
        gestures = {
            'tap': False,
            'double_tap': False
        }
        
        current_time = time.time() * 1000
        
        # Check for double tap
        if (self.last_touch and 
            current_time - self.last_touch_time < AppConfig.DOUBLE_TAP_THRESHOLD):
            # Calculate distance between taps
            dx = abs(event.x - self.last_touch[0])
            dy = abs(event.y - self.last_touch[1])
            
            if dx < AppConfig.TOUCH_MARGIN and dy < AppConfig.TOUCH_MARGIN:
                gestures['double_tap'] = True
        else:
            gestures['tap'] = True
        
        return gestures
    
    def _handle_touch_motion(self, event) -> dict:
        """Handle touch motion event and detect swipes."""
        gestures = {
            'swipe_up': False,
            'swipe_down': False,
            'swipe_left': False,
            'swipe_right': False
        }
        
        if not self.current_touch:
            return gestures
        
        # Calculate swipe
        dx = event.x - self.current_touch[0]
        dy = event.y - self.current_touch[1]
        dt = (time.time() * 1000) - self.current_touch_time
        
        # Only detect swipe if within time threshold
        if dt > 0 and dt < AppConfig.SWIPE_TIME_THRESHOLD:
            # Calculate velocity
            velocity = (abs(dx) + abs(dy)) / dt
            
            # Check if swipe meets threshold
            if velocity >= AppConfig.SWIPE_VELOCITY_THRESHOLD:
                if abs(dx) > abs(dy):  # Horizontal swipe
                    if abs(dx) > AppConfig.SWIPE_THRESHOLD:
                        if dx > 0:
                            gestures['swipe_right'] = True
                        else:
                            gestures['swipe_left'] = True
                else:  # Vertical swipe
                    if abs(dy) > AppConfig.SWIPE_THRESHOLD:
                        if dy > 0:
                            gestures['swipe_down'] = True
                        else:
                            gestures['swipe_up'] = True
        
        return gestures