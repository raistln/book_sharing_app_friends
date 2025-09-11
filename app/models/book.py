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


class BookType(enum.Enum):
    novel = "novel"
    comic = "comic"
    manga = "manga"
    graphic_novel = "graphic_novel"
    short_story = "short_story"
    poetry = "poetry"
    essay = "essay"
    biography = "biography"
    autobiography = "autobiography"
    other = "other"


class BookGenre(enum.Enum):
    # Ficción
    fiction = "fiction"
    science_fiction = "science_fiction"
    fantasy = "fantasy"
    mystery = "mystery"
    thriller = "thriller"
    horror = "horror"
    romance = "romance"
    historical_fiction = "historical_fiction"
    literary_fiction = "literary_fiction"
    adventure = "adventure"
    western = "western"
    dystopian = "dystopian"
    magical_realism = "magical_realism"
    
    # No ficción
    non_fiction = "non_fiction"
    biography = "biography"
    autobiography = "autobiography"
    history = "history"
    philosophy = "philosophy"
    psychology = "psychology"
    science = "science"
    technology = "technology"
    business = "business"
    self_help = "self_help"
    travel = "travel"
    cooking = "cooking"
    health = "health"
    religion = "religion"
    politics = "politics"
    economics = "economics"
    education = "education"
    
    # Otros
    children = "children"
    young_adult = "young_adult"
    reference = "reference"
    academic = "academic"
    other = "other"


class Book(Base):
    __tablename__ = "books"

    # Campos principales
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False, index=True)
    author = Column(String(150), nullable=False, index=True)
    isbn = Column(String(20), nullable=True, unique=False, index=True)
    cover_url = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Clasificación
    book_type = Column(Enum(BookType, name="book_type"), nullable=True, index=True)
    genre = Column(Enum(BookGenre, name="book_genre"), nullable=True, index=True)

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


