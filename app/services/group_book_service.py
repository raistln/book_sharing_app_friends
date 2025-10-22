"""
Servicio para gestión de libros en grupos.
"""
from typing import List, Optional, Dict, Any
import logging
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
from uuid import UUID

from app.models.group import Group, GroupMember
from app.models.book import Book
from app.models.user import User
from app.schemas.group_book import GroupBookFilter, GroupBookStats


logger = logging.getLogger(__name__)


class GroupBookService:
    def __init__(self, db: Session):
        self.db = db

    def get_group_books(
        self, 
        group_id: UUID, 
        user_id: UUID, 
        filters: Optional[GroupBookFilter] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Book]:
        """Obtener libros de un grupo con filtros."""
        # Verificar que el usuario es miembro del grupo
        if not self._is_group_member(group_id, user_id):
            return None

        # Query base para libros del grupo
        query = self.db.query(Book).join(
            GroupMember, Book.owner_id == GroupMember.user_id
        ).filter(
            and_(
                GroupMember.group_id == group_id,
                Book.is_archived == False  # Solo libros no archivados
            )
        ).options(
            joinedload(Book.owner),
            joinedload(Book.current_borrower)
        )

        # Aplicar filtros
        if filters:
            if filters.search:
                # Filtrado en memoria para soportar acentos/case-insensitive de forma robusta
                from unicodedata import normalize
                def _norm(s: str) -> str:
                    return ''.join(c for c in normalize('NFD', s or '') if ord(c) < 128).lower()
                needle = _norm(filters.search)
                # Obtener por ahora sin el filtro de búsqueda; aplicar resto primero
                pre_query = query
                # El resto de filtros se aplicarán más abajo como siempre
                # Marcamos que haremos filtrado en memoria al final
                memory_search = True
            else:
                memory_search = False
            
            if filters.owner_id:
                query = query.filter(Book.owner_id == filters.owner_id)
            
            if filters.status:
                # Aceptar tanto el valor del enum como su nombre en string
                try:
                    from app.models.book import BookStatus as BookStatusEnum
                    status_value = (
                        filters.status
                        if isinstance(filters.status, str)
                        else filters.status.name
                    )
                    # Comparar contra nombre almacenado
                    query = query.filter(Book.status == status_value)
                except Exception:
                    query = query.filter(Book.status == str(filters.status))
            
            if filters.is_available is not None:
                if filters.is_available:
                    query = query.filter(Book.current_borrower_id.is_(None))
                else:
                    query = query.filter(Book.current_borrower_id.isnot(None))
            
            if filters.genre:
                from sqlalchemy import cast, String, or_
                from app.models.book import BookGenre as BookGenreEnum
                g = filters.genre
                g_enum = g if not isinstance(g, str) else BookGenreEnum(g)
                g_name = g if isinstance(g, str) else getattr(g, "value", str(g))
                query = query.filter(or_(Book.genre == g_enum, cast(Book.genre, String) == g_name))
            
            if filters.isbn:
                query = query.filter(Book.isbn == filters.isbn)

        # Ejecutar query base con filtros excepto búsqueda textual
        try:
            logger.info("executing books query (group=%s, user=%s, search=%s)", str(group_id), str(user_id), filters.search if filters else None)
            books_result = query.order_by(desc(Book.created_at)).offset(offset).limit(limit).all()
        except Exception as exc:
            logger.exception("DB query failed fetching group books: %s", exc)
            return []

        # Aplicar búsqueda textual en memoria si corresponde
        if filters and filters.search:
            def _safe(s):
                try:
                    return _norm(s)
                except Exception:
                    return ""
            books_result = [
                b for b in books_result
                if needle in _safe(b.title) or needle in _safe(b.author)
            ]

        return books_result

    def get_group_book(self, group_id: UUID, book_id: UUID, user_id: UUID) -> Optional[Book]:
        """Obtener un libro específico del grupo."""
        # Verificar que el usuario es miembro del grupo
        if not self._is_group_member(group_id, user_id):
            return None

        return self.db.query(Book).join(
            GroupMember, Book.owner_id == GroupMember.user_id
        ).filter(
            and_(
                GroupMember.group_id == group_id,
                Book.id == book_id,
                Book.is_archived == False
            )
        ).options(
            joinedload(Book.owner),
            joinedload(Book.current_borrower)
        ).first()

    def get_group_book_stats(self, group_id: UUID, user_id: UUID) -> Optional[GroupBookStats]:
        """Obtener estadísticas de libros del grupo."""
        # Verificar que el usuario es miembro del grupo
        if not self._is_group_member(group_id, user_id):
            return None

        # Contar total de libros
        total_books = self.db.query(Book).join(
            GroupMember, Book.owner_id == GroupMember.user_id
        ).filter(
            and_(
                GroupMember.group_id == group_id,
                Book.is_archived == False
            )
        ).count()

        # Contar libros disponibles
        available_books = self.db.query(Book).join(
            GroupMember, Book.owner_id == GroupMember.user_id
        ).filter(
            and_(
                GroupMember.group_id == group_id,
                Book.is_archived == False,
                Book.current_borrower_id.is_(None)
            )
        ).count()

        # Contar libros prestados
        loaned_books = self.db.query(Book).join(
            GroupMember, Book.owner_id == GroupMember.user_id
        ).filter(
            and_(
                GroupMember.group_id == group_id,
                Book.is_archived == False,
                Book.current_borrower_id.isnot(None)
            )
        ).count()

        # Contar libros reservados
        reserved_books = self.db.query(Book).join(
            GroupMember, Book.owner_id == GroupMember.user_id
        ).filter(
            and_(
                GroupMember.group_id == group_id,
                Book.is_archived == False,
                Book.status == "reserved"
            )
        ).count()

        # Contar propietarios únicos
        total_owners = self.db.query(Book.owner_id).join(
            GroupMember, Book.owner_id == GroupMember.user_id
        ).filter(
            and_(
                GroupMember.group_id == group_id,
                Book.is_archived == False
            )
        ).distinct().count()

        # Autor más común
        most_common_author = self.db.query(
            Book.author, func.count(Book.id).label('count')
        ).join(
            GroupMember, Book.owner_id == GroupMember.user_id
        ).filter(
            and_(
                GroupMember.group_id == group_id,
                Book.is_archived == False
            )
        ).group_by(Book.author).order_by(desc('count')).first()

        # Género más común
        most_common_genre = self.db.query(
            Book.genre, func.count(Book.id).label('count')
        ).join(
            GroupMember, Book.owner_id == GroupMember.user_id
        ).filter(
            and_(
                GroupMember.group_id == group_id,
                Book.is_archived == False,
                Book.genre.isnot(None)
            )
        ).group_by(Book.genre).order_by(desc('count')).first()

        return GroupBookStats(
            total_books=total_books,
            available_books=available_books,
            loaned_books=loaned_books,
            reserved_books=reserved_books,
            total_owners=total_owners,
            most_common_author=most_common_author[0] if most_common_author else None,
            most_common_genre=most_common_genre[0] if most_common_genre else None
        )

    def get_group_owners(self, group_id: UUID, user_id: UUID) -> List[User]:
        """Obtener lista de propietarios de libros en el grupo."""
        # Verificar que el usuario es miembro del grupo
        if not self._is_group_member(group_id, user_id):
            return None

        return self.db.query(User).join(
            Book, User.id == Book.owner_id
        ).join(
            GroupMember, Book.owner_id == GroupMember.user_id
        ).filter(
            and_(
                GroupMember.group_id == group_id,
                Book.is_archived == False
            )
        ).distinct().all()

    def search_group_books(
        self, 
        group_id: UUID, 
        user_id: UUID, 
        query: str,
        limit: int = 20
    ) -> List[Book]:
        """Búsqueda de libros en el grupo."""
        # Verificar que el usuario es miembro del grupo
        if not self._is_group_member(group_id, user_id):
            return []

        search_term = f"%{query}%"
        
        return self.db.query(Book).join(
            GroupMember, Book.owner_id == GroupMember.user_id
        ).filter(
            and_(
                GroupMember.group_id == group_id,
                Book.is_archived == False,
                or_(
                    Book.title.ilike(search_term),
                    Book.author.ilike(search_term),
                    Book.isbn.ilike(search_term) if Book.isbn else False
                )
            )
        ).options(
            joinedload(Book.owner),
            joinedload(Book.current_borrower)
        ).limit(limit).all()

    def _is_group_member(self, group_id: UUID, user_id: UUID) -> bool:
        """Verificar si un usuario es miembro de un grupo."""
        return self.db.query(GroupMember).filter(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id
            )
        ).first() is not None
