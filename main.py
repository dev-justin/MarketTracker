import pygame
import os
from crypto_tracker.services.display import Display
from crypto_tracker.services.screen_manager import ScreenManager
from crypto_tracker.screens.dashboard_screen import DashboardScreen
from crypto_tracker.screens.ticker_screen import TickerScreen
from crypto_tracker.screens.settings_screen import SettingsScreen
from crypto_tracker.screens.add_ticker_screen import AddTickerScreen
from crypto_tracker.screens.edit_ticker_screen import EditTickerScreen
from crypto_tracker.config.settings import AppConfig
from crypto_tracker.utils.logger import get_logger
from crypto_tracker.services.crypto.crypto_manager import CryptoManager

logger = get_logger(__name__)

def main():
    """Initialize and run the application."""
    try:
        # Initialize pygame
        pygame.init()
        
        # Initialize crypto manager and start price updates
        crypto_manager = CryptoManager()
        crypto_manager.start_price_updates()
        
        # Create display
        display = Display()
        
        # Create screen manager
        screen_manager = ScreenManager(display)
        
        # Add screens
        screen_manager.add_screen('dashboard', DashboardScreen)
        screen_manager.add_screen('ticker', TickerScreen)
        screen_manager.add_screen('settings', SettingsScreen)
        screen_manager.add_screen('add_ticker', AddTickerScreen)
        screen_manager.add_screen('edit_ticker', EditTickerScreen, is_singleton=False)
        
        # Set initial screen
        screen_manager.switch_screen('ticker')
        
        # Create data directory if it doesn't exist
        os.makedirs(AppConfig.DATA_DIR, exist_ok=True)
        os.makedirs(AppConfig.CACHE_DIR, exist_ok=True)
        
        # Main game loop
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    screen_manager.handle_event(event)
            
            screen_manager.update_screen()
            clock.tick(AppConfig.FPS)
        
        # Clean up
        crypto_manager.stop_price_updates()
        pygame.quit()
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        crypto_manager.stop_price_updates()
        pygame.quit()
        raise

if __name__ == "__main__":
    main()