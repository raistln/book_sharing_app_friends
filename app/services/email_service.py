"""
Servicio de emails (opcional)
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio para enviar emails (opcional, se activa con ENABLE_EMAIL_NOTIFICATIONS)"""
    
    def __init__(self):
        self.enabled = settings.ENABLE_EMAIL_NOTIFICATIONS
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
        self.from_name = settings.SMTP_FROM_NAME
        self.use_tls = settings.SMTP_USE_TLS
    
    def is_configured(self) -> bool:
        """Verifica si el servicio de email está configurado correctamente"""
        return (
            self.enabled and
            self.smtp_host is not None and
            self.smtp_user is not None and
            self.smtp_password is not None
        )
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None
    ) -> bool:
        """
        Envía un email
        
        Args:
            to_email: Email del destinatario
            subject: Asunto del email
            body_html: Cuerpo del email en HTML
            body_text: Cuerpo del email en texto plano (opcional)
        
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        if not self.is_configured():
            logger.warning("Email service is not configured or disabled")
            return False
        
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Agregar cuerpo de texto plano
            if body_text:
                part1 = MIMEText(body_text, 'plain')
                msg.attach(part1)
            
            # Agregar cuerpo HTML
            part2 = MIMEText(body_html, 'html')
            msg.attach(part2)
            
            # Conectar al servidor SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_loan_request_email(
        self,
        to_email: str,
        lender_name: str,
        borrower_name: str,
        book_title: str,
        loan_url: str
    ) -> bool:
        """Envía email de notificación de solicitud de préstamo"""
        subject = f"📚 Nueva solicitud de préstamo: {book_title}"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #5D4E37;">Nueva solicitud de préstamo</h2>
                <p>Hola <strong>{lender_name}</strong>,</p>
                <p><strong>{borrower_name}</strong> quiere pedir prestado tu libro:</p>
                <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #D4AF37; margin: 20px 0;">
                    <h3 style="margin: 0; color: #5D4E37;">{book_title}</h3>
                </div>
                <p>
                    <a href="{loan_url}" style="background-color: #5D4E37; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Ver solicitud
                    </a>
                </p>
                <p style="color: #666; font-size: 12px; margin-top: 30px;">
                    Book Sharing App - Compartiendo conocimiento
                </p>
            </body>
        </html>
        """
        
        text = f"""
        Nueva solicitud de préstamo
        
        Hola {lender_name},
        
        {borrower_name} quiere pedir prestado tu libro: {book_title}
        
        Ver solicitud: {loan_url}
        
        Book Sharing App - Compartiendo conocimiento
        """
        
        return self.send_email(to_email, subject, html, text)
    
    def send_loan_approved_email(
        self,
        to_email: str,
        borrower_name: str,
        lender_name: str,
        book_title: str,
        due_date: Optional[str] = None
    ) -> bool:
        """Envía email de notificación de préstamo aprobado"""
        subject = f"✅ Préstamo aprobado: {book_title}"
        
        due_date_text = f"<p><strong>Fecha de devolución:</strong> {due_date}</p>" if due_date else ""
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #065f46;">¡Préstamo aprobado!</h2>
                <p>Hola <strong>{borrower_name}</strong>,</p>
                <p><strong>{lender_name}</strong> ha aprobado tu solicitud de préstamo:</p>
                <div style="background-color: #d1fae5; padding: 15px; border-left: 4px solid #065f46; margin: 20px 0;">
                    <h3 style="margin: 0; color: #065f46;">{book_title}</h3>
                </div>
                {due_date_text}
                <p>¡Disfruta la lectura! 📖</p>
                <p style="color: #666; font-size: 12px; margin-top: 30px;">
                    Book Sharing App - Compartiendo conocimiento
                </p>
            </body>
        </html>
        """
        
        text = f"""
        ¡Préstamo aprobado!
        
        Hola {borrower_name},
        
        {lender_name} ha aprobado tu solicitud de préstamo: {book_title}
        
        {"Fecha de devolución: " + due_date if due_date else ""}
        
        ¡Disfruta la lectura!
        
        Book Sharing App - Compartiendo conocimiento
        """
        
        return self.send_email(to_email, subject, html, text)
    
    def send_due_date_reminder_email(
        self,
        to_email: str,
        borrower_name: str,
        book_title: str,
        due_date: str
    ) -> bool:
        """Envía email de recordatorio de fecha de devolución"""
        subject = f"⏰ Recordatorio: Devolver '{book_title}'"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #92400e;">Recordatorio de devolución</h2>
                <p>Hola <strong>{borrower_name}</strong>,</p>
                <p>Te recordamos que debes devolver el libro:</p>
                <div style="background-color: #fef3c7; padding: 15px; border-left: 4px solid #92400e; margin: 20px 0;">
                    <h3 style="margin: 0; color: #92400e;">{book_title}</h3>
                    <p style="margin: 10px 0 0 0;"><strong>Fecha límite:</strong> {due_date}</p>
                </div>
                <p>Por favor, coordina con el prestador para devolver el libro a tiempo.</p>
                <p style="color: #666; font-size: 12px; margin-top: 30px;">
                    Book Sharing App - Compartiendo conocimiento
                </p>
            </body>
        </html>
        """
        
        text = f"""
        Recordatorio de devolución
        
        Hola {borrower_name},
        
        Te recordamos que debes devolver el libro: {book_title}
        Fecha límite: {due_date}
        
        Por favor, coordina con el prestador para devolver el libro a tiempo.
        
        Book Sharing App - Compartiendo conocimiento
        """
        
        return self.send_email(to_email, subject, html, text)


# Instancia global del servicio
email_service = EmailService()
