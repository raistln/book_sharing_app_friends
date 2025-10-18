"""
Schemas Pydantic para Libro
"""
from pydantic import BaseModel, Field
from pydantic import ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.book import BookCondition, BookGenre


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=150)
    isbn: Optional[str] = Field(None, max_length=20)
    cover_url: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    publisher: Optional[str] = Field(None, max_length=200)
    published_date: Optional[str] = Field(None, max_length=50)
    page_count: Optional[str] = Field(None, max_length=10)
    language: Optional[str] = Field(None, max_length=10)
    genre: Optional[BookGenre] = None
    condition: Optional[BookCondition] = Field(default=BookCondition.good)
    is_archived: Optional[bool] = False
    archived_reason: Optional[str] = Field(None, max_length=120)


class BookCreate(BookBase):
    # owner_id será tomado del usuario autenticado en el endpoint
    owner_id: Optional[UUID] = None
    current_borrower_id: Optional[UUID] = None


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=150)
    isbn: Optional[str] = Field(None, max_length=20)
    cover_url: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    publisher: Optional[str] = Field(None, max_length=200)
    published_date: Optional[str] = Field(None, max_length=50)
    page_count: Optional[str] = Field(None, max_length=10)
    language: Optional[str] = Field(None, max_length=10)
    genre: Optional[BookGenre] = None
    condition: Optional[BookCondition] = None
    status: Optional[str] = Field(None, pattern="^(available|loaned|reserved)$")
    is_archived: Optional[bool] = None
    archived_reason: Optional[str] = Field(None, max_length=120)
    current_borrower_id: Optional[UUID] = None


class BookInDB(BookBase):
    id: UUID
    owner_id: UUID
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
    current_borrower_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class Book(BookInDB):
    pass


class UserInResponse(BaseModel):
    """Schema for user information in responses"""
    id: UUID
    username: str
    email: str
    full_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class BookResponse(BookInDB):
    """
    Schema for book responses, including related user information.
    
    This is used for API responses where we want to include
    complete information about the book and its relationships.
    """
    owner: 'UserInResponse'
    current_borrower: Optional['UserInResponse'] = None
    average_rating: Optional[float] = None  # Promedio de ratings de reseñas
    total_reviews: Optional[int] = None     # Número total de reseñas
    
    model_config = ConfigDict(from_attributes=True)


# Update forward references for UserInResponse in BookResponse
BookResponse.model_rebuild()

