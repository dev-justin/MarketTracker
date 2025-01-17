"""Central manager for cryptocurrency and stock operations."""

from typing import Dict, List, Optional
from .coingecko_service import CoinGeckoService
from ..stock.stock_service import StockService
from .storage import CryptoStorage
from ...utils.logger import get_logger
import threading
import time

logger = get_logger(__name__)

class CryptoManager:
    """
    Central manager for cryptocurrency and stock operations.
    Coordinates between CoinGecko API, Yahoo Finance, and local storage.
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
            self.stock_service = StockService()
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
                tracked_items = self.storage.get_all_coins()
                for item in tracked_items:
                    if item.get('type') == 'stock':
                        # Update stock data
                        updated_data = self.stock_service.get_stock_data(item['id'], force_refresh=True)
                    else:
                        # Update crypto data
                        updated_data = self.coingecko.get_coin_data(item['id'], force_refresh=True)
                    
                    if updated_data:
                        # Preserve favorite state and other stored data while updating prices
                        favorite_state = item.get('favorite', False)
                        item.update(updated_data)
                        item['favorite'] = favorite_state
                
                # Save updated data
                self.storage._save_tracked_coins()
            except Exception as e:
                logger.error(f"Error updating prices: {e}")
            time.sleep(60)  # Wait for 1 minute
    
    def add_coin(self, symbol: str) -> bool:
        """
        Add a new coin or stock to track.
        Handles both API lookup and storage.
        """
        try:
            logger.info(f"Starting add process for symbol: {symbol}")
            
            # Try as cryptocurrency first
            coin_info = self.coingecko.search_coin(symbol)
            if coin_info:
                logger.info(f"Found as cryptocurrency: {symbol}")
                coin_data = self.coingecko.get_coin_data(coin_info['id'])
                if coin_data:
                    success = self.storage.add_coin(coin_data)
                    if success:
                        # Notify screens to refresh
                        from ...services.service_manager import ServiceManager
                        service_manager = ServiceManager()
                        screen_manager = service_manager.get_screen_manager()
                        if screen_manager:
                            for screen_name in ['ticker', 'dashboard', 'settings']:
                                screen = screen_manager.screens.get(screen_name)
                                if screen and hasattr(screen, 'refresh_coins'):
                                    screen.refresh_coins()
                    return success
            
            # If not found as crypto, try as stock
            stock_info = self.stock_service.search_stock(symbol)
            if stock_info:
                logger.info(f"Found as stock: {symbol}")
                stock_data = self.stock_service.get_stock_data(symbol)
                if stock_data:
                    success = self.stock_service.storage.add_stock(stock_data)
                    if success:
                        # Notify screens to refresh
                        from ...services.service_manager import ServiceManager
                        service_manager = ServiceManager()
                        screen_manager = service_manager.get_screen_manager()
                        if screen_manager:
                            for screen_name in ['ticker', 'dashboard', 'settings']:
                                screen = screen_manager.screens.get(screen_name)
                                if screen and hasattr(screen, 'refresh_coins'):
                                    screen.refresh_coins()
                    return success
            
            logger.warning(f"Symbol not found as either crypto or stock: {symbol}")
            return False
            
        except Exception as e:
            logger.error(f"Error in add process: {e}", exc_info=True)
            return False
    
    def remove_coin(self, coin_id: str) -> bool:
        """Remove a coin from tracking."""
        # Try to remove from crypto storage first
        if self.storage.remove_coin(coin_id):
            self.coingecko.clear_cache(coin_id)
            return True
        
        # If not found in crypto storage, try stock storage
        if self.stock_service.storage.remove_stock(coin_id):
            self.stock_service.clear_cache(coin_id)
            return True
        
        return False
    
    def get_coin_data(self, coin_id: str) -> Optional[Dict]:
        """
        Get current coin data.
        Returns cached data if available and fresh.
        """
        # Try crypto first
        coin_data = self.coingecko.get_coin_data(coin_id)
        if coin_data:
            return coin_data
        
        # If not found, try stock
        return self.stock_service.get_stock_data(coin_id)
    
    def get_tracked_coins(self) -> List[Dict]:
        """Get all tracked coins and stocks with current data."""
        # Get both crypto and stock data
        crypto_coins = self.storage.get_all_coins()
        stocks = self.stock_service.storage.get_all_stocks()
        
        # Update stock data with current prices
        updated_stocks = []
        for stock in stocks:
            current_data = self.stock_service.get_stock_data(stock['id'])
            if current_data:
                # Preserve favorite status
                current_data['favorite'] = stock.get('favorite', False)
                updated_stocks.append(current_data)
            else:
                updated_stocks.append(stock)
        
        # Combine and return all data
        return crypto_coins + updated_stocks
    
    def toggle_favorite(self, coin_id: str) -> bool:
        """Toggle favorite status for a coin or stock."""
        # Try crypto first
        if self.storage.toggle_favorite(coin_id):
            return True
        
        # If not found, try stock
        return self.stock_service.storage.toggle_favorite(coin_id)
    
    def get_favorites(self) -> List[Dict]:
        """Get list of favorite coins and stocks."""
        crypto_favorites = [coin for coin in self.storage.get_all_coins() if coin.get('favorite', False)]
        stock_favorites = [stock for stock in self.stock_service.storage.get_all_stocks() if stock.get('favorite', False)]
        return crypto_favorites + stock_favorites 