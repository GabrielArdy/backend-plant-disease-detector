import logging
import sys
import os
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
def setup_logging(log_level=logging.INFO, log_dir='logs'):
    """
    Setup application logging
    
    Parameters:
    - log_level: Logging level (default: INFO)
    - log_dir: Directory to store log files (default: 'logs')
    
    Returns:
    - The configured logger
    """
    # Create logs directory if it doesn't exist
    try:
        app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        log_path = os.path.join(app_root, log_dir)
        if not os.path.exists(log_path):
            os.makedirs(log_path)
    except Exception:
        # If we can't create a directory, we'll just log to console
        log_path = None
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Clear any existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if possible
    if log_path:
        try:
            file_handler = RotatingFileHandler(
                os.path.join(log_path, 'plant_disease.log'),
                maxBytes=10485760,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not create file handler: {str(e)}")
    
    return logger

# Default instance that can be imported directly
default_logger = setup_logging()

def get_logger(name):
    """
    Get a logger with the specified name
    
    Parameters:
    - name: Logger name (usually __name__)
    
    Returns:
    - Logger instance
    """
    return logging.getLogger(name)
