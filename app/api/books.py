from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from uuid import UUID
from typing import List, Optional
import logging

from app.dependencies import get_current_db, optional_current_user
from app.models.book import Book as BookModel, BookStatus, BookCondition, BookGenre
from app.models.user import User
from app.models.review import Review as ReviewModel
from app.schemas.book import Book as BookSchema, BookCreate, BookUpdate, BookResponse
from app.services.auth_service import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[BookResponse])
def list_books(
    include_reviews: bool = False,
    db: Session = Depends(get_current_db)
):
    """List all available books with optional reviews and ratings."""
    logger.info("Listing all available books, include_reviews=%s", include_reviews)
    
    # Base query with eager loading of related data
    query = db.query(BookModel).options(
        joinedload(BookModel.owner),
        joinedload(BookModel.current_borrower)
    ).filter(BookModel.is_archived == False)
    
    if include_reviews:
        # Add eager loading for reviews if requested
        query = query.options(joinedload(BookModel.reviews))
    
    books = query.all()
    
    # Calculate ratings if reviews are included
    if include_reviews:
        for book in books:
            if book.reviews:
                ratings = [review.rating for review in book.reviews]
                book.average_rating = sum(ratings) / len(ratings) if ratings else None
                book.total_reviews = len(ratings)
            else:
                book.average_rating = None
                book.total_reviews = 0
    
    logger.info("Retrieved %d books", len(books))
    return books

@router.get("/{book_id}", response_model=BookResponse)
def get_book(
    book_id: UUID,
    include_reviews: bool = False,
    db: Session = Depends(get_current_db)
):
    """Get a single book by ID with optional reviews and ratings."""
    logger.info("Getting book: id=%s, include_reviews=%s", book_id, include_reviews)
    
    # Base query with eager loading
    query = db.query(BookModel).options(
        joinedload(BookModel.owner),
        joinedload(BookModel.current_borrower)
    ).filter(
        and_(BookModel.id == book_id, BookModel.is_archived == False)
    )
    
    if include_reviews:
        # Add eager loading for reviews if requested
        query = query.options(joinedload(BookModel.reviews))
    
    book = query.first()
    
    if not book:
        logger.warning("Book not found: id=%s", book_id)
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    # Calculate ratings if reviews are included
    if include_reviews and book.reviews:
        ratings = [review.rating for review in book.reviews]
        book.average_rating = sum(ratings) / len(ratings) if ratings else None
        book.total_reviews = len(ratings)
    elif include_reviews:
        book.average_rating = None
        book.total_reviews = 0
    
    return book

@router.post("/", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book(
    payload: BookCreate,
    request: Request,
    db: Session = Depends(get_current_db),
    current_user: Optional[User] = Depends(optional_current_user),
):
    """Create a new book with comprehensive validation and logging."""
    try:
        logger.info("create_book title=%s owner_id=%s auth=%s", 
                  payload.title, 
                  getattr(current_user, 'id', None), 
                  bool(current_user))
        
        # Handle owner assignment
        owner_id = current_user.id if current_user else payload.owner_id
        if owner_id is None:
            # Fallback: read from raw body if Pydantic didn't map it
            try:
                body = await request.json()
                raw_owner = body.get("owner_id")
                if raw_owner:
                    owner_id = UUID(str(raw_owner))
            except Exception as e:
                logger.warning("Failed to parse owner_id from request: %s", str(e))
                
        if owner_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Se requiere autenticación o owner_id"
            )
            
        # Validate owner exists if not current user
        if not current_user:
            owner_exists = db.query(User).filter(User.id == owner_id).first()
            if not owner_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="owner_id inválido"
                )
        
        # Check for duplicate ISBN for this owner
        if payload.isbn:
            existing_book = db.query(BookModel).filter(
                and_(
                    BookModel.isbn == payload.isbn,
                    BookModel.owner_id == owner_id,
                    BookModel.is_archived == False
                )
            ).first()
            
            if existing_book:
                logger.warning("Duplicate ISBN detected: isbn=%s owner_id=%s existing_book_id=%s", 
                             payload.isbn, owner_id, existing_book.id)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya tienes un libro con el ISBN {payload.isbn} en tu biblioteca: '{existing_book.title}'"
                )
        
        # Normalize enums if they come as strings
        g = None
        if payload.genre is not None:
            g = (payload.genre if not isinstance(payload.genre, str) 
                  else BookGenre(payload.genre))
        
        c = None
        if payload.condition is not None:
            c = (payload.condition if not isinstance(payload.condition, str) 
                  else BookCondition(payload.condition))
        else:
            c = BookCondition.good  # Default condition

        # Create book
        db_book = BookModel(
            title=payload.title,
            author=payload.author,
            isbn=payload.isbn,
            cover_url=payload.cover_url,
            description=payload.description,
            publisher=payload.publisher,
            published_date=payload.published_date,
            page_count=payload.page_count,
            language=payload.language,
            genre=g,
            condition=c,
            owner_id=owner_id,
            is_archived=getattr(payload, 'is_archived', False),
            status=BookStatus.available
        )
        
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        
        logger.info("Book created successfully: id=%s title=%s owner_id=%s", 
                   db_book.id, db_book.title, db_book.owner_id)
        return db_book
        
    except Exception as e:
        db.rollback()
        logger.exception("Error creating book: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el libro: {str(e)}"
        )

@router.put("/{book_id}", response_model=BookSchema)
async def update_book(
    book_id: UUID,
    payload: BookUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_current_db)
):
    """Update a book with comprehensive validation and logging."""
    logger.info("Updating book: id=%s user=%s", book_id, current_user.id)
    
    try:
        # Get book with eager loading
        book = db.query(BookModel).options(
            joinedload(BookModel.owner),
            joinedload(BookModel.current_borrower)
        ).filter(
            and_(BookModel.id == book_id, BookModel.is_archived == False)
        ).first()
        
        if not book:
            logger.warning("Book not found for update: id=%s", book_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Libro no encontrado"
            )
        
        # Check ownership
        if book.owner_id != current_user.id:
            logger.warning(
                "Unauthorized update attempt: book_id=%s user=%s owner=%s", 
                book_id, current_user.id, book.owner_id
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para modificar este libro"
            )
        
        # Update fields
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(book, field):
                setattr(book, field, value)
        
        db.commit()
        db.refresh(book)
        
        logger.info("Book updated successfully: id=%s", book_id)
        return book
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 403, 404) as they are
        raise
    except Exception as e:
        db.rollback()
        logger.exception("Error updating book: id=%s", book_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el libro: {str(e)}"
        )

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: UUID, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_current_db)
):
    """Soft delete a book with comprehensive logging."""
    logger.info("Deleting book (soft delete): id=%s user=%s", 
               book_id, current_user.id)
    
    try:
        book = db.query(BookModel).filter(
            and_(BookModel.id == book_id, BookModel.is_archived == False)
        ).first()
        
        if not book:
            logger.warning("Book not found for deletion: id=%s", book_id)
            raise HTTPException(status_code=404, detail="Libro no encontrado")
    
        # Check ownership
        if book.owner_id != current_user.id:
            logger.warning("Unauthorized deletion attempt: book_id=%s user=%s owner=%s",
                         book_id, current_user.id, book.owner_id)
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para eliminar este libro"
            )
    
        # Check if book is currently loaned
        if book.status == BookStatus.loaned:
            logger.warning("Attempted to delete loaned book: id=%s", book_id)
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar un libro prestado"
            )
    
        # Soft delete
        book.is_archived = True
        db.commit()
        
        logger.info("Book soft deleted successfully: id=%s title=%s", 
                   book_id, book.title)
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception("Error deleting book: id=%s", book_id)
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar el libro: {str(e)}"
        )
