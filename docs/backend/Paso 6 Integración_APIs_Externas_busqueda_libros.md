## 🌐 Paso 6: Integración de APIs Externas (OpenLibrary + Google Books)

Este paso agrega búsqueda de libros contra servicios externos. Se usa OpenLibrary como fuente principal y Google Books como fallback. Se expone un endpoint unificado `GET /search/books` para buscar por título o ISBN.

### 🎯 Objetivos
- Cliente `OpenLibrary` para búsquedas por título/ISBN.
- Cliente `Google Books` como respaldo.
- Servicio de orquestación con fallback y normalización de resultados.
- Endpoint `GET /search/books` listo para consumo del frontend.

---

### 1) Cliente OpenLibrary
Archivo: `app/services/openlibrary_client.py`

- `search_by_title(title, limit)`
- `search_by_isbn(isbn)`
- Normaliza campos: `title`, `authors`, `isbn`, `cover_url`, `description`, `source="openlibrary"`.

Notas:
- Base URL configurable en `app/config.py` (`OPENLIBRARY_BASE_URL`).
- Construye portada con `covers.openlibrary.org` si hay `cover_i`.

---

### 2) Cliente Google Books (fallback)
Archivo: `app/services/googlebooks_client.py`

- `search_by_title(title, limit)`
- `search_by_isbn(isbn, limit)`
- Normaliza campos: `title`, `authors`, `isbn` (de `industryIdentifiers`), `cover_url`, `description`, `source="googlebooks"`.

Notas:
- Usa `GOOGLE_BOOKS_API_KEY` si está disponible (opcional en dev).

---

### 3) Servicio de Búsqueda con Fallback
Archivo: `app/services/book_search_service.py`

Flujo:
1. Si se pasa `isbn`, intenta OpenLibrary por ISBN; si no hay resultados o falla, intenta Google Books.
2. Si se pasa `title`, intenta OpenLibrary por título; si no hay resultados o falla, intenta Google Books.
3. Devuelve lista normalizada con máximo `limit` elementos.

Campos normalizados por elemento:
- `title`, `authors[]`, `isbn`, `cover_url`, `description`, `source`.

---

### 4) Endpoint de Búsqueda
Archivo: `app/api/search.py` (registrado en `app/main.py`)

Ruta:
- `GET /search/books?q=<título_o_isbn>&limit=5`

Detalles:
- Si `q` parece un ISBN (solo dígitos con 10/13 caracteres, ignorando guiones/espacios), busca por ISBN.
- En otro caso, busca por título.
- Retorna una lista (posiblemente vacía si la API externa falla o no hay resultados).

---

### 5) Ejemplos de uso

Swagger:
- Abrir `/docs` → `GET /search/books` → Param `q`.

CLI:
```bash
# Por título
curl "http://localhost:8000/search/books?q=The%20Hobbit&limit=3"

# Por ISBN (con o sin guiones)
curl "http://localhost:8000/search/books?q=9780261102217&limit=3"
curl "http://localhost:8000/search/books?q=978-0261102217&limit=3"
```

Respuesta (ejemplo abreviado):
```json
[
  {
    "title": "The Hobbit",
    "authors": ["J. R. R. Tolkien"],
    "isbn": "9780261102217",
    "cover_url": "https://...",
    "description": "...",
    "source": "openlibrary" | "googlebooks"
  }
]
```

---

### 6) Tests
Archivo: `tests/test_search.py`

- `test_search_by_title_returns_results_or_empty`
- `test_search_by_isbn_returns_results_or_empty`

Los tests no fuerzan resultados porque dependen de servicios externos y posibles rate limits.

---

### 7) Consideraciones y mejoras
- Caching de resultados (e.g. Redis) para reducir llamadas y latencia.
- Retries con backoff ante fallos de red.
- Mejor heurística ISBN (validación checksum ISBN-10/13).
- Localización de títulos/autores.
- Enriquecimiento con más metadatos (páginas, categorías, etc.).


