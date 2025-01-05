from pycoingecko import CoinGeckoAPI
import requests
import json
from typing import Optional, Dict, List
from ..utils.logger import get_logger
import os
from ..config.settings import AppConfig

logger = get_logger(__name__)

class CryptoService:
    """Service for fetching cryptocurrency data."""
    
    def __init__(self):
        """Initialize the crypto service."""
        self.client = CoinGeckoAPI()
        os.makedirs(AppConfig.CACHE_DIR, exist_ok=True)
        os.makedirs(AppConfig.DATA_DIR, exist_ok=True)
        self.tracked_symbols = self._load_tracked_symbols()
        logger.info("CryptoService initialized")
    
    def _load_tracked_symbols(self) -> List[str]:
        """Load tracked symbols from file."""
        try:
            if os.path.exists(AppConfig.TRACKED_COINS_FILE):
                with open(AppConfig.TRACKED_COINS_FILE, 'r') as f:
                    symbols = json.load(f)
                    logger.info(f"Loaded tracked symbols: {symbols}")
                    return symbols
        except Exception as e:
            logger.error(f"Error loading tracked symbols: {e}")
        
        # Default to empty list if file doesn't exist or error occurs
        return []
    
    def _save_tracked_symbols(self):
        """Save tracked symbols to file."""
        try:
            with open(AppConfig.TRACKED_COINS_FILE, 'w') as f:
                json.dump(self.tracked_symbols, f, indent=2)
            logger.info(f"Saved tracked symbols: {self.tracked_symbols}")
        except Exception as e:
            logger.error(f"Error saving tracked symbols: {e}")
    
    def search_coin(self, symbol: str) -> Optional[Dict]:
        """
        Search for a coin by symbol.
        
        Args:
            symbol: The coin symbol to search for (e.g., 'btc')
            
        Returns:
            Dictionary with coin ID and name if found, None otherwise
        """
        try:
            # Search CoinGecko
            symbol = symbol.lower()
            search_results = self.client.search(symbol)
            
            # Look for exact symbol match in coins
            for coin in search_results.get('coins', []):
                if coin['symbol'].lower() == symbol:
                    return {
                        'id': coin['id'],
                        'symbol': coin['symbol'].upper(),
                        'name': coin['name']
                    }
            
            logger.warning(f"No exact match found for symbol: {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error searching for coin: {e}")
            return None
    
    def add_tracked_symbol(self, symbol: str) -> bool:
        """
        Add a symbol to track.
        
        Args:
            symbol: The symbol to track (e.g., 'btc')
            
        Returns:
            True if successfully added, False otherwise
        """
        symbol = symbol.upper()
        if symbol in self.tracked_symbols:
            logger.info(f"Symbol already tracked: {symbol}")
            return True
            
        # Verify symbol exists before adding
        if self.search_coin(symbol):
            self.tracked_symbols.append(symbol)
            self._save_tracked_symbols()
            logger.info(f"Added symbol to track: {symbol}")
            return True
        
        return False
    
    def remove_tracked_symbol(self, symbol: str) -> bool:
        """
        Remove a symbol from tracking.
        
        Args:
            symbol: The symbol to remove (e.g., 'btc')
            
        Returns:
            True if successfully removed, False otherwise
        """
        symbol = symbol.upper()
        if symbol in self.tracked_symbols:
            self.tracked_symbols.remove(symbol)
            self._save_tracked_symbols()
            logger.info(f"Removed symbol from tracking: {symbol}")
            return True
        
        logger.warning(f"Symbol not tracked: {symbol}")
        return False
    
    def get_coin_data(self, symbol: str) -> Optional[Dict]:
        """
        Fetch coin data including price, name, and logo.
        
        Args:
            symbol: The coin symbol (e.g., 'btc')
            
        Returns:
            Dictionary containing coin data or None if fetch fails
        """
        try:
            # Search for coin
            coin_info = self.search_coin(symbol)
            if not coin_info:
                return None
            
            # Fetch coin data
            coin_data = self.client.get_coin_by_id(
                coin_info['id'],
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
            logo_path = os.path.join(AppConfig.CACHE_DIR, f"{symbol.lower()}_logo.png")
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