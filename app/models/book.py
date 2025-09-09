"""
Modelo de Libro
"""
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base
from app.models.user import User


class BookStatus(enum.Enum):
    available = "available"
    loaned = "loaned"
    reserved = "reserved"


class Book(Base):
    __tablename__ = "books"

    # Campos principales
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False, index=True)
    author = Column(String(150), nullable=False, index=True)
    isbn = Column(String(20), nullable=True, unique=False, index=True)
    cover_url = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    # Relaciones
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    current_borrower_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Estado y auditoría
    status = Column(Enum(BookStatus, name="book_status"), nullable=False, server_default=BookStatus.available.name)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Soft delete / archivado
    is_archived = Column(Boolean, nullable=False, server_default="false")
    archived_at = Column(DateTime(timezone=True), nullable=True)
    archived_reason = Column(String(120), nullable=True)

    # ORM relationships
    owner = relationship(User, foreign_keys=[owner_id], backref="books", lazy="joined")
    current_borrower = relationship(User, foreign_keys=[current_borrower_id], lazy="joined")

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}')>"


