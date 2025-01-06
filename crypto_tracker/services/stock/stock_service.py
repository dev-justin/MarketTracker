"""Service for interacting with Yahoo Finance API."""

import yfinance as yf
import requests
from typing import Optional, Dict, List
from ...utils.logger import get_logger
from ...config.settings import AppConfig
import time
import os

logger = get_logger(__name__)

class StockService:
    """Service for interacting with Yahoo Finance API."""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 60  # 60 seconds cache
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
    
    def search_stock(self, symbol: str) -> Optional[Dict]:
        """
        Search for a stock by symbol.
        Returns stock info if found, otherwise None.
        """
        try:
            logger.info(f"Searching for stock with symbol: {symbol}")
            ticker = yf.Ticker(symbol)
            
            try:
                info = ticker.info
                if info:
                    # Get logo URL from Yahoo Finance
                    logo_url = info.get('logo_url', '')
                    if logo_url:
                        self._download_logo(symbol, logo_url)
                    
                    logger.info(f"Found stock: {symbol}")
                    return {
                        'id': symbol,  # Use symbol as ID for stocks
                        'symbol': symbol.upper(),
                        'name': info.get('longName', info.get('shortName', symbol)),
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
            info = ticker.info
            
            # Debug log the available info keys
            logger.debug(f"Available info keys: {info.keys() if info else 'No info available'}")
            
            if not info:
                logger.error(f"No data returned from Yahoo Finance for {symbol}")
                return None
            
            # Get current price (try multiple fields as backup)
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            if not current_price:
                logger.error(f"No price data returned from Yahoo Finance for {symbol}")
                return None
            
            # Get historical data for sparkline (5 days, 30-minute intervals)
            # Note: Yahoo Finance requires specific period values
            hist = ticker.history(period='5d', interval='30m')  # Using 5d as it's a valid Yahoo Finance period
            logger.debug(f"Historical data shape: {hist.shape if not hist.empty else 'Empty'}")
            logger.debug(f"Historical data columns: {hist.columns.tolist() if not hist.empty else 'No columns'}")
            
            prices = hist['Close'].tolist() if not hist.empty else []
            logger.debug(f"Number of price points: {len(prices)}")
            
            # If we don't have enough data points, try a different interval
            if len(prices) < 50:  # We want at least 50 points for a good sparkline
                logger.debug("Not enough data points, trying different interval")
                hist = ticker.history(period='5d', interval='1h')
                prices = hist['Close'].tolist() if not hist.empty else []
                logger.debug(f"Number of price points after adjustment: {len(prices)}")
            
            # Ensure we have enough points for the sparkline
            if prices:
                # Normalize the number of points to match crypto format
                target_points = 120  # 5 days * 24 hours
                if len(prices) > target_points:
                    # Take evenly spaced samples
                    step = len(prices) // target_points
                    prices = prices[::step][:target_points]
                logger.debug(f"Final number of price points: {len(prices)}")
            
            # Calculate 24h price change
            if len(prices) >= 24:
                price_change_24h = ((prices[-1] - prices[-24]) / prices[-24]) * 100
            else:
                price_change_24h = info.get('regularMarketChangePercent', 0)
            
            # Get and cache logo if available
            # Try multiple sources for the logo
            website = info.get('website', '')
            domain = website.replace('http://', '').replace('https://', '').split('/')[0] if website else ''
            
            logo_url = (
                info.get('logo_url') or 
                info.get('logoUrl') or 
                info.get('logo') or
                (f"https://logo.clearbit.com/{domain}" if domain else None) or
                f"https://storage.googleapis.com/iex/api/logos/{symbol.upper()}.png"  # IEX fallback
            )
            logger.debug(f"Logo URL found: {logo_url if logo_url else 'No logo URL'}")
            
            if logo_url and logo_url.startswith('http'):
                try:
                    # Test if the URL is accessible
                    response = requests.head(logo_url, timeout=5)
                    if response.status_code == 200:
                        logo_path = self._download_logo(symbol, logo_url)
                        logger.debug(f"Logo saved to: {logo_path if logo_path else 'Logo not saved'}")
                    else:
                        logger.warning(f"Logo URL returned status code {response.status_code}")
                except Exception as e:
                    logger.warning(f"Error checking logo URL: {e}")
            else:
                logger.warning(f"No valid logo URL found for {symbol}")
            
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
            
            # Debug log the processed data
            logger.debug(f"Processed data: {processed_data}")
            
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