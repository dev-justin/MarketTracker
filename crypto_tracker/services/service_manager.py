"""Service manager for centralizing service instances."""

from .display import Display
from .crypto.crypto_manager import CryptoManager
from ..utils.logger import get_logger
import pygame
from typing import Dict, Any, Optional

logger = get_logger(__name__)

class ServiceManager:
    """Manages all application services."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_services()
        return cls._instance
    
    def _init_services(self):
        """Initialize all services."""
        if not hasattr(self, 'initialized'):
            self.services = {}
            self.initialized = True
            logger.info("ServiceManager initialized")
    
    def register_service(self, name: str, service: Any) -> None:
        """Register a service."""
        self.services[name] = service
        logger.info(f"Registered service: {name}")
    
    def get_service(self, name: str) -> Optional[Any]:
        """Get a service by name."""
        if name not in self.services:
            logger.warning(f"Service {name} not found")
            return None
        return self.services[name]
    
    def get_display(self) -> Optional[Any]:
        """Get the display service."""
        return self.get_service('display')
    
    def get_crypto_manager(self) -> Optional[Any]:
        """Get the crypto manager service."""
        return self.get_service('crypto_manager')
    
    def get_screen_manager(self) -> Optional[Any]:
        """Get the screen manager service."""
        return self.get_service('screen_manager')
    
    def get_screen_state(self) -> Optional[Any]:
        """Get the screen state service."""
        return self.get_service('screen_state')
    
    def get_error_service(self) -> Optional[Any]:
        """Get the error service."""
        return self.get_service('error')
    
    def get_performance_service(self) -> Optional[Any]:
        """Get the performance service."""
        return self.get_service('performance') 