"""
Health check and system status endpoints
"""
from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
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

router = APIRouter()
logger = logging.getLogger("book_sharing.health")

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "environment": getattr(settings, 'ENVIRONMENT', 'development')
    }

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with system information"""
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

@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Kubernetes-style readiness probe"""
    try:
        # Check database connection
        db.execute("SELECT 1")
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"status": "not ready", "error": str(e)}

@router.get("/health/live")
async def liveness_check():
    """Kubernetes-style liveness probe"""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
