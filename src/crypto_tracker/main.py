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
            
            # Update display
            if prices:  # Only update if we got valid prices
                display.update(prices)
            
            # Wait for 5 seconds before next update
            time.sleep(5)
            
    except KeyboardInterrupt:
        display.cleanup()

if __name__ == "__main__":
    main() 