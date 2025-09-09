"""
Endpoint de búsqueda automática de libros usando OpenLibrary con fallback a Google Books.
"""
from fastapi import APIRouter, Query

from app.services.book_search_service import BookSearchService


router = APIRouter(prefix="/search", tags=["search"])


@router.get("/books")
def search_books(q: str = Query("", description="Título o ISBN"), limit: int = 5):
    service = BookSearchService()
    if not q:
        return []
    # Heurística simple: si q es dígitos/guiones y longitud típica, tratar como ISBN
    cleaned = q.replace("-", "").replace(" ", "")
    is_isbn = cleaned.isdigit() and len(cleaned) in {10, 13}
    if is_isbn:
        return service.search(isbn=cleaned, limit=limit)
    return service.search(title=q, limit=limit)


