from fastapi import APIRouter, Depends, HTTPException, status
import logging
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID

from app.dependencies import get_current_db
from app.services.loan_service import LoanService
from app.models.loan import Loan as LoanModel


router = APIRouter(prefix="/loans", tags=["loans"])
logger = logging.getLogger(__name__)


@router.post("/request", response_model=None, status_code=status.HTTP_201_CREATED)
def request_loan(book_id: UUID, borrower_id: UUID, db: Session = Depends(get_current_db)):
    svc = LoanService(db)
    loan = svc.request_loan(book_id, borrower_id)
    if not loan:
        raise HTTPException(status_code=400, detail="No se pudo solicitar el préstamo")
    return {"loan_id": str(loan.id)}


@router.post("/{loan_id}/approve", status_code=status.HTTP_200_OK)
def approve_loan(loan_id: UUID, lender_id: UUID, due_date: datetime | None = None, db: Session = Depends(get_current_db)):
    svc = LoanService(db)
    loan = svc.approve_loan(loan_id, lender_id, due_date)
    if not loan:
        raise HTTPException(status_code=400, detail="No se pudo aprobar/activar el préstamo")
    return {"loan_id": str(loan.id), "status": loan.status.name}


@router.post("/{loan_id}/reject", status_code=status.HTTP_200_OK)
def reject_loan(loan_id: UUID, lender_id: UUID, db: Session = Depends(get_current_db)):
    svc = LoanService(db)
    ok = svc.reject_loan(loan_id, lender_id)
    if not ok:
        raise HTTPException(status_code=400, detail="No se pudo rechazar el préstamo")
    return {"ok": True}


@router.post("/return", status_code=status.HTTP_200_OK)
def return_book(book_id: UUID, db: Session = Depends(get_current_db)):
    svc = LoanService(db)
    ok = svc.return_book(book_id)
    if not ok:
        raise HTTPException(status_code=400, detail="No se pudo devolver el libro")
    return {"ok": True}


@router.post("/{loan_id}/due-date", status_code=status.HTTP_200_OK)
def set_due_date(loan_id: UUID, lender_id: UUID, due_date: datetime, db: Session = Depends(get_current_db)):
    svc = LoanService(db)
    loan = svc.set_due_date(loan_id, lender_id, due_date)
    if not loan:
        raise HTTPException(status_code=400, detail="No se pudo actualizar la fecha de vencimiento")
    return {"loan_id": str(loan.id), "due_date": loan.due_date}


@router.get("/history/book/{book_id}", response_model=None)
def get_book_history(book_id: UUID, db: Session = Depends(get_current_db)):
    svc = LoanService(db)
    items = svc.get_book_history(book_id)
    return [
        {"id": str(l.id), "status": l.status.name, "requested_at": l.requested_at, "returned_at": l.returned_at}
        for l in items
    ]


# Compatibilidad con tests existentes: préstamo inmediato
@router.post("/loan", status_code=status.HTTP_200_OK)
def loan_book(book_id: UUID, borrower_id: UUID, db: Session = Depends(get_current_db)):
    svc = LoanService(db)
    # crear solicitud
    loan = svc.request_loan(book_id, borrower_id)
    if not loan:
        raise HTTPException(status_code=400, detail="No se pudo solicitar el préstamo")
    # obtener dueño del libro para aprobar
    from app.models.book import Book as BookModel
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    loan = svc.approve_loan(loan.id, book.owner_id)
    if not loan:
        raise HTTPException(status_code=400, detail="No se pudo aprobar el préstamo")
    return {"message": "Libro prestado", "book_id": str(book.id), "loan_id": str(loan.id)}


