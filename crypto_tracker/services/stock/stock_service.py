"""Service for interacting with Yahoo Finance API."""

import yfinance as yf
from typing import Optional, Dict, List
from ...utils.logger import get_logger
import time

logger = get_logger(__name__)

class StockService:
    """Service for interacting with Yahoo Finance API."""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 60  # 60 seconds cache
        logger.info("StockService initialized")
    
    def search_stock(self, symbol: str) -> Optional[Dict]:
        """
        Search for a stock by symbol.
        Returns stock info if found, otherwise None.
        """
        try:
            logger.info(f"Searching for stock with symbol: {symbol}")
            ticker = yf.Ticker(symbol)
            
            # First check if we can get a valid price
            try:
                current_price = ticker.info.get('currentPrice') or ticker.info.get('regularMarketPrice')
                if current_price:
                    logger.info(f"Found stock: {symbol}")
                    return {
                        'id': symbol,  # Use symbol as ID for stocks
                        'symbol': symbol.upper(),
                        'name': ticker.info.get('longName', ticker.info.get('shortName', symbol)),
                        'type': 'stock'  # Mark as stock for differentiation
                    }
            except Exception as e:
                logger.error(f"Error getting ticker info: {e}")
            
            logger.warning(f"No stock found for symbol: {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error searching stock: {e}", exc_info=True)
            return None
    
    def get_stock_data(self, symbol: str, force_refresh: bool = False) -> Optional[Dict]:
        """
        Get detailed stock data from Yahoo Finance.
        Uses caching to prevent excessive API calls.
        """
        try:
            logger.info(f"Getting stock data for {symbol} (force_refresh: {force_refresh})")
            
            # Check cache first if not forcing refresh
            if not force_refresh and symbol in self.cache:
                cache_entry = self.cache[symbol]
                if time.time() - cache_entry['timestamp'] < self.cache_duration:
                    logger.debug(f"Using cached data for {symbol}")
                    return cache_entry['data']
            
            # Fetch fresh data
            logger.debug(f"Fetching fresh data from Yahoo Finance for {symbol}")
            ticker = yf.Ticker(symbol)
            
            # Get current price (try multiple fields as backup)
            current_price = ticker.info.get('currentPrice') or ticker.info.get('regularMarketPrice')
            if not current_price:
                logger.error(f"No price data returned from Yahoo Finance for {symbol}")
                return None
            
            # Get historical data for sparkline
            hist = ticker.history(period='7d', interval='1h')
            prices = hist['Close'].tolist() if not hist.empty else []
            
            # Calculate 24h price change
            if len(prices) >= 24:
                price_change_24h = ((prices[-1] - prices[-24]) / prices[-24]) * 100
            else:
                # Fallback to regular market change if available
                price_change_24h = ticker.info.get('regularMarketChangePercent', 0)
            
            # Process and cache the data
            processed_data = {
                'id': symbol,
                'name': ticker.info.get('longName', ticker.info.get('shortName', symbol)),
                'symbol': symbol.upper(),
                'type': 'stock',
                'image': ticker.info.get('logo_url', ''),
                'current_price': current_price,
                'price_change_24h': price_change_24h,
                'sparkline_7d': prices,
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S'),
                'market_cap': ticker.info.get('marketCap', 0),
                'volume': ticker.info.get('volume', 0)
            }
            
            # Update cache
            self.cache[symbol] = {
                'data': processed_data,
                'timestamp': time.time()
            }
            
            logger.info(f"Successfully fetched and processed data for {symbol}")
            return processed_data
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}", exc_info=True)
            return None
    
    def clear_cache(self, symbol: Optional[str] = None):
        """Clear cache for a specific stock or all stocks."""
        if symbol:
            self.cache.pop(symbol, None)
            logger.debug(f"Cleared cache for {symbol}")
        else:
            self.cache.clear()
            logger.debug("Cleared all cache") 