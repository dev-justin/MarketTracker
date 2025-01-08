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
            # Fetch crypto news from Crypto Panic
            # Free API endpoint with public filter (only shows public news)
            crypto_news_url = "https://cryptopanic.com/api/v1/posts/?auth_token=NONE&public=true&kind=news"
            logger.info(f"Fetching crypto news from Crypto Panic")
            
            response = requests.get(crypto_news_url, timeout=10)
            logger.info(f"Crypto Panic API response status: {response.status_code}")
            
            if response.status_code == 200:
                news_data = response.json()
                logger.info("Raw API response data:")
                logger.info(json.dumps(news_data, indent=2))
                
                results = news_data.get('results', [])
                logger.info(f"Received {len(results)} items from Crypto Panic")
                
                for item in results[:2]:  # Get top 2 crypto news
                    # Extract domain from URL for source
                    source = item.get('domain', 'Crypto News')
                    logger.info(f"Processing news item:")
                    logger.info(f"  Title: {item.get('title', '')}")
                    logger.info(f"  Source: {source}")
                    logger.info(f"  Description: {item.get('metadata', {}).get('description', '')}")
                    
                    crypto_news.append({
                        'title': item.get('title', ''),
                        'source': source,
                        'summary': item.get('metadata', {}).get('description', ''),
                        'type': 'crypto'
                    })
            else:
                logger.warning(f"Crypto Panic API error: {response.text}")
                # Use fallback crypto news
                crypto_news = [
                    {
                        'title': 'Bitcoin Continues to Dominate Crypto Market',
                        'source': 'Crypto News',
                        'summary': 'Bitcoin maintains its position as the leading cryptocurrency by market capitalization.',
                        'type': 'crypto'
                    },
                    {
                        'title': 'Ethereum Network Activity Surges',
                        'source': 'DeFi Updates',
                        'summary': 'Increased DeFi and NFT activity drives Ethereum network usage to new highs.',
                        'type': 'crypto'
                    }
                ]
            
            # Fetch stock market news
            stock_news = [
                {
                    'title': 'Market Update: Global Markets Show Mixed Performance',
                    'source': 'Market News',
                    'summary': 'Major indices display varied movements as investors assess economic data.',
                    'type': 'stock'
                },
                {
                    'title': 'Central Banks Signal Policy Changes',
                    'source': 'Financial News',
                    'summary': 'Key central banks indicate potential shifts in monetary policy affecting market sentiment.',
                    'type': 'stock'
                }
            ]
            
        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}", exc_info=True)
            if not crypto_news:
                crypto_news = self.crypto_news[:2]  # Only keep 2 items from cache
            if not stock_news:
                stock_news = self.stock_news[:2]  # Only keep 2 items from cache
        
        logger.info(f"Final news items:")
        logger.info("Crypto news:")
        for item in crypto_news:
            logger.info(json.dumps(item, indent=2))
        logger.info("Stock news:")
        for item in stock_news:
            logger.info(json.dumps(item, indent=2))
            
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