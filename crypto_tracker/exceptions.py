class CryptoTrackerError(Exception):
    """Base exception for the application"""
    pass

class APIError(CryptoTrackerError):
    """Raised when API calls fail"""
    pass

class ConfigError(CryptoTrackerError):
    """Raised when configuration is invalid"""
    pass

class ValidationError(CryptoTrackerError):
    """Raised when input validation fails"""
    pass

class ScreenError(CryptoTrackerError):
    """Raised when screen-related operations fail"""
    pass

class StorageError(CryptoTrackerError):
    """Raised when storage operations fail"""
    pass 