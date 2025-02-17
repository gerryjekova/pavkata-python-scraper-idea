import logging
import sys
from typing import Dict, Any
from pydantic import BaseSettings
from pathlib import Path

class LogConfig(BaseSettings):
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "scraper.log"

def setup_logging() -> None:
    """Configure logging for the application"""
    config = LogConfig()
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    handlers = [
        logging.StreamHandler(sys.stdout),  # Console handler
        logging.FileHandler(log_dir / config.LOG_FILE)  # File handler
    ]
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        handlers=handlers
    )
    
    # Set third-party loggers to WARNING
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)