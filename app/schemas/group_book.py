"""
Schemas Pydantic para libros en grupos.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.schemas.book import Book
from app.schemas.user import UserBasic
from app.models.book import BookType, BookGenre


class GroupBook(Book):
    """Schema para libro en un grupo con información del propietario."""
    owner: UserBasic = Field(..., description="Información del propietario del libro")
    is_available: bool = Field(..., description="Si el libro está disponible para préstamo")
    current_borrower: Optional[UserBasic] = Field(None, description="Usuario que tiene prestado el libro")
    
    model_config = ConfigDict(from_attributes=True)


class GroupBookSummary(BaseModel):
    """Schema resumido para listar libros de grupo."""
    id: UUID
    title: str
    author: str
    isbn: Optional[str] = None
    cover_url: Optional[str] = None
    status: str
    owner: UserBasic
    is_available: bool
    current_borrower: Optional[UserBasic] = None
    
    model_config = ConfigDict(from_attributes=True)


class GroupBookFilter(BaseModel):
    """Schema para filtros de búsqueda en grupo."""
    search: Optional[str] = Field(None, description="Búsqueda por título o autor")
    owner_id: Optional[UUID] = Field(None, description="Filtrar por propietario")
    status: Optional[str] = Field(None, description="Filtrar por estado (available, loaned, reserved)")
    is_available: Optional[bool] = Field(None, description="Filtrar por disponibilidad")
    book_type: Optional[BookType] = Field(None, description="Filtrar por tipo de libro")
    genre: Optional[BookGenre] = Field(None, description="Filtrar por género")
    isbn: Optional[str] = Field(None, description="Filtrar por ISBN")


class GroupBookStats(BaseModel):
    """Schema para estadísticas de libros en grupo."""
    total_books: int = Field(..., description="Total de libros en el grupo")
    available_books: int = Field(..., description="Libros disponibles para préstamo")
    loaned_books: int = Field(..., description="Libros prestados")
    reserved_books: int = Field(..., description="Libros reservados")
    total_owners: int = Field(..., description="Número de propietarios únicos")
    most_common_author: Optional[str] = Field(None, description="Autor más común")
    most_common_genre: Optional[str] = Field(None, description="Género más común")
