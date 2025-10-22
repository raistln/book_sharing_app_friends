"""
Servicio de búsqueda de libros con fallback: primero OpenLibrary, luego Google Books.
"""
from typing import Any, Dict, List, Optional
import time
import logging

from app.services.openlibrary_client import OpenLibraryClient
from app.services.googlebooks_client import GoogleBooksClient
from app.services.cache import RedisCache


class BookSearchService:
    def __init__(
        self,
        openlibrary: Optional[OpenLibraryClient] = None,
        googlebooks: Optional[GoogleBooksClient] = None,
        cache: Optional[RedisCache] = None,
    ) -> None:
        self.openlibrary = openlibrary or OpenLibraryClient()
        self.googlebooks = googlebooks or GoogleBooksClient()
        self.cache = cache or RedisCache()

    def search(self, *, title: Optional[str] = None, isbn: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        if not title and not isbn:
            return []

        logger = logging.getLogger(__name__)
        t0 = time.perf_counter()

        # Intentar caché
        key = self._make_cache_key(title=title, isbn=isbn, limit=limit)
        cached = self.cache.get_json(key)
        if cached is not None:
            duration_ms = int((time.perf_counter() - t0) * 1000)
            logger.info(
                "search cache_hit key=%s query={title=%s isbn=%s limit=%s} duration_ms=%s results=%s",
                key,
                title,
                isbn,
                limit,
                duration_ms,
                len(cached),
            )
            return cached

        results: List[Dict[str, Any]] = []
        provider_duration_ms: Optional[int] = None
        provider: Optional[str] = None
        try:
            if isbn:
                p0 = time.perf_counter()
                results = self.openlibrary.search_by_isbn(isbn)
                provider_duration_ms = int((time.perf_counter() - p0) * 1000)
                provider = "openlibrary"
            elif title:
                p0 = time.perf_counter()
                results = self.openlibrary.search_by_title(title, limit=limit)
                provider_duration_ms = int((time.perf_counter() - p0) * 1000)
                provider = "openlibrary"
        except Exception:
            results = []

        if not results:
            try:
                if isbn:
                    p0 = time.perf_counter()
                    results = self.googlebooks.search_by_isbn(isbn, limit=limit)
                    provider_duration_ms = int((time.perf_counter() - p0) * 1000)
                    provider = "googlebooks"
                elif title:
                    p0 = time.perf_counter()
                    results = self.googlebooks.search_by_title(title, limit=limit)
                    provider_duration_ms = int((time.perf_counter() - p0) * 1000)
                    provider = "googlebooks"
            except Exception:
                results = []

        # Limitar cantidad y normalizar estructura común para el frontend
        normalized: List[Dict[str, Any]] = []
        for r in results[:limit]:
            normalized.append(
                {
                    "title": r.get("title"),
                    "authors": r.get("authors") or [],
                    "isbn": r.get("isbn"),
                    "cover_url": r.get("cover_url"),
                    "description": r.get("description"),
                    "publisher": r.get("publisher"),
                    "published_date": r.get("published_date"),
                    "page_count": r.get("page_count"),
                    "language": r.get("language"),
                    "source": r.get("source"),
                }
            )
        # Guardar en caché y registrar métricas
        self.cache.set_json(key, normalized)
        total_ms = int((time.perf_counter() - t0) * 1000)
        logger.info(
            "search cache_miss key=%s provider=%s provider_ms=%s total_ms=%s results=%s",
            key,
            provider,
            provider_duration_ms,
            total_ms,
            len(normalized),
        )
        return normalized

    def _make_cache_key(self, *, title: Optional[str], isbn: Optional[str], limit: int) -> str:
        # v2: incluye publisher, published_date, page_count, language
        if isbn:
            return f"search:v2:isbn:{isbn}:{limit}"
        t = (title or "").strip().lower().replace(" ", "+")
        return f"search:v2:title:{t}:{limit}"


