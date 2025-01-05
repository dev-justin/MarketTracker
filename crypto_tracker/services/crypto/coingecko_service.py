from pycoingecko import CoinGeckoAPI
from typing import Optional, Dict, List
from ...utils.logger import get_logger

logger = get_logger(__name__)

class CoinGeckoService:
    """Service for interacting with CoinGecko API."""
    
    def __init__(self):
        self.coingecko = CoinGeckoAPI()
    
    def search_coin(self, symbol: str) -> Optional[Dict]:
        """
        Search for a coin by symbol.
        Returns 'id' if found, otherwise None.
        """
        try:
            search_results = self.coingecko.search(symbol.lower())
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

            coin_data = self.coingecko.get_coin_by_id(
                coin_id,
                localization=False,
                tickers=False,
                market_data=True,
                community_data=False,
                developer_data=False,
                sparkline=True
            )

            print(coin_data)

            return {
                'id': coin_data['id'],
                'name': coin_data['name'],
                'symbol': coin_data['symbol'],
                'image': coin_data['image']['small'],
                'price_change_24h': coin_data['market_data']['price_change_percentage_24h'],
                'sparkline_7d': coin_data['market_data']['sparkline_7d']['price']
            }
            
        except Exception as e:
            logger.error(f"Error fetching coin data for {coin_id}: {e}")
            return None