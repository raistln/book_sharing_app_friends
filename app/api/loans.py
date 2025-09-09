from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID

from app.dependencies import get_current_db
from app.models.book import Book as BookModel, BookStatus
from app.models.loan import Loan as LoanModel, LoanStatus


router = APIRouter()


@router.post("/loan", status_code=status.HTTP_200_OK)
def loan_book(book_id: UUID, borrower_id: UUID, db: Session = Depends(get_current_db)):
    book = db.query(BookModel).filter(BookModel.id == book_id, BookModel.is_archived == False).first()
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    if book.status == BookStatus.loaned:
        raise HTTPException(status_code=400, detail="El libro ya está prestado")

    # Crear préstamo activo
    loan = LoanModel(
        book_id=book.id,
        borrower_id=borrower_id,
        lender_id=book.owner_id,
        status=LoanStatus.active,
        approved_at=datetime.utcnow(),
    )
    db.add(loan)

    # Actualizar libro a prestado y asignar current_borrower
    book.status = BookStatus.loaned
    book.current_borrower_id = borrower_id

    db.commit()
    return {"message": "Libro prestado", "book_id": str(book.id), "loan_id": str(loan.id)}


@router.post("/return", status_code=status.HTTP_200_OK)
def return_book(book_id: UUID, db: Session = Depends(get_current_db)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    if book.status != BookStatus.loaned:
        raise HTTPException(status_code=400, detail="El libro no está prestado")

    # Buscar préstamo activo
    loan = db.query(LoanModel).filter(LoanModel.book_id == book.id, LoanModel.status == LoanStatus.active).first()
    if loan:
        loan.status = LoanStatus.returned
        loan.returned_at = datetime.utcnow()

    # Actualizar libro a available
    book.status = BookStatus.available
    book.current_borrower_id = None

    db.commit()
    return {"message": "Libro devuelto", "book_id": str(book.id)}


