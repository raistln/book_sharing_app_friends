"""
Módulo de gestión de usuarios

Este módulo proporciona endpoints para la gestión de perfiles de usuario.
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, status, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.schemas.user import User as UserSchema
from app.schemas.book import BookResponse
from app.schemas.error import ErrorResponse, ErrorDetail
from app.models.user import User
from app.models.book import Book
from app.services.auth_service import get_current_user
from app.dependencies import get_current_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        401: {"description": "No autorizado - Se requiere autenticación"},
        500: {"description": "Error interno del servidor"}
    }
)

@router.get(
    "/me",
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
    summary="Obtener perfil del usuario autenticado",
    description="""
    Retorna la información del perfil del usuario actualmente autenticado.
    
    Este endpoint requiere autenticación mediante token JWT.
    """,
    responses={
        200: {
            "description": "Perfil del usuario obtenido exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "usuario@ejemplo.com",
                        "full_name": "Juan Pérez",
                        "is_active": True,
                        "created_at": "2023-01-01T12:00:00Z",
                        "updated_at": "2023-01-01T12:00:00Z"
                    }
                }
            }
        },
        401: {
            "description": "No autorizado - Token inválido o expirado",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "msg": "No se pudo validar el token",
                            "type": "authentication_error"
                        }
                    }
                }
            }
        },
        403: {
            "description": "Acceso denegado - Usuario inactivo",
            "model": ErrorResponse
        }
    }
)
async def read_own_profile(current_user: User = Depends(get_current_user)):
    """
    Obtiene el perfil del usuario autenticado.

    Args:
        current_user (User): Usuario autenticado (obtenido del token JWT).

    Returns:
        UserSchema: Perfil del usuario autenticado.
        
    Raises:
        HTTPException: 401 si el token es inválido o ha expirado.
        HTTPException: 403 si el usuario está inactivo.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"msg": "Usuario inactivo", "type": "inactive_user"}
        )
        
    return current_user


@router.get(
    "/me/books",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Obtener libros del usuario autenticado",
    description="""
    Retorna una lista paginada de libros del usuario actualmente autenticado.
    
    Este endpoint requiere autenticación mediante token JWT.
    """
)
async def get_my_books(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_current_db),
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(12, ge=1, le=100, description="Libros por página")
):
    """
    Obtiene los libros del usuario autenticado con paginación.

    Args:
        current_user (User): Usuario autenticado.
        db (Session): Sesión de base de datos.
        page (int): Número de página (empezando en 1).
        per_page (int): Número de libros por página.

    Returns:
        Dict: Diccionario con items (libros), total, page, per_page, total_pages.
    """
    # Calcular offset
    offset = (page - 1) * per_page
    
    # Query para obtener libros del usuario
    query = db.query(Book).options(
        joinedload(Book.owner),
        joinedload(Book.current_borrower)
    ).filter(
        and_(
            Book.owner_id == current_user.id,
            Book.is_archived == False
        )
    )
    
    # Contar total
    total = query.count()
    
    # Obtener libros paginados
    books = query.offset(offset).limit(per_page).all()
    
    # Calcular total de páginas
    total_pages = (total + per_page - 1) // per_page
    
    # Convertir a schemas Pydantic
    from app.schemas.book import BookResponse
    books_response = [BookResponse.model_validate(book) for book in books]
    
    return {
        "items": books_response,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    }


