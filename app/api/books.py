from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from uuid import UUID
from typing import List, Optional
import logging

from app.dependencies import get_current_db, optional_current_user
from app.models.book import Book as BookModel, BookStatus, BookType, BookGenre
from app.models.user import User
from app.schemas.book import Book as BookSchema, BookCreate, BookUpdate
from app.services.auth_service import get_current_user


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book(
    payload: BookCreate,
    request: Request,
    db: Session = Depends(get_current_db),
    current_user: Optional[User] = Depends(optional_current_user),
):
    try:
        logger.info("create_book title=%s owner_id=%s auth=%s", payload.title, getattr(current_user, 'id', None), bool(current_user))
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
            is_archived=payload.is_archived if hasattr(payload, 'is_archived') else False,
        )
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        logger.info("Book created successfully: id=%s title=%s owner_id=%s", db_book.id, db_book.title, db_book.owner_id)
        return db_book
    except Exception as exc:
        logger.exception("Error creating book: title=%s owner_id=%s", payload.title, owner_id)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear libro: {exc}")


@router.get("/", response_model=List[BookSchema])
def list_books(db: Session = Depends(get_current_db)):
    """List all available books with optimized query to prevent N+1 problems."""
    logger.info("Listing all available books")
    
    # Optimized query with eager loading of related data
    books = db.query(BookModel).options(
        joinedload(BookModel.owner),
        joinedload(BookModel.current_borrower)
    ).filter(BookModel.is_archived == False).all()
    
    logger.info("Retrieved %d books", len(books))
    return books


@router.get("/{book_id}", response_model=BookSchema)
def get_book(book_id: UUID, db: Session = Depends(get_current_db)):
    """Get a specific book by ID with optimized query."""
    logger.info("Getting book: id=%s", book_id)
    
    # Optimized query with eager loading
    book = db.query(BookModel).options(
        joinedload(BookModel.owner),
        joinedload(BookModel.current_borrower)
    ).filter(
        and_(BookModel.id == book_id, BookModel.is_archived == False)
    ).first()
    
    if not book:
        logger.warning("Book not found: id=%s", book_id)
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    logger.info("Book retrieved successfully: id=%s title=%s", book.id, book.title)
    return book


@router.put("/{book_id}", response_model=BookSchema)
async def update_book(book_id: UUID, payload: BookUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_current_db)):
    """Update a book with comprehensive logging and validation."""
    logger.info("Updating book: id=%s user=%s", book_id, current_user.id)
    
    book = db.query(BookModel).filter(
        and_(BookModel.id == book_id, BookModel.is_archived == False)
    ).first()
    
    if not book:
        logger.warning("Book not found for update: id=%s", book_id)
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    # Check ownership
    if book.owner_id != current_user.id:
        logger.warning("Unauthorized book update attempt: book_id=%s user=%s owner=%s", book_id, current_user.id, book.owner_id)
        raise HTTPException(status_code=403, detail="No tienes permisos para modificar este libro")

    update_data = payload.dict(exclude_unset=True)
    logger.info("Update data for book %s: %s", book_id, update_data)
    
    # Validación simple de status
    status_value = update_data.get("status")
    if status_value is not None and status_value not in {e.name for e in BookStatus}:
        logger.error("Invalid status for book %s: %s", book_id, status_value)
        raise HTTPException(status_code=400, detail="Estado inválido")

    try:
        for field, value in update_data.items():
            old_value = getattr(book, field, None)
            setattr(book, field, value)
            logger.debug("Updated field %s: %s -> %s", field, old_value, value)

        db.commit()
        db.refresh(book)
        logger.info("Book updated successfully: id=%s", book_id)
        return book
    except Exception as exc:
        logger.exception("Error updating book: id=%s", book_id)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar libro: {exc}")


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_current_db)):
    """Soft delete a book with comprehensive logging."""
    logger.info("Deleting book (soft delete): id=%s user=%s", book_id, current_user.id)
    
    book = db.query(BookModel).filter(
        and_(BookModel.id == book_id, BookModel.is_archived == False)
    ).first()
    
    if not book:
        logger.warning("Book not found for deletion: id=%s", book_id)
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    # Check ownership
    if book.owner_id != current_user.id:
        logger.warning("Unauthorized book deletion attempt: book_id=%s user=%s owner=%s", book_id, current_user.id, book.owner_id)
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar este libro")

    # Check if book is currently loaned
    if book.status == BookStatus.loaned:
        logger.warning("Attempted to delete loaned book: id=%s", book_id)
        raise HTTPException(status_code=400, detail="No se puede eliminar un libro prestado")

    try:
        book.is_archived = True
        db.commit()
        logger.info("Book soft deleted successfully: id=%s title=%s", book_id, book.title)
        return None
    except Exception as exc:
        logger.exception("Error deleting book: id=%s", book_id)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar libro: {exc}")


