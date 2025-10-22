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


class BookCondition(enum.Enum):
    new = "new"
    like_new = "like_new"
    good = "good"
    fair = "fair"
    poor = "poor"


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
    author = Column(String(150), nullable=True, index=True)
    isbn = Column(String(20), nullable=True, unique=False, index=True)
    cover_url = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    publisher = Column(String(200), nullable=True)
    published_date = Column(String(50), nullable=True)
    page_count = Column(String(10), nullable=True)
    language = Column(String(10), nullable=True)
    
    # Clasificación
    genre = Column(Enum(BookGenre, name="book_genre"), nullable=True, index=True)
    condition = Column(Enum(BookCondition, name="book_condition"), nullable=True, server_default="good")

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


