import time
import pygame
from crypto_tracker.crypto_api import CryptoAPI
from crypto_tracker.display import Display

def main():
    # Initialize display and API
    display = Display()
    crypto_api = CryptoAPI()
    
    try:
        while True:
            # Get crypto prices
            prices = crypto_api.get_crypto_prices(['BTC', 'ETH', 'DOGE'])
            
            # Update display
            display.update(prices)
            
            # Wait for 5 seconds before next update
            time.sleep(5)
            
    except KeyboardInterrupt:
        display.cleanup()

if __name__ == "__main__":
    main() 