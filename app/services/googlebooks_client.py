"""
Cliente para Google Books API como fallback.
"""
from typing import Any, Dict, List, Optional
import logging

import httpx

from app.config import settings


class GoogleBooksClient:
    def __init__(self, api_key: Optional[str] = None, http_client: Optional[httpx.Client] = None) -> None:
        self.base_url = "https://www.googleapis.com/books/v1"
        self.api_key = api_key or settings.GOOGLE_BOOKS_API_KEY
        self.http = http_client or httpx.Client(timeout=10.0)
        self.logger = logging.getLogger(__name__)

    def search_by_title(self, title: str, limit: int = 5) -> List[Dict[str, Any]]:
        q = f"intitle:{title}"
        return self._search(q=q, limit=limit)

    def search_by_isbn(self, isbn: str, limit: int = 5) -> List[Dict[str, Any]]:
        q = f"isbn:{isbn}"
        return self._search(q=q, limit=limit)

    def _search(self, q: str, limit: int) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/volumes"
        params = {"q": q, "maxResults": limit}
        if self.api_key:
            params["key"] = self.api_key
        self.logger.info("googlebooks _search q=%s limit=%s", q, limit)
        try:
            r = self.http.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            items = data.get("items", [])
            return [self._normalize_item(it) for it in items]
        except Exception as e:
            self.logger.error("googlebooks _search error: %s", e)
            return []

    def _normalize_item(self, it: Dict[str, Any]) -> Dict[str, Any]:
        info = it.get("volumeInfo", {})
        title = info.get("title")
        authors = info.get("authors") or []
        industry_ids = info.get("industryIdentifiers") or []
        isbn = None
        for ident in industry_ids:
            if ident.get("type") in {"ISBN_13", "ISBN_10"}:
                isbn = ident.get("identifier")
                break
        image_links = info.get("imageLinks") or {}
        cover_url = image_links.get("thumbnail")
        description = info.get("description")
        return {
            "title": title,
            "authors": authors,
            "isbn": isbn,
            "cover_url": cover_url,
            "description": description,
            "source": "googlebooks",
        }


