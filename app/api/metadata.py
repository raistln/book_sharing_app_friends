"""
Módulo de metadatos para la aplicación de préstamo de libros

Este módulo proporciona endpoints para obtener metadatos y configuraciones
que son utilizados por el frontend para mostrar opciones, validar entradas
y mantener la consistencia en toda la aplicación.
"""
from fastapi import APIRouter, Request, status
from typing import List, Dict, Any, Literal
from pydantic import BaseModel, Field
from app.utils.rate_limiter import api_rate_limit
from app.schemas.error import ErrorResponse

router = APIRouter(
    prefix="/metadata",
    tags=["metadata"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "No autorizado",
            "model": ErrorResponse
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "description": "Límite de tasa excedido",
            "model": ErrorResponse
        }
    }
)

# Modelos de respuesta para la documentación
class BookCondition(BaseModel):
    """Modelo para las condiciones de los libros"""
    value: Literal["excellent", "good", "fair", "poor"]
    label: str = Field(..., description="Nombre legible de la condición")

class Language(BaseModel):
    """Modelo para los idiomas soportados"""
    code: str = Field(..., description="Código ISO 639-1 del idioma")
    name: str = Field(..., description="Nombre del idioma en su propio idioma")

class PaginationOptions(BaseModel):
    """Opciones de paginación"""
    default_page_size: int = Field(..., ge=1, le=100, description="Tamaño de página por defecto")
    available_page_sizes: List[int] = Field(..., description="Tamaños de página disponibles")
    max_page_size: int = Field(..., ge=1, description="Tamaño máximo de página permitido")

class FileUploadLimits(BaseModel):
    """Límites de carga de archivos"""
    max_file_size_mb: int = Field(..., ge=1, description="Tamaño máximo de archivo en MB")
    allowed_image_types: List[str] = Field(..., description="Extensiones de archivo permitidas")
    allowed_mime_types: List[str] = Field(..., description="Tipos MIME permitidos")

@router.get(
    "/genres",
    response_model=List[str],
    status_code=status.HTTP_200_OK,
    summary="Obtener géneros literarios disponibles",
    description="""
    Devuelve una lista de géneros literarios disponibles para clasificar los libros.
    
    Estos géneros son utilizados para categorizar los libros en la aplicación y facilitar
    la búsqueda y filtrado de los mismos.
    
    **Ejemplo de uso:**
    - Mostrar opciones en un desplegable de selección de género
    - Filtrar libros por género
    - Estadísticas de géneros más populares
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Lista de géneros literarios disponibles",
            "content": {
                "application/json": {
                    "example": [
                        "Ficción",
                        "No ficción",
                        "Ciencia",
                        "Historia"
                    ]
                }
            }
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {"$ref": "#/components/responses/TooManyRequestsError"}
    }
)
@api_rate_limit()
async def get_genres(request: Request) -> List[str]:
    """
    Obtiene la lista de géneros literarios disponibles.
    
    Args:
        request: Objeto de solicitud HTTP
        
    Returns:
        List[str]: Lista de nombres de géneros literarios
    """
    return [
        "Ficción",
        "No ficción",
        "Ciencia",
        "Historia",
        "Biografía",
        "Técnico",
        "Romance",
        "Misterio",
        "Fantasía",
        "Ciencia ficción",
        "Terror",
        "Aventura",
        "Autoayuda",
        "Cocina",
        "Arte",
        "Filosofía",
        "Religión",
        "Política",
        "Economía",
        "Psicología"
    ]

@router.get(
    "/book-types",
    response_model=List[Literal["physical", "digital"]],
    status_code=status.HTTP_200_OK,
    summary="Obtener tipos de libros disponibles",
    description="""
    Devuelve los tipos de libros soportados por la aplicación.
    
    Los tipos disponibles son:
    - `physical`: Libro físico (copia impresa)
    - `digital`: Libro digital (archivo electrónico)
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Lista de tipos de libros disponibles",
            "content": {
                "application/json": {
                    "example": ["physical", "digital"]
                }
            }
        }
    }
)
@api_rate_limit()
async def get_book_types(request: Request) -> List[str]:
    """
    Obtiene los tipos de libros disponibles en la plataforma.
    
    Returns:
        List[str]: Lista de tipos de libros ("physical", "digital")
    """
    return ["physical", "digital"]

@router.get(
    "/book-conditions",
    response_model=List[BookCondition],
    status_code=status.HTTP_200_OK,
    summary="Obtener condiciones de libros disponibles",
    description="""
    Devuelve las posibles condiciones en las que puede encontrarse un libro físico.
    
    Cada condición incluye:
    - `value`: Identificador único de la condición (inglés)
    - `label`: Nombre legible de la condición (español)
    
    **Valores posibles:**
    - `excellent`: Como nuevo, sin señales de uso
    - `good`: Algunas señales de uso menores
    - `fair`: Desgaste moderado, pero completo y legible
    - `poor`: Desgaste severo, puede faltar páginas o tener daños
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Lista de condiciones de libros disponibles",
            "content": {
                "application/json": {
                    "example": [
                        {"value": "excellent", "label": "Excelente"},
                        {"value": "good", "label": "Bueno"},
                        {"value": "fair", "label": "Regular"},
                        {"value": "poor", "label": "Malo"}
                    ]
                }
            }
        }
    }
)
@api_rate_limit()
async def get_book_conditions(request: Request) -> List[Dict[str, str]]:
    """
    Obtiene las condiciones disponibles para los libros físicos.
    
    Returns:
        List[Dict[str, str]]: Lista de condiciones con sus etiquetas
    """
    return [
        {"value": "excellent", "label": "Excelente"},
        {"value": "good", "label": "Bueno"},
        {"value": "fair", "label": "Regular"},
        {"value": "poor", "label": "Malo"}
    ]

@router.get(
    "/loan-statuses",
    response_model=List[Dict[str, str]],
    status_code=status.HTTP_200_OK,
    summary="Obtener estados de préstamo disponibles",
    description="""
    Devuelve los posibles estados por los que puede pasar un préstamo de libro.
    
    **Estados disponibles:**
    - `pending`: Solicitud de préstamo pendiente de aprobación
    - `approved`: Préstamo aprobado, pendiente de recogida
    - `rejected`: Solicitud de préstamo rechazada
    - `active`: Libro prestado actualmente
    - `returned`: Libro devuelto correctamente
    - `overdue`: Préstamo vencido sin devolución
    
    Cada estado incluye:
    - `value`: Identificador único del estado (en inglés)
    - `label`: Nombre legible del estado (en español)
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Lista de estados de préstamo disponibles",
            "content": {
                "application/json": {
                    "example": [
                        {"value": "pending", "label": "Pendiente"},
                        {"value": "approved", "label": "Aprobado"},
                        {"value": "rejected", "label": "Rechazado"},
                        {"value": "active", "label": "Activo"},
                        {"value": "returned", "label": "Devuelto"},
                        {"value": "overdue", "label": "Vencido"}
                    ]
                }
            }
        }
    }
)
@api_rate_limit()
async def get_loan_statuses(request: Request) -> List[Dict[str, str]]:
    """
    Obtiene los estados disponibles para los préstamos de libros.
    
    Returns:
        List[Dict[str, str]]: Lista de estados con sus etiquetas
    """
    return [
        {"value": "pending", "label": "Pendiente"},
        {"value": "approved", "label": "Aprobado"},
        {"value": "rejected", "label": "Rechazado"},
        {"value": "active", "label": "Activo"},
        {"value": "returned", "label": "Devuelto"},
        {"value": "overdue", "label": "Vencido"}
    ]

@router.get(
    "/languages",
    response_model=List[Language],
    status_code=status.HTTP_200_OK,
    summary="Obtener idiomas disponibles",
    description="""
    Devuelve los idiomas soportados por la aplicación.
    
    Cada idioma incluye:
    - `code`: Código ISO 639-1 del idioma (2 letras)
    - `name`: Nombre del idioma en su propio idioma
    
    **Idiomas soportados actualmente:**
    - Español (es)
    - Inglés (en)
    - Francés (fr)
    - Alemán (de)
    - Italiano (it)
    - Portugués (pt)
    - Catalán (ca)
    - Euskera (eu)
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Lista de idiomas disponibles",
            "content": {
                "application/json": {
                    "example": [
                        {"code": "es", "name": "Español"},
                        {"code": "en", "name": "English"},
                        {"code": "fr", "name": "Français"}
                    ]
                }
            }
        }
    }
)
@api_rate_limit()
async def get_languages(request: Request) -> List[Dict[str, str]]:
    """
    Obtiene los idiomas soportados por la aplicación.
    
    Returns:
        List[Dict[str, str]]: Lista de idiomas con código y nombre
    """
    return [
        {"code": "es", "name": "Español"},
        {"code": "en", "name": "English"},
        {"code": "fr", "name": "Français"},
        {"code": "de", "name": "Deutsch"},
        {"code": "it", "name": "Italiano"},
        {"code": "pt", "name": "Português"},
        {"code": "ca", "name": "Català"},
        {"code": "eu", "name": "Euskera"}
    ]

@router.get(
    "/pagination-options",
    response_model=PaginationOptions,
    status_code=status.HTTP_200_OK,
    summary="Obtener opciones de paginación",
    description="""
    Devuelve la configuración de paginación utilizada en la aplicación.
    
    Esta configuración es útil para los componentes de paginación en el frontend,
    permitiendo mostrar las opciones de tamaño de página y establecer valores por defecto.
    
    **Campos devueltos:**
    - `default_page_size`: Número de elementos por página por defecto (20)
    - `available_page_sizes`: Lista de tamaños de página disponibles
    - `max_page_size`: Número máximo de elementos permitidos por página
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Configuración de paginación",
            "content": {
                "application/json": {
                    "example": {
                        "default_page_size": 20,
                        "available_page_sizes": [10, 20, 50, 100],
                        "max_page_size": 100
                    }
                }
            }
        }
    }
)
@api_rate_limit()
async def get_pagination_options(request: Request) -> Dict[str, Any]:
    """
    Obtiene la configuración de paginación para las listas de la aplicación.
    
    Returns:
        Dict[str, Any]: Configuración de paginación
    """
    return {
        "default_page_size": 20,
        "available_page_sizes": [10, 20, 50, 100],
        "max_page_size": 100
    }

@router.get(
    "/file-upload-limits",
    response_model=FileUploadLimits,
    status_code=status.HTTP_200_OK,
    summary="Obtener límites de carga de archivos",
    description="""
    Devuelve las restricciones para la carga de archivos en la aplicación.
    
    Esta información es esencial para validar las cargas de archivos en el frontend
    antes de enviarlas al servidor, mejorando la experiencia de usuario.
    
    **Límites actuales:**
    - Tamaño máximo: 5MB
    - Formatos de imagen soportados: JPG, PNG, WebP, GIF, BMP
    
    **Nota:** Siempre valide los archivos en el servidor, incluso si ya se validaron en el frontend.
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Límites de carga de archivos",
            "content": {
                "application/json": {
                    "example": {
                        "max_file_size_mb": 5,
                        "allowed_image_types": [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"],
                        "allowed_mime_types": [
                            "image/jpeg", 
                            "image/png", 
                            "image/webp", 
                            "image/gif", 
                            "image/bmp"
                        ]
                    }
                }
            }
        }
    }
)
@api_rate_limit()
async def get_file_upload_limits(request: Request) -> Dict[str, Any]:
    """
    Obtiene los límites y restricciones para la carga de archivos.
    
    Returns:
        Dict[str, Any]: Límites y tipos de archivo permitidos
    """
    return {
        "max_file_size_mb": 5,
        "allowed_image_types": [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"],
        "allowed_mime_types": ["image/jpeg", "image/png", "image/webp", "image/gif", "image/bmp"]
    }
