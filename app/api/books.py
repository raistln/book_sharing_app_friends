from fastapi import APIRouter, Depends, HTTPException, status, Request
import logging
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.dependencies import get_current_db, require_user, optional_current_user
from typing import Optional
from app.models.user import User
from app.models.book import Book as BookModel, BookStatus, BookType, BookGenre
from app.schemas.book import Book as BookSchema, BookCreate, BookUpdate


router = APIRouter()


@router.post("/", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book(
    payload: BookCreate,
    request: Request,
    db: Session = Depends(get_current_db),
    current_user: Optional[User] = Depends(optional_current_user),
):
    try:
        logging.info("create_book title=%s owner_id=%s auth=%s", payload.title, getattr(current_user, 'id', None), bool(current_user))
        # Normalizar enums si vienen como string
        bt = None
        if payload.book_type is not None:
            bt = payload.book_type if not isinstance(payload.book_type, str) else BookType(payload.book_type)
        g = None
        if payload.genre is not None:
            g = payload.genre if not isinstance(payload.genre, str) else BookGenre(payload.genre)

        owner_id = current_user.id if current_user else payload.owner_id
        if owner_id is None:
            # Fallback: leer del cuerpo crudo por si Pydantic no lo mapeó
            try:
                body = await request.json()
                raw_owner = body.get("owner_id")
            except Exception:
                raw_owner = None
            if raw_owner:
                from uuid import UUID as _UUID
                try:
                    owner_id = _UUID(str(raw_owner))
                except Exception:
                    owner_id = None
        if owner_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        # Validar que el owner exista si viene por payload sin auth
        if not current_user:
            from app.models.user import User as UserModel
            exists = db.query(UserModel).filter(UserModel.id == owner_id).first()
            if not exists:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="owner_id inválido")

        db_book = BookModel(
            title=payload.title,
            author=payload.author,
            isbn=payload.isbn,
            cover_url=payload.cover_url,
            description=payload.description,
            book_type=bt,
            genre=g,
            owner_id=owner_id,
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


