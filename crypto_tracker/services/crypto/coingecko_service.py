"""

Service for interacting with CoinGecko API.

"""

from pycoingecko import CoinGeckoAPI
from typing import Optional, Dict, List
from ...utils.logger import get_logger
import time

logger = get_logger(__name__)

class CoinGeckoService:
    """Service for interacting with CoinGecko API."""
    
    def __init__(self):
        self.coingecko = CoinGeckoAPI()
        self.cache = {}
        self.cache_duration = 60  # 60 seconds cache
    
    def search_coin(self, symbol: str) -> Optional[Dict]:
        """
        Search for a coin by symbol.
        Returns coin info if found, otherwise None.
        """
        try:
            search_results = self.coingecko.search(symbol.lower())
            for coin in search_results.get('coins', []):
                if coin['symbol'].lower() == symbol.lower():
                    return {
                        'id': coin['id'],
                        'symbol': coin['symbol'].upper(),
                        'name': coin['name']
                    }
            logger.warning(f"No exact match found for symbol: {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error searching coin: {e}")
            return None
    
    def get_coin_data(self, coin_id: str, force_refresh: bool = False) -> Optional[Dict]:
        """
        Get detailed coin data from CoinGecko.
        Uses caching to prevent excessive API calls.
        """
        try:
            # Check cache first if not forcing refresh
            if not force_refresh and coin_id in self.cache:
                cache_entry = self.cache[coin_id]
                if time.time() - cache_entry['timestamp'] < self.cache_duration:
                    logger.debug(f"Using cached data for {coin_id}")
                    return cache_entry['data']
            
            # Fetch fresh data
            coin_data = self.coingecko.get_coin_by_id(
                coin_id,
                localization=False,
                tickers=False,
                market_data=True,
                community_data=False,
                developer_data=False,
                sparkline=True
            )
            
            # Process and cache the data
            processed_data = {
                'id': coin_data['id'],
                'name': coin_data['name'],
                'symbol': coin_data['symbol'].upper(),
                'image': coin_data['image']['small'],
                'current_price': coin_data['market_data']['current_price']['usd'],
                'price_change_24h': coin_data['market_data']['price_change_percentage_24h'],
                'sparkline_7d': coin_data['market_data'].get('sparkline_7d', {}).get('price', []),
                'last_updated': coin_data['market_data']['last_updated']
            }
            
            # Update cache
            self.cache[coin_id] = {
                'data': processed_data,
                'timestamp': time.time()
            }
            
            logger.info(f"Fetched fresh data for {coin_id}")
            return processed_data
            
        except Exception as e:
            logger.error(f"Error fetching coin data for {coin_id}: {e}")
            return None
    
    def clear_cache(self, coin_id: Optional[str] = None):
        """Clear cache for a specific coin or all coins."""
        if coin_id:
            self.cache.pop(coin_id, None)
            logger.debug(f"Cleared cache for {coin_id}")
        else:
            self.cache.clear()
            logger.debug("Cleared all cache")