"""
Servicio de notificaciones
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.models.notification import Notification, NotificationType, NotificationPriority
from app.schemas.notification import NotificationCreate, NotificationUpdate


class NotificationService:
    """Servicio para gestionar notificaciones"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_notification(
        self,
        user_id: UUID,
        notification_type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        data: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """Crear una nueva notificación"""
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            priority=priority,
            data=data or {}
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        return notification
    
    def get_user_notifications(
        self,
        user_id: UUID,
        is_read: Optional[bool] = None,
        notification_type: Optional[NotificationType] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """Obtener notificaciones de un usuario"""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
        
        if notification_type:
            query = query.filter(Notification.type == notification_type)
        
        query = query.order_by(Notification.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        return query.all()
    
    def get_notification(self, notification_id: UUID) -> Optional[Notification]:
        """Obtener una notificación por ID"""
        return self.db.query(Notification).filter(Notification.id == notification_id).first()
    
    def mark_as_read(self, notification_id: UUID) -> Optional[Notification]:
        """Marcar notificación como leída"""
        notification = self.get_notification(notification_id)
        if notification and not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(notification)
        
        return notification
    
    def mark_all_as_read(self, user_id: UUID) -> int:
        """Marcar todas las notificaciones de un usuario como leídas"""
        count = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })
        
        self.db.commit()
        return count
    
    def delete_notification(self, notification_id: UUID) -> bool:
        """Eliminar una notificación"""
        notification = self.get_notification(notification_id)
        if notification:
            self.db.delete(notification)
            self.db.commit()
            return True
        return False
    
    def get_unread_count(self, user_id: UUID) -> int:
        """Obtener cantidad de notificaciones no leídas"""
        return self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
    
    def get_stats(self, user_id: UUID) -> Dict[str, Any]:
        """Obtener estadísticas de notificaciones"""
        notifications = self.db.query(Notification).filter(
            Notification.user_id == user_id
        ).all()
        
        stats = {
            "total": len(notifications),
            "unread": sum(1 for n in notifications if not n.is_read),
            "by_type": {},
            "by_priority": {}
        }
        
        # Contar por tipo
        for notif_type in NotificationType:
            stats["by_type"][notif_type.value] = sum(
                1 for n in notifications if n.type == notif_type
            )
        
        # Contar por prioridad
        for priority in NotificationPriority:
            stats["by_priority"][priority.value] = sum(
                1 for n in notifications if n.priority == priority
            )
        
        return stats


# Funciones helper para crear notificaciones específicas

def create_loan_request_notification(
    db: Session,
    lender_id: UUID,
    borrower_name: str,
    book_title: str,
    loan_id: UUID
):
    """Crear notificación de solicitud de préstamo"""
    service = NotificationService(db)
    return service.create_notification(
        user_id=lender_id,
        notification_type=NotificationType.LOAN_REQUEST,
        title="Nueva solicitud de préstamo",
        message=f"{borrower_name} quiere pedir prestado '{book_title}'",
        priority=NotificationPriority.HIGH,
        data={"loan_id": str(loan_id), "book_title": book_title, "sender_name": borrower_name}
    )


def create_loan_approved_notification(
    db: Session,
    borrower_id: UUID,
    lender_name: str,
    book_title: str,
    loan_id: UUID
):
    """Crear notificación de préstamo aprobado"""
    service = NotificationService(db)
    return service.create_notification(
        user_id=borrower_id,
        notification_type=NotificationType.LOAN_APPROVED,
        title="¡Préstamo aprobado!",
        message=f"{lender_name} ha aprobado tu solicitud de '{book_title}'",
        priority=NotificationPriority.HIGH,
        data={"loan_id": str(loan_id), "book_title": book_title, "sender_name": lender_name}
    )


def create_loan_rejected_notification(
    db: Session,
    borrower_id: UUID,
    lender_name: str,
    book_title: str,
    loan_id: UUID
):
    """Crear notificación de préstamo rechazado"""
    service = NotificationService(db)
    return service.create_notification(
        user_id=borrower_id,
        notification_type=NotificationType.LOAN_REJECTED,
        title="Préstamo rechazado",
        message=f"{lender_name} ha rechazado tu solicitud de '{book_title}'",
        priority=NotificationPriority.MEDIUM,
        data={"loan_id": str(loan_id), "book_title": book_title, "sender_name": lender_name}
    )


def create_due_date_reminder_notification(
    db: Session,
    borrower_id: UUID,
    book_title: str,
    due_date: str,
    loan_id: UUID
):
    """Crear notificación de recordatorio de devolución"""
    service = NotificationService(db)
    return service.create_notification(
        user_id=borrower_id,
        notification_type=NotificationType.DUE_DATE_REMINDER,
        title="Recordatorio de devolución",
        message=f"Recuerda devolver '{book_title}' antes del {due_date}",
        priority=NotificationPriority.MEDIUM,
        data={"loan_id": str(loan_id), "book_title": book_title, "due_date": due_date}
    )


def create_overdue_notification(
    db: Session,
    borrower_id: UUID,
    book_title: str,
    loan_id: UUID
):
    """Crear notificación de préstamo vencido"""
    service = NotificationService(db)
    return service.create_notification(
        user_id=borrower_id,
        notification_type=NotificationType.OVERDUE,
        title="¡Préstamo vencido!",
        message=f"El préstamo de '{book_title}' está vencido. Por favor, devuélvelo pronto.",
        priority=NotificationPriority.URGENT,
        data={"loan_id": str(loan_id), "book_title": book_title}
    )
