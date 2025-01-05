import json
import os
import requests
from typing import Optional, Dict, List
from ...utils.logger import get_logger
from ...config.settings import AppConfig
from .coingecko_service import CoinGeckoService

logger = get_logger(__name__)

class TrackedCoinsService:
    """Service for managing tracked cryptocurrency coins."""
    
    def __init__(self):
        self.coingecko = CoinGeckoService()
        self.tracked_coins = self._load_tracked_coins()
        os.makedirs(AppConfig.CACHE_DIR, exist_ok=True)
        os.makedirs(AppConfig.DATA_DIR, exist_ok=True)
        logger.info("TrackedCoinsService initialized")
    
    def _load_tracked_coins(self) -> List[Dict]:
        """Load tracked coins from file."""
        try:
            if os.path.exists(AppConfig.TRACKED_COINS_FILE):
                with open(AppConfig.TRACKED_COINS_FILE, 'r') as f:
                    tracked_coins = json.load(f)
                    logger.info(f"Loaded tracked coins: {[coin.get('symbol') for coin in tracked_coins]}")
                    return tracked_coins
        except Exception as e:
            logger.error(f"Error loading tracked coins: {e}")
        return []
    
    def _save_tracked_coins(self):
        """Save tracked coins to file."""
        try:
            with open(AppConfig.TRACKED_COINS_FILE, 'w') as f:
                json.dump(self.tracked_coins, f, indent=2)
            logger.info(f"Saved tracked coins: {[coin.get('symbol') for coin in self.tracked_coins]}")
        except Exception as e:
            logger.error(f"Error saving tracked coins: {e}")
    
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
    
    def add_coin(self, symbol: str) -> bool:
        """Add a new coin to track."""
        try:
            # Search for coin
            coin_info = self.coingecko.search_coin(symbol)
            if not coin_info:
                logger.warning(f"Could not find coin: {symbol}")
                return False
            
            # Get full coin data
            coin_data = self.coingecko.get_coin_data(coin_info['id'])
            if not coin_data:
                logger.warning(f"Could not fetch data for coin: {symbol}")
                return False
            
            # Process and prepare coin data
            new_coin = {
                'id': coin_info['id'],
                'symbol': coin_info['symbol'],
                'name': coin_info['name'],
                'logo_path': self._cache_coin_logo(coin_data),
                'favorite': False
            }
            
            # Check if coin already exists
            if not any(coin.get('id') == new_coin['id'] for coin in self.tracked_coins):
                self.tracked_coins.append(new_coin)
                self._save_tracked_coins()
                logger.info(f"Added new coin: {new_coin['name']} ({new_coin['symbol']})")
                return True
            
            logger.info(f"Coin already tracked: {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding coin: {e}")
            return False
    
    def remove_coin(self, symbol: str) -> bool:
        """Remove a coin from tracking."""
        try:
            symbol = symbol.upper()
            for coin in self.tracked_coins[:]:
                if coin.get('symbol') == symbol:
                    self.tracked_coins.remove(coin)
                    self._save_tracked_coins()
                    logger.info(f"Removed coin: {symbol}")
                    return True
            
            logger.warning(f"Coin not tracked: {symbol}")
            return False
            
        except Exception as e:
            logger.error(f"Error removing coin: {e}")
            return False
    
    def toggle_favorite(self, symbol: str) -> bool:
        """Toggle favorite status for a coin."""
        try:
            symbol = symbol.upper()
            for coin in self.tracked_coins:
                if coin.get('symbol') == symbol:
                    coin['favorite'] = not coin.get('favorite', False)
                    self._save_tracked_coins()
                    status = "favorited" if coin['favorite'] else "unfavorited"
                    logger.info(f"Coin {symbol} {status}")
                    return True
            
            logger.warning(f"Coin not found for favoriting: {symbol}")
            return False
            
        except Exception as e:
            logger.error(f"Error toggling favorite: {e}")
            return False
    
    def get_tracked_coins(self) -> List[Dict]:
        """Get list of all tracked coins."""
        return self.tracked_coins
    
    def get_coin(self, symbol: str) -> Optional[Dict]:
        """Get a specific tracked coin by symbol."""
        symbol = symbol.upper()
        for coin in self.tracked_coins:
            if coin.get('symbol') == symbol:
                return coin
        return None
    
    def get_favorite_coins(self) -> List[Dict]:
        """Get list of favorite coins."""
        return [coin for coin in self.tracked_coins if coin.get('favorite', False)]
    
    def update_coin_data(self, symbol: str) -> Optional[Dict]:
        """Update and return current price data for a coin."""
        coin = self.get_coin(symbol)
        if not coin:
            return None
            
        price_data = self.coingecko.get_coin_price_data(coin['id'])
        if price_data:
            return {**coin, **price_data}
        return None 