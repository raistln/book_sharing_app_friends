"""
Configuración de APScheduler para tareas programadas
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.tasks.notification_tasks import (
    check_due_date_reminders,
    check_overdue_loans,
    cleanup_old_notifications
)

logger = logging.getLogger(__name__)

# Crear scheduler global
scheduler = BackgroundScheduler()


def start_scheduler():
    """
    Inicia el scheduler con todas las tareas programadas
    """
    if scheduler.running:
        logger.warning("Scheduler already running")
        return
    
    # Tarea 1: Verificar recordatorios de vencimiento
    # Se ejecuta todos los días a las 9:00 AM
    scheduler.add_job(
        check_due_date_reminders,
        trigger=CronTrigger(hour=9, minute=0),
        id='check_due_date_reminders',
        name='Check due date reminders',
        replace_existing=True
    )
    logger.info("Scheduled task: check_due_date_reminders (daily at 9:00 AM)")
    
    # Tarea 2: Verificar préstamos vencidos
    # Se ejecuta todos los días a las 10:00 AM
    scheduler.add_job(
        check_overdue_loans,
        trigger=CronTrigger(hour=10, minute=0),
        id='check_overdue_loans',
        name='Check overdue loans',
        replace_existing=True
    )
    logger.info("Scheduled task: check_overdue_loans (daily at 10:00 AM)")
    
    # Tarea 3: Limpiar notificaciones antiguas
    # Se ejecuta todos los domingos a las 2:00 AM
    scheduler.add_job(
        cleanup_old_notifications,
        trigger=CronTrigger(day_of_week='sun', hour=2, minute=0),
        id='cleanup_old_notifications',
        name='Cleanup old notifications',
        replace_existing=True
    )
    logger.info("Scheduled task: cleanup_old_notifications (weekly on Sunday at 2:00 AM)")
    
    # Iniciar scheduler
    scheduler.start()
    logger.info("Scheduler started successfully")


def stop_scheduler():
    """
    Detiene el scheduler
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")


def get_scheduler_status():
    """
    Obtiene el estado del scheduler y sus tareas
    """
    return {
        'running': scheduler.running,
        'jobs': [
            {
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None
            }
            for job in scheduler.get_jobs()
        ]
    }
