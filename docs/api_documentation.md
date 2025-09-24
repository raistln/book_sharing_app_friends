# Documentación de la API

## Tabla de Contenidos

- [Búsqueda](#búsqueda)
- [Préstamos](#préstamos)

---

## Búsqueda

### `GET /search/books`

Busca libros por título o ISBN en múltiples fuentes de datos.

**Parámetros:**

| Nombre | Tipo | Requerido | Descripción |
|--------|------|-----------|-------------|
| `q` | `str` | Sí |  |
| `limit` | `int` | Sí |  |

**Respuestas:**

- **200**: Lista de libros encontrados
  ```json
  {}
  ```

- **400**: Parámetros de búsqueda inválidos
  ```json
  {
    "detail": "El término de búsqueda no puede estar vacío"
  }
  ```

- **429**: Límite de tasa excedido
  ```json
  {
    "detail": "Demasiadas solicitudes. Por favor, intente de nuevo más tarde."
  }
  ```

- **500**: Error interno del servidor
  ```json
  {
    "detail": "Error en el servicio de búsqueda"
  }
  ```

**Documentación detallada:**
```python
Busca libros por título o ISBN en múltiples fuentes de datos.

    Este endpoint realiza búsquedas utilizando servicios externos como OpenLibrary
    con fallback a Google Books si es necesario. Soporta búsqueda por título o ISBN
    (tanto de 10 como de 13 dígitos).

    Args:
        q (str): Término de búsqueda (título o ISBN).
        limit (int, optional): Número máximo de resultados a devolver. Por defecto 5.

    Returns:
        List[Dict[str, Any]]: Lista de diccionarios con la información de los libros encontrados.

    Raises:
        HTTPException:
            - 400: Si el término de búsqueda está vacío o es inválido
            - 429: Si se excede el límite de tasa de solicitudes
            - 500: Si ocurre un error en el servicio de búsqueda
```


## Préstamos

### `POST /loans/loan`

Immediate loan (request + approve) for compatibility with existing tests.

**Parámetros:**

| Nombre | Tipo | Requerido | Descripción |
|--------|------|-----------|-------------|
| `book_id` | `UUID` | Sí |  |
| `borrower_id` | `UUID` | Sí |  |
| `db` | `Session` | Sí |  |

**Documentación detallada:**
```python
Immediate loan (request + approve) for compatibility with existing tests.
```

