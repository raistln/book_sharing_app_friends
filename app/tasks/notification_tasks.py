"""
Tareas programadas para notificaciones automáticas
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.loan import Loan, LoanStatus
from app.services.notification_service import (
    create_due_date_reminder_notification,
    create_overdue_notification
)

logger = logging.getLogger(__name__)


def check_due_date_reminders():
    """
    Verifica préstamos que están próximos a vencer (3 días antes)
    y crea notificaciones de recordatorio
    """
    db: Session = SessionLocal()
    try:
        logger.info("Running due date reminder check...")
        
        # Fecha de hoy y dentro de 3 días
        today = datetime.utcnow().date()
        three_days_later = today + timedelta(days=3)
        
        # Buscar préstamos activos que vencen en 3 días
        loans = db.query(Loan).filter(
            Loan.status == LoanStatus.active,
            Loan.due_date.isnot(None),
            Loan.due_date >= today,
            Loan.due_date <= three_days_later
        ).all()
        
        count = 0
        for loan in loans:
            try:
                # Verificar si ya se envió recordatorio hoy
                # (evitar spam si la tarea se ejecuta varias veces al día)
                from app.models.notification import Notification, NotificationType
                existing = db.query(Notification).filter(
                    Notification.user_id == loan.borrower_id,
                    Notification.type == NotificationType.DUE_DATE_REMINDER,
                    Notification.data['loan_id'].astext == str(loan.id),
                    Notification.created_at >= today
                ).first()
                
                if not existing:
                    create_due_date_reminder_notification(
                        db=db,
                        borrower_id=loan.borrower_id,
                        book_title=loan.book.title,
                        due_date=loan.due_date.strftime('%d/%m/%Y'),
                        loan_id=loan.id
                    )
                    count += 1
                    logger.info(f"Reminder notification created for loan {loan.id}")
            except Exception as e:
                logger.error(f"Error creating reminder for loan {loan.id}: {str(e)}")
        
        logger.info(f"Due date reminder check completed. Created {count} notifications.")
        
    except Exception as e:
        logger.error(f"Error in due date reminder check: {str(e)}")
    finally:
        db.close()


def check_overdue_loans():
    """
    Verifica préstamos vencidos y crea notificaciones urgentes
    """
    db: Session = SessionLocal()
    try:
        logger.info("Running overdue loans check...")
        
        today = datetime.utcnow().date()
        
        # Buscar préstamos activos que ya vencieron
        loans = db.query(Loan).filter(
            Loan.status == LoanStatus.active,
            Loan.due_date.isnot(None),
            Loan.due_date < today
        ).all()
        
        count = 0
        for loan in loans:
            try:
                # Verificar si ya se envió notificación de vencimiento hoy
                from app.models.notification import Notification, NotificationType
                existing = db.query(Notification).filter(
                    Notification.user_id == loan.borrower_id,
                    Notification.type == NotificationType.OVERDUE,
                    Notification.data['loan_id'].astext == str(loan.id),
                    Notification.created_at >= today
                ).first()
                
                if not existing:
                    create_overdue_notification(
                        db=db,
                        borrower_id=loan.borrower_id,
                        book_title=loan.book.title,
                        loan_id=loan.id
                    )
                    count += 1
                    logger.info(f"Overdue notification created for loan {loan.id}")
            except Exception as e:
                logger.error(f"Error creating overdue notification for loan {loan.id}: {str(e)}")
        
        logger.info(f"Overdue loans check completed. Created {count} notifications.")
        
    except Exception as e:
        logger.error(f"Error in overdue loans check: {str(e)}")
    finally:
        db.close()


def cleanup_old_notifications():
    """
    Limpia notificaciones leídas más antiguas de 30 días
    para mantener la base de datos limpia
    """
    db: Session = SessionLocal()
    try:
        logger.info("Running notification cleanup...")
        
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        from app.models.notification import Notification
        deleted = db.query(Notification).filter(
            Notification.is_read == True,
            Notification.created_at < thirty_days_ago
        ).delete()
        
        db.commit()
        logger.info(f"Notification cleanup completed. Deleted {deleted} old notifications.")
        
    except Exception as e:
        logger.error(f"Error in notification cleanup: {str(e)}")
        db.rollback()
    finally:
        db.close()
