"""
Schemas de notificaciones
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models.notification import NotificationType, NotificationPriority


class NotificationBase(BaseModel):
    """Base para notificaciones"""
    type: NotificationType
    title: str = Field(..., max_length=255)
    message: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    data: Optional[Dict[str, Any]] = None


class NotificationCreate(NotificationBase):
    """Crear notificación"""
    user_id: UUID


class NotificationUpdate(BaseModel):
    """Actualizar notificación"""
    is_read: Optional[bool] = None


class Notification(NotificationBase):
    """Notificación completa"""
    id: UUID
    user_id: UUID
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationStats(BaseModel):
    """Estadísticas de notificaciones"""
    total: int
    unread: int
    by_type: Dict[str, int]
    by_priority: Dict[str, int]
