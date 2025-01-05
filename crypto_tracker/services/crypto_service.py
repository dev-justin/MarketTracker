from pycoingecko import CoinGeckoAPI
import requests
import json
import time
from typing import Optional, Dict, List
from ..utils.logger import get_logger
import os
from ..config.settings import AppConfig
from abc import ABC, abstractmethod

logger = get_logger(__name__)

class CryptoDataCache:
    """Handles caching of cryptocurrency data."""
    
    def __init__(self, cache_duration: int = 60):
        self.cache = {}
        self.cache_duration = cache_duration
    
    def get(self, key: str) -> Optional[Dict]:
        """Get data from cache if valid."""
        if key not in self.cache:
            return None
            
        cache_age = time.time() - self.cache[key]['timestamp']
        if cache_age >= self.cache_duration:
            return None
            
        return self.cache[key]['data']
    
    def set(self, key: str, data: Dict):
        """Store data in cache."""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }

class CryptoAPIClient(ABC):
    """Abstract base class for cryptocurrency API clients."""
    
    @abstractmethod
    def get_coin_data(self, coin_id: str) -> Optional[Dict]:
        """Fetch coin data from API."""
        pass
    
    @abstractmethod
    def search_coin(self, symbol: str) -> Optional[Dict]:
        """Search for a coin by symbol."""
        pass

class CoinGeckoClient(CryptoAPIClient):
    """CoinGecko API implementation."""
    
    def __init__(self):
        self.client = CoinGeckoAPI()
    
    def get_coin_data(self, coin_id: str) -> Optional[Dict]:
        try:
            return self.client.get_coin_by_id(
                coin_id,
                localization=False,
                tickers=False,
                market_data=True,
                community_data=False,
                developer_data=False,
                sparkline=True
            )
        except Exception as e:
            logger.error(f"Error fetching coin data: {e}")
            return None
    
    def search_coin(self, symbol: str) -> Optional[Dict]:
        try:
            search_results = self.client.search(symbol.lower())
            for coin in search_results.get('coins', []):
                if coin['symbol'].lower() == symbol.lower():
                    return {
                        'id': coin['id'],
                        'symbol': coin['symbol'].upper(),
                        'name': coin['name']
                    }
            return None
        except Exception as e:
            logger.error(f"Error searching coin: {e}")
            return None

class CryptoService:
    """Service for managing cryptocurrency data and caching."""
    
    def __init__(self):
        """Initialize the crypto service."""
        self.api_client = CoinGeckoClient()
        self.cache = CryptoDataCache()
        self.tracked_symbols = self._load_tracked_symbols()
        os.makedirs(AppConfig.CACHE_DIR, exist_ok=True)
        os.makedirs(AppConfig.DATA_DIR, exist_ok=True)
        logger.info("CryptoService initialized")
    
    def get_coin_data(self, symbol: str) -> Optional[Dict]:
        """Get coin data with caching."""
        # Check cache first
        cached_data = self.cache.get(symbol)
        if cached_data:
            logger.debug(f"Using cached data for {symbol}")
            return cached_data
        
        # Search for coin if not in cache
        coin_info = self.api_client.search_coin(symbol)
        if not coin_info:
            return None
        
        # Fetch fresh data
        coin_data = self.api_client.get_coin_data(coin_info['id'])
        if not coin_data:
            return None
        
        # Process and cache the data
        result = self._process_coin_data(coin_data)
        if result:
            self.cache.set(symbol, result)
            logger.info(f"Cached fresh data for {symbol}")
        
        return result
    
    def _process_coin_data(self, coin_data: Dict) -> Optional[Dict]:
        """Process raw coin data into standard format."""
        try:
            symbol = coin_data['symbol'].upper()
            logo_path = self._cache_coin_logo(coin_data)
            
            return {
                'symbol': symbol,
                'name': coin_data['name'],
                'price': coin_data['market_data']['current_price']['usd'],
                'price_change_24h': round(coin_data['market_data']['price_change_percentage_24h'], 2),
                'sparkline_7d': coin_data['market_data']['sparkline_7d']['price'],
                'logo_path': logo_path,
            }
        except Exception as e:
            logger.error(f"Error processing coin data: {e}")
            return None
    
    def _is_cache_valid(self, symbol: str) -> bool:
        """Check if cached data is still valid."""
        if symbol not in self.cache:
            return False
        
        cache_age = time.time() - self.cache[symbol]['timestamp']
        return cache_age < self.cache_duration
    
    def _load_tracked_symbols(self) -> List[Dict]:
        """Load tracked coins from file."""
        try:
            if os.path.exists(AppConfig.TRACKED_COINS_FILE):
                with open(AppConfig.TRACKED_COINS_FILE, 'r') as f:
                    tracked_coins = json.load(f)
                    logger.info(f"Loaded tracked coins: {[coin.get('symbol') for coin in tracked_coins]}")
                    return tracked_coins
        except Exception as e:
            logger.error(f"Error loading tracked coins: {e}")
        
        # Default to empty list if file doesn't exist or error occurs
        return []
    
    def _save_tracked_symbols(self):
        """Save tracked coins to file."""
        try:
            with open(AppConfig.TRACKED_COINS_FILE, 'w') as f:
                json.dump(self.tracked_symbols, f, indent=2)
            logger.info(f"Saved tracked coins: {[coin.get('symbol') for coin in self.tracked_symbols]}")
        except Exception as e:
            logger.error(f"Error saving tracked coins: {e}")
    
    def add_tracked_symbol(self, symbol: str) -> bool:
        """
        Add a symbol to track.
        
        Args:
            symbol: The symbol to track (e.g., 'btc')
            
        Returns:
            True if successfully added, False otherwise
        """
        try:
            # Search for coin details
            coin_info = self.api_client.search_coin(symbol)
            if not coin_info:
                logger.warning(f"Could not find coin: {symbol}")
                return False
            
            # Get full coin data
            coin_data = self.api_client.get_coin_data(coin_info['id'])
            if not coin_data:
                logger.warning(f"Could not fetch data for coin: {symbol}")
                return False
            
            # Process and prepare coin data for storage
            processed_data = {
                'id': coin_info['id'],
                'symbol': coin_info['symbol'],
                'name': coin_info['name'],
                'logo_path': self._cache_coin_logo(coin_data),
                'favorite': False
            }
            
            # Check if coin already exists
            if not any(coin.get('id') == processed_data['id'] for coin in self.tracked_symbols):
                self.tracked_symbols.append(processed_data)
                self._save_tracked_symbols()
                logger.info(f"Added new coin to track: {processed_data['name']} ({processed_data['symbol']})")
                return True
            
            logger.info(f"Coin already tracked: {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding tracked symbol: {e}")
            return False
    
    def _cache_coin_logo(self, coin_data: Dict) -> str:
        """Cache coin logo and return the local path."""
        try:
            if not coin_data.get('image', {}).get('large'):
                return ""
                
            symbol = coin_data['symbol'].lower()
            logo_path = os.path.join(AppConfig.CACHE_DIR, f"{symbol}_logo.png")
            
            # Download and cache logo if not exists
            if not os.path.exists(logo_path):
                response = requests.get(coin_data['image']['large'])
                if response.status_code == 200:
                    with open(logo_path, 'wb') as f:
                        f.write(response.content)
                    logger.debug(f"Cached logo for {symbol}")
            
            return logo_path
            
        except Exception as e:
            logger.error(f"Error caching logo: {e}")
            return ""
    
    def remove_tracked_symbol(self, symbol: str) -> bool:
        """
        Remove a symbol from tracking.
        
        Args:
            symbol: The symbol to remove (e.g., 'btc')
            
        Returns:
            True if successfully removed, False otherwise
        """
        try:
            symbol = symbol.upper()
            # Find and remove the coin by symbol
            for coin in self.tracked_symbols[:]:  # Create a copy to safely modify during iteration
                if coin.get('symbol') == symbol:
                    self.tracked_symbols.remove(coin)
                    self._save_tracked_symbols()
                    logger.info(f"Removed coin from tracking: {symbol}")
                    return True
            
            logger.warning(f"Symbol not tracked: {symbol}")
            return False
            
        except Exception as e:
            logger.error(f"Error removing tracked symbol: {e}")
            return False
    
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