import time
import pygame
from crypto_tracker.services.crypto_api import CryptoAPI
from crypto_tracker.services.screen_manager import ScreenManager
from crypto_tracker.constants import EventTypes
from crypto_tracker.utils.logger import get_logger
from crypto_tracker.exceptions import CryptoTrackerError

logger = get_logger(__name__)

def main() -> None:
    """Main application entry point."""
    try:
        logger.info("Starting CryptoTracker application")
        crypto_api = CryptoAPI()
        screen_manager = ScreenManager(crypto_api)
        prices = None
        
        while True:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    logger.info("Quit event received")
                    return
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    logger.info("Quit key pressed")
                    return
                elif event.type in (
                    EventTypes.FINGER_DOWN.value,
                    EventTypes.FINGER_UP.value,
                    EventTypes.FINGER_MOTION.value
                ):
                    logger.debug(f"Touch event: {event}")
                    screen_manager.handle_event(event)
            
            # Try to get new prices for all tracked symbols
            try:
                tracked_symbols = crypto_api.get_tracked_symbols()
                new_prices = crypto_api.get_crypto_prices(tracked_symbols)
                if new_prices:  # Only update if we got valid prices
                    prices = new_prices
            except Exception as e:
                logger.error(f"Error fetching prices: {e}")
            
            # Update and draw regardless of whether we got new prices
            screen_manager.update(prices)
            screen_manager.draw()
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except CryptoTrackerError as e:
        logger.error(f"Application error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("Cleaning up application")
        screen_manager.cleanup()

if __name__ == "__main__":
    main() 