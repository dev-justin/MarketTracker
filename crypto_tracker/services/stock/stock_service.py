"""Service for interacting with Yahoo Finance API."""

import yfinance as yf
import requests
from typing import Optional, Dict, List, Tuple
from ...utils.logger import get_logger
from ...config.settings import AppConfig
from .stock_storage import StockStorage
import time
import os

logger = get_logger(__name__)

class StockService:
    """Service for interacting with Yahoo Finance API."""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutes cache duration
        self.storage = StockStorage()
        logger.info("StockService initialized")
    
    def _download_logo(self, symbol: str, logo_url: str) -> str:
        """Download and cache the stock logo."""
        try:
            logo_path = os.path.join(AppConfig.CACHE_DIR, f"{symbol.lower()}_logo.png")
            if not os.path.exists(logo_path):
                response = requests.get(logo_url)
                if response.status_code == 200:
                    with open(logo_path, 'wb') as f:
                        f.write(response.content)
                    logger.info(f"Downloaded logo for {symbol}")
                    return logo_path
            return logo_path
        except Exception as e:
            logger.error(f"Error downloading logo for {symbol}: {e}")
            return ""
    
    def get_available_exchanges(self, symbol: str) -> List[Dict[str, str]]:
        """
        Get available exchanges for a stock symbol.
        Returns a list of dictionaries with exchange info.
        """
        try:
            logger.info(f"Getting available exchanges for symbol: {symbol}")
            exchanges = []
            
            # Check US markets first (NYSE/NASDAQ)
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.fast_info
                if hasattr(info, 'last_price') and info.last_price is not None:
                    # Get detailed info only if basic check passes
                    full_info = ticker.info
                    exchange_name = full_info.get('exchange', 'NYSE/NASDAQ')
                    if exchange_name == 'NMS':
                        exchange_name = 'NASDAQ'
                    elif exchange_name in ['NYQ', 'NGM']:
                        exchange_name = 'NYSE'
                    
                    exchanges.append({
                        'symbol': symbol,
                        'name': exchange_name,
                        'suffix': ''
                    })
            except Exception as e:
                logger.debug(f"Error checking US markets: {e}")
            
            # If we found a US listing, don't check international exchanges
            if exchanges:
                logger.info(f"Found US listing for {symbol}, skipping international exchanges")
                return exchanges
            
            # Common international exchanges to check
            suffixes = [
                ('.L', 'London Stock Exchange'),
                ('.TO', 'Toronto Stock Exchange'),
                ('.F', 'Frankfurt Stock Exchange'),
                ('.PA', 'Euronext Paris'),
                ('.MI', 'Borsa Italiana'),
                ('.DE', 'Deutsche Börse'),
                ('.AX', 'Australian Securities Exchange'),
                ('.HK', 'Hong Kong Stock Exchange'),
                ('.T', 'Tokyo Stock Exchange')
            ]
            
            for suffix, exchange_name in suffixes:
                try:
                    test_symbol = f"{symbol}{suffix}"
                    ticker = yf.Ticker(test_symbol)
                    info = ticker.fast_info
                    
                    # Only get full info if basic check passes
                    if hasattr(info, 'last_price') and info.last_price is not None:
                        exchanges.append({
                            'symbol': test_symbol,
                            'name': exchange_name,
                            'suffix': suffix
                        })
                        time.sleep(0.1)  # Add small delay between requests
                except Exception as e:
                    logger.debug(f"Error checking {exchange_name}: {e}")
                    continue
            
            logger.info(f"Found {len(exchanges)} exchanges for {symbol}")
            return exchanges
            
        except Exception as e:
            logger.error(f"Error getting exchanges: {e}")
            return []
    
    def search_stock(self, symbol: str, exchange_suffix: str = '') -> Optional[Dict]:
        """
        Search for a stock by symbol and exchange.
        Returns stock info if found, otherwise None.
        """
        try:
            full_symbol = f"{symbol}{exchange_suffix}"
            logger.info(f"Searching for stock with symbol: {full_symbol}")
            ticker = yf.Ticker(full_symbol)
            
            try:
                info = ticker.info
                if info:
                    # Get logo URL from Yahoo Finance
                    website = info.get('website', '')
                    domain = website.replace('http://', '').replace('https://', '').split('/')[0] if website else ''
                    
                    logo_url = (
                        info.get('logo_url') or 
                        info.get('logoUrl') or 
                        info.get('logo') or
                        (f"https://logo.clearbit.com/{domain}" if domain else None) or
                        f"https://storage.googleapis.com/iex/api/logos/{symbol.upper()}.png"  # IEX fallback
                    )
                    
                    if logo_url and logo_url.startswith('http'):
                        self._download_logo(symbol, logo_url)
                    
                    logger.info(f"Found stock: {full_symbol}")
                    return {
                        'id': full_symbol,  # Use full symbol as ID for stocks
                        'symbol': full_symbol.upper(),
                        'name': info.get('longName', info.get('shortName', symbol)),
                        'type': 'stock',  # Mark as stock for differentiation
                        'exchange_suffix': exchange_suffix  # Store the exchange suffix
                    }
            except Exception as e:
                logger.error(f"Error getting ticker info: {e}")
            
            logger.warning(f"No stock found for symbol: {full_symbol}")
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
            # Check cache first if not forcing refresh
            if not force_refresh and symbol in self.cache:
                cache_entry = self.cache[symbol]
                if time.time() - cache_entry['timestamp'] < self.cache_duration:
                    return cache_entry['data']
            
            # Fetch fresh data
            logger.info(f"Fetching fresh data for {symbol}")
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                logger.error(f"No data returned from Yahoo Finance for {symbol}")
                return None
            
            # Get current price (try multiple fields as backup)
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            if not current_price:
                logger.error(f"No price data returned from Yahoo Finance for {symbol}")
                return None
            
            # Get historical data for sparkline (5 days, 30-minute intervals)
            hist = ticker.history(period='5d', interval='30m')
            prices = hist['Close'].tolist() if not hist.empty else []
            
            # If we don't have enough data points, try a different interval
            if len(prices) < 50:
                hist = ticker.history(period='5d', interval='1h')
                prices = hist['Close'].tolist() if not hist.empty else []
            
            # Ensure we have enough points for the sparkline
            if prices:
                target_points = 120  # 5 days * 24 hours
                if len(prices) > target_points:
                    step = len(prices) // target_points
                    prices = prices[::step][:target_points]
            
            # Calculate 24h price change
            if len(prices) >= 24:
                price_change_24h = ((prices[-1] - prices[-24]) / prices[-24]) * 100
            else:
                price_change_24h = info.get('regularMarketChangePercent', 0)
            
            # Process and cache the data (matching crypto format)
            processed_data = {
                'id': symbol,
                'name': info.get('longName', info.get('shortName', symbol)),
                'symbol': symbol.upper(),
                'type': 'stock',
                'current_price': current_price,
                'price_change_24h': price_change_24h,
                'sparkline_7d': prices,
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S'),
                'market_cap': info.get('marketCap', 0),
                'volume': info.get('volume', 0),
                'favorite': False  # Default to not favorited
            }
            
            # Update cache
            self.cache[symbol] = {
                'data': processed_data,
                'timestamp': time.time()
            }
            
            # Update storage with new data
            stored_stock = self.storage.get_stock(symbol)
            if stored_stock:
                processed_data['favorite'] = stored_stock.get('favorite', False)
                self.storage.update_stock_data(symbol, processed_data)
            
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