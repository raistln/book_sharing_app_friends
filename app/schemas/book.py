"""
Schemas Pydantic para Libro
"""
from pydantic import BaseModel, Field
from pydantic import ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=150)
    isbn: Optional[str] = Field(None, max_length=20)
    cover_url: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    is_archived: Optional[bool] = False
    archived_reason: Optional[str] = Field(None, max_length=120)


class BookCreate(BookBase):
    owner_id: UUID
    current_borrower_id: Optional[UUID] = None


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=150)
    isbn: Optional[str] = Field(None, max_length=20)
    cover_url: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
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


