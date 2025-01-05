from pycoingecko import CoinGeckoAPI
import requests
from typing import Optional, Dict
from ..utils.logger import get_logger
import os
from ..config.settings import AppConfig

logger = get_logger(__name__)

class CryptoService:
    """Service for fetching cryptocurrency data."""
    
    def __init__(self):
        """Initialize the crypto service."""
        self.client = CoinGeckoAPI()
        self.cache_dir = os.path.join(AppConfig.ASSETS_DIR, 'cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        logger.info("CryptoService initialized")
    
    def get_coin_data(self, symbol: str) -> Optional[Dict]:
        """
        Fetch coin data including price, name, and logo.
        
        Args:
            symbol: The coin symbol (e.g., 'btc')
            
        Returns:
            Dictionary containing coin data or None if fetch fails
        """
        try:
            # Map of common symbols to CoinGecko IDs
            symbol_to_id = {
                'btc': 'bitcoin',
                'eth': 'ethereum',
                'doge': 'dogecoin',
                'sol': 'solana',
            }
            
            symbol = symbol.lower()
            coin_id = symbol_to_id.get(symbol)
            if not coin_id:
                logger.error(f"Unknown symbol: {symbol}")
                return None
            
            # Fetch coin data
            coin_data = self.client.get_coin_by_id(
                coin_id,
                localization=False,
                tickers=False,
                market_data=True,
                community_data=False,
                developer_data=False,
                sparkline=False
            )
            
            # Extract relevant data
            price = coin_data['market_data']['current_price']['usd']
            name = coin_data['name']
            symbol = coin_data['symbol'].upper()
            image_url = coin_data['image']['large']
            
            # Download and cache the logo
            logo_path = os.path.join(self.cache_dir, f"{symbol.lower()}_logo.png")
            if not os.path.exists(logo_path):
                response = requests.get(image_url)
                if response.status_code == 200:
                    with open(logo_path, 'wb') as f:
                        f.write(response.content)
                    logger.debug(f"Cached logo for {symbol}")
            
            result = {
                'symbol': symbol,
                'name': name,
                'price': price,
                'logo_path': logo_path
            }
            
            logger.info(f"Fetched data for {symbol}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching coin data: {e}")
            return None 