"""
Schemas Pydantic para Review (Reseñas)
"""
from pydantic import BaseModel, Field
from pydantic import ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Calificación del libro (1-5)")
    comment: Optional[str] = Field(None, description="Comentario opcional sobre el libro")


class ReviewCreate(ReviewBase):
    book_id: UUID = Field(..., description="ID del libro reseñado")
    group_id: Optional[UUID] = Field(None, description="ID del grupo asociado (opcional)")


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None


class ReviewInDB(ReviewBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    book_id: UUID
    user_id: UUID
    group_id: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ReviewResponse(ReviewInDB):
    # Relaciones opcionales para respuestas enriquecidas
    book_title: Optional[str] = None
    user_username: Optional[str] = None
    group_name: Optional[str] = None
