"""
Módulo de chat para la aplicación de préstamo de libros

Este módulo proporciona endpoints para la funcionalidad de mensajería entre usuarios
relacionados con préstamos de libros. Permite el envío y consulta de mensajes
asociados a un préstamo específico.

**Autenticación requerida:** Todas las rutas requieren autenticación.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.message_service import MessageService
from app.schemas.message import MessageCreate, Message as MessageSchema
from app.schemas.error import ErrorResponse
from app.models.user import User

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "No autorizado",
            "model": ErrorResponse
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "No tienes permiso para acceder a este recurso",
            "model": ErrorResponse
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Recurso no encontrado",
            "model": ErrorResponse
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Error interno del servidor",
            "model": ErrorResponse
        }
    }
)

# Ejemplos para la documentación
message_example = {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "loan_id": "123e4567-e89b-12d3-a456-426614174000",
    "sender_id": "550e8400-e29b-41d4-a716-446655440000",
    "content": "¿Cuándo podrías devolverme el libro?",
    "created_at": "2023-10-20T12:00:00Z"
}

message_create_example = {
    "loan_id": "123e4567-e89b-12d3-a456-426614174000",
    "content": "¿Cuándo podrías devolverme el libro?"
}

error_response_example = {
    "detail": {
        "msg": "No tienes acceso a este préstamo",
        "type": "forbidden"
    }
}


@router.post(
    "/send",
    response_model=MessageSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar un mensaje",
    description="""
    Envía un mensaje relacionado con un préstamo específico.
    
    Este endpoint permite a los usuarios enviar mensajes a otros usuarios
    que están involucrados en un préstamo de libro (ya sea como prestador o prestatario).
    
    **Permisos requeridos:**
    - Debes ser el propietario del libro o el prestatario.
    - El préstamo debe estar activo o pendiente.
    """,
    responses={
        201: {
            "description": "Mensaje enviado exitosamente",
            "content": {
                "application/json": {
                    "example": message_example
                }
            }
        },
        400: {
            "description": "Solicitud inválida",
            "model": ErrorResponse
        },
        403: {
            "description": "No tienes permiso para enviar mensajes en este préstamo",
            "content": {
                "application/json": {
                    "example": error_response_example
                }
            }
        },
        404: {
            "description": "El préstamo no existe",
            "model": ErrorResponse
        }
    }
)
def send_message(
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> MessageSchema:
    """
    Envía un nuevo mensaje en el contexto de un préstamo.
    
    Args:
        payload: Datos del mensaje a enviar
        current_user: Usuario autenticado (inyectado automáticamente)
        db: Sesión de base de datos (inyectada automáticamente)
        
    Returns:
        MessageSchema: El mensaje creado con su información completa
        
    Raises:
        HTTPException: 403 si el usuario no tiene permiso para enviar mensajes en este préstamo
        HTTPException: 404 si el préstamo no existe
    """
    svc = MessageService(db)
    msg = svc.send(payload.loan_id, current_user.id, payload.content)
    if not msg:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "msg": "No tienes acceso a este préstamo o el préstamo no existe",
                "type": "forbidden"
            }
        )
    return msg


@router.get(
    "/loan/{loan_id}",
    response_model=List[MessageSchema],
    summary="Obtener mensajes de un préstamo",
    description="""
    Obtiene todos los mensajes asociados a un préstamo específico.
    
    Este endpoint devuelve la lista completa de mensajes intercambiados
    entre los participantes de un préstamo de libro, ordenados por fecha de creación.
    
    **Permisos requeridos:**
    - Debes ser el propietario del libro o el prestatario.
    
    **Parámetros opcionales:**
    - `since`: Timestamp ISO 8601 para obtener solo mensajes posteriores a esa fecha
    """,
    responses={
        200: {
            "description": "Lista de mensajes del préstamo",
            "content": {
                "application/json": {
                    "example": [message_example]
                }
            }
        },
        400: {
            "description": "ID de préstamo inválido",
            "model": ErrorResponse
        },
        403: {
            "description": "No tienes permiso para ver los mensajes de este préstamo",
            "content": {
                "application/json": {
                    "example": error_response_example
                }
            }
        },
        404: {
            "description": "El préstamo no existe",
            "model": ErrorResponse
        }
    }
)
def get_messages(
    loan_id: UUID,
    since: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[MessageSchema]:
    """
    Obtiene todos los mensajes de un préstamo específico.
    
    Args:
        loan_id: ID único del préstamo
        since: Timestamp ISO 8601 opcional para obtener solo mensajes nuevos
        current_user: Usuario autenticado (inyectado automáticamente)
        db: Sesión de base de datos (inyectada automáticamente)
        
    Returns:
        List[MessageSchema]: Lista de mensajes ordenados por fecha de creación
        
    Raises:
        HTTPException: 403 si el usuario no tiene permiso para ver los mensajes
        HTTPException: 404 si el préstamo no existe
    """
    svc = MessageService(db)
    items = svc.list_for_loan(loan_id, current_user.id, since=since)
    if items is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "msg": "No tienes acceso a este préstamo o el préstamo no existe",
                "type": "forbidden"
            }
        )
    return items


