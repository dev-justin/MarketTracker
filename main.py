from crypto_tracker.config.settings import AppConfig
from crypto_tracker.services.display import Display
from crypto_tracker.services.screen_manager import ScreenManager
from crypto_tracker.screens.dashboard_screen import DashboardScreen

class MarkertTrackerApp():
    def __init__(self):
        self.display = Display()
        self.screen_manager = ScreenManager()

        # Initialize screens
        self.screen_manager.add_screen('dashboard', DashboardScreen(self.display))

    def run(self):
        while True:
            self.screen_manager.handle_event(pygame.event.poll())
            self.screen_manager.update_screen()
            self.display.tick(AppConfig.FPS)

def main():
    app = MarkertTrackerApp()
    app.run()

if __name__ == "__main__":
    main()