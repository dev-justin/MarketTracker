"""Service for managing cryptocurrency storage."""

import json
import os
from typing import List, Dict, Optional
from ...config.settings import AppConfig
from ...utils.logger import get_logger
import requests

logger = get_logger(__name__)

class CryptoStorage:
    """Manages persistent storage of cryptocurrency data."""
    
    def __init__(self):
        self.tracked_coins = self._load_tracked_coins()
        os.makedirs(AppConfig.DATA_DIR, exist_ok=True)
        os.makedirs(AppConfig.CACHE_DIR, exist_ok=True)
        logger.info("CryptoStorage initialized")
    
    def _load_tracked_coins(self) -> List[Dict]:
        """Load tracked coins from storage."""
        try:
            if os.path.exists(AppConfig.TRACKED_COINS_FILE):
                with open(AppConfig.TRACKED_COINS_FILE, 'r') as f:
                    coins = json.load(f)
                    logger.info(f"Loaded {len(coins)} tracked coins")
                    return coins
        except Exception as e:
            logger.error(f"Error loading tracked coins: {e}")
        return []
    
    def _save_tracked_coins(self):
        """Save tracked coins to storage."""
        try:
            with open(AppConfig.TRACKED_COINS_FILE, 'w') as f:
                json.dump(self.tracked_coins, f, indent=2)
            logger.info(f"Saved {len(self.tracked_coins)} tracked coins")
        except Exception as e:
            logger.error(f"Error saving tracked coins: {e}")
    
    def add_coin(self, coin_data: Dict) -> bool:
        """
        Add a new coin to storage.
        
        Args:
            coin_data: Dictionary containing coin information
                      (id, symbol, name, image)
        """
        try:
            # Check if coin already exists
            if not any(c['id'] == coin_data['id'] for c in self.tracked_coins):
                # Add favorite status if not present
                if 'favorite' not in coin_data:
                    coin_data['favorite'] = False
                
                # Cache the coin logo
                if 'image' in coin_data:
                    coin_data['logo_path'] = self._cache_logo(
                        coin_data['symbol'].lower(),
                        coin_data['image']
                    )
                
                self.tracked_coins.append(coin_data)
                self._save_tracked_coins()
                logger.info(f"Added coin: {coin_data['symbol']}")
                return True
            
            logger.info(f"Coin already exists: {coin_data['symbol']}")
            return False
            
        except Exception as e:
            logger.error(f"Error adding coin: {e}")
            return False
    
    def remove_coin(self, coin_id: str) -> bool:
        """Remove a coin from storage."""
        try:
            initial_length = len(self.tracked_coins)
            self.tracked_coins = [c for c in self.tracked_coins if c['id'] != coin_id]
            
            if len(self.tracked_coins) < initial_length:
                self._save_tracked_coins()
                logger.info(f"Removed coin: {coin_id}")
                return True
            
            logger.info(f"Coin not found: {coin_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error removing coin: {e}")
            return False
    
    def get_coin(self, coin_id: str) -> Optional[Dict]:
        """Get a specific coin's data."""
        try:
            return next((c for c in self.tracked_coins if c['id'] == coin_id), None)
        except Exception as e:
            logger.error(f"Error getting coin: {e}")
            return None
    
    def get_all_coins(self) -> List[Dict]:
        """Get all tracked coins."""
        return self.tracked_coins
    
    def toggle_favorite(self, coin_id: str) -> bool:
        """Toggle favorite status for a coin."""
        try:
            for coin in self.tracked_coins:
                if coin['id'] == coin_id:
                    coin['favorite'] = not coin.get('favorite', False)
                    self._save_tracked_coins()
                    logger.info(f"Toggled favorite for {coin['symbol']}")
                    return True
            return False
            
        except Exception as e:
            logger.error(f"Error toggling favorite: {e}")
            return False
    
    def _cache_logo(self, symbol: str, url: str) -> str:
        """
        Download and cache a coin's logo.
        Returns the local path to the cached logo.
        """
        try:
            import requests
            logo_path = os.path.join(AppConfig.CACHE_DIR, f"{symbol.lower()}_logo.png")
            
            # Only download if not already cached
            if not os.path.exists(logo_path):
                response = requests.get(url)
                if response.status_code == 200:
                    os.makedirs(AppConfig.CACHE_DIR, exist_ok=True)
                    with open(logo_path, 'wb') as f:
                        f.write(response.content)
                    logger.debug(f"Cached logo for {symbol}")
            
            return logo_path
            
        except Exception as e:
            logger.error(f"Error caching logo: {e}")
            return ""