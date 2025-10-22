"""
Endpoints para bibliotecas compartidas en grupos.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from app.schemas.error import ErrorResponse
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
from app.models.book import BookGenre

router = APIRouter(prefix="/groups", tags=["group-books"])
logger = logging.getLogger(__name__)


@router.get(
    "/{group_id}/books",
    response_model=List[GroupBookSummary],
    status_code=status.HTTP_200_OK,
    summary="Obtener libros del grupo con filtros",
    description="""
    Obtiene una lista paginada de libros pertenecientes a un grupo específico con capacidad de filtrado avanzado.
    
    Permite filtrar por:
    - Título o autor mediante búsqueda de texto
    - Propietario del libro
    - Estado del libro (disponible, prestado, etc.)
    - Tipo de libro (físico, digital, audiolibro)
    - Género literario
    - ISBN
    
    La respuesta incluye metadatos del libro y su disponibilidad actual.
    """,
    responses={
        200: {
            "description": "Lista de libros del grupo que coinciden con los filtros",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "title": "Cien años de soledad",
                            "author": "Gabriel García Márquez",
                            "isbn": "9780307474728",
                            "cover_url": "https://example.com/covers/cien-anos-soledad.jpg",
                            "status": "available",
                            "owner": {
                                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "username": "usuario1",
                                "email": "usuario1@example.com",
                                "full_name": "Usuario Uno",
                                "avatar_url": "https://example.com/avatars/usuario1.jpg"
                            },
                            "is_available": True,
                            "current_borrower": None
                        }
                    ]
                }
            }
        },
        403: {
            "description": "No autorizado para acceder a este grupo",
            "model": ErrorResponse
        },
        404: {
            "description": "Grupo no encontrado o usuario no es miembro",
            "model": ErrorResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": ErrorResponse
        }
    }
)
async def get_group_books(
    group_id: UUID = Path(..., description="ID único del grupo"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Búsqueda por título o autor"),
    owner_id: Optional[UUID] = Query(None, description="Filtrar por ID del propietario del libro"),
    book_status: Optional[str] = Query(None, description="Filtrar por estado del libro (disponible, prestado, etc.)"),
    is_available: Optional[bool] = Query(None, description="Filtrar solo por disponibilidad (true = disponible, false = prestado)"),
    genre: Optional[BookGenre] = Query(None, description="Filtrar por género literario"),
    isbn: Optional[str] = Query(None, description="Filtrar por ISBN (10 o 13 dígitos)"),
    limit: int = Query(50, ge=1, le=100, description="Número máximo de resultados por página (1-100)"),
    offset: int = Query(0, ge=0, description="Número de resultados a omitir (para paginación)")
):
    """
    Obtiene libros de un grupo con capacidades avanzadas de filtrado y paginación.
    
    Solo los miembros del grupo pueden ver los libros. Los filtros se pueden combinar
    para realizar búsquedas más específicas.
    """
    group_book_service = GroupBookService(db)
    
    # Crear filtros
    filters = GroupBookFilter(
        search=search,
        owner_id=owner_id,
        status=book_status,
        is_available=is_available,
        genre=genre,
        isbn=isbn
    )
    
    try:
        logger.debug("get_group_books called")
        logger.info(
            "group_books params group_id=%s user_id=%s search=%s owner_id=%s status=%s is_available=%s genre=%s isbn=%s limit=%s offset=%s",
            str(group_id), str(current_user.id), search, str(owner_id) if owner_id else None, book_status, is_available,
            getattr(genre, "value", genre), isbn, limit, offset,
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


@router.get(
    "/{group_id}/books/stats",
    response_model=GroupBookStats,
    status_code=status.HTTP_200_OK,
    summary="Obtener estadísticas de libros del grupo",
    description="""
    Obtiene estadísticas detalladas sobre los libros en un grupo específico.
    
    Incluye:
    - Total de libros en el grupo
    - Libros disponibles para préstamo
    - Libros actualmente prestados
    - Distribución por género literario
    - Distribución por tipo de libro
    
    Solo los miembros del grupo pueden ver estas estadísticas.
    """,
    responses={
        200: {
            "description": "Estadísticas detalladas de los libros del grupo",
            "content": {
                "application/json": {
                    "example": {
                        "total_books": 42,
                        "available_books": 25,
                        "borrowed_books": 17,
                        "by_genre": [
                            {"genre": "fiction", "count": 15},
                            {"genre": "non_fiction", "count": 27}
                        ],
                        "by_type": [
                            {"type": "physical", "count": 35},
                            {"type": "ebook", "count": 7}
                        ]
                    }
                }
            }
        },
        403: {
            "description": "No autorizado para acceder a este grupo",
            "model": ErrorResponse
        },
        404: {
            "description": "Grupo no encontrado o usuario no es miembro",
            "model": ErrorResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": ErrorResponse
        }
    }
)
async def get_group_book_stats(
    group_id: UUID = Path(..., description="ID único del grupo"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene métricas y estadísticas sobre los libros en un grupo.
    
    Solo los miembros del grupo pueden ver estas estadísticas.
    """
    group_book_service = GroupBookService(db)
    
    stats = group_book_service.get_group_book_stats(group_id, current_user.id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado o no tienes acceso"
        )
    
    return stats


@router.get(
    "/{group_id}/books/owners",
    response_model=List[dict],
    status_code=status.HTTP_200_OK,
    summary="Obtener lista de propietarios de libros",
    description="""
    Obtiene una lista de todos los usuarios que son propietarios de libros en el grupo.
    
    Para cada propietario se incluye:
    - ID del usuario
    - Nombre de usuario
    - Nombre completo
    - URL del avatar (si está disponible)
    
    Útil para crear filtros de búsqueda o mostrar información de propietarios.
    """,
    responses={
        200: {
            "description": "Lista de propietarios de libros en el grupo",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "username": "usuario1",
                            "full_name": "Usuario Uno",
                            "avatar_url": "https://example.com/avatars/usuario1.jpg"
                        },
                        {
                            "id": "4fb85f64-5717-4562-b3fc-2c963f66afa7",
                            "username": "usuario2",
                            "full_name": "Usuario Dos",
                            "avatar_url": "https://example.com/avatars/usuario2.jpg"
                        }
                    ]
                }
            }
        },
        403: {
            "description": "No autorizado para acceder a este grupo",
            "model": ErrorResponse
        },
        404: {
            "description": "Grupo no encontrado o usuario no es miembro",
            "model": ErrorResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": ErrorResponse
        }
    }
)
async def get_group_book_owners(
    group_id: UUID = Path(..., description="ID único del grupo"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene una lista de usuarios que son propietarios de libros en el grupo.
    
    Solo los miembros del grupo pueden ver la lista de propietarios.
    """
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


@router.get(
    "/{group_id}/books/search",
    response_model=List[GroupBookSummary],
    status_code=status.HTTP_200_OK,
    summary="Buscar libros en el grupo",
    description="""
    Realiza una búsqueda de libros dentro de un grupo específico.
    
    La búsqueda se realiza sobre:
    - Título del libro
    - Nombre del autor
    - Descripción del libro
    
    Los resultados incluyen información básica del libro y su disponibilidad actual.
    """,
    responses={
        200: {
            "description": "Lista de libros que coinciden con el término de búsqueda",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "title": "Cien años de soledad",
                            "author": "Gabriel García Márquez",
                            "isbn": "9780307474728",
                            "cover_url": "https://example.com/covers/cien-anos-soledad.jpg",
                            "status": "available",
                            "owner": {
                                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "username": "usuario1",
                                "email": "usuario1@example.com",
                                "full_name": "Usuario Uno",
                                "avatar_url": "https://example.com/avatars/usuario1.jpg"
                            },
                            "is_available": True,
                            "current_borrower": None
                        }
                    ]
                }
            }
        },
        400: {
            "description": "Término de búsqueda inválido o demasiado corto",
            "model": ErrorResponse
        },
        403: {
            "description": "No autorizado para buscar en este grupo",
            "model": ErrorResponse
        },
        404: {
            "description": "Grupo no encontrado o usuario no es miembro",
            "model": ErrorResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": ErrorResponse
        }
    }
)
async def search_group_books(
    group_id: UUID = Path(..., description="ID único del grupo"),
    q: str = Query(..., min_length=1, max_length=100, description="Término de búsqueda (mínimo 1 carácter)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=50, description="Número máximo de resultados (1-50)")
):
    """
    Busca libros en el grupo que coincidan con el término de búsqueda.
    
    La búsqueda no distingue entre mayúsculas y minúsculas.
    Solo los miembros del grupo pueden realizar búsquedas.
    """
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


@router.get(
    "/{group_id}/books/{book_id}",
    response_model=GroupBook,
    status_code=status.HTTP_200_OK,
    summary="Obtener detalles de un libro del grupo",
    description="""
    Obtiene información detallada de un libro específico dentro de un grupo.
    
    Incluye:
    - Metadatos completos del libro (título, autor, ISBN, etc.)
    - Información del propietario
    - Estado actual del libro (disponible, prestado, etc.)
    - Información del prestatario actual (si aplica)
    
    Solo los miembros del grupo pueden ver los detalles del libro.
    """,
    responses={
        200: {
            "description": "Detalles completos del libro solicitado",
            "content": {
                "application/json": {
                    "example": {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "title": "Cien años de soledad",
                        "author": "Gabriel García Márquez",
                        "isbn": "9780307474728",
                        "cover_url": "https://example.com/covers/cien-anos-soledad.jpg",
                        "description": "Una obra maestra de la literatura hispanoamericana...",
                        "status": "available",
                        "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "current_borrower_id": None,
                        "is_archived": False,
                        "created_at": "2023-01-01T00:00:00",
                        "updated_at": "2023-01-01T00:00:00",
                        "owner": {
                            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "username": "usuario1",
                            "email": "usuario1@example.com",
                            "full_name": "Usuario Uno",
                            "avatar_url": "https://example.com/avatars/usuario1.jpg"
                        },
                        "is_available": True,
                        "current_borrower": None
                    }
                }
            }
        },
        403: {
            "description": "No autorizado para ver este libro",
            "model": ErrorResponse
        },
        404: {
            "description": "Libro o grupo no encontrado, o usuario no es miembro",
            "model": ErrorResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": ErrorResponse
        }
    }
)
async def get_group_book(
    group_id: UUID = Path(..., description="ID único del grupo"),
    book_id: UUID = Path(..., description="ID único del libro"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene los detalles completos de un libro específico en el grupo.
    
    Solo los miembros del grupo pueden ver los detalles del libro.
    Si el libro no existe o el usuario no tiene acceso, se devuelve un error 404.
    """
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
