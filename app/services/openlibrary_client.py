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
            
            results = []
            for doc in docs:
                # Intentar enriquecer con datos de la edición si hay ISBN
                isbns = doc.get("isbn") or []
                enriched = None
                
                if isbns:
                    # Intentar obtener detalles completos del primer ISBN
                    for isbn in isbns[:2]:  # Probar con los primeros 2 ISBNs
                        try:
                            edition_url = f"{self.base_url}/isbn/{isbn}.json"
                            edition_r = self.http.get(edition_url, timeout=2.0)
                            if edition_r.status_code == 200:
                                edition_data = edition_r.json()
                                enriched = self._normalize_edition(edition_data)
                                if enriched:
                                    break
                        except:
                            continue
                
                # Si no pudimos enriquecer, usar datos básicos
                if not enriched:
                    enriched = self._normalize_doc(doc)
                
                results.append(enriched)
            
            return results
        except Exception as e:
            self.logger.error("openlibrary search_by_title error: %s", e)
            return []

    def search_by_isbn(self, isbn: str) -> List[Dict[str, Any]]:
        # Intentar primero con el endpoint de ISBN que da más detalles
        url = f"{self.base_url}/isbn/{isbn}.json"
        self.logger.info("openlibrary search_by_isbn isbn=%s", isbn)
        try:
            r = self.http.get(url)
            if r.status_code == 200:
                data = r.json()
                # Este endpoint devuelve un solo libro con detalles completos
                normalized = self._normalize_edition(data)
                return [normalized] if normalized else []
        except Exception as e:
            self.logger.debug("openlibrary isbn endpoint failed: %s", e)
        
        # Fallback: usar búsqueda normal
        try:
            url = f"{self.base_url}/search.json"
            params = {"q": f"isbn:{isbn}", "limit": 5}
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
        
        # Descripción - puede venir en varios campos
        description = d.get("description")
        if isinstance(description, list):
            description = description[0] if description else None
        
        # Extraer campos adicionales
        publishers = d.get("publisher") or []
        publisher = publishers[0] if publishers else None
        
        # Fecha de publicación - intentar varios campos
        published_date = None
        # Primero intentar publish_year (array de años)
        publish_years = d.get("publish_year") or []
        if publish_years:
            published_date = str(publish_years[0])
        # Si no, intentar first_publish_year
        if not published_date:
            first_year = d.get("first_publish_year")
            if first_year:
                published_date = str(first_year)
        # Si no, intentar publish_date (array de fechas)
        if not published_date:
            publish_dates = d.get("publish_date") or []
            if publish_dates:
                published_date = publish_dates[0]
        
        # Número de páginas - intentar varios campos
        page_count = d.get("number_of_pages_median")
        if not page_count:
            # Intentar con el array de páginas
            pages_array = d.get("number_of_pages") or []
            if pages_array and isinstance(pages_array, list):
                page_count = pages_array[0] if pages_array else None
            elif isinstance(pages_array, int):
                page_count = pages_array
        
        # Idioma (toma el primero si hay varios)
        languages = d.get("language") or []
        language = languages[0] if languages else None
        
        result = {
            "title": title,
            "authors": authors,
            "isbn": isbns[0] if isbns else None,
            "cover_url": cover_url,
            "description": description,
            "publisher": publisher,
            "published_date": published_date,
            "page_count": page_count,
            "language": language,
            "source": "openlibrary",
        }
        
        # Log para debugging
        self.logger.debug(
            "OpenLibrary normalized: title=%s publisher=%s date=%s pages=%s lang=%s",
            title, publisher, published_date, page_count, language
        )
        
        return result

    def _normalize_edition(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normaliza datos del endpoint /isbn/{isbn}.json que devuelve una edición completa."""
        try:
            title = data.get("title")
            if not title:
                return None
            
            # Autores - viene como lista de objetos {key: "/authors/..."}
            authors = []
            author_data = data.get("authors") or []
            for author in author_data:
                if isinstance(author, dict):
                    # Necesitaríamos hacer otra llamada para obtener el nombre
                    # Por ahora, extraemos la key
                    author_key = author.get("key", "")
                    if author_key:
                        # Extraer nombre del key si es posible
                        authors.append(author_key.split("/")[-1].replace("_", " ").title())
            
            # ISBN
            isbn_10 = data.get("isbn_10")
            isbn_13 = data.get("isbn_13")
            isbn = None
            if isbn_13:
                isbn = isbn_13[0] if isinstance(isbn_13, list) else isbn_13
            elif isbn_10:
                isbn = isbn_10[0] if isinstance(isbn_10, list) else isbn_10
            
            # Portada
            covers = data.get("covers") or []
            cover_id = covers[0] if covers else None
            cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else None
            
            # Descripción
            description = data.get("description")
            if isinstance(description, dict):
                description = description.get("value")
            
            # Editorial
            publishers = data.get("publishers") or []
            publisher = publishers[0] if publishers else None
            
            # Fecha de publicación
            publish_date = data.get("publish_date")
            
            # Número de páginas
            page_count = data.get("number_of_pages")
            
            # Idiomas
            languages = data.get("languages") or []
            language = None
            if languages:
                lang_obj = languages[0]
                if isinstance(lang_obj, dict):
                    language = lang_obj.get("key", "").split("/")[-1]
                else:
                    language = str(lang_obj)
            
            result = {
                "title": title,
                "authors": authors,
                "isbn": isbn,
                "cover_url": cover_url,
                "description": description,
                "publisher": publisher,
                "published_date": publish_date,
                "page_count": page_count,
                "language": language,
                "source": "openlibrary",
            }
            
            self.logger.debug(
                "OpenLibrary edition normalized: title=%s publisher=%s date=%s pages=%s lang=%s",
                title, publisher, publish_date, page_count, language
            )
            
            return result
        except Exception as e:
            self.logger.error("Error normalizing OpenLibrary edition: %s", e)
            return None


