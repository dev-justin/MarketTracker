"""Central manager for cryptocurrency operations."""

from typing import Dict, List, Optional
from .coingecko_service import CoinGeckoService
from .storage import CryptoStorage
from ...utils.logger import get_logger
import threading
import time

logger = get_logger(__name__)

class CryptoManager:
    """
    Central manager for cryptocurrency operations.
    Coordinates between CoinGecko API and local storage.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.coingecko = CoinGeckoService()
            self.storage = CryptoStorage()
            self.price_update_thread = None
            self.should_update = True
            self.initialized = True
            logger.info("CryptoManager initialized")
    
    def start_price_updates(self):
        """Start background price updates."""
        if self.price_update_thread is None:
            self.should_update = True
            self.price_update_thread = threading.Thread(target=self._update_prices_loop)
            self.price_update_thread.daemon = True
            self.price_update_thread.start()
            logger.info("Started price update thread")
    
    def stop_price_updates(self):
        """Stop background price updates."""
        self.should_update = False
        if self.price_update_thread:
            self.price_update_thread.join()
            self.price_update_thread = None
            logger.info("Stopped price update thread")
    
    def _update_prices_loop(self):
        """Background loop to update prices."""
        while self.should_update:
            try:
                tracked_coins = self.storage.get_all_coins()
                for coin in tracked_coins:
                    updated_data = self.coingecko.get_coin_data(coin['id'], force_refresh=True)
                    if updated_data:
                        coin.update(updated_data)
                logger.debug("Updated prices for all tracked coins")
            except Exception as e:
                logger.error(f"Error updating prices: {e}")
            time.sleep(60)  # Wait for 1 minute
    
    def add_coin(self, symbol: str) -> bool:
        """
        Add a new coin to track.
        Handles both API lookup and storage.
        """
        try:
            # Search for coin
            coin_info = self.coingecko.search_coin(symbol)
            if not coin_info:
                logger.warning(f"Coin not found: {symbol}")
                return False
            
            # Get full coin data
            coin_data = self.coingecko.get_coin_data(coin_info['id'])
            if not coin_data:
                logger.warning(f"Could not fetch coin data: {symbol}")
                return False
            
            # Store coin
            return self.storage.add_coin(coin_data)
            
        except Exception as e:
            logger.error(f"Error adding coin: {e}")
            return False
    
    def remove_coin(self, coin_id: str) -> bool:
        """Remove a coin from tracking."""
        success = self.storage.remove_coin(coin_id)
        if success:
            self.coingecko.clear_cache(coin_id)
        return success
    
    def get_coin_data(self, coin_id: str) -> Optional[Dict]:
        """
        Get current coin data.
        Returns cached data if available and fresh.
        """
        return self.coingecko.get_coin_data(coin_id)
    
    def get_tracked_coins(self) -> List[Dict]:
        """Get all tracked coins with current data."""
        return self.storage.get_all_coins()
    
    def toggle_favorite(self, coin_id: str) -> bool:
        """Toggle favorite status for a coin."""
        return self.storage.toggle_favorite(coin_id)
    
    def get_favorites(self) -> List[Dict]:
        """Get list of favorite coins."""
        return self.storage.get_favorite_coins() 