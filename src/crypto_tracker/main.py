import time
import pygame
from crypto_tracker.crypto_api import CryptoAPI
from crypto_tracker.display import Display

def main():
    # Initialize API first
    crypto_api = CryptoAPI()
    # Pass API to display
    display = Display(crypto_api)
    
    try:
        while True:
            # Get crypto prices (just BTC for now)
            prices = crypto_api.get_crypto_prices(['BTC'])
            
            # Process all events
            events = pygame.event.get()
            for event in events:
                print(f"Main loop event: {event.type} ({event.__dict__})")  # More detailed debug
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return
                elif event.type in (1792, 1793, 1794):  # FINGERMOTION, FINGERDOWN, FINGERUP
                    if prices:  # Only process touch events if we have prices
                        display.handle_event(event)
            
            # Update display
            if prices:  # Only update if we got valid prices
                display.update(prices)
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        display.cleanup()
    finally:
        display.cleanup()

if __name__ == "__main__":
    main() 