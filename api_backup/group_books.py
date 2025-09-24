"""
Endpoints para bibliotecas compartidas en grupos.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
import logging
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.group_book_service import GroupBookService
from app.models.user import User
from app.schemas.group_book import (
    GroupBook, GroupBookSummary, GroupBookFilter, GroupBookStats
)
from app.models.book import BookType, BookGenre

router = APIRouter(prefix="/groups", tags=["group-books"])
logger = logging.getLogger(__name__)


@router.get("/{group_id}/books", response_model=List[GroupBookSummary])
async def get_group_books(
    group_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Búsqueda por título o autor"),
    owner_id: Optional[UUID] = Query(None, description="Filtrar por propietario"),
    book_status: Optional[str] = Query(None, description="Filtrar por estado"),
    is_available: Optional[bool] = Query(None, description="Filtrar por disponibilidad"),
    book_type: Optional[BookType] = Query(None, description="Filtrar por tipo de libro"),
    genre: Optional[BookGenre] = Query(None, description="Filtrar por género"),
    isbn: Optional[str] = Query(None, description="Filtrar por ISBN"),
    limit: int = Query(50, ge=1, le=100, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación")
):
    """Obtener libros de un grupo con filtros."""
    group_book_service = GroupBookService(db)
    
    # Crear filtros
    filters = GroupBookFilter(
        search=search,
        owner_id=owner_id,
        status=book_status,
        is_available=is_available,
        book_type=book_type,
        genre=genre,
        isbn=isbn
    )
    
    try:
        logger.debug("get_group_books called")
        logger.info(
            "group_books params group_id=%s user_id=%s search=%s owner_id=%s status=%s is_available=%s book_type=%s genre=%s isbn=%s limit=%s offset=%s",
            str(group_id), str(current_user.id), search, str(owner_id) if owner_id else None, book_status, is_available,
            getattr(book_type, "value", book_type), getattr(genre, "value", genre), isbn, limit, offset,
        )
        books = group_book_service.get_group_books(
            group_id, current_user.id, filters, limit, offset
        )
    except Exception as exc:
        logger.exception("group_books get_group_books failed: %s", exc)
        raise HTTPException(status_code=500, detail="Internal error fetching group books")
    
    if books is None:
        # Usuario no miembro o grupo inexistente
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado o no tienes acceso"
        )
    
    # Convertir a GroupBookSummary (evitar errores de serialización)
    book_summaries = []
    for book in books:
        status_value = getattr(book.status, "value", str(book.status))
        owner = book.owner
        owner_payload = {
            "id": owner.id,
            "username": owner.username,
            "email": owner.email,
            "full_name": owner.full_name,
            "avatar_url": owner.avatar_url,
        } if owner else None
        borrower = book.current_borrower
        borrower_payload = (
            {
                "id": borrower.id,
                "username": borrower.username,
                "email": borrower.email,
                "full_name": borrower.full_name,
                "avatar_url": borrower.avatar_url,
            }
            if borrower
            else None
        )
        try:
            book_summaries.append(
                GroupBookSummary(
                    id=book.id,
                    title=book.title,
                    author=book.author,
                    isbn=book.isbn,
                    cover_url=book.cover_url,
                    status=status_value,
                    owner=owner_payload,
                    is_available=book.current_borrower_id is None,
                    current_borrower=borrower_payload,
                )
            )
        except Exception as exc:
            logger.exception("Failed to serialize GroupBookSummary for book id=%s: %s", book.id, exc)
            raise
    
    return book_summaries


# NOTA: rutas específicas deben declararse antes que la ruta con {book_id}


@router.get("/{group_id}/books/stats", response_model=GroupBookStats)
async def get_group_book_stats(
    group_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de libros del grupo."""
    group_book_service = GroupBookService(db)
    
    stats = group_book_service.get_group_book_stats(group_id, current_user.id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado o no tienes acceso"
        )
    
    return stats


@router.get("/{group_id}/books/owners", response_model=List[dict])
async def get_group_book_owners(
    group_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de propietarios de libros en el grupo."""
    group_book_service = GroupBookService(db)
    
    owners = group_book_service.get_group_owners(group_id, current_user.id)
    
    if owners is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado o no tienes acceso"
        )
    
    # Convertir a diccionario simple
    return [
        {
            "id": owner.id,
            "username": owner.username,
            "full_name": owner.full_name,
            "avatar_url": owner.avatar_url
        }
        for owner in owners
    ]


@router.get("/{group_id}/books/search", response_model=List[GroupBookSummary])
async def search_group_books(
    group_id: UUID,
    q: str = Query(..., min_length=1, description="Término de búsqueda"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=50, description="Límite de resultados")
):
    """Buscar libros en el grupo."""
    group_book_service = GroupBookService(db)
    
    books = group_book_service.search_group_books(
        group_id, current_user.id, q, limit
    )
    
    if books is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado o no tienes acceso"
        )
    
    # Convertir a GroupBookSummary (evitar errores de serialización)
    book_summaries = []
    for book in books:
        status_value = getattr(book.status, "value", str(book.status))
        owner = book.owner
        owner_payload = {
            "id": owner.id,
            "username": owner.username,
            "email": owner.email,
            "full_name": owner.full_name,
            "avatar_url": owner.avatar_url,
        } if owner else None
        borrower = book.current_borrower
        borrower_payload = (
            {
                "id": borrower.id,
                "username": borrower.username,
                "email": borrower.email,
                "full_name": borrower.full_name,
                "avatar_url": borrower.avatar_url,
            }
            if borrower
            else None
        )
        try:
            book_summaries.append(
                GroupBookSummary(
                    id=book.id,
                    title=book.title,
                    author=book.author,
                    isbn=book.isbn,
                    cover_url=book.cover_url,
                    status=status_value,
                    owner=owner_payload,
                    is_available=book.current_borrower_id is None,
                    current_borrower=borrower_payload,
                )
            )
        except Exception as exc:
            logger.exception("Failed to serialize GroupBookSummary (search) for book id=%s: %s", book.id, exc)
            raise
    
    return book_summaries


@router.get("/{group_id}/books/{book_id}", response_model=GroupBook)
async def get_group_book(
    group_id: UUID,
    book_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener un libro específico del grupo."""
    group_book_service = GroupBookService(db)
    
    book = group_book_service.get_group_book(group_id, book_id, current_user.id)
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado o no tienes acceso"
        )
    
    return GroupBook(
        id=book.id,
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        cover_url=book.cover_url,
        description=book.description,
        status=book.status,
        owner_id=book.owner_id,
        current_borrower_id=book.current_borrower_id,
        is_archived=book.is_archived,
        created_at=book.created_at,
        updated_at=book.updated_at,
        owner=book.owner,
        is_available=book.current_borrower_id is None,
        current_borrower=book.current_borrower
    )
