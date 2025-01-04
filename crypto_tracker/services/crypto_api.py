from pycoingecko import CoinGeckoAPI
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests

from ..utils.logger import get_logger

logger = get_logger(__name__)

class CryptoAPI:
    """Service for interacting with cryptocurrency APIs."""
    
    # Mapping of common symbols to CoinGecko IDs
    COINGECKO_IDS = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'SOL': 'solana',
        'DOGE': 'dogecoin',
        'XRP': 'ripple',
        'ADA': 'cardano',
        'DOT': 'polkadot',
        'MATIC': 'matic-network',
        'LINK': 'chainlink',
        'AVAX': 'avalanche-2'
    }
    
    def __init__(self):
        """Initialize the crypto API service."""
        logger.info("Initializing CryptoAPI...")
        self.client = CoinGeckoAPI()
        self.cached_prices: Dict[str, Dict] = {}
        self.cache_time = 0
        self.cache_duration = 10  # seconds
        logger.info("CryptoAPI initialized")
    
    def verify_symbol(self, symbol: str) -> bool:
        """Verify if a symbol exists on CoinGecko."""
        try:
            coingecko_id = self.COINGECKO_IDS.get(symbol)
            if not coingecko_id:
                return False
            
            # Try to get the coin info
            coin_data = self.client.get_coin_by_id(coingecko_id)
            logger.debug(f"Verified coin data: {coin_data}")
            return True
        except Exception as e:
            logger.error(f"Error verifying symbol {symbol}: {e}")
            return False
    
    def get_current_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Get current prices and metadata for multiple symbols.
        Returns a dictionary with symbol keys and values containing:
        - price: current price in USD
        - change_24h: 24h price change percentage
        - image: URL to the coin's image
        """
        if time.time() - self.cache_time < self.cache_duration:
            return self.cached_prices

        prices = {}
        try:
            # Get list of CoinGecko IDs for our symbols
            coingecko_ids = [
                self.COINGECKO_IDS.get(symbol) 
                for symbol in symbols 
                if symbol in self.COINGECKO_IDS
            ]
            
            if not coingecko_ids:
                return {}
            
            logger.info("Fetching fresh data from CoinGecko")
            # Get market data for all coins at once
            market_data = self.client.get_coins_markets(
                vs_currency='usd',
                ids=coingecko_ids,
                order='market_cap_desc',
                per_page=100,
                page=1,
                sparkline=False,
                price_change_percentage='24h'
            )
            
            logger.debug("\nRaw data from CoinGecko:")
            for coin in market_data:
                logger.debug(f"Coin data: {coin}")
            
            # Process the data
            for coin in market_data:
                # Find the symbol for this coin
                symbol = next(
                    (s for s, cg_id in self.COINGECKO_IDS.items() 
                     if cg_id == coin['id']),
                    None
                )
                if symbol:
                    prices[symbol] = {
                        'price': coin['current_price'],
                        'change_24h': coin['price_change_percentage_24h'],
                        'image': coin['image']
                    }
                    logger.info(
                        f"Price for {symbol}: ${coin['current_price']:,.2f} "
                        f"({coin['price_change_percentage_24h']:+.2f}%)"
                    )
            
            self.cached_prices = prices
            self.cache_time = time.time()
            
        except Exception as e:
            logger.error(f"Error fetching prices ({datetime.now()}): {e}")
            return self.cached_prices if self.cached_prices else {}
            
        return prices
    
    def get_historical_prices(self, symbol: str, days: int = 7) -> List[float]:
        """Get historical price data for a symbol."""
        try:
            coingecko_id = self.COINGECKO_IDS.get(symbol)
            if not coingecko_id:
                return []
            
            # Get market chart data
            chart_data = self.client.get_coin_market_chart_by_id(
                id=coingecko_id,
                vs_currency='usd',
                days=days
            )
            
            # Extract just the prices
            prices = [price[1] for price in chart_data['prices']]
            logger.info(f"Got {len(prices)} historical prices for {symbol}")
            logger.debug(f"Raw historical data: {chart_data}")
            return prices
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return []
    
    def get_coin_name(self, symbol: str) -> str:
        """Get the full name of a coin from its symbol."""
        try:
            coingecko_id = self.COINGECKO_IDS.get(symbol)
            if not coingecko_id:
                return symbol
            
            coin_data = self.client.get_coin_by_id(coingecko_id)
            return coin_data['name']
        except Exception as e:
            logger.error(f"Error fetching coin name for {symbol}: {e}")
            return symbol 