"""Manager for handling cryptocurrency data and operations."""

import os
import json
import requests
from typing import List, Dict, Optional
from ..config.settings import AppConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class CryptoManager:
    """Manager for handling cryptocurrency data and operations."""
    
    def __init__(self) -> None:
        """Initialize the crypto manager."""
        self.tracked_coins: List[Dict] = []
        self._load_tracked_coins()
        logger.info("CryptoManager initialized")
    
    def _load_tracked_coins(self) -> None:
        """Load tracked coins from storage."""
        try:
            if os.path.exists(AppConfig.TRACKED_COINS_FILE):
                with open(AppConfig.TRACKED_COINS_FILE, 'r') as f:
                    coin_ids = json.load(f)
                    self.tracked_coins = self._fetch_coin_data(coin_ids)
            else:
                # Default to some popular coins if no file exists
                default_coins = ['bitcoin', 'ethereum', 'dogecoin']
                self.tracked_coins = self._fetch_coin_data(default_coins)
                self._save_tracked_coins()
        except Exception as e:
            logger.error(f"Error loading tracked coins: {e}")
            self.tracked_coins = []
    
    def _save_tracked_coins(self) -> None:
        """Save tracked coins to storage."""
        try:
            coin_ids = [coin['id'] for coin in self.tracked_coins]
            os.makedirs(os.path.dirname(AppConfig.TRACKED_COINS_FILE), exist_ok=True)
            with open(AppConfig.TRACKED_COINS_FILE, 'w') as f:
                json.dump(coin_ids, f)
        except Exception as e:
            logger.error(f"Error saving tracked coins: {e}")
    
    def _fetch_coin_data(self, coin_ids: List[str]) -> List[Dict]:
        """Fetch current data for the given coin IDs."""
        try:
            # Convert single ID to list if necessary
            if isinstance(coin_ids, str):
                coin_ids = [coin_ids]
            
            # Join coin IDs with commas for the API
            ids_string = ','.join(coin_ids)
            
            # Make API request
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': ids_string,
                'vs_currencies': 'usd',
                'include_24hr_change': True,
                'include_market_cap': True,
                'include_last_updated_at': True
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process response into our format
            coins = []
            for coin_id, coin_data in data.items():
                coin = {
                    'id': coin_id,
                    'symbol': coin_id,  # We'll update this with proper symbols later
                    'price_usd': coin_data['usd'],
                    'price_change_24h': coin_data['usd_24h_change'],
                    'market_cap': coin_data['usd_market_cap'],
                    'last_updated': coin_data['last_updated_at']
                }
                coins.append(coin)
            
            # Update symbols and logos
            self._update_coin_metadata(coins)
            
            return coins
            
        except Exception as e:
            logger.error(f"Error fetching coin data: {e}")
            return []
    
    def _update_coin_metadata(self, coins: List[Dict]) -> None:
        """Update coin metadata like symbols and logos."""
        try:
            for coin in coins:
                # Try to get coin info including symbol
                info_url = f"https://api.coingecko.com/api/v3/coins/{coin['id']}"
                response = requests.get(info_url)
                response.raise_for_status()
                info = response.json()
                
                # Update symbol
                coin['symbol'] = info['symbol']
                
                # Download and cache logo if needed
                logo_url = info['image']['large']
                logo_path = os.path.join(AppConfig.CACHE_DIR, f"{coin['symbol'].lower()}_logo.png")
                
                if not os.path.exists(logo_path):
                    os.makedirs(AppConfig.CACHE_DIR, exist_ok=True)
                    logo_response = requests.get(logo_url)
                    logo_response.raise_for_status()
                    with open(logo_path, 'wb') as f:
                        f.write(logo_response.content)
                
        except Exception as e:
            logger.error(f"Error updating coin metadata: {e}")
    
    def get_tracked_coins(self) -> List[Dict]:
        """Get the list of tracked coins with current data."""
        return self.tracked_coins
    
    def refresh_data(self) -> None:
        """Refresh data for all tracked coins."""
        coin_ids = [coin['id'] for coin in self.tracked_coins]
        self.tracked_coins = self._fetch_coin_data(coin_ids)
    
    def add_coin(self, coin_id: str) -> bool:
        """Add a new coin to track."""
        try:
            # Check if coin is already tracked
            if any(coin['id'] == coin_id for coin in self.tracked_coins):
                return False
            
            # Fetch data for new coin
            new_coin_data = self._fetch_coin_data(coin_id)
            if new_coin_data:
                self.tracked_coins.extend(new_coin_data)
                self._save_tracked_coins()
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding coin: {e}")
            return False
    
    def remove_coin(self, coin_id: str) -> bool:
        """Remove a coin from tracking."""
        try:
            self.tracked_coins = [coin for coin in self.tracked_coins if coin['id'] != coin_id]
            self._save_tracked_coins()
            return True
        except Exception as e:
            logger.error(f"Error removing coin: {e}")
            return False
    
    def get_coin_by_id(self, coin_id: str) -> Optional[Dict]:
        """Get coin data by ID."""
        for coin in self.tracked_coins:
            if coin['id'] == coin_id:
                return coin
        return None 