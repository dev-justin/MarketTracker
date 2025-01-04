import logging
from typing import Optional

def setup_logger(name: str = 'crypto_tracker', level: int = logging.INFO) -> logging.Logger:
    """
    Set up and configure the application logger.
    
    Args:
        name: The name of the logger
        level: The logging level
        
    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

# Create a default logger instance
logger = setup_logger()

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance. If name is provided, returns a child logger.
    
    Args:
        name: Optional name for a child logger
        
    Returns:
        A logger instance
    """
    if name:
        return logging.getLogger(f'crypto_tracker.{name}')
    return logger 