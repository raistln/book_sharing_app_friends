from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from uuid import UUID
from typing import List, Optional
import logging

from app.dependencies import get_current_db, optional_current_user
from app.models.book import Book as BookModel, BookStatus, BookType, BookGenre
from app.models.user import User
from app.schemas.book import Book as BookSchema, BookCreate, BookUpdate, BookInDB
from app.schemas.error import ErrorResponse
from app.services.auth_service import get_current_user


router = APIRouter(tags=["books"])
logger = logging.getLogger(__name__)


@router.post(
    "/",
    response_model=BookSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo libro",
    description="""
    Crea un nuevo libro en el sistema.
    
    - Requiere autenticación para crear un libro en nombre del usuario autenticado.
    - Si se proporciona owner_id, debe coincidir con el ID del usuario autenticado.
    - Para usuarios no autenticados, se requiere un owner_id válido.
    """,
    responses={
        201: {
            "description": "Libro creado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Cien años de soledad",
                        "author": "Gabriel García Márquez",
                        "status": "available",
                        "owner_id": "123e4567-e89b-12d3-a456-426614174000"
                    }
                }
            }
        },
        400: {
            "model": ErrorResponse,
            "description": "Datos inválidos o owner_id no válido"
        },
        401: {
            "model": ErrorResponse,
            "description": "No autenticado o credenciales inválidas"
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor al crear el libro"
        }
    }
)
async def create_book(
    payload: BookCreate,
    request: Request,
    db: Session = Depends(get_current_db),
    current_user: Optional[User] = Depends(optional_current_user),
) -> BookInDB:
    """
    Crea un nuevo libro en el sistema.
    
    Args:
        payload: Datos del libro a crear.
        request: Objeto Request de FastAPI para acceso a datos crudos.
        db: Sesión de base de datos inyectada por dependencia.
        current_user: Usuario autenticado (opcional).
        
    Returns:
        BookInDB: El libro creado.
        
    Raises:
        HTTPException: 
            - 401: Si no hay usuario autenticado ni se proporciona owner_id.
            - 400: Si el owner_id proporcionado no es válido.
            - 500: Error interno del servidor.
    """
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


@router.get(
    "/",
    response_model=List[BookSchema],
    summary="Listar todos los libros disponibles",
    description="""
    Obtiene una lista de todos los libros disponibles en el sistema.
    
    - No requiere autenticación.
    - Incluye información del propietario y del prestatario actual (si aplica).
    - Solo devuelve libros que no estén archivados.
    """,
    responses={
        200: {
            "description": "Lista de libros obtenida exitosamente",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "title": "Cien años de soledad",
                            "author": "Gabriel García Márquez",
                            "status": "available",
                            "owner_id": "123e4567-e89b-12d3-a456-426614174000"
                        },
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440001",
                            "title": "Rayuela",
                            "author": "Julio Cortázar",
                            "status": "loaned",
                            "owner_id": "123e4567-e89b-12d3-a456-426614174000",
                            "current_borrower_id": "123e4567-e89b-12d3-a456-426614174001"
                        }
                    ]
                }
            }
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor al obtener la lista de libros"
        }
    }
)
def list_books(db: Session = Depends(get_current_db)) -> List[BookInDB]:
    """
    Lista todos los libros disponibles en el sistema.
    
    Args:
        db: Sesión de base de datos inyectada por dependencia.
        
    Returns:
        List[BookInDB]: Lista de libros disponibles.
        
    Raises:
        HTTPException: Si ocurre un error al acceder a la base de datos.
    """
    logger.info("Listing all available books")
    
    # Optimized query with eager loading of related data
    books = db.query(BookModel).options(
        joinedload(BookModel.owner),
        joinedload(BookModel.current_borrower)
    ).filter(BookModel.is_archived == False).all()
    
    logger.info("Retrieved %d books", len(books))
    return books


@router.get(
    "/{book_id}",
    response_model=BookSchema,
    summary="Obtener un libro por ID",
    description="""
    Obtiene los detalles de un libro específico por su ID.
    
    - No requiere autenticación.
    - Incluye información del propietario y del prestatario actual (si aplica).
    - Solo devuelve libros que no estén archivados.
    """,
    responses={
        200: {
            "description": "Libro obtenido exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Cien años de soledad",
                        "author": "Gabriel García Márquez",
                        "isbn": "9780307474728",
                        "cover_url": "https://example.com/covers/cien-anos-soledad.jpg",
                        "description": "Una obra maestra del realismo mágico...",
                        "book_type": "NOVEL",
                        "genre": "FICTION",
                        "status": "available",
                        "owner_id": "123e4567-e89b-12d3-a456-426614174000",
                        "created_at": "2023-01-01T12:00:00Z"
                    }
                }
            }
        },
        404: {
            "model": ErrorResponse,
            "description": "Libro no encontrado o no disponible"
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor al obtener el libro"
        }
    }
)
def get_book(book_id: UUID, db: Session = Depends(get_current_db)) -> BookInDB:
    """
    Obtiene un libro específico por su ID.
    
    Args:
        book_id: UUID del libro a buscar.
        db: Sesión de base de datos inyectada por dependencia.
        
    Returns:
        BookInDB: El libro encontrado.
        
    Raises:
        HTTPException: Si el libro no se encuentra o está archivado (404).
    """
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


@router.put(
    "/{book_id}",
    response_model=BookSchema,
    summary="Actualizar un libro",
    description="""
    Actualiza los datos de un libro existente.
    
    - Requiere autenticación.
    - Solo el propietario del libro puede actualizarlo.
    - Los campos no proporcionados mantendrán sus valores actuales.
    """,
    responses={
        200: {
            "description": "Libro actualizado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Cien años de soledad (Edición Especial)",
                        "author": "Gabriel García Márquez",
                        "status": "available",
                        "owner_id": "123e4567-e89b-12d3-a456-426614174000",
                        "updated_at": "2023-01-02T15:30:00Z"
                    }
                }
            }
        },
        400: {
            "model": ErrorResponse,
            "description": "Datos inválidos o estado no válido"
        },
        403: {
            "model": ErrorResponse,
            "description": "No autorizado para actualizar este libro"
        },
        404: {
            "model": ErrorResponse,
            "description": "Libro no encontrado"
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor al actualizar el libro"
        }
    }
)
async def update_book(
    book_id: UUID, 
    payload: BookUpdate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_current_db)
) -> BookInDB:
    """
    Actualiza un libro existente.
    
    Args:
        book_id: UUID del libro a actualizar.
        payload: Datos para actualizar el libro.
        current_user: Usuario autenticado obtenido del token.
        db: Sesión de base de datos inyectada por dependencia.
        
    Returns:
        BookInDB: El libro actualizado.
        
    Raises:
        HTTPException: 
            - 403: Si el usuario no es el propietario del libro.
            - 404: Si el libro no se encuentra o está archivado.
            - 400: Si los datos son inválidos.
            - 500: Error interno del servidor.
    """
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

    update_data = payload.model_dump(exclude_unset=True)
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


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un libro (borrado lógico)",
    description="""
    Realiza un borrado lógico de un libro marcándolo como archivado.
    
    - Requiere autenticación.
    - Solo el propietario del libro puede eliminarlo.
    - No se puede eliminar un libro que esté actualmente prestado.
    - El libro no se elimina físicamente, solo se marca como archivado.
    """,
    responses={
        204: {
            "description": "Libro eliminado exitosamente (marcado como archivado)"
        },
        400: {
            "model": ErrorResponse,
            "description": "No se puede eliminar un libro prestado"
        },
        403: {
            "model": ErrorResponse,
            "description": "No autorizado para eliminar este libro"
        },
        404: {
            "model": ErrorResponse,
            "description": "Libro no encontrado"
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor al eliminar el libro"
        }
    }
)
async def delete_book(
    book_id: UUID, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_current_db)
) -> None:
    """
    Realiza un borrado lógico de un libro (marcado como archivado).
    
    Args:
        book_id: UUID del libro a eliminar.
        current_user: Usuario autenticado obtenido del token.
        db: Sesión de base de datos inyectada por dependencia.
        
    Raises:
        HTTPException: 
            - 403: Si el usuario no es el propietario del libro.
            - 404: Si el libro no se encuentra o ya está archivado.
            - 400: Si el libro está actualmente prestado.
            - 500: Error interno del servidor.
    """
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


