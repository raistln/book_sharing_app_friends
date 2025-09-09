from fastapi import APIRouter, Depends, HTTPException, status
import logging
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.dependencies import get_current_db
from app.models.book import Book as BookModel, BookStatus
from app.schemas.book import Book as BookSchema, BookCreate, BookUpdate


router = APIRouter()


@router.post("/", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
def create_book(payload: BookCreate, db: Session = Depends(get_current_db)):
    try:
        db_book = BookModel(
            title=payload.title,
            author=payload.author,
            isbn=payload.isbn,
            cover_url=payload.cover_url,
            description=payload.description,
            owner_id=payload.owner_id,
            current_borrower_id=payload.current_borrower_id,
        )
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book
    except Exception as exc:
        logging.exception("Error creando libro")
        raise HTTPException(status_code=500, detail=f"Error al crear libro: {exc}")


@router.get("/", response_model=List[BookSchema])
def list_books(db: Session = Depends(get_current_db)):
    return db.query(BookModel).filter(BookModel.is_archived == False).all()


@router.get("/{book_id}", response_model=BookSchema)
def get_book(book_id: UUID, db: Session = Depends(get_current_db)):
    book = db.query(BookModel).filter(BookModel.id == book_id, BookModel.is_archived == False).first()
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return book


@router.put("/{book_id}", response_model=BookSchema)
def update_book(book_id: UUID, payload: BookUpdate, db: Session = Depends(get_current_db)):
    book = db.query(BookModel).filter(BookModel.id == book_id, BookModel.is_archived == False).first()
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    update_data = payload.dict(exclude_unset=True)
    # Validación simple de status
    status_value = update_data.get("status")
    if status_value is not None and status_value not in {e.name for e in BookStatus}:
        raise HTTPException(status_code=400, detail="Estado inválido")

    for field, value in update_data.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: UUID, db: Session = Depends(get_current_db)):
    book = db.query(BookModel).filter(BookModel.id == book_id, BookModel.is_archived == False).first()
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    book.is_archived = True
    db.commit()
    return None


