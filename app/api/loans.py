from fastapi import APIRouter, Depends, HTTPException, status
import logging
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from datetime import datetime
from uuid import UUID
from typing import List

from app.dependencies import get_current_db
from app.services.loan_service import LoanService
from app.models.loan import Loan as LoanModel
from app.schemas.loan import Loan as LoanSchema


router = APIRouter(prefix="/loans", tags=["loans"])
logger = logging.getLogger(__name__)


@router.post("/request", response_model=None, status_code=status.HTTP_201_CREATED)
def request_loan(book_id: UUID, borrower_id: UUID, db: Session = Depends(get_current_db)):
    """Request a loan for a book with comprehensive logging."""
    logger.info("Requesting loan: book_id=%s borrower_id=%s", book_id, borrower_id)
    
    svc = LoanService(db)
    loan = svc.request_loan(book_id, borrower_id)
    
    if not loan:
        logger.warning("Failed to request loan: book_id=%s borrower_id=%s", book_id, borrower_id)
        raise HTTPException(status_code=400, detail="No se pudo solicitar el préstamo")
    
    logger.info("Loan requested successfully: loan_id=%s", loan.id)
    return {"loan_id": str(loan.id)}


@router.post("/{loan_id}/approve", status_code=status.HTTP_200_OK)
def approve_loan(loan_id: UUID, lender_id: UUID, due_date: datetime | None = None, db: Session = Depends(get_current_db)):
    """Approve a loan request with comprehensive logging."""
    logger.info("Approving loan: loan_id=%s lender_id=%s due_date=%s", loan_id, lender_id, due_date)
    
    svc = LoanService(db)
    loan = svc.approve_loan(loan_id, lender_id, due_date)
    
    if not loan:
        logger.warning("Failed to approve loan: loan_id=%s lender_id=%s", loan_id, lender_id)
        raise HTTPException(status_code=400, detail="No se pudo aprobar/activar el préstamo")
    
    logger.info("Loan approved successfully: loan_id=%s status=%s", loan.id, loan.status.name)
    return {"loan_id": str(loan.id), "status": loan.status.name}


@router.post("/{loan_id}/reject", status_code=status.HTTP_200_OK)
def reject_loan(loan_id: UUID, lender_id: UUID, db: Session = Depends(get_current_db)):
    """Reject a loan request with comprehensive logging."""
    logger.info("Rejecting loan: loan_id=%s lender_id=%s", loan_id, lender_id)
    
    svc = LoanService(db)
    ok = svc.reject_loan(loan_id, lender_id)
    
    if not ok:
        logger.warning("Failed to reject loan: loan_id=%s lender_id=%s", loan_id, lender_id)
        raise HTTPException(status_code=400, detail="No se pudo rechazar el préstamo")
    
    logger.info("Loan rejected successfully: loan_id=%s", loan_id)
    return {"ok": True}


@router.post("/return", status_code=status.HTTP_200_OK)
def return_book(book_id: UUID, db: Session = Depends(get_current_db)):
    """Return a loaned book with comprehensive logging."""
    logger.info("Returning book: book_id=%s", book_id)
    
    svc = LoanService(db)
    ok = svc.return_book(book_id)
    
    if not ok:
        logger.warning("Failed to return book: book_id=%s", book_id)
        raise HTTPException(status_code=400, detail="No se pudo devolver el libro")
    
    logger.info("Book returned successfully: book_id=%s", book_id)
    return {"message": "Libro devuelto exitosamente"}


@router.post("/{loan_id}/due-date", status_code=status.HTTP_200_OK)
def set_due_date(loan_id: UUID, lender_id: UUID, due_date: datetime, db: Session = Depends(get_current_db)):
    """Set due date for a loan with comprehensive logging."""
    logger.info("Setting due date: loan_id=%s lender_id=%s due_date=%s", loan_id, lender_id, due_date)
    
    svc = LoanService(db)
    loan = svc.set_due_date(loan_id, lender_id, due_date)
    
    if not loan:
        logger.warning("Failed to set due date: loan_id=%s lender_id=%s", loan_id, lender_id)
        raise HTTPException(status_code=400, detail="No se pudo actualizar la fecha de vencimiento")
    
    logger.info("Due date set successfully: loan_id=%s due_date=%s", loan.id, loan.due_date)
    return {"loan_id": str(loan.id), "due_date": loan.due_date}


@router.get("/", response_model=List[dict])
def list_user_loans(db: Session = Depends(get_current_db), user_id: UUID = None):
    """List loans for a user with optimized query to prevent N+1 problems."""
    logger.info("Listing loans for user: user_id=%s", user_id)
    
    from app.models.book import Book as BookModel
    
    query = db.query(LoanModel).options(
        joinedload(LoanModel.book).joinedload(BookModel.owner),
        joinedload(LoanModel.borrower),
        joinedload(LoanModel.lender)
    )
    
    if user_id:
        query = query.filter(
            (LoanModel.borrower_id == user_id) | (LoanModel.lender_id == user_id)
        )
    
    loans = query.order_by(LoanModel.requested_at.desc()).all()
    
    logger.info("Retrieved %d loans for user %s", len(loans), user_id)
    
    return [
        {
            "id": str(loan.id),
            "book": {
                "id": str(loan.book.id),
                "title": loan.book.title,
                "author": loan.book.author
            },
            "borrower": {
                "id": str(loan.borrower.id),
                "username": loan.borrower.username
            } if loan.borrower else None,
            "lender": {
                "id": str(loan.lender.id),
                "username": loan.lender.username
            } if loan.lender else None,
            "status": loan.status.name,
            "requested_at": loan.requested_at,
            "approved_at": loan.approved_at,
            "returned_at": loan.returned_at,
            "due_date": loan.due_date
        }
        for loan in loans
    ]


@router.get("/history/book/{book_id}", response_model=None)
def get_book_history(book_id: UUID, db: Session = Depends(get_current_db)):
    """Get loan history for a specific book with optimized query."""
    logger.info("Getting loan history for book: book_id=%s", book_id)
    
    # Optimized query with eager loading
    loans = db.query(LoanModel).options(
        joinedload(LoanModel.borrower),
        joinedload(LoanModel.lender),
        joinedload(LoanModel.book)
    ).filter(LoanModel.book_id == book_id).order_by(LoanModel.requested_at.desc()).all()
    
    logger.info("Retrieved %d loan records for book %s", len(loans), book_id)
    
    return [
        {
            "id": str(l.id),
            "status": l.status.name,
            "requested_at": l.requested_at,
            "approved_at": l.approved_at,
            "returned_at": l.returned_at,
            "due_date": l.due_date,
            "borrower": {"id": str(l.borrower.id), "username": l.borrower.username} if l.borrower else None,
            "lender": {"id": str(l.lender.id), "username": l.lender.username} if l.lender else None
        }
        for l in loans
    ]


# Compatibilidad con tests existentes: préstamo inmediato
@router.post("/loan", status_code=status.HTTP_201_CREATED)
def loan_book(book_id: UUID, borrower_id: UUID, db: Session = Depends(get_current_db)):
    """Immediate loan (request + approve) for compatibility with existing tests."""
    logger.info("Processing immediate loan: book_id=%s borrower_id=%s", book_id, borrower_id)
    
    svc = LoanService(db)
    
    # crear solicitud
    loan = svc.request_loan(book_id, borrower_id)
    if not loan:
        logger.warning("Failed to create loan request: book_id=%s borrower_id=%s", book_id, borrower_id)
        raise HTTPException(status_code=400, detail="No se pudo solicitar el préstamo")
    
    # obtener dueño del libro para aprobar
    from app.models.book import Book as BookModel
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        logger.error("Book not found for loan: book_id=%s", book_id)
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    loan = svc.approve_loan(loan.id, book.owner_id)
    if not loan:
        logger.warning("Failed to approve loan: loan_id=%s owner_id=%s", loan.id, book.owner_id)
        raise HTTPException(status_code=400, detail="No se pudo aprobar el préstamo")
    
    logger.info("Immediate loan completed successfully: book_id=%s loan_id=%s", book_id, loan.id)
    return {"message": "Libro prestado", "book_id": str(book.id), "loan_id": str(loan.id)}


