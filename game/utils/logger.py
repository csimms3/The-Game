"""
Logging utilities for the game
"""

import logging
import os
from datetime import datetime

def setup_logger(name: str = "the_game", level: int = logging.INFO) -> logging.Logger:
    """Setup and configure the game logger"""
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_handler = logging.FileHandler(f"logs/game_{timestamp}.log")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
