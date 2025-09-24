"""
Módulo de gestión de usuarios

Este módulo proporciona endpoints para la gestión de perfiles de usuario.
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse

from app.schemas.user import User as UserSchema
from app.schemas.error import ErrorResponse, ErrorDetail
from app.models.user import User
from app.services.auth_service import get_current_user

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


