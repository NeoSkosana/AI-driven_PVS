"""Logging configuration for the application."""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
import os

def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Log format
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    
    # Set uvicorn access logger level
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    
    logger.info("Logging configured successfully")
