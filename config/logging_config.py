import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime
from config.settings import settings

def setup_logging():
    """Configure application logging"""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        settings.log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def log_interaction(user_id: str, session_id: str, message: str, response: str, metadata: dict = None):
    """Log user interaction for analytics"""
    logger = logging.getLogger(__name__)
    
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "session_id": session_id,
        "input": message,
        "output": response,
        "metadata": metadata or {}
    }
    
    logger.info(f"Interaction: {json.dumps(log_data)}")