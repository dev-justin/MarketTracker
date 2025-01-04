from binance.spot import Spot
import time
from datetime import datetime, timedelta

class CryptoAPI:
    def __init__(self):
        self.client = Spot()
        self.cached_prices = {}
        self.cache_time = 0
        self.cache_duration = 10
        self.symbol_mapping = {
            'BTC': 'BTCUSDT'
        }
        self.historical_prices = {}
        self._init_historical_data()

    def _init_historical_data(self):
        """Fetch 7 days of 3-hour historical data"""
        try:
            end_time = int(time.time() * 1000)
            start_time = end_time - (7 * 24 * 60 * 60 * 1000)

            for symbol in self.symbol_mapping:
                binance_symbol = self.symbol_mapping[symbol]
                klines = self.client.klines(
                    symbol=binance_symbol,
                    interval='3h',
                    startTime=start_time,
                    endTime=end_time,
                    limit=56
                )
                self.historical_prices[symbol] = [float(k[4]) for k in klines]

        except Exception as e:
            print(f"Error fetching historical data ({datetime.now()}): {e}")
            self.historical_prices = {}

    def get_crypto_prices(self, symbols):
        """Get current prices using Binance API"""
        if time.time() - self.cache_time < self.cache_duration:
            return self.cached_prices

        prices = {}
        try:
            tickers = self.client.ticker_price()
            ticker_dict = {t['symbol']: float(t['price']) for t in tickers}
            
            for symbol in symbols:
                binance_symbol = self.symbol_mapping.get(symbol)
                if binance_symbol in ticker_dict:
                    price = ticker_dict[binance_symbol]
                    prices[symbol] = price
                    
                    if symbol in self.historical_prices:
                        self.historical_prices[symbol].append(price)
                        self.historical_prices[symbol] = self.historical_prices[symbol][-56:]
            
            self.cached_prices = prices
            self.cache_time = time.time()
            
        except Exception as e:
            print(f"Error fetching prices ({datetime.now()}): {e}")
            return self.cached_prices if self.cached_prices else {}
            
        return prices

    def get_historical_prices(self, symbol):
        """Get historical price data for a symbol"""
        return self.historical_prices.get(symbol, []) 