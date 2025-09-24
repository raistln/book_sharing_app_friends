"""
Schemas Pydantic para Libro
"""
from pydantic import BaseModel, Field
from pydantic import ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.book import BookType, BookGenre


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=150)
    isbn: Optional[str] = Field(None, max_length=20)
    cover_url: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    book_type: Optional[BookType] = None
    genre: Optional[BookGenre] = None
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
    book_type: Optional[BookType] = None
    genre: Optional[BookGenre] = None
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
    
    model_config = ConfigDict(from_attributes=True)


# Update forward references for UserInResponse in BookResponse
BookResponse.model_rebuild()

