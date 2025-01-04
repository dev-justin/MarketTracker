import requests
import time
from datetime import datetime

class CryptoAPI:
    def __init__(self):
        self.last_request_time = 0
        self.min_request_interval = 2  # Minimum seconds between requests
        self.base_url = "https://api.coingecko.com/api/v3"
        self.symbol_mapping = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'DOGE': 'dogecoin'
        }
        self.cached_prices = {}
        self.cache_time = 0
        self.cache_duration = 30  # Cache duration in seconds

    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def get_crypto_prices(self, symbols):
        """
        Get current prices for specified crypto symbols using CoinGecko API
        """
        # Check cache first
        if time.time() - self.cache_time < self.cache_duration:
            return self.cached_prices

        prices = {}
        
        try:
            # Get all prices in one request
            coin_ids = ','.join(self.symbol_mapping[s] for s in symbols if s in self.symbol_mapping)
            
            self._wait_for_rate_limit()
            
            response = requests.get(
                f"{self.base_url}/simple/price",
                params={
                    "ids": coin_ids,
                    "vs_currencies": "usd"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Map the responses back to symbols
            for symbol in symbols:
                coin_id = self.symbol_mapping.get(symbol)
                if coin_id and coin_id in data:
                    prices[symbol] = data[coin_id]["usd"]
            
            # Update cache
            self.cached_prices = prices
            self.cache_time = time.time()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching prices ({datetime.now()}): {e}")
            # Return cached data if available, otherwise empty dict
            return self.cached_prices if self.cached_prices else {}
            
        return prices 