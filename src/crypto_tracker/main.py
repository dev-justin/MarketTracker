import time
import pygame
from crypto_tracker.crypto_api import get_crypto_prices
from crypto_tracker.display import Display

def main():
    # Initialize display
    display = Display()
    
    try:
        while True:
            # Get crypto prices
            prices = get_crypto_prices(['BTC', 'ETH', 'DOGE'])
            
            # Update display
            display.update(prices)
            
            # Wait for 1 minute before next update
            time.sleep(60)
            
    except KeyboardInterrupt:
        display.cleanup()

if __name__ == "__main__":
    main() 