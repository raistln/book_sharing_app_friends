"""
API de notificaciones
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.notification_service import NotificationService
from app.models.user import User
from app.models.notification import NotificationType
from app.schemas.notification import Notification, NotificationUpdate, NotificationStats
from app.schemas.error import ErrorResponse

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    responses={
        401: {"description": "No autorizado", "model": ErrorResponse},
        404: {"description": "No encontrado", "model": ErrorResponse},
        500: {"description": "Error interno del servidor", "model": ErrorResponse}
    }
)


@router.get(
    "/",
    response_model=List[Notification],
    summary="Obtener notificaciones del usuario",
    description="Obtiene todas las notificaciones del usuario autenticado con filtros opcionales"
)
def get_notifications(
    is_read: Optional[bool] = Query(None, description="Filtrar por leídas/no leídas"),
    notification_type: Optional[NotificationType] = Query(None, description="Filtrar por tipo"),
    limit: int = Query(50, ge=1, le=100, description="Cantidad máxima de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener notificaciones del usuario autenticado"""
    service = NotificationService(db)
    return service.get_user_notifications(
        user_id=current_user.id,
        is_read=is_read,
        notification_type=notification_type,
        limit=limit,
        offset=offset
    )


@router.get(
    "/unread/count",
    response_model=dict,
    summary="Obtener cantidad de notificaciones no leídas",
    description="Devuelve el número de notificaciones no leídas del usuario"
)
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener cantidad de notificaciones no leídas"""
    service = NotificationService(db)
    count = service.get_unread_count(current_user.id)
    return {"unread_count": count}


@router.get(
    "/stats",
    response_model=NotificationStats,
    summary="Obtener estadísticas de notificaciones",
    description="Devuelve estadísticas detalladas de las notificaciones del usuario"
)
def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de notificaciones"""
    service = NotificationService(db)
    return service.get_stats(current_user.id)


@router.get(
    "/{notification_id}",
    response_model=Notification,
    summary="Obtener una notificación específica",
    description="Obtiene los detalles de una notificación por su ID"
)
def get_notification(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener una notificación específica"""
    service = NotificationService(db)
    notification = service.get_notification(notification_id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    
    # Verificar que la notificación pertenece al usuario
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a esta notificación"
        )
    
    return notification


@router.patch(
    "/{notification_id}/read",
    response_model=Notification,
    summary="Marcar notificación como leída",
    description="Marca una notificación específica como leída"
)
def mark_as_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marcar notificación como leída"""
    service = NotificationService(db)
    notification = service.get_notification(notification_id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    
    # Verificar que la notificación pertenece al usuario
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar esta notificación"
        )
    
    return service.mark_as_read(notification_id)


@router.post(
    "/read-all",
    response_model=dict,
    summary="Marcar todas como leídas",
    description="Marca todas las notificaciones del usuario como leídas"
)
def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marcar todas las notificaciones como leídas"""
    service = NotificationService(db)
    count = service.mark_all_as_read(current_user.id)
    return {"marked_as_read": count}


@router.delete(
    "/{notification_id}",
    response_model=dict,
    summary="Eliminar notificación",
    description="Elimina una notificación específica"
)
def delete_notification(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar una notificación"""
    service = NotificationService(db)
    notification = service.get_notification(notification_id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    
    # Verificar que la notificación pertenece al usuario
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar esta notificación"
        )
    
    service.delete_notification(notification_id)
    return {"message": "Notificación eliminada exitosamente"}
