"""
Modelo de notificaciones para la aplicación
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class NotificationType(str, enum.Enum):
    """Tipos de notificaciones"""
    LOAN_REQUEST = "LOAN_REQUEST"
    LOAN_APPROVED = "LOAN_APPROVED"
    LOAN_REJECTED = "LOAN_REJECTED"
    LOAN_RETURNED = "LOAN_RETURNED"
    DUE_DATE_REMINDER = "DUE_DATE_REMINDER"
    OVERDUE = "OVERDUE"
    NEW_MESSAGE = "NEW_MESSAGE"
    GROUP_INVITATION = "GROUP_INVITATION"
    GROUP_JOINED = "GROUP_JOINED"


class NotificationPriority(str, enum.Enum):
    """Prioridades de notificaciones"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    """Modelo de notificación"""
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(SQLEnum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.MEDIUM)
    is_read = Column(Boolean, default=False)
    data = Column(JSONB, nullable=True)  # Datos adicionales en formato JSON
    
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    
    # Relaciones
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.id} - {self.type} for user {self.user_id}>"
