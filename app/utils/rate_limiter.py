"""
Rate limiting utilities for API endpoints
"""
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    SLOWAPI_AVAILABLE = True
except ImportError:
    SLOWAPI_AVAILABLE = False
    
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# Initialize Redis connection for rate limiting (optional)
@lru_cache()
def get_redis_client():
    try:
        import redis
        from app.config import settings
        client = redis.Redis(
            host=getattr(settings, 'REDIS_HOST', 'localhost'),
            port=getattr(settings, 'REDIS_PORT', 6379),
            db=getattr(settings, 'REDIS_DB', 0),
            decode_responses=True
        )
        # Test connection
        client.ping()
        logger.info("Redis connection established for rate limiting")
        return client
    except Exception as e:
        logger.warning(f"Redis not available, using in-memory rate limiting: {e}")
        return None

def is_rate_limiting_disabled():
    """Check if rate limiting should be disabled based on environment variables"""
    import os
    return os.getenv("TESTING") == "true" or os.getenv("DISABLE_RATE_LIMITING") == "true"

# Create limiter instance if slowapi is available and not in testing mode
@lru_cache()
def get_limiter():
    from app.config import settings
    
    if is_rate_limiting_disabled():
        logger.info("Rate limiting disabled via environment variables")
        return None
    
    if not SLOWAPI_AVAILABLE:
        logger.warning("slowapi not available, rate limiting disabled")
        return None
    
    try:
        redis_client = get_redis_client()
        limiter = Limiter(
            key_func=get_remote_address,
            storage_uri=f"redis://{getattr(settings, 'REDIS_HOST', 'localhost')}:{getattr(settings, 'REDIS_PORT', 6379)}" if redis_client else "memory://",
            default_limits=["100/minute"]
        )
        logger.info("Rate limiter initialized")
        return limiter
    except Exception as e:
        logger.warning(f"Failed to create rate limiter: {e}")
        return None

# Initialize limiter
limiter = get_limiter()

# Force disable rate limiting if environment variables are set
if is_rate_limiting_disabled():
    limiter = None

# Custom rate limit exceeded handler
def rate_limit_handler(request: Request, exc):
    """Custom handler for rate limit exceeded"""
    if SLOWAPI_AVAILABLE:
        logger.warning(f"Rate limit exceeded for {get_remote_address(request)}: {exc.detail}")
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Demasiadas solicitudes. Por favor, intenta más tarde.",
                "retry_after": getattr(exc, 'retry_after', 60)
            }
        )
    return JSONResponse(status_code=500, content={"detail": "Rate limiting not available"})

# Rate limiting decorators for different endpoint types
def auth_rate_limit():
    """Rate limit for authentication endpoints (stricter)"""
    import os
    if os.getenv("TESTING") == "true" or os.getenv("DISABLE_RATE_LIMITING") == "true":
        return lambda func: func  # Disabled for testing
    limiter = get_limiter()
    if limiter is not None:
        return limiter.limit("5/minute")
    return lambda func: func  # No-op decorator if slowapi not available

def api_rate_limit():
    """Rate limit for general API endpoints"""
    import os
    if os.getenv("TESTING") == "true" or os.getenv("DISABLE_RATE_LIMITING") == "true":
        return lambda func: func  # Disabled for testing
    limiter = get_limiter()
    if limiter is not None:
        return limiter.limit("30/minute")
    return lambda func: func  # No-op decorator

def upload_rate_limit():
    """Rate limit for file upload endpoints"""
    import os
    if os.getenv("TESTING") == "true" or os.getenv("DISABLE_RATE_LIMITING") == "true":
        return lambda func: func  # Disabled for testing
    limiter = get_limiter()
    if limiter is not None:
        return limiter.limit("10/minute")
    return lambda func: func  # No-op decorator

def search_rate_limit():
    """Rate limit for search endpoints"""
    import os
    if os.getenv("TESTING") == "true" or os.getenv("DISABLE_RATE_LIMITING") == "true":
        return lambda func: func  # Disabled for testing
    limiter = get_limiter()
    if limiter is not None:
        return limiter.limit("30/minute")
    return lambda func: func  # No-op decorator
