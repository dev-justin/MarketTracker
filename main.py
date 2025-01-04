import sys
import pygame
from crypto_tracker.config.settings import AppConfig
from crypto_tracker.constants import EventTypes, ScreenNames
from crypto_tracker.services.crypto_api import CryptoAPI
from crypto_tracker.services.crypto_store import CryptoStore
from crypto_tracker.services.display import Display
from crypto_tracker.services.screen_manager import ScreenManager
from crypto_tracker.screens.ticker_screen import TickerScreen
from crypto_tracker.screens.settings_screen import SettingsScreen
from crypto_tracker.screens.keyboard_screen import KeyboardScreen
from crypto_tracker.screens.dashboard_screen import DashboardScreen

def main():
    # Initialize services
    display = Display()
    crypto_api = CryptoAPI()
    crypto_store = CryptoStore()
    screen_manager = ScreenManager(display, crypto_api, crypto_store)
    
    # Initialize screens
    dashboard_screen = DashboardScreen(screen_manager)
    ticker_screen = TickerScreen(screen_manager)
    settings_screen = SettingsScreen(screen_manager, ticker_screen)
    keyboard_screen = KeyboardScreen(screen_manager, settings_screen.add_ticker)
    
    # Add screens to manager
    screen_manager.add_screen(ScreenNames.TICKER.value, ticker_screen)
    screen_manager.add_screen(ScreenNames.SETTINGS.value, settings_screen)
    screen_manager.add_screen(ScreenNames.KEYBOARD.value, keyboard_screen)
    screen_manager.add_screen(ScreenNames.DASHBOARD.value, dashboard_screen)
    
    # Set initial screen
    screen_manager.switch_screen(ScreenNames.TICKER.value)
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type in (
                EventTypes.FINGER_DOWN.value,
                EventTypes.FINGER_UP.value,
                EventTypes.FINGER_MOTION.value
            ):
                screen_manager.handle_event(event)
        
        # Update prices and screen
        tracked_symbols = crypto_store.get_tracked_symbols()
        prices = crypto_api.get_current_prices(tracked_symbols)
        
        # Map prices to just the price values for backward compatibility
        mapped_prices = {
            symbol: data['price']
            for symbol, data in prices.items()
        }
        screen_manager.update(mapped_prices)
        
        # Draw screen
        screen_manager.draw()
        
        # Control frame rate
        display.tick(AppConfig.FPS)
    
    # Cleanup
    display.cleanup()
    sys.exit()

if __name__ == '__main__':
    main() 