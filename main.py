import time
import pygame
from crypto_tracker.services.crypto_api import CryptoAPI
from crypto_tracker.services.display import Display

def main():
    crypto_api = CryptoAPI()
    display = Display(crypto_api)
    prices = None
    
    try:
        while True:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    return
                elif event.type in (1792, 1793, 1794):  # Touch events
                    print(f"Touch event: {event}")
                    display.handle_event(event)
            
            # Try to get new prices for all tracked symbols
            try:
                tracked_symbols = crypto_api.get_tracked_symbols()
                new_prices = crypto_api.get_crypto_prices(tracked_symbols)
                if new_prices:  # Only update if we got valid prices
                    prices = new_prices
            except Exception as e:
                print(f"Error fetching prices: {e}")
            
            # Update and draw regardless of whether we got new prices
            display.update(prices)
            display.draw()
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        display.cleanup()
    finally:
        display.cleanup()

if __name__ == "__main__":
    main() 