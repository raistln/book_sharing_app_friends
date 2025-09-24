"""
Enhanced Search Module

Este módulo proporciona funcionalidades avanzadas de búsqueda para libros, usuarios y grupos
con soporte para filtrado, ordenación y paginación.
"""
from fastapi import APIRouter, Depends, Query, Request, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_ 
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.book import Book
from app.models.user import User
from app.models.group import Group
from app.schemas.error import ErrorResponse
from app.utils.pagination import paginate_query, PaginationParams
from app.utils.rate_limiter import search_rate_limit
from app.utils.logger import log_endpoint_call
import logging

# Configuración del router con respuestas por defecto
router = APIRouter(
    prefix="/search",
    tags=["search"],
    responses={
        401: {"description": "No autorizado - Se requiere autenticación"},
        422: {"description": "Error de validación en los parámetros"},
        500: {"description": "Error interno del servidor"}
    }
)
logger = logging.getLogger("book_sharing.search")

class BookSearchResult(BaseModel):
    """Modelo para los resultados de búsqueda de libros"""
    id: str = Field(..., description="ID único del libro")
    title: str = Field(..., description="Título del libro")
    author: str = Field(..., description="Autor del libro")
    description: Optional[str] = Field(None, description="Descripción del libro")
    isbn: Optional[str] = Field(None, description="ISBN del libro")
    genre: Optional[str] = Field(None, description="Género del libro")
    book_type: str = Field(..., description="Tipo de libro (físico/digital)")
    language: Optional[str] = Field(None, description="Idioma del libro")
    status: str = Field(..., description="Estado del libro")
    condition: Optional[str] = Field(None, description="Condición del libro")
    rating: Optional[float] = Field(None, description="Calificación promedio")
    created_at: str = Field(..., description="Fecha de creación")

class BookSearchResponse(BaseModel):
    """Modelo para la respuesta de búsqueda de libros"""
    items: List[BookSearchResult] = Field(..., description="Lista de libros encontrados")
    total: int = Field(..., description="Número total de resultados")
    page: int = Field(..., description="Página actual")
    per_page: int = Field(..., description="Resultados por página")
    total_pages: int = Field(..., description="Número total de páginas")

class UserSearchResult(BaseModel):
    """Modelo para los resultados de búsqueda de usuarios"""
    id: str = Field(..., description="ID único del usuario")
    username: str = Field(..., description="Nombre de usuario")
    email: str = Field(..., description="Correo electrónico")
    full_name: Optional[str] = Field(None, description="Nombre completo del usuario")
    is_active: bool = Field(..., description="Indica si el usuario está activo")
    created_at: str = Field(..., description="Fecha de creación de la cuenta")
    
class UserSearchResponse(BaseModel):
    """Modelo para la respuesta de búsqueda de usuarios"""
    items: List[UserSearchResult] = Field(..., description="Lista de usuarios encontrados")
    total: int = Field(..., description="Número total de resultados")
    page: int = Field(..., description="Página actual")
    per_page: int = Field(..., description="Resultados por página")
    total_pages: int = Field(..., description="Número total de páginas")

class GroupSearchResult(BaseModel):
    """Modelo para los resultados de búsqueda de grupos"""
    id: str = Field(..., description="ID único del grupo")
    name: str = Field(..., description="Nombre del grupo")
    description: Optional[str] = Field(None, description="Descripción del grupo")
    is_public: bool = Field(..., description="Indica si el grupo es público")
    member_count: int = Field(..., description="Número de miembros del grupo")
    created_at: str = Field(..., description="Fecha de creación del grupo")
    
class GroupSearchResponse(BaseModel):
    """Modelo para la respuesta de búsqueda de grupos"""
    items: List[GroupSearchResult] = Field(..., description="Lista de grupos encontrados")
    total: int = Field(..., description="Número total de resultados")
    page: int = Field(..., description="Página actual")
    per_page: int = Field(..., description="Resultados por página")
    total_pages: int = Field(..., description="Número total de páginas")

class SearchSuggestionsResponse(BaseModel):
    """Modelo para la respuesta de sugerencias de búsqueda"""
    books: List[str] = Field(..., description="Sugerencias de títulos de libros")
    authors: List[str] = Field(..., description="Sugerencias de nombres de autores")
    genres: List[str] = Field(..., description="Sugerencias de géneros literarios")

@router.get(
    "/books",
    response_model=BookSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Búsqueda avanzada de libros",
    description="""
    Realiza búsquedas avanzadas de libros con múltiples filtros y opciones de ordenación.
    
    Características:
    - Búsqueda por texto en título, autor, descripción e ISBN
    - Filtrado por género, tipo, idioma, disponibilidad y condición
    - Ordenación por relevancia, título, autor, fecha de creación o calificación
    - Paginación de resultados
    - Soporte para consultas vacías (devuelve todos los libros)
    """,
    responses={
        200: {
            "description": "Resultados de búsqueda",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "title": "El nombre del viento",
                                "author": "Patrick Rothfuss",
                                "description": "Una historia de aventuras y magia...",
                                "isbn": "9788499082480",
                                "genre": "Fantasía",
                                "book_type": "physical",
                                "language": "es",
                                "status": "available",
                                "condition": "like_new",
                                "rating": 4.5,
                                "created_at": "2023-01-01T12:00:00Z"
                            }
                        ],
                        "total": 1,
                        "page": 1,
                        "per_page": 20,
                        "total_pages": 1
                    }
                }
            }
        },
        400: {
            "description": "Parámetros de búsqueda inválidos",
            "model": ErrorResponse
        },
        500: {
            "description": "Error en el servidor al procesar la búsqueda",
            "model": ErrorResponse
        }
    }
)
@search_rate_limit()
@log_endpoint_call("/search/books", "GET")
async def search_books(
    request: Request,
    q: Optional[str] = Query(
        None, 
        description="Término de búsqueda (título, autor, descripción o ISBN). Opcional. Si se omite o está vacío, se devolverán todos los libros que coincidan con los filtros.",
        example="El nombre del viento"
    ),
    page: int = Query(1, 
                     ge=1, 
                     description="Número de página",
                     example=1),
    per_page: int = Query(20, 
                         description="Número de resultados por página",
                         example=20),
    genre: Optional[str] = Query(None, 
                               description="Filtrar por género",
                               example="Fantasía"),
    book_type: Optional[str] = Query(None, 
                                   description="Tipo de libro (physical/digital)",
                                   example="physical"),
    language: Optional[str] = Query(None, 
                                   description="Filtrar por idioma (código ISO 639-1)",
                                   example="es"),
    available_only: bool = Query(False, 
                               description="Mostrar solo libros disponibles",
                               example=False),
    condition: Optional[str] = Query(None, 
                                   description="Filtrar por condición (new/like_new/good/fair/poor)",
                                   example="like_new"),
    min_rating: Optional[float] = Query(None, 
                                      ge=0, 
                                      le=5, 
                                      description="Puntuación mínima (0-5)",
                                      example=4.0),
    sort_by: str = Query("relevance", 
                        description="Campo para ordenar los resultados (relevance/title/author/created_at/rating)",
                        example="rating"),
    sort_order: str = Query("desc", 
                           description="Orden de clasificación (asc/desc)",
                           example="desc"),
    db: Session = Depends(get_db)
):
    """
    Realiza una búsqueda avanzada de libros con múltiples filtros y opciones de ordenación.
    
    Args:
        request: Objeto de solicitud HTTP
        q: Término de búsqueda (mínimo 2 caracteres)
        page: Número de página (1-based)
        per_page: Número de resultados por página (1-100)
        genre: Filtrar por género
        book_type: Filtrar por tipo de libro (físico/digital)
        language: Filtrar por idioma (código ISO 639-1)
        available_only: Mostrar solo libros disponibles
        condition: Filtrar por condición del libro
        min_rating: Filtrar por puntuación mínima (0-5)
        sort_by: Campo para ordenar los resultados
        sort_order: Orden de clasificación (ascendente/descendente)
        db: Sesión de base de datos
        
    Returns:
        BookSearchResponse: Resultados de la búsqueda con metadatos de paginación
        
    Raises:
        HTTPException: 400 si los parámetros son inválidos
        HTTPException: 404 si no se encuentran resultados
        HTTPException: 422 si hay errores de validación
        HTTPException: 500 si ocurre un error en el servidor
    """
    try:
        # Base query - only non-deleted books
        query = db.query(Book).filter(Book.is_deleted == False)
        
        # Text search in title, author, description, and ISBN (optional)
        if q is not None and q.strip():
            search_term = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    Book.title.ilike(search_term),
                    Book.author.ilike(search_term),
                    Book.description.ilike(search_term),
                    Book.isbn.ilike(search_term)
                )
            )
    except Exception as e:
        logger.error(f"Error processing search query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar la búsqueda"
        )
    
    # Apply filters
    if genre:
        query = query.filter(Book.genre.ilike(f"%{genre}%"))
    
    if book_type:
        query = query.filter(Book.book_type == book_type)
    
    if language:
        query = query.filter(Book.language == language)
    
    if available_only:
        query = query.filter(Book.status == "available")
    
    if condition:
        query = query.filter(Book.condition == condition)
    
    if min_rating is not None:
        query = query.filter(Book.rating >= min_rating)
    
    # Apply sorting
    if sort_by == "title":
        order_field = Book.title
    elif sort_by == "author":
        order_field = Book.author
    elif sort_by == "created_at":
        order_field = Book.created_at
    elif sort_by == "rating":
        order_field = Book.rating
    else:  # relevance or default
        order_field = Book.created_at  # Default to newest first
    
    if sort_order == "asc":
        query = query.order_by(order_field.asc())
    else:
        query = query.order_by(order_field.desc())
    
    # Log search parameters
    logger.info(f"Book search: query='{q}', filters={{'genre': {genre}, 'type': {book_type}, 'available_only': {available_only}}}")
    
    # Paginate results
    return paginate_query(query, page, per_page)

@router.get(
    "/users",
    response_model=UserSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Búsqueda de usuarios",
    description="""
    Busca usuarios por nombre de usuario o correo electrónico.
    
    Características:
    - Búsqueda por nombre de usuario o correo electrónico
    - Resultados paginados
    - Solo usuarios activos
    - Ordenación alfabética por nombre de usuario
    """,
    responses={
        200: {
            "description": "Resultados de búsqueda de usuarios",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "username": "usuario123",
                                "email": "usuario@ejemplo.com",
                                "full_name": "Juan Pérez",
                                "is_active": True,
                                "created_at": "2023-01-01T12:00:00Z"
                            }
                        ],
                        "total": 1,
                        "page": 1,
                        "per_page": 20,
                        "total_pages": 1
                    }
                }
            }
        },
        400: {
            "description": "Parámetros de búsqueda inválidos",
            "model": ErrorResponse
        },
        422: {
            "description": "Error de validación en los parámetros",
            "model": ErrorResponse
        },
        500: {
            "description": "Error en el servidor al procesar la búsqueda",
            "model": ErrorResponse
        }
    }
)
@search_rate_limit()
@log_endpoint_call("/search/users", "GET")
async def search_users(
    request: Request,
    q: str = Query(
        "", 
        description="Término de búsqueda (nombre de usuario o correo electrónico). Dejar vacío para obtener todos los resultados.",
        example="usuario123"
    ),
    page: int = Query(
        1, 
        ge=1, 
        description="Número de página",
        example=1
    ),
    per_page: int = Query(
        20, 
        ge=1, 
        le=100, 
        description="Número de resultados por página (máx. 100)",
        example=20
    ),
    db: Session = Depends(get_db)
):
    """
    Busca usuarios por nombre de usuario o correo electrónico.
    
    Args:
        request: Objeto de solicitud HTTP
        q: Término de búsqueda (mínimo 2 caracteres)
        page: Número de página (1-based)
        per_page: Número de resultados por página (1-100)
        db: Sesión de base de datos
        
    Returns:
        UserSearchResponse: Resultados de la búsqueda con metadatos de paginación
        
    Raises:
        HTTPException: 400 si los parámetros son inválidos
        HTTPException: 422 si hay errores de validación
        HTTPException: 500 si ocurre un error en el servidor
    """
    from app.models.user import User
    
    # Base query - only active users
    query = db.query(User).filter(User.is_active == True)
    
    # Text search in username and email
    if q.strip():
        search_term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                User.username.ilike(search_term),
                User.email.ilike(search_term)
            )
        )
    
    # Order by username
    query = query.order_by(User.username.asc())
    
    logger.info(f"User search: query='{q}'")
    
    # Paginate results
    return paginate_query(query, page, per_page)

@router.get(
    "/groups",
    response_model=GroupSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Búsqueda de grupos",
    description="""
    Busca grupos por nombre o descripción.
    
    Características:
    - Búsqueda por nombre o descripción del grupo
    - Filtrado por visibilidad (públicos/privados)
    - Resultados paginados
    - Ordenación alfabética por nombre del grupo
    """,
    responses={
        200: {
            "description": "Resultados de búsqueda de grupos",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "id": "660e8400-e29b-41d4-a716-446655440000",
                                "name": "Club de Lectura Madrid",
                                "description": "Grupo de amantes de la lectura en Madrid",
                                "is_public": True,
                                "member_count": 42,
                                "created_at": "2023-01-15T10:30:00Z"
                            }
                        ],
                        "total": 1,
                        "page": 1,
                        "per_page": 20,
                        "total_pages": 1
                    }
                }
            }
        },
        400: {
            "description": "Parámetros de búsqueda inválidos",
            "model": ErrorResponse
        },
        422: {
            "description": "Error de validación en los parámetros",
            "model": ErrorResponse
        },
        500: {
            "description": "Error en el servidor al procesar la búsqueda",
            "model": ErrorResponse
        }
    }
)
@search_rate_limit()
@log_endpoint_call("/search/groups", "GET")
async def search_groups(
    request: Request,
    q: str = Query(
        ..., 
        min_length=2, 
        max_length=100,
        description="Término de búsqueda (nombre o descripción del grupo)",
        example="lectura"
    ),
    page: int = Query(
        1, 
        ge=1, 
        description="Número de página",
        example=1
    ),
    per_page: int = Query(
        20, 
        ge=1, 
        le=100, 
        description="Número de resultados por página (máx. 100)",
        example=20
    ),
    public_only: bool = Query(
        False, 
        description="Mostrar solo grupos públicos",
        example=True
    ),
    db: Session = Depends(get_db)
):
    """
    Busca grupos por nombre o descripción.
    
    Args:
        request: Objeto de solicitud HTTP
        q: Término de búsqueda (mínimo 2 caracteres)
        page: Número de página (1-based)
        per_page: Número de resultados por página (1-100)
        public_only: Si es True, solo devuelve grupos públicos
        db: Sesión de base de datos
        
    Returns:
        GroupSearchResponse: Resultados de la búsqueda con metadatos de paginación
        
    Raises:
        HTTPException: 400 si los parámetros son inválidos
        HTTPException: 422 si hay errores de validación
        HTTPException: 500 si ocurre un error en el servidor
    """
    from app.models.group import Group
    
    # Base query
    query = db.query(Group)
    
    # Filter public groups if requested
    if public_only:
        query = query.filter(Group.is_public == True)
    
    # Text search in name and description
    if q.strip():
        search_term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Group.name.ilike(search_term),
                Group.description.ilike(search_term)
            )
        )
    
    # Order by name
    query = query.order_by(Group.name.asc())
    
    logger.info(f"Group search: query='{q}', public_only={public_only}")
    
    # Paginate results
    return paginate_query(query, page, per_page)

@router.get(
    "/suggestions",
    response_model=SearchSuggestionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener sugerencias de búsqueda",
    description="""
    Proporciona sugerencias de búsqueda basadas en una consulta parcial.
    
    Características:
    - Sugerencias de títulos de libros
    - Sugerencias de nombres de autores
    - Sugerencias de géneros literarios
    - Límite ajustable de sugerencias por categoría
    """,
    responses={
        200: {
            "description": "Sugerencias de búsqueda",
            "content": {
                "application/json": {
                    "example": {
                        "books": ["El nombre del viento", "El temor de un hombre sabio"],
                        "authors": ["Patrick Rothfuss", "Brandon Sanderson"],
                        "genres": ["Fantasía", "Ciencia ficción"]
                    }
                }
            }
        },
        400: {
            "description": "Consulta de búsqueda demasiado corta",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "msg": "La consulta debe tener al menos 2 caracteres",
                            "type": "validation_error"
                        }
                    }
                }
            }
        },
        422: {
            "description": "Error de validación en los parámetros",
            "model": ErrorResponse
        },
        500: {
            "description": "Error en el servidor al generar sugerencias",
            "model": ErrorResponse
        }
    }
)
@search_rate_limit()
@log_endpoint_call("/search/suggestions", "GET")
async def get_search_suggestions(
    request: Request,
    q: str = Query(
        ..., 
        min_length=2, 
        max_length=100,
        description="Texto de búsqueda para generar sugerencias (mínimo 2 caracteres)",
        example="fantas"
    ),
    limit: int = Query(
        10, 
        description="Número máximo de sugerencias por categoría",
        example=5
    ),
    db: Session = Depends(get_db)
):
    """
    Proporciona sugerencias de búsqueda basadas en una consulta parcial.
    
    Args:
        request: Objeto de solicitud HTTP
        q: Texto de búsqueda (mínimo 2 caracteres)
        limit: Número máximo de sugerencias por categoría (1-20)
        db: Sesión de base de datos
        
    Returns:
        SearchSuggestionsResponse: Sugerencias de búsqueda organizadas por categorías
        
    Raises:
        HTTPException: 400 si el texto de búsqueda es demasiado corto
        HTTPException: 422 si hay errores de validación
        HTTPException: 500 si ocurre un error en el servidor
    """
    # Inicializar respuesta con listas vacías
    suggestions = {
        "books": [],
        "authors": [],
        "genres": []
    }
    
    # Si la consulta está vacía, devolver sugerencias vacías
    if not q or not q.strip():
        return suggestions
    
    search_term = f"%{q.strip()}%"
    
    # Si la consulta está vacía, no buscar nada
    if not q or not q.strip():
        return suggestions
        
    try:
        search_term = f"%{q.strip()}%"
        
        # Sugerencias de títulos de libros
        book_titles = db.query(Book.title).filter(
            and_(
                Book.title.ilike(search_term),
                Book.is_deleted == False
            )
        ).distinct().limit(limit).all()
        
        suggestions["books"] = [title[0] for title in book_titles if title[0]]
        
        # Sugerencias de autores
        authors = db.query(Book.author).filter(
            and_(
                Book.author.ilike(search_term),
                Book.author.isnot(None),
                Book.is_deleted == False
            )
        ).distinct().limit(limit).all()
        
        suggestions["authors"] = [author[0] for author in authors if author and author[0]]
        
        # Sugerencias de géneros (de una lista predefinida)
        all_genres = [
            "Ficción", "No ficción", "Ciencia", "Historia", "Biografía",
            "Técnico", "Romance", "Misterio", "Fantasía", "Ciencia ficción",
            "Aventura", "Terror", "Policíaco", "Poesía", "Teatro", "Ensayo",
            "Autoayuda", "Negocios", "Infantil", "Juvenil", "Cómic", "Manga"
        ]
        
        # Filtrar géneros que contengan el término de búsqueda (insensible a mayúsculas)
        suggestions["genres"] = [
            genre for genre in all_genres 
            if q.lower() in genre.lower()
        ][:limit]
        
        logger.info(f"Generated {sum(len(v) for v in suggestions.values())} search suggestions")
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error generating search suggestions: {str(e)}", exc_info=True)
        # En caso de error, lanzar una excepción para que se maneje como un error 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al generar sugerencias de búsqueda"
        )
