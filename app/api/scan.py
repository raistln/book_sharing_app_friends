"""
Módulo de escaneo de libros

Este módulo proporciona endpoints para escanear libros utilizando códigos de barras y OCR,
permitiendo a los usuarios identificar libros a partir de imágenes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Dict, Any, List, Optional
import logging

from app.services.book_scan_service import BookScanService
from app.services.auth_service import get_current_user
from app.models.user import User
from app.schemas.error import ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/scan",
    tags=["scan"],
    responses={
        401: {"description": "No autorizado", "model": ErrorResponse},
        500: {"description": "Error interno del servidor", "model": ErrorResponse}
    }
)

# Modelos de ejemplo para documentación
scan_result_example = {
    "isbn": "9788490626464",
    "title": "El Principito",
    "author": "Antoine de Saint-Exupéry",
    "scanned_by": {
        "user_id": "507f1f77bcf86cd799439011",
        "username": "usuario_ejemplo"
    },
    "scan_method": "barcode"
}

error_response_example = {
    "detail": {
        "msg": "El archivo debe ser una imagen",
        "type": "validation_error"
    }
}


@router.post(
    "/book",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Escanear un libro por código de barras o portada",
    description="""
    Escanea un libro utilizando reconocimiento de códigos de barras y OCR.
    
    Este endpoint permite a los usuarios escanear la portada o el código de barras de un libro
    para obtener información detallada del mismo. El sistema intentará primero reconocer
    el código de barras y, si no lo encuentra, aplicará OCR al texto de la portada.
    
    **Requisitos de la imagen:**
    - Formatos soportados: JPG, PNG, JPEG
    - Tamaño máximo: 10MB
    - Resolución recomendada: Mínimo 300x300 píxeles
    
    **Autenticación requerida:** Sí
    """,
    responses={
        200: {
            "description": "Libro escaneado exitosamente",
            "content": {
                "application/json": {
                    "example": scan_result_example
                }
            }
        },
        400: {
            "description": "Error en la solicitud",
            "content": {
                "application/json": {
                    "example": error_response_example
                }
            }
        },
        401: {"$ref": "#/components/responses/UnauthorizedError"},
        500: {"$ref": "#/components/responses/InternalServerError"}
    }
)
async def scan_book(
    file: UploadFile = File(..., 
        description="Imagen del libro (portada o código de barras)",
        example="imagen_libro.jpg"
    ),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    # Validar tipo de archivo
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "msg": "El archivo debe ser una imagen (JPG, PNG, JPEG)",
                "type": "validation_error"
            }
        )
    
    # Validar tamaño (máximo 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size and file.size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "msg": f"El archivo es demasiado grande. Tamaño máximo permitido: {max_size/1024/1024}MB",
                "type": "validation_error",
                "max_size_mb": 10,
                "actual_size_mb": round(file.size/1024/1024, 2)
            }
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
        logger.error(f"Error escaneando libro: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "msg": "Error interno del servidor al procesar la imagen",
                "type": "server_error"
            }
        )


@router.post(
    "/book/multiple",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Escanear un libro usando múltiples métodos",
    description="""
    Escanea un libro utilizando todos los métodos de reconocimiento disponibles.
    
    Este endpoint aplica múltiples técnicas de reconocimiento (códigos de barras y OCR)
    y devuelve los resultados de cada método, permitiendo comparar y validar la información.
    
    **Métodos utilizados:**
    1. Reconocimiento de códigos de barras
    2. OCR en la portada del libro
    3. Búsqueda por título/autor extraído
    
    **Requisitos de la imagen:**
    - Formatos soportados: JPG, PNG, JPEG
    - Tamaño máximo: 10MB
    - Resolución recomendada: Mínimo 500x500 píxeles
    
    **Autenticación requerida:** Sí
    """,
    responses={
        200: {
            "description": "Libro escaneado con múltiples métodos",
            "content": {
                "application/json": {
                    "example": {
                        **scan_result_example,
                        "scan_methods": ["barcode", "ocr", "title_search"],
                        "confidence_scores": {
                            "barcode": 0.95,
                            "ocr": 0.85,
                            "title_search": 0.78
                        },
                        "all_results": {
                            "barcode": scan_result_example,
                            "ocr": {
                                "title": "El Principito",
                                "author": "Antoine de Saint-Exupéry",
                                "confidence": 0.85
                            }
                        }
                    }
                }
            }
        },
        400: {
            "description": "Error en la solicitud",
            "content": {
                "application/json": {
                    "example": error_response_example
                }
            }
        },
        401: {"$ref": "#/components/responses/UnauthorizedError"},
        500: {"$ref": "#/components/responses/InternalServerError"}
    }
)
async def scan_book_multiple_methods(
    file: UploadFile = File(..., 
        description="Imagen del libro (portada o código de barras)",
        example="imagen_libro.jpg"
    ),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    # Validar tipo de archivo
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "msg": "El archivo debe ser una imagen (JPG, PNG, JPEG)",
                "type": "validation_error"
            }
        )
    
    # Validar tamaño (máximo 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size and file.size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "msg": f"El archivo es demasiado grande. Tamaño máximo permitido: {max_size/1024/1024}MB",
                "type": "validation_error",
                "max_size_mb": 10,
                "actual_size_mb": round(file.size/1024/1024, 2)
            }
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
