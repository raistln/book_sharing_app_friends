"""
Servicio de préstamos (LoanService): solicitud, aprobación/rechazo,
activación, devolución, fechas de vencimiento e historial.
"""
from __future__ import annotations

from typing import List, Optional
from datetime import datetime, timedelta, timezone
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.book import Book as BookModel, BookStatus
from app.models.loan import Loan as LoanModel, LoanStatus
from app.models.user import User
from app.services.email_service import email_service


logger = logging.getLogger(__name__)


class LoanService:
    def __init__(self, db: Session):
        self.db = db

    def request_loan(self, book_id, borrower_id) -> Optional[LoanModel]:
        book = self.db.query(BookModel).filter(
            and_(BookModel.id == book_id, BookModel.is_archived == False)
        ).first()
        if not book:
            return None
        # Si está prestado, no se puede solicitar
        if book.status == BookStatus.loaned:
            return None
        # Evitar solicitudes duplicadas activas para mismo libro/borrower
        existing = self.db.query(LoanModel).filter(
            and_(
                LoanModel.book_id == book_id,
                LoanModel.borrower_id == borrower_id,
                LoanModel.status.in_([LoanStatus.requested, LoanStatus.approved, LoanStatus.active]),
            )
        ).first()
        if existing:
            if existing.status == LoanStatus.requested:
                logger.info("request_loan returning existing pending loan loan_id=%s", str(existing.id))
                return existing
            return None
        loan = LoanModel(
            book_id=book.id,
            borrower_id=borrower_id,
            lender_id=book.owner_id,
            status=LoanStatus.requested,
        )
        self.db.add(loan)
        self.db.commit()
        self.db.refresh(loan)
        logger.info("request_loan created loan_id=%s", str(loan.id))
        
        # Crear notificación para el prestador
        try:
            borrower = self.db.query(User).filter(User.id == borrower_id).first()
            lender = self.db.query(User).filter(User.id == book.owner_id).first()
            
            if borrower and lender:
                logger.info("Loan request notifications disabled; skipping for loan_id=%s", str(loan.id))
                
                # Enviar email si está configurado
                if email_service.is_configured() and lender.email:
                    loan_url = f"http://localhost:3000/loans/{loan.id}"  # TODO: Use proper frontend URL
                    email_service.send_loan_request_email(
                        to_email=lender.email,
                        lender_name=lender.username,
                        borrower_name=borrower.username,
                        book_title=book.title,
                        loan_url=loan_url
                    )
                    logger.info("Email sent for loan request: loan_id=%s", str(loan.id))
        except Exception as e:
            logger.error("Failed to process loan request hooks: %s", str(e))
        
        return loan

    def approve_loan(self, loan_id, lender_id, due_date: Optional[datetime] = None) -> Optional[LoanModel]:
        loan = self.db.query(LoanModel).filter(LoanModel.id == loan_id).first()
        if not loan:
            return None
        # Solo el dueño del libro (lender) puede aprobar
        if loan.lender_id != lender_id:
            return None
        if loan.status not in [LoanStatus.requested, LoanStatus.approved]:
            return None
        # Marcar como active y actualizar libro
        loan.status = LoanStatus.active
        loan.approved_at = datetime.now(timezone.utc)
        if due_date is not None:
            loan.due_date = due_date
        book = self.db.query(BookModel).filter(BookModel.id == loan.book_id).first()
        if not book or book.status == BookStatus.loaned:
            return None
        book.status = BookStatus.loaned
        book.current_borrower_id = loan.borrower_id
        self.db.commit()
        self.db.refresh(loan)
        
        # Crear notificación para el prestatario
        try:
            lender = self.db.query(User).filter(User.id == lender_id).first()
            borrower = self.db.query(User).filter(User.id == loan.borrower_id).first()
            
            if lender and borrower:
                logger.info("Loan approval notifications disabled; skipping for loan_id=%s", str(loan.id))
                
                # Enviar email si está configurado
                if email_service.is_configured() and borrower.email:
                    due_date_str = loan.due_date.strftime('%d/%m/%Y') if loan.due_date else None
                    email_service.send_loan_approved_email(
                        to_email=borrower.email,
                        borrower_name=borrower.username,
                        lender_name=lender.username,
                        book_title=book.title,
                        due_date=due_date_str
                    )
                    logger.info("Email sent for loan approval: loan_id=%s", str(loan.id))
        except Exception as e:
            logger.error("Failed to process loan approval hooks: %s", str(e))
        
        return loan

    def reject_loan(self, loan_id, lender_id) -> bool:
        loan = self.db.query(LoanModel).filter(LoanModel.id == loan_id).first()
        if not loan:
            return False
        if loan.lender_id != lender_id:
            return False
        if loan.status not in [LoanStatus.requested, LoanStatus.approved]:
            return False
        
        # Crear notificación antes de eliminar el préstamo
        try:
            lender = self.db.query(User).filter(User.id == lender_id).first()
            book = self.db.query(BookModel).filter(BookModel.id == loan.book_id).first()
            if lender and book:
                logger.info("Loan rejection notifications disabled; skipping for loan_id=%s", str(loan.id))
        except Exception as e:
            logger.error("Failed to process loan rejection hooks: %s", str(e))
        
        # Rechazo: eliminamos la solicitud para no requerir nuevo estado en enum
        self.db.delete(loan)
        self.db.commit()
        return True

    def return_book(self, book_id) -> bool:
        book = self.db.query(BookModel).filter(BookModel.id == book_id).first()
        if not book:
            return False
        if book.status != BookStatus.loaned:
            return False
        loan = self.db.query(LoanModel).filter(
            and_(LoanModel.book_id == book.id, LoanModel.status == LoanStatus.active)
        ).first()
        if loan:
            loan.status = LoanStatus.returned
            loan.returned_at = datetime.now(timezone.utc)
        book.status = BookStatus.available
        book.current_borrower_id = None
        self.db.commit()
        return True

    def set_due_date(self, loan_id, lender_id, due_date: datetime) -> Optional[LoanModel]:
        loan = self.db.query(LoanModel).filter(LoanModel.id == loan_id).first()
        if not loan:
            return None
        if loan.lender_id != lender_id:
            return None
        if loan.status not in [LoanStatus.approved, LoanStatus.active]:
            return None
        loan.due_date = due_date
        self.db.commit()
        self.db.refresh(loan)
        return loan

    def get_user_loans(self, user_id) -> List[LoanModel]:
        return self.db.query(LoanModel).filter(
            (LoanModel.borrower_id == user_id) | (LoanModel.lender_id == user_id)
        ).order_by(LoanModel.requested_at.desc()).all()

    def get_book_history(self, book_id) -> List[LoanModel]:
        return self.db.query(LoanModel).filter(LoanModel.book_id == book_id).order_by(LoanModel.requested_at.desc()).all()


