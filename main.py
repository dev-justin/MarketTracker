import sys
import pygame
from crypto_tracker.config.settings import AppConfig
from crypto_tracker.constants import EventTypes
from crypto_tracker.services.crypto_api import CryptoAPI
from crypto_tracker.services.screen_manager import ScreenManager

def main():
    # Initialize services
    crypto_api = CryptoAPI()
    screen_manager = ScreenManager(crypto_api)
    
    # Main game loop
    clock = pygame.time.Clock()
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
        tracked_symbols = crypto_api.get_tracked_symbols()
        prices = crypto_api.get_crypto_prices(tracked_symbols)
        screen_manager.update(prices)
        
        # Draw screen
        screen_manager.draw()
        
        # Control frame rate
        clock.tick(AppConfig.FPS)
    
    # Cleanup
    screen_manager.cleanup()
    sys.exit()

if __name__ == '__main__':
    main() 