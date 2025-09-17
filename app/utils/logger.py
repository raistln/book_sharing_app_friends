"""
Comprehensive logging system for the Book Sharing App
"""
import logging
import sys
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path
import json
from functools import wraps
from fastapi import Request
import time

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint
        if hasattr(record, 'method'):
            log_entry['method'] = record.method
        if hasattr(record, 'status_code'):
            log_entry['status_code'] = record.status_code
        if hasattr(record, 'duration'):
            log_entry['duration'] = record.duration
            
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logging(log_level: str = "INFO", enable_file_logging: bool = True):
    """
    Setup comprehensive logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_file_logging: Whether to enable file logging
    """
    # Clear existing handlers
    logging.getLogger().handlers.clear()
    
    # Set root logger level
    logging.getLogger().setLevel(getattr(logging, log_level.upper()))
    
    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Add console handler to root logger
    logging.getLogger().addHandler(console_handler)
    
    if enable_file_logging:
        # File handler for general logs
        file_handler = logging.FileHandler(
            logs_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        file_handler.setFormatter(JSONFormatter())
        file_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(file_handler)
        
        # Separate error log file
        error_handler = logging.FileHandler(
            logs_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        error_handler.setFormatter(JSONFormatter())
        error_handler.setLevel(logging.ERROR)
        logging.getLogger().addHandler(error_handler)
    
    # Configure specific loggers
    loggers = [
        "app.api",
        "app.services", 
        "app.models",
        "app.utils",
        "book_sharing"
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, log_level.upper()))
        logger.propagate = True

# Main application logger
logger = logging.getLogger("book_sharing")

def log_endpoint_call(endpoint: str, method: str = "GET"):
    """
    Decorator to log API endpoint calls
    
    Args:
        endpoint: The endpoint being called
        method: HTTP method
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            request_id = f"{int(time.time() * 1000)}"
            
            # Extract user info if available
            user_id = None
            try:
                # Try to get user from dependencies
                for arg in args:
                    if hasattr(arg, 'id'):
                        user_id = arg.id
                        break
            except:
                pass
            
            # Log request start
            logger.info(
                f"API call started: {method} {endpoint}",
                extra={
                    'endpoint': endpoint,
                    'method': method,
                    'request_id': request_id,
                    'user_id': user_id
                }
            )
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log successful completion
                logger.info(
                    f"API call completed: {method} {endpoint}",
                    extra={
                        'endpoint': endpoint,
                        'method': method,
                        'request_id': request_id,
                        'user_id': user_id,
                        'duration': round(duration, 3),
                        'status_code': 200
                    }
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Log error
                logger.error(
                    f"API call failed: {method} {endpoint} - {str(e)}",
                    extra={
                        'endpoint': endpoint,
                        'method': method,
                        'request_id': request_id,
                        'user_id': user_id,
                        'duration': round(duration, 3),
                        'error': str(e)
                    },
                    exc_info=True
                )
                
                raise
                
        return wrapper
    return decorator

def log_service_call(service_name: str, operation: str):
    """
    Decorator to log service layer calls
    
    Args:
        service_name: Name of the service
        operation: Operation being performed
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            logger.info(f"Service call: {service_name}.{operation}")
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(
                    f"Service call completed: {service_name}.{operation}",
                    extra={'duration': round(duration, 3)}
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                logger.error(
                    f"Service call failed: {service_name}.{operation} - {str(e)}",
                    extra={'duration': round(duration, 3)},
                    exc_info=True
                )
                
                raise
                
        return wrapper
    return decorator

def log_database_operation(operation: str, table: str):
    """
    Decorator to log database operations
    
    Args:
        operation: Type of operation (SELECT, INSERT, UPDATE, DELETE)
        table: Table being operated on
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            logger.debug(f"Database operation: {operation} on {table}")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.debug(
                    f"Database operation completed: {operation} on {table}",
                    extra={'duration': round(duration, 3)}
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                logger.error(
                    f"Database operation failed: {operation} on {table} - {str(e)}",
                    extra={'duration': round(duration, 3)},
                    exc_info=True
                )
                
                raise
                
        return wrapper
    return decorator

# Security logging functions
def log_auth_attempt(username: str, success: bool, ip_address: str = None):
    """Log authentication attempts"""
    if success:
        logger.info(
            f"Successful login for user: {username}",
            extra={'user_id': username, 'ip_address': ip_address}
        )
    else:
        logger.warning(
            f"Failed login attempt for user: {username}",
            extra={'user_id': username, 'ip_address': ip_address}
        )

def log_security_event(event_type: str, details: str, user_id: str = None):
    """Log security-related events"""
    logger.warning(
        f"Security event: {event_type} - {details}",
        extra={'user_id': user_id, 'event_type': event_type}
    )

def log_rate_limit_exceeded(ip_address: str, endpoint: str):
    """Log rate limit violations"""
    logger.warning(
        f"Rate limit exceeded from {ip_address} on {endpoint}",
        extra={'ip_address': ip_address, 'endpoint': endpoint}
    )

# Initialize logging when module is imported
setup_logging()
