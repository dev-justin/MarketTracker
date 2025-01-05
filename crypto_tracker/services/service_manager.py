"""Service manager for centralizing service instances."""

from .display import Display
from .crypto.crypto_manager import CryptoManager
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ServiceManager:
    """Centralized manager for all application services."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_services()
        return cls._instance
    
    def _init_services(self):
        """Initialize all application services."""
        if not hasattr(self, 'initialized'):
            self.crypto_manager = CryptoManager()
            self.display = Display()
            self.initialized = True
            logger.info("ServiceManager initialized")
    
    def get_crypto_manager(self):
        """Get the crypto manager instance."""
        return self.crypto_manager
    
    def get_display(self):
        """Get the display service instance."""
        return self.display 