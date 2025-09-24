"""
Módulo de monitoreo de salud del sistema

Este módulo proporciona endpoints para verificar el estado de salud de la aplicación,
incluyendo la conectividad con la base de datos, Redis y el uso de recursos del sistema.

**Endpoints disponibles:**
- GET /health: Verificación básica de salud
- GET /health/detailed: Verificación detallada con diagnóstico del sistema
- GET /health/ready: Sonda de preparación (readiness) para orquestadores
- GET /health/live: Sonda de vida (liveness) para orquestadores
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.database import get_db
from app.config import settings
from app.schemas.error import ErrorResponse
import logging
import os

# Optional imports
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

router = APIRouter(
    tags=["health"],
    responses={
        500: {
            "description": "Error interno del servidor",
            "model": ErrorResponse
        }
    }
)
logger = logging.getLogger("book_sharing.health")

# Modelos de respuesta para la documentación
class HealthCheckResponse(BaseModel):
    """Modelo de respuesta para el endpoint de salud básica"""
    status: str = Field(..., example="healthy", description="Estado general del servicio")
    timestamp: str = Field(..., example="2023-10-20T12:00:00+00:00", description="Marca de tiempo de la verificación")
    version: str = Field(..., example="1.0.0", description="Versión de la API")
    environment: str = Field(..., example="production", description="Entorno de ejecución")

class HealthCheckDetailResponse(HealthCheckResponse):
    """Modelo de respuesta extendido para el endpoint de salud detallada"""
    checks: Dict[str, Dict[str, Any]] = Field(
        ...,
        example={
            "database": {
                "status": "healthy",
                "message": "Database connection successful"
            },
            "redis": {
                "status": "warning",
                "message": "Redis connection failed: Connection refused"
            },
            "system": {
                "status": "healthy",
                "cpu_percent": 25.5,
                "memory_percent": 45.2,
                "disk_percent": 65.3,
                "available_memory_gb": 7.8
            }
        },
        description="Resultados detallados de las verificaciones de salud"
    )

class ReadinessResponse(BaseModel):
    """Modelo de respuesta para el endpoint de readiness"""
    status: str = Field(..., example="ready", description="Estado de preparación del servicio")
    error: Optional[str] = Field(None, example="Database connection failed", description="Mensaje de error si el estado no es 'ready'")

class LivenessResponse(BaseModel):
    """Modelo de respuesta para el endpoint de liveness"""
    status: str = Field(..., example="alive", description="Estado de vida del servicio")
    timestamp: str = Field(..., example="2023-10-20T12:00:00+00:00", description="Marca de tiempo de la verificación")

@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Verificación básica de salud",
    description="""
    Realiza una verificación básica del estado de salud de la aplicación.
    
    Este endpoint devuelve un estado simple que indica si el servicio está en funcionamiento
    junto con información básica como la versión y el entorno.
    
    **Códigos de estado HTTP:**
    - 200: El servicio está en funcionamiento correctamente
    """,
    responses={
        200: {
            "description": "El servicio está funcionando correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2023-10-20T12:00:00+00:00",
                        "version": "1.0.0",
                        "environment": "production"
                    }
                }
            }
        }
    }
)
async def health_check() -> HealthCheckResponse:
    """
    Verificación básica de salud del servicio.
    
    Returns:
        HealthCheckResponse: Estado actual del servicio con información básica
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "environment": getattr(settings, 'ENVIRONMENT', 'development')
    }

@router.get(
    "/health/detailed",
    response_model=HealthCheckDetailResponse,
    summary="Verificación detallada de salud",
    description="""
    Realiza una verificación detallada del estado de salud de la aplicación.
    
    Este endpoint verifica el estado de todos los componentes críticos del sistema,
    incluyendo la base de datos, Redis (si está configurado) y los recursos del sistema.
    
    **Estados posibles:**
    - `healthy`: El componente funciona correctamente
    - `warning`: El componente tiene problemas pero no críticos
    - `unhealthy`: El componente tiene problemas críticos
    
    **Códigos de estado HTTP:**
    - 200: Verificación completada (puede contener advertencias)
    - 500: Error interno del servidor
    """,
    responses={
        200: {
            "description": "Verificación de salud completada",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2023-10-20T12:00:00+00:00",
                        "version": "1.0.0",
                        "environment": "production",
                        "checks": {
                            "database": {
                                "status": "healthy",
                                "message": "Database connection successful"
                            },
                            "redis": {
                                "status": "warning",
                                "message": "Redis connection failed: Connection refused"
                            },
                            "system": {
                                "status": "healthy",
                                "cpu_percent": 25.5,
                                "memory_percent": 45.2,
                                "disk_percent": 65.3,
                                "available_memory_gb": 7.8
                            }
                        }
                    }
                }
            }
        }
    }
)
async def detailed_health_check(db: Session = Depends(get_db)) -> HealthCheckDetailResponse:
    """
    Realiza una verificación detallada del estado de salud del servicio.
    
    Verifica el estado de la base de datos, Redis (si está disponible) y los recursos del sistema.
    
    Args:
        db: Sesión de base de datos (inyectada automáticamente)
        
    Returns:
        HealthCheckDetailResponse: Estado detallado del servicio con información de diagnóstico
        
    Raises:
        HTTPException: 500 si ocurre un error inesperado durante la verificación
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "environment": getattr(settings, 'ENVIRONMENT', 'development'),
            "checks": {}
        }
        
        # Database check
        try:
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            health_status["checks"]["database"] = {
                "status": "healthy",
                "message": "Database connection successful"
            }
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["checks"]["database"] = {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}"
            }
            logger.error(f"Database health check failed: {e}")
        
        # Redis check (if available)
        if REDIS_AVAILABLE:
            try:
                redis_client = redis.Redis(
                    host=getattr(settings, 'REDIS_HOST', 'localhost'),
                    port=getattr(settings, 'REDIS_PORT', 6379),
                    db=getattr(settings, 'REDIS_DB', 0),
                    socket_timeout=5
                )
                redis_client.ping()
                health_status["checks"]["redis"] = {
                    "status": "healthy",
                    "message": "Redis connection successful"
                }
            except Exception as e:
                health_status["checks"]["redis"] = {
                    "status": "warning",
                    "message": f"Redis connection failed: {str(e)}"
                }
                logger.warning(f"Redis health check failed: {e}")
        else:
            health_status["checks"]["redis"] = {
                "status": "warning",
                "message": "Redis library not available"
            }
        
        # System resources check (if available)
        if PSUTIL_AVAILABLE:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                health_status["checks"]["system"] = {
                    "status": "healthy",
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "available_memory_gb": round(memory.available / (1024**3), 2)
                }
                
                # Mark as warning if resources are high
                if cpu_percent > 80 or memory.percent > 85 or disk.percent > 90:
                    health_status["checks"]["system"]["status"] = "warning"
                    if health_status["status"] == "healthy":
                        health_status["status"] = "warning"
                        
            except Exception as e:
                health_status["checks"]["system"] = {
                    "status": "warning",
                    "message": f"System check failed: {str(e)}"
                }
                logger.warning(f"System health check failed: {e}")
        else:
            health_status["checks"]["system"] = {
                "status": "warning",
                "message": "psutil library not available"
            }
        
        return health_status
        
    except Exception as e:
        logger.critical(f"Critical error during health check: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "msg": "Error interno durante la verificación de salud",
                "type": "health_check_error"
            }
        )

@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    summary="Sonda de preparación (readiness)",
    description="""
    Verifica si el servicio está listo para recibir tráfico.
    
    Este endpoint es utilizado por orquestadores como Kubernetes para determinar
    si el servicio está listo para manejar solicitudes. Verifica la conectividad
    con la base de datos y otros servicios críticos.
    
    **Códigos de estado HTTP:**
    - 200: El servicio está listo para recibir tráfico
    - 503: El servicio no está listo (se devuelve como 200 con status='not ready')
    """,
    responses={
        200: {
            "description": "Estado de preparación del servicio",
            "content": {
                "application/json": {
                    "examples": {
                        "ready": {
                            "summary": "Servicio listo",
                            "value": {"status": "ready"}
                        },
                        "not_ready": {
                            "summary": "Servicio no listo",
                            "value": {
                                "status": "not ready",
                                "error": "Database connection failed"
                            }
                        }
                    }
                }
            }
        }
    }
)
async def readiness_check(db: Session = Depends(get_db)) -> ReadinessResponse:
    """
    Verifica si el servicio está listo para recibir tráfico.
    
    Args:
        db: Sesión de base de datos (inyectada automáticamente)
        
    Returns:
        ReadinessResponse: Estado de preparación del servicio
    """
    try:
        # Verificar conexión a la base de datos
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "status": "not ready",
            "error": f"Database connection failed: {str(e)}"
        }

@router.get(
    "/health/live",
    response_model=LivenessResponse,
    summary="Sonda de vida (liveness)",
    description="""
    Verifica si el servicio está en ejecución.
    
    Este endpoint es utilizado por orquestadores como Kubernetes para determinar
    si el servicio está en ejecución y debe reiniciarse. Es una verificación
    muy ligera que solo comprueba que el proceso está activo.
    
    **Códigos de estado HTTP:**
    - 200: El servicio está en ejecución
    """,
    responses={
        200: {
            "description": "El servicio está en ejecución",
            "content": {
                "application/json": {
                    "example": {
                        "status": "alive",
                        "timestamp": "2023-10-20T12:00:00+00:00"
                    }
                }
            }
        }
    }
)
async def liveness_check() -> LivenessResponse:
    """
    Verifica si el servicio está en ejecución.
    
    Returns:
        LivenessResponse: Estado de vida del servicio con marca de tiempo
    """
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
