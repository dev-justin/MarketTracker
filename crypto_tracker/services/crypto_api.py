from binance.spot import Spot
import time
from datetime import datetime, timedelta
import json
import os

class CryptoAPI:
    def __init__(self):
        print("Initializing CryptoAPI...")
        self.client = Spot()
        self.cached_prices = {}
        self.cache_time = 0
        self.cache_duration = 10
        self.config_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'tickers.json')
        print(f"Config file path: {self.config_file}")
        self.symbol_mapping = self._load_tickers()
        print(f"Loaded tickers: {self.symbol_mapping}")
        self.historical_prices = {}
        self._init_historical_data()

    def _load_tickers(self):
        print("Loading tickers from file...")
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # Default tickers
        default_mapping = {
            'BTC': 'BTCUSDT',
            'ETH': 'ETHUSDT'
        }
        
        try:
            if os.path.exists(self.config_file):
                print(f"Found existing tickers file")
                with open(self.config_file, 'r') as f:
                    loaded_mapping = json.load(f)
                    print(f"Loaded tickers: {loaded_mapping}")
                    return loaded_mapping
            else:
                print("No tickers file found, creating with defaults")
                self._save_tickers(default_mapping)
                return default_mapping
        except Exception as e:
            print(f"Error loading tickers: {e}")
            return default_mapping

    def _save_tickers(self, mapping):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(mapping, f, indent=4)
        except Exception as e:
            print(f"Error saving tickers: {e}")

    def add_ticker(self, symbol):
        """Add a new ticker to track"""
        symbol = symbol.upper()
        print(f"Attempting to add ticker: {symbol}")
        if symbol not in self.symbol_mapping:
            binance_symbol = f"{symbol}USDT"
            
            # Verify the symbol exists on Binance
            try:
                print(f"Verifying {binance_symbol} exists on Binance")
                self.client.ticker_price(symbol=binance_symbol)
                self.symbol_mapping[symbol] = binance_symbol
                self._save_tickers(self.symbol_mapping)
                print(f"Successfully added {symbol}")
                # Initialize historical data for new symbol
                self._init_historical_data_for_symbol(symbol)
                return True
            except Exception as e:
                print(f"Error adding ticker {symbol}: {e}")
                return False
        print(f"Ticker {symbol} already exists")
        return False

    def remove_ticker(self, symbol):
        """Remove a ticker from tracking"""
        symbol = symbol.upper()
        if symbol in self.symbol_mapping:
            del self.symbol_mapping[symbol]
            if symbol in self.historical_prices:
                del self.historical_prices[symbol]
            self._save_tickers(self.symbol_mapping)
            return True
        return False

    def get_tracked_symbols(self):
        """Get list of currently tracked symbols"""
        return list(self.symbol_mapping.keys())

    def _init_historical_data_for_symbol(self, symbol):
        """Fetch historical data for a single symbol"""
        print(f"Fetching historical data for {symbol}")
        try:
            end_time = int(time.time() * 1000)
            start_time = end_time - (7 * 24 * 60 * 60 * 1000)
            
            binance_symbol = self.symbol_mapping[symbol]
            klines = self.client.klines(
                symbol=binance_symbol,
                interval='6h',
                startTime=start_time,
                endTime=end_time,
                limit=28
            )
            self.historical_prices[symbol] = [float(k[4]) for k in klines]
            print(f"Got {len(self.historical_prices[symbol])} historical prices for {symbol}")
        except Exception as e:
            print(f"Error fetching historical data for {symbol} ({datetime.now()}): {e}")

    def _init_historical_data(self):
        """Fetch 7 days of 6-hour historical data for all symbols"""
        print("Initializing historical data for all symbols")
        for symbol in self.symbol_mapping:
            self._init_historical_data_for_symbol(symbol)

    def get_crypto_prices(self, symbols):
        """Get current prices using Binance API"""
        print(f"Fetching prices for symbols: {symbols}")
        if time.time() - self.cache_time < self.cache_duration:
            print("Using cached prices")
            return self.cached_prices

        prices = {}
        try:
            print("Fetching fresh prices from Binance")
            tickers = self.client.ticker_price()
            ticker_dict = {t['symbol']: float(t['price']) for t in tickers}
            
            for symbol in symbols:
                binance_symbol = self.symbol_mapping.get(symbol)
                if binance_symbol in ticker_dict:
                    price = ticker_dict[binance_symbol]
                    prices[symbol] = price
                    print(f"Price for {symbol}: ${price:,.2f}")
                    
                    # Only update historical prices if we've entered a new 6-hour interval
                    current_hour = datetime.now().hour
                    if current_hour % 6 == 0 and symbol in self.historical_prices:
                        last_price_time = self.cache_time
                        last_price_hour = datetime.fromtimestamp(last_price_time).hour
                        if last_price_hour % 6 != 0:  # Only append if we haven't already for this interval
                            print(f"Adding new historical price for {symbol}")
                            self.historical_prices[symbol].append(price)
                            self.historical_prices[symbol] = self.historical_prices[symbol][-28:]
            
            self.cached_prices = prices
            self.cache_time = time.time()
            
        except Exception as e:
            print(f"Error fetching prices ({datetime.now()}): {e}")
            return self.cached_prices if self.cached_prices else {}
            
        return prices

    def get_historical_prices(self, symbol):
        """Get historical price data for a symbol"""
        return self.historical_prices.get(symbol, []) 