"""
Comprehensive error handling middleware
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Union
import traceback
from datetime import datetime

logger = logging.getLogger("book_sharing.error_handler")

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent format"""
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={
            'status_code': exc.status_code,
            'path': str(request.url),
            'method': request.method,
            'client_ip': request.client.host if request.client else None
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors"""
    logger.warning(
        f"Validation Error: {exc.errors()}",
        extra={
            'path': str(request.url),
            'method': request.method,
            'validation_errors': exc.errors()
        }
    )
    
    # Format validation errors for better UX
    formatted_errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        formatted_errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "status_code": 422,
            "message": "Error de validación en los datos enviados",
            "details": formatted_errors,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    # Log the full traceback for debugging
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={
            'path': str(request.url),
            'method': request.method,
            'client_ip': request.client.host if request.client else None,
            'traceback': traceback.format_exc()
        },
        exc_info=True
    )
    
    # Don't expose internal error details in production
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "message": "Error interno del servidor. Por favor, intenta más tarde.",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )

async def starlette_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette HTTP exceptions"""
    logger.warning(
        f"Starlette HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={
            'status_code': exc.status_code,
            'path': str(request.url),
            'method': request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )

# Custom exception classes for better error handling
class BusinessLogicError(Exception):
    """Custom exception for business logic errors"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class DatabaseError(Exception):
    """Custom exception for database errors"""
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    def __init__(self, message: str = "Authentication failed"):
        self.message = message
        super().__init__(self.message)

class AuthorizationError(Exception):
    """Custom exception for authorization errors"""
    def __init__(self, message: str = "Access denied"):
        self.message = message
        super().__init__(self.message)

async def business_logic_exception_handler(request: Request, exc: BusinessLogicError) -> JSONResponse:
    """Handle business logic exceptions"""
    logger.info(
        f"Business Logic Error: {exc.message}",
        extra={
            'path': str(request.url),
            'method': request.method,
            'status_code': exc.status_code
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.message,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )

async def database_exception_handler(request: Request, exc: DatabaseError) -> JSONResponse:
    """Handle database exceptions"""
    logger.error(
        f"Database Error: {exc.message}",
        extra={
            'path': str(request.url),
            'method': request.method,
            'original_error': str(exc.original_error) if exc.original_error else None
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "message": "Error de base de datos. Por favor, intenta más tarde.",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )

async def auth_exception_handler(request: Request, exc: Union[AuthenticationError, AuthorizationError]) -> JSONResponse:
    """Handle authentication and authorization exceptions"""
    status_code = 401 if isinstance(exc, AuthenticationError) else 403
    
    logger.warning(
        f"Auth Error: {exc.message}",
        extra={
            'path': str(request.url),
            'method': request.method,
            'status_code': status_code,
            'client_ip': request.client.host if request.client else None
        }
    )
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": True,
            "status_code": status_code,
            "message": exc.message,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )
