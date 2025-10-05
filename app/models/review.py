"""
Modelo de Review (Reseñas de libros)
"""
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Index, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    # Campos principales
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones con índices para optimización en producción
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=True)

    # Índices y constraints para optimización y validación
    __table_args__ = (
        UniqueConstraint("book_id", "user_id", name="unique_book_user_review"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="rating_range_check"),
        Index("ix_reviews_book_id", "book_id"),
        Index("ix_reviews_group_id", "group_id"),
        Index("ix_reviews_user_id", "user_id"),
    )

    # ORM relationships
    book = relationship("Book", backref="reviews")
    user = relationship("User", backref="reviews")
    group = relationship("Group", backref="reviews")

    def __repr__(self):
        return f"<Review(id={self.id}, book_id={self.book_id}, user_id={self.user_id}, rating={self.rating})>"
