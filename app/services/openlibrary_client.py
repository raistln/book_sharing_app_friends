"""
Cliente para OpenLibrary API: búsqueda por título y por ISBN.
"""
from typing import Any, Dict, List, Optional
import logging

import httpx

from app.config import settings


class OpenLibraryClient:
    def __init__(self, base_url: Optional[str] = None, http_client: Optional[httpx.Client] = None) -> None:
        self.base_url = base_url or settings.OPENLIBRARY_BASE_URL.rstrip("/")
        self.http = http_client or httpx.Client(timeout=10.0)
        self.logger = logging.getLogger(__name__)

    def search_by_title(self, title: str, limit: int = 5) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/search.json"
        params = {"q": title, "limit": limit}
        self.logger.info("openlibrary search_by_title title=%s limit=%s", title, limit)
        try:
            r = self.http.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            docs = data.get("docs", [])
            return [self._normalize_doc(d) for d in docs]
        except Exception as e:
            self.logger.error("openlibrary search_by_title error: %s", e)
            return []

    def search_by_isbn(self, isbn: str) -> List[Dict[str, Any]]:
        # Usamos el endpoint de búsqueda por título con filtro isbn para consistencia
        url = f"{self.base_url}/search.json"
        params = {"q": f"isbn:{isbn}", "limit": 5}
        self.logger.info("openlibrary search_by_isbn isbn=%s", isbn)
        try:
            r = self.http.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            docs = data.get("docs", [])
            return [self._normalize_doc(d) for d in docs]
        except Exception as e:
            self.logger.error("openlibrary search_by_isbn error: %s", e)
            return []

    def _normalize_doc(self, d: Dict[str, Any]) -> Dict[str, Any]:
        title = d.get("title")
        authors = d.get("author_name") or []
        isbns = d.get("isbn") or []
        cover_id = d.get("cover_i")
        cover_url = (
            f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id is not None else None
        )
        description = None
        return {
            "title": title,
            "authors": authors,
            "isbn": isbns[0] if isbns else None,
            "cover_url": cover_url,
            "description": description,
            "source": "openlibrary",
        }


