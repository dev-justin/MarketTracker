"""Service for managing stock storage."""

import json
import os
from typing import List, Dict, Optional
from ...config.settings import AppConfig
from ...utils.logger import get_logger
import requests

logger = get_logger(__name__)

class StockStorage:
    """Manages persistent storage of stock data."""
    
    def __init__(self):
        self.tracked_stocks = self._load_tracked_stocks()
        os.makedirs(AppConfig.DATA_DIR, exist_ok=True)
        os.makedirs(AppConfig.CACHE_DIR, exist_ok=True)
        logger.info("StockStorage initialized")
    
    def _load_tracked_stocks(self) -> List[Dict]:
        """Load tracked stocks from storage."""
        try:
            stocks_file = os.path.join(AppConfig.DATA_DIR, "tracked_stocks.json")
            if os.path.exists(stocks_file):
                with open(stocks_file, 'r') as f:
                    stocks = json.load(f)
                    logger.info(f"Loaded {len(stocks)} tracked stocks")
                    return stocks
        except Exception as e:
            logger.error(f"Error loading tracked stocks: {e}")
        return []
    
    def _save_tracked_stocks(self):
        """Save tracked stocks to storage."""
        try:
            stocks_file = os.path.join(AppConfig.DATA_DIR, "tracked_stocks.json")
            with open(stocks_file, 'w') as f:
                json.dump(self.tracked_stocks, f, indent=2)
            logger.info(f"Saved {len(self.tracked_stocks)} tracked stocks")
        except Exception as e:
            logger.error(f"Error saving tracked stocks: {e}")
    
    def add_stock(self, stock_data: Dict) -> bool:
        """
        Add a new stock to storage.
        
        Args:
            stock_data: Dictionary containing stock information
                      (id, symbol, name, logo_url)
        """
        try:
            # Check if stock already exists
            if not any(s['id'] == stock_data['id'] for s in self.tracked_stocks):
                # Add favorite status if not present
                if 'favorite' not in stock_data:
                    stock_data['favorite'] = False
                
                self.tracked_stocks.append(stock_data)
                self._save_tracked_stocks()
                logger.info(f"Added stock: {stock_data['symbol']}")
                return True
            
            logger.info(f"Stock already exists: {stock_data['symbol']}")
            return False
            
        except Exception as e:
            logger.error(f"Error adding stock: {e}")
            return False
    
    def remove_stock(self, stock_id: str) -> bool:
        """Remove a stock from storage."""
        try:
            initial_length = len(self.tracked_stocks)
            self.tracked_stocks = [s for s in self.tracked_stocks if s['id'] != stock_id]
            
            if len(self.tracked_stocks) < initial_length:
                self._save_tracked_stocks()
                logger.info(f"Removed stock: {stock_id}")
                return True
            
            logger.info(f"Stock not found: {stock_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error removing stock: {e}")
            return False
    
    def get_stock(self, stock_id: str) -> Optional[Dict]:
        """Get a specific stock's data."""
        try:
            return next((s for s in self.tracked_stocks if s['id'] == stock_id), None)
        except Exception as e:
            logger.error(f"Error getting stock: {e}")
            return None
    
    def get_all_stocks(self) -> List[Dict]:
        """Get all tracked stocks."""
        return self.tracked_stocks
    
    def toggle_favorite(self, stock_id: str) -> bool:
        """Toggle favorite status for a stock."""
        try:
            for stock in self.tracked_stocks:
                if stock['id'] == stock_id:
                    stock['favorite'] = not stock.get('favorite', False)
                    self._save_tracked_stocks()
                    logger.info(f"Toggled favorite for {stock['symbol']}")
                    return True
            return False
            
        except Exception as e:
            logger.error(f"Error toggling favorite: {e}")
            return False
    
    def update_stock_data(self, stock_id: str, new_data: Dict) -> bool:
        """Update stock data in storage."""
        try:
            for stock in self.tracked_stocks:
                if stock['id'] == stock_id:
                    # Update only the dynamic fields
                    stock.update({
                        'current_price': new_data['current_price'],
                        'price_change_24h': new_data['price_change_24h'],
                        'sparkline_7d': new_data['sparkline_7d'],
                        'last_updated': new_data['last_updated'],
                        'market_cap': new_data['market_cap'],
                        'volume': new_data['volume']
                    })
                    self._save_tracked_stocks()
                    logger.info(f"Updated data for {stock['symbol']}")
                    return True
            return False
            
        except Exception as e:
            logger.error(f"Error updating stock data: {e}")
            return False 