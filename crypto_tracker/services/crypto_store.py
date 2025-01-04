import os
import json
from typing import Dict, List, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)

class CryptoStore:
    """Service for managing tracked cryptocurrency data."""
    
    def __init__(self):
        """Initialize the crypto store."""
        self.config_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'tickers.json')
        self.tracked_symbols = self._load_tickers()
        self.historical_prices: Dict[str, List[float]] = {}
        logger.info("CryptoStore initialized")
    
    def _load_tickers(self) -> List[str]:
        """Load tracked tickers from file."""
        logger.info("Loading tickers from file...")
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # Default tickers
        default_symbols = ['BTC', 'ETH']
        
        try:
            if os.path.exists(self.config_file):
                logger.info("Found existing tickers file")
                with open(self.config_file, 'r') as f:
                    loaded_symbols = json.load(f)
                    logger.info(f"Loaded tickers: {loaded_symbols}")
                    return loaded_symbols
            else:
                logger.info("No tickers file found, creating with defaults")
                self._save_tickers(default_symbols)
                return default_symbols
        except Exception as e:
            logger.error(f"Error loading tickers: {e}")
            return default_symbols
    
    def _save_tickers(self, symbols: List[str]) -> None:
        """Save tracked tickers to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(symbols, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving tickers: {e}")
    
    def add_ticker(self, symbol: str) -> bool:
        """Add a new ticker to track."""
        symbol = symbol.upper()
        logger.info(f"Adding ticker: {symbol}")
        
        if symbol not in self.tracked_symbols:
            self.tracked_symbols.append(symbol)
            self._save_tickers(self.tracked_symbols)
            logger.info(f"Successfully added {symbol}")
            return True
            
        logger.info(f"Ticker {symbol} already exists")
        return False
    
    def remove_ticker(self, symbol: str) -> bool:
        """Remove a ticker from tracking."""
        symbol = symbol.upper()
        if symbol in self.tracked_symbols:
            self.tracked_symbols.remove(symbol)
            if symbol in self.historical_prices:
                del self.historical_prices[symbol]
            self._save_tickers(self.tracked_symbols)
            logger.info(f"Removed ticker: {symbol}")
            return True
        return False
    
    def get_tracked_symbols(self) -> List[str]:
        """Get list of currently tracked symbols."""
        return self.tracked_symbols
    
    def update_historical_prices(self, symbol: str, prices: List[float]) -> None:
        """Update historical prices for a symbol."""
        self.historical_prices[symbol] = prices
    
    def get_historical_prices(self, symbol: str) -> List[float]:
        """Get historical prices for a symbol."""
        return self.historical_prices.get(symbol, []) 