"""Logging configuration for the application."""
import logging
import json
import sys
import uuid
from datetime import datetime
from typing import Any, Dict
from pythonjsonlogger import jsonlogger
from contextvars import ContextVar

# Context variable to store correlation ID
correlation_id: ContextVar[str] = ContextVar('correlation_id', default='')

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """Add custom fields to the log record."""
        super().add_fields(log_record, record, message_dict)
        
        # Add standard fields
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno
        
        # Add correlation ID if available
        try:
            log_record['correlation_id'] = correlation_id.get()
        except LookupError:
            log_record['correlation_id'] = ''

def setup_logging(level: str = 'INFO') -> None:
    """Setup application logging with JSON formatting."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)
    
    # Create console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(module)s %(correlation_id)s %(message)s'
    )
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler for errors
    error_handler = logging.FileHandler('errors.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

def get_correlation_id() -> str:
    """Get the current correlation ID or generate a new one."""
    try:
        return correlation_id.get()
    except LookupError:
        new_id = str(uuid.uuid4())
        correlation_id.set(new_id)
        return new_id

def set_correlation_id(id: str) -> None:
    """Set the correlation ID for the current context."""
    correlation_id.set(id)

class LoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that adds contextual information."""
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Process the logging message and keyword arguments."""
        extra = kwargs.get('extra', {})
        
        # Add correlation ID
        if 'correlation_id' not in extra:
            extra['correlation_id'] = get_correlation_id()
            
        # Add timestamp if not present
        if 'timestamp' not in extra:
            extra['timestamp'] = datetime.utcnow().isoformat()
            
        kwargs['extra'] = extra
        return msg, kwargs

def get_logger(name: str) -> LoggerAdapter:
    """Get a logger instance with the custom adapter."""
    logger = logging.getLogger(name)
    return LoggerAdapter(logger, {})
