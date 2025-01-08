"""Service for fetching and managing news data."""

import time
import os
import json
import requests
from typing import List, Dict, Tuple
from ..utils.logger import get_logger
from ..config.settings import AppConfig

logger = get_logger(__name__)

class NewsService:
    """Service for fetching and managing news data."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize the news service."""
        if not hasattr(self, 'initialized'):
            self.crypto_news = []
            self.stock_news = []
            self.last_update = 0
            self.update_interval = 3600  # 1 hour
            self.cache_file = os.path.join(AppConfig.CACHE_DIR, 'news_cache.json')
            
            # Load cache first for immediate display
            self._load_cache()
            
            # Then fetch fresh news
            crypto_news, stock_news = self._fetch_news()
            if crypto_news or stock_news:
                self.crypto_news = crypto_news
                self.stock_news = stock_news
                self.last_update = time.time()
                self._save_cache()
            
            self.initialized = True
            logger.info("NewsService initialized")
    
    def _load_cache(self) -> None:
        """Load cached news data."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    self.crypto_news = cache_data.get('crypto_news', [])
                    self.stock_news = cache_data.get('stock_news', [])
                    self.last_update = cache_data.get('timestamp', 0)
                    logger.info("Loaded news from cache")
        except Exception as e:
            logger.error(f"Error loading news cache: {e}")
            # Initialize with default news items if cache load fails
            default_news = {
                'title': 'Loading Market News...',
                'source': 'System',
                'summary': 'Please wait while we fetch the latest market updates.',
                'image_path': '',
                'timestamp': time.time()
            }
            self.crypto_news = [default_news.copy()]
            self.stock_news = [default_news.copy()]
    
    def _save_cache(self) -> None:
        """Save news data to cache."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump({
                    'crypto_news': self.crypto_news,
                    'stock_news': self.stock_news,
                    'timestamp': self.last_update
                }, f)
            logger.info("Saved news to cache")
        except Exception as e:
            logger.error(f"Error saving news cache: {e}")
    
    def _download_image(self, image_url: str, symbol: str) -> str:
        """Download and cache a news image."""
        try:
            if not image_url:
                return ""
                
            # Create a filename based on the symbol and timestamp
            filename = f"news_{symbol}_{int(time.time())}.jpg"
            image_path = os.path.join(AppConfig.CACHE_DIR, filename)
            
            # Download and save the image
            response = requests.get(image_url, timeout=5)
            if response.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                return image_path
            
            return ""
        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            return ""
    
    def _fetch_news(self) -> Tuple[List[Dict], List[Dict]]:
        """Fetch news from various sources."""
        crypto_news = []
        stock_news = []
        
        try:
            # Fetch crypto news from CoinGecko
            crypto_news_url = "https://api.coingecko.com/api/v3/news"
            response = requests.get(crypto_news_url, timeout=10)
            if response.status_code == 200:
                news_data = response.json()
                for item in news_data[:5]:  # Get top 5 crypto news
                    image_path = self._download_image(
                        item.get('thumb_2x', ''),
                        f"crypto_{len(crypto_news)}"
                    )
                    crypto_news.append({
                        'title': item.get('title', ''),
                        'source': 'CoinGecko',
                        'summary': item.get('description', ''),
                        'image_path': image_path,
                        'url': item.get('url', ''),
                        'timestamp': time.time(),
                        'type': 'crypto'
                    })
            
            # Fetch stock market news
            # Note: You'll need to replace this with your preferred financial news API
            stock_news = [
                {
                    'title': 'Market Update: Global Markets Show Mixed Performance',
                    'source': 'Market News',
                    'summary': 'Major indices display varied movements as investors assess economic data.',
                    'image_path': '',
                    'timestamp': time.time(),
                    'type': 'stock'
                },
                {
                    'title': 'Central Banks Signal Policy Changes',
                    'source': 'Financial News',
                    'summary': 'Key central banks indicate potential shifts in monetary policy affecting market sentiment.',
                    'image_path': '',
                    'timestamp': time.time(),
                    'type': 'stock'
                },
                {
                    'title': 'Tech Sector Leads Market Rally',
                    'source': 'Stock News',
                    'summary': 'Technology stocks surge as earnings reports exceed expectations.',
                    'image_path': '',
                    'timestamp': time.time(),
                    'type': 'stock'
                },
                {
                    'title': 'Energy Stocks React to Global Supply Changes',
                    'source': 'Market Watch',
                    'summary': 'Oil and gas companies see price movements following international developments.',
                    'image_path': '',
                    'timestamp': time.time(),
                    'type': 'stock'
                },
                {
                    'title': 'Manufacturing Data Impacts Industrial Stocks',
                    'source': 'Financial Times',
                    'summary': 'Industrial sector responds to latest manufacturing PMI data.',
                    'image_path': '',
                    'timestamp': time.time(),
                    'type': 'stock'
                }
            ]
            
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            if not crypto_news:
                crypto_news = self.crypto_news
            if not stock_news:
                stock_news = self.stock_news
        
        return crypto_news, stock_news
    
    def get_news(self) -> Tuple[List[Dict], List[Dict]]:
        """Get crypto and stock news."""
        current_time = time.time()
        if current_time - self.last_update > self.update_interval:
            logger.info("Fetching fresh news data")
            crypto_news, stock_news = self._fetch_news()
            if crypto_news or stock_news:
                self.crypto_news = crypto_news
                self.stock_news = stock_news
                self.last_update = current_time
                self._save_cache()
        
        return self.crypto_news, self.stock_news 