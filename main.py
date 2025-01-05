from crypto_tracker.services.display import Display
from crypto_tracker.services.screen_manager import ScreenManager
from crypto_tracker.screens.dashboard_screen import DashboardScreen
from crypto_tracker.screens.settings_screen import SettingsScreen
import pygame
from crypto_tracker.services.crypto_service import CryptoService
class MarkertTrackerApp():
    def __init__(self):
        self.display = Display()
        self.screen_manager = ScreenManager(self.display)
        self.crypto_service = CryptoService()

        # Initialize screens
        self.screen_manager.add_screen('dashboard', DashboardScreen(self.display))
        settings_screen = SettingsScreen(self.display)
        settings_screen.crypto_service = self.crypto_service  # Pass crypto service
        self.screen_manager.add_screen('settings', settings_screen)
        self.screen_manager.switch_screen('dashboard')

    def run(self):
        while True:
            self.screen_manager.handle_event(pygame.event.poll())
            self.screen_manager.update_screen()

def main():
    app = MarkertTrackerApp()
    app.run()

if __name__ == "__main__":
    main()