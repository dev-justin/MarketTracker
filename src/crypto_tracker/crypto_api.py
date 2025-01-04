from binance.spot import Spot
import time
from datetime import datetime

class CryptoAPI:
    def __init__(self):
        self.client = Spot()
        self.cached_prices = {}
        self.cache_time = 0
        self.cache_duration = 10  # Cache duration in seconds
        self.symbol_mapping = {
            'BTC': 'BTCUSDT',
            'ETH': 'ETHUSDT',
            'DOGE': 'DOGEUSDT'
        }

    def get_crypto_prices(self, symbols):
        """Get current prices using Binance API"""
        # Check cache first
        if time.time() - self.cache_time < self.cache_duration:
            return self.cached_prices

        prices = {}
        try:
            # Get all tickers in one request
            tickers = self.client.ticker_price()
            ticker_dict = {t['symbol']: float(t['price']) for t in tickers}
            
            for symbol in symbols:
                binance_symbol = self.symbol_mapping.get(symbol)
                if binance_symbol in ticker_dict:
                    prices[symbol] = ticker_dict[binance_symbol]
            
            # Update cache
            self.cached_prices = prices
            self.cache_time = time.time()
            
        except Exception as e:
            print(f"Error fetching prices ({datetime.now()}): {e}")
            return self.cached_prices if self.cached_prices else {}
            
        return prices 