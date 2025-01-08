"""Main entry point for the crypto tracker application."""

import pygame
import sys
import logging
from crypto_tracker.config.settings import AppConfig
from crypto_tracker.services.service_manager import ServiceManager
from crypto_tracker.services.display import Display
from crypto_tracker.services.screen_manager import ScreenManager
from crypto_tracker.services.crypto.crypto_manager import CryptoManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the crypto tracker application."""
    try:
        # Initialize pygame
        pygame.init()
        
        # Initialize services
        service_manager = ServiceManager()
        
        # Initialize crypto manager first
        crypto_manager = CryptoManager()
        service_manager.register_service('crypto_manager', crypto_manager)
        crypto_manager.start_price_updates()
        
        # Initialize display
        display = Display()
        service_manager.register_service('display', display)
        
        # Initialize screen manager
        screen_manager = ScreenManager(display)
        service_manager.register_service('screen_manager', screen_manager)
        
        # Main game loop
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                else:
                    screen_manager.handle_event(event)
            
            screen_manager.update_screen()
            clock.tick(AppConfig.FPS)
        
        # Clean up
        crypto_manager.stop_price_updates()
        pygame.quit()
        sys.exit()
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        if 'crypto_manager' in locals():
            crypto_manager.stop_price_updates()
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()