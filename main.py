import time
import pygame
from crypto_tracker.crypto_api import CryptoAPI
from crypto_tracker.display import Display

def main():
    crypto_api = CryptoAPI()
    display = Display(crypto_api)
    
    try:
        while True:
            # Get crypto prices for all symbols
            prices = crypto_api.get_crypto_prices(['BTC', 'ETH'])
            
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    return
                elif event.type in (1792, 1793, 1794):  # Touch events
                    if prices:
                        display.handle_event(event)
            
            if prices:
                display.update(prices)
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        display.cleanup()
    finally:
        display.cleanup()

if __name__ == "__main__":
    main() 