from pycoingecko import CoinGeckoAPI
from typing import Optional, Dict, List
from ...utils.logger import get_logger
import time

logger = get_logger(__name__)

class CoinGeckoService:
    """Service for interacting with CoinGecko API."""
    
    def __init__(self):
        self.client = CoinGeckoAPI()
        self.cache = {}
        self.cache_duration = 60  # 60 seconds cache
    
    def search_coin(self, symbol: str) -> Optional[Dict]:
        """
        Search for a coin by symbol.
        Returns 'id' if found, otherwise None.
        """
        try:
            search_results = self.client.search(symbol.lower())
            logger.info(f"Search results: {search_results.get('coins', [])}")
            for coin in search_results.get('coins', []):
                if coin['symbol'].lower() == symbol.lower():
                    return coin['id']
            logger.warning(f"No exact match found for symbol: {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error searching coin: {e}")
            return None
    
    def get_coin_data(self, coin_id: str) -> Optional[Dict]:
        """
        Get detailed coin data from CoinGecko.
        Uses caching to prevent excessive API calls.
        """
        try:
            # Check cache first
            if coin_id in self.cache:
                cache_entry = self.cache[coin_id]
                if time.time() - cache_entry['timestamp'] < self.cache_duration:
                    return cache_entry['data']
            
            # Fetch fresh data
            coin_data = self.client.get_coin_by_id(
                coin_id,
                localization=False,
                tickers=False,
                market_data=True,
                community_data=False,
                developer_data=False,
                sparkline=True
            )
            
            # Cache the result
            self.cache[coin_id] = {
                'data': coin_data,
                'timestamp': time.time()
            }
            
            return coin_data
            
        except Exception as e:
            logger.error(f"Error fetching coin data for {coin_id}: {e}")
            return None
    
    def get_coin_price_data(self, coin_id: str) -> Optional[Dict]:
        """
        Get current price and market data for a coin.
        Returns formatted price data dictionary.
        """
        try:
            coin_data = self.get_coin_data(coin_id)
            if not coin_data or 'market_data' not in coin_data:
                return None
            
            market_data = coin_data['market_data']
            return {
                'current_price': market_data['current_price']['usd'],
                'price_change_24h': round(market_data['price_change_percentage_24h'], 2),
                'sparkline_7d': market_data['sparkline_7d']['price']
            }
            
        except Exception as e:
            logger.error(f"Error getting price data for {coin_id}: {e}")
            return None 