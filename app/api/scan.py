"""
Endpoints para escanear libros con códigos de barras y OCR.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Dict, Any
import logging

from app.services.book_scan_service import BookScanService
from app.services.auth_service import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scan", tags=["scan"])


@router.post("/book", response_model=Dict[str, Any])
async def scan_book(
    file: UploadFile = File(..., description="Imagen del libro"),
    current_user: User = Depends(get_current_user)
):
    """
    Escanea un libro usando códigos de barras y OCR.
    
    - **file**: Imagen del libro (JPG, PNG, etc.)
    - **current_user**: Usuario autenticado
    
    Retorna información extraída del libro y resultados de búsqueda.
    """
    # Validar tipo de archivo
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser una imagen"
        )
    
    # Validar tamaño (máximo 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size and file.size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo es demasiado grande (máximo 10MB)"
        )
    
    try:
        # Leer datos de la imagen
        image_data = await file.read()
        
        if len(image_data) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo está vacío"
            )
        
        # Escanear el libro
        scan_service = BookScanService()
        result = scan_service.scan_book(image_data)
        
        # Añadir información del usuario
        result["scanned_by"] = {
            "user_id": str(current_user.id),
            "username": current_user.username
        }
        
        logger.info(f"Libro escaneado por usuario {current_user.username}: {result}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error escaneando libro: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/book/multiple", response_model=Dict[str, Any])
async def scan_book_multiple_methods(
    file: UploadFile = File(..., description="Imagen del libro"),
    current_user: User = Depends(get_current_user)
):
    """
    Escanea un libro usando todos los métodos disponibles (códigos de barras + OCR).
    
    - **file**: Imagen del libro (JPG, PNG, etc.)
    - **current_user**: Usuario autenticado
    
    Retorna resultados detallados de ambos métodos.
    """
    # Validar tipo de archivo
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser una imagen"
        )
    
    # Validar tamaño (máximo 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size and file.size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo es demasiado grande (máximo 10MB)"
        )
    
    try:
        # Leer datos de la imagen
        image_data = await file.read()
        
        if len(image_data) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo está vacío"
            )
        
        # Escanear el libro con todos los métodos
        scan_service = BookScanService()
        result = scan_service.scan_multiple_methods(image_data)
        
        # Añadir información del usuario
        result["scanned_by"] = {
            "user_id": str(current_user.id),
            "username": current_user.username
        }
        
        logger.info(f"Libro escaneado (múltiples métodos) por usuario {current_user.username}: {result}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error escaneando libro (múltiples métodos): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )
