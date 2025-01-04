import pygame
import os
from pathlib import Path
from .screen_manager import ScreenManager
from ..screens import TickerScreen, SettingsScreen, KeyboardScreen

class Display:
    def __init__(self, crypto_api):
        self.crypto_api = crypto_api
        self._setup_runtime_dir()
        self._init_pygame()
        self._init_display()
        self._init_screen_manager()

    def _setup_runtime_dir(self):
        if os.geteuid() == 0:
            uid = int(os.environ.get('SUDO_UID', 1000))
            runtime_dir = f"/run/user/{uid}"
            os.environ['XDG_RUNTIME_DIR'] = runtime_dir
            Path(runtime_dir).mkdir(parents=True, exist_ok=True)
            os.chmod(runtime_dir, 0o700)
            os.chown(runtime_dir, uid, uid)

    def _init_pygame(self):
        pygame.init()
        pygame.mouse.set_visible(False)
        os.putenv('SDL_VIDEODRIVER', 'fbcon')
        os.putenv('SDL_FBDEV', '/dev/fb0')

    def _init_display(self):
        self.width = 800
        self.height = 480
        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            pygame.FULLSCREEN | pygame.NOFRAME | pygame.HWSURFACE
        )

    def _init_screen_manager(self):
        self.screen_manager = ScreenManager(self.screen, self.width, self.height)
        
        # Add screens to manager
        self.screen_manager.add_screen('ticker', TickerScreen, self.crypto_api)
        
        # Get the ticker screen instance to pass to settings
        ticker_screen = self.screen_manager.screens['ticker']
        settings_screen = SettingsScreen(self.screen_manager, ticker_screen)
        self.screen_manager.add_screen('settings', settings_screen)
        
        # Add keyboard screen
        self.screen_manager.add_screen('keyboard', KeyboardScreen, settings_screen.add_ticker)
        
        # Set initial screen
        self.screen_manager.switch_to('ticker')

    def handle_event(self, event):
        self.screen_manager.handle_event(event)

    def update(self, prices):
        self.screen_manager.update(prices)

    def draw(self):
        self.screen_manager.draw()

    def cleanup(self):
        pygame.quit() 