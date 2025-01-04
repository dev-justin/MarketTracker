from binance.spot import Spot
import time
from datetime import datetime, timedelta

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
        # Initialize with historical data
        self.historical_prices = {}
        self._init_historical_data()

    def _init_historical_data(self):
        """Fetch 7 days of hourly historical data"""
        try:
            # Get timestamps for start and end
            end_time = int(time.time() * 1000)  # Current time in milliseconds
            start_time = end_time - (7 * 24 * 60 * 60 * 1000)  # 7 days ago

            # Get historical data for each symbol
            for symbol in self.symbol_mapping:
                binance_symbol = self.symbol_mapping[symbol]
                # Fetch 1-hour klines (candlesticks)
                klines = self.client.klines(
                    symbol=binance_symbol,
                    interval='1h',
                    startTime=start_time,
                    endTime=end_time,
                    limit=168  # 7 days * 24 hours
                )
                # Extract closing prices from klines
                self.historical_prices[symbol] = [float(k[4]) for k in klines]  # k[4] is closing price

        except Exception as e:
            print(f"Error fetching historical data ({datetime.now()}): {e}")
            self.historical_prices = {}

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
                    price = ticker_dict[binance_symbol]
                    prices[symbol] = price
                    
                    # Update historical data with new price
                    if symbol in self.historical_prices:
                        self.historical_prices[symbol].append(price)
                        # Keep only last 168 points (7 days * 24 hours)
                        self.historical_prices[symbol] = self.historical_prices[symbol][-168:]
            
            # Update cache
            self.cached_prices = prices
            self.cache_time = time.time()
            
        except Exception as e:
            print(f"Error fetching prices ({datetime.now()}): {e}")
            return self.cached_prices if self.cached_prices else {}
            
        return prices

    def get_historical_prices(self, symbol):
        """Get historical price data for a symbol"""
        return self.historical_prices.get(symbol, []) 