import os
import time
import requests
import pygame
from typing import Dict, Optional
from ..config.settings import AppConfig
from .logger import get_logger

logger = get_logger(__name__)

class IconManager:
    """Service for managing cryptocurrency icons."""
    
    def __init__(self):
        """Initialize the icon manager."""
        self.icons: Dict[str, pygame.Surface] = {}
        self.last_update: Dict[str, float] = {}
        os.makedirs(AppConfig.ICONS_DIR, exist_ok=True)
        
    def get_icon(self, symbol: str) -> Optional[pygame.Surface]:
        """
        Get the icon for a cryptocurrency symbol.
        
        Args:
            symbol: The cryptocurrency symbol (e.g., 'BTC', 'ETH')
            
        Returns:
            A pygame Surface containing the icon, or None if not found
        """
        # Check if we have a cached icon that's not too old
        if symbol in self.icons:
            if time.time() - self.last_update[symbol] < AppConfig.ICON_CACHE_TIME:
                return self.icons[symbol]
        
        # Try to load from file first
        icon_path = os.path.join(AppConfig.ICONS_DIR, f"{symbol.lower()}.png")
        if os.path.exists(icon_path):
            try:
                icon = pygame.image.load(icon_path)
                icon = pygame.transform.scale(icon, (AppConfig.ICON_SIZE, AppConfig.ICON_SIZE))
                self.icons[symbol] = icon
                self.last_update[symbol] = time.time()
                return icon
            except Exception as e:
                logger.error(f"Failed to load icon for {symbol}: {e}")
        
        # If not found locally, try to fetch from API
        try:
            # Convert symbol to CoinGecko ID (you might need a mapping for some symbols)
            coin_id = symbol.lower()
            response = requests.get(AppConfig.ICON_API_URL.format(id=coin_id))
            if response.status_code == 200:
                data = response.json()
                image_url = data['image']['large']
                
                # Download the image
                img_response = requests.get(image_url)
                if img_response.status_code == 200:
                    # Save to file
                    with open(icon_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    # Load into pygame
                    icon = pygame.image.load(icon_path)
                    icon = pygame.transform.scale(icon, (AppConfig.ICON_SIZE, AppConfig.ICON_SIZE))
                    self.icons[symbol] = icon
                    self.last_update[symbol] = time.time()
                    logger.info(f"Successfully downloaded and cached icon for {symbol}")
                    return icon
            
            logger.warning(f"Could not fetch icon for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching icon for {symbol}: {e}")
            return None 