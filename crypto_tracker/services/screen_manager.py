import pygame

class Screen:
    def __init__(self, screen_manager):
        self.manager = screen_manager
        self.screen = screen_manager.screen
        self.width = screen_manager.width
        self.height = screen_manager.height

    def handle_event(self, event):
        pass

    def update(self, data=None):
        pass

    def draw(self):
        pass

class ScreenManager:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.current_screen = None
        self.screens = {}
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)

    def add_screen(self, name, screen_class, *args, **kwargs):
        self.screens[name] = screen_class(self, *args, **kwargs)
        if self.current_screen is None:
            self.current_screen = self.screens[name]

    def switch_to(self, screen_name):
        if screen_name in self.screens:
            self.current_screen = self.screens[screen_name]

    def handle_event(self, event):
        if self.current_screen:
            self.current_screen.handle_event(event)

    def update(self, data=None):
        if self.current_screen:
            self.current_screen.update(data)

    def draw(self):
        if self.current_screen:
            self.current_screen.draw()
            pygame.display.flip() 