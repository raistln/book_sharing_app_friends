# Prompt para Windsurf AI: Sistema de Reseñas de Libros

## Contexto del Proyecto
Tengo una aplicación FastAPI de compartir libros con PostgreSQL, SQLAlchemy 2.0, autenticación JWT y sistema de grupos. Necesito agregar un **sistema de reseñas de libros** sin romper ninguna funcionalidad existente.

## Requisitos Funcionales

### 1. Modelo de Datos (SQLAlchemy)
Crear modelo `Review` en `app/models/review.py` con:
- **Relaciones**:
  - `book_id` (FK a `Book`) - libro reseñado
  - `user_id` (FK a `User`) - autor de la reseña
  - `group_id` (FK a `Group`) - grupo donde se comparte
- **Campos**:
  - `id`: UUID primary key
  - `title`: String(200), obligatorio
  - `content`: Text, obligatorio, máximo 1000 caracteres
  - `rating`: Integer, obligatorio, rango 1-5
  - `has_spoilers`: Boolean, default False
  - `created_at`: DateTime con timezone
  - `updated_at`: DateTime con timezone
- **Constraints**:
  - Unique constraint: (book_id, user_id) - una reseña por usuario por libro
  - Check constraint: rating BETWEEN 1 AND 5
  - Index en book_id para consultas rápidas
  - Index en group_id para filtrado por grupo

### 2. Schemas Pydantic
Crear en `app/schemas/review.py`:

**ReviewBase**:
- `title`: str, min 3 chars, max 200 chars
- `content`: str, min 10 chars, max 1000 chars
- `rating`: int, ge=1, le=5
- `has_spoilers`: bool = False

**ReviewCreate** (hereda ReviewBase):
- `book_id`: UUID

**ReviewUpdate**:
- Todos los campos opcionales de ReviewBase

**ReviewResponse** (hereda ReviewBase):
- `id`: UUID
- `book_id`: UUID
- `user_id`: UUID
- `group_id`: UUID
- `author_name`: str (nombre del usuario)
- `created_at`: datetime
- `updated_at`: datetime
- Config: `from_attributes = True`

**BookWithReviews** (extender esquema Book existente):
- Agregar campo opcional `reviews: List[ReviewResponse]`
- Agregar campo `average_rating`: Optional[float]
- Agregar campo `total_reviews`: int = 0

### 3. Endpoints REST (`app/api/reviews.py`)

#### `POST /reviews/`
- **Descripción**: Crear una reseña
- **Body**: ReviewCreate
- **Validaciones**:
  - Usuario autenticado (JWT)
  - Libro existe y no está eliminado
  - Usuario pertenece al mismo grupo que el libro
  - Usuario no ha reseñado este libro previamente
- **Response**: 201 Created, ReviewResponse
- **Errores**:
  - 400: "Ya has reseñado este libro"
  - 403: "No perteneces al grupo de este libro"
  - 404: "Libro no encontrado"
  - 422: Errores de validación

#### `GET /reviews/book/{book_id}`
- **Descripción**: Obtener todas las reseñas de un libro
- **Query params**: 
  - `skip`: int = 0
  - `limit`: int = 20
  - `order_by`: str = "created_at" (opciones: created_at, rating)
- **Validaciones**:
  - Libro existe
  - Usuario autenticado pertenece al grupo del libro
- **Response**: 200 OK, List[ReviewResponse]
- **Errores**:
  - 403: "No tienes acceso a este libro"
  - 404: "Libro no encontrado"

#### `GET /reviews/{review_id}`
- **Descripción**: Obtener una reseña específica
- **Validaciones**:
  - Reseña existe
  - Usuario pertenece al grupo de la reseña
- **Response**: 200 OK, ReviewResponse
- **Errores**:
  - 403: "No tienes acceso a esta reseña"
  - 404: "Reseña no encontrada"

#### `PUT /reviews/{review_id}`
- **Descripción**: Actualizar reseña propia
- **Body**: ReviewUpdate
- **Validaciones**:
  - Usuario autenticado es el autor de la reseña
  - Reseña existe
- **Response**: 200 OK, ReviewResponse
- **Errores**:
  - 403: "No puedes editar reseñas de otros usuarios"
  - 404: "Reseña no encontrada"

#### `DELETE /reviews/{review_id}`
- **Descripción**: Eliminar reseña propia (hard delete)
- **Validaciones**:
  - Usuario autenticado es el autor de la reseña
  - Reseña existe
- **Response**: 204 No Content
- **Errores**:
  - 403: "No puedes eliminar reseñas de otros usuarios"
  - 404: "Reseña no encontrada"

#### `GET /reviews/my-reviews`
- **Descripción**: Obtener todas las reseñas del usuario autenticado
- **Query params**: skip, limit
- **Response**: 200 OK, List[ReviewResponse]

### 4. Modificaciones al Endpoint de Libros
**Actualizar `GET /books/{book_id}` en `app/api/books.py`**:
- Agregar query param opcional: `include_reviews: bool = False`
- Si `include_reviews=True`:
  - Incluir lista de reseñas del libro
  - Calcular y agregar `average_rating`
  - Agregar `total_reviews`
- Usar eager loading para evitar N+1 queries

### 5. Servicio de Lógica de Negocio
Crear `app/services/review_service.py` con funciones:

```python
async def create_review(
    db: AsyncSession,
    review_data: ReviewCreate,
    user_id: UUID
) -> Review:
    """
    Crea una reseña con validaciones de permisos
    Logs: Creación exitosa con user_id, book_id
    """

async def get_book_reviews(
    db: AsyncSession,
    book_id: UUID,
    user_id: UUID,
    skip: int = 0,
    limit: int = 20,
    order_by: str = "created_at"
) -> List[Review]:
    """
    Obtiene reseñas con validación de permisos de grupo
    Incluye eager loading de User para author_name
    """

async def update_review(
    db: AsyncSession,
    review_id: UUID,
    review_data: ReviewUpdate,
    user_id: UUID
) -> Review:
    """
    Actualiza reseña con validación de propiedad
    Actualiza updated_at automáticamente
    """

async def delete_review(
    db: AsyncSession,
    review_id: UUID,
    user_id: UUID
) -> None:
    """
    Elimina reseña (hard delete) con validación de propiedad
    """

async def calculate_book_rating(
    db: AsyncSession,
    book_id: UUID
) -> tuple[float, int]:
    """
    Calcula rating promedio y total de reseñas
    Returns: (average_rating, total_reviews)
    """

async def user_can_review_book(
    db: AsyncSession,
    user_id: UUID,
    book_id: UUID
) -> bool:
    """
    Verifica si usuario pertenece al grupo del libro
    """
```

### 6. Migración de Alembic
- Crear migración en `alembic/versions/` con:
  - Tabla `reviews` con todas las columnas
  - Foreign keys con ON DELETE CASCADE
  - Indexes necesarios
  - Constraints (unique, check)
- Comando: `alembic revision --autogenerate -m "add_reviews_table"`

### 7. Testing Completo

#### Tests Unitarios (`tests/test_review_service_unit.py`):
- `test_create_review_success`
- `test_create_review_duplicate_fails`
- `test_create_review_invalid_rating_fails`
- `test_create_review_user_not_in_group_fails`
- `test_update_review_success`
- `test_update_review_not_owner_fails`
- `test_delete_review_success`
- `test_delete_review_not_owner_fails`
- `test_calculate_book_rating`
- Usar mocks para db session

#### Tests de Integración (`tests/test_review_endpoints.py`):
- `test_create_review_integration`
- `test_get_book_reviews_integration`
- `test_get_review_by_id_integration`
- `test_update_review_integration`
- `test_delete_review_integration`
- `test_my_reviews_integration`
- `test_book_with_reviews_integration`
- `test_review_permissions_across_groups`
- Usar TestClient de FastAPI

#### Tests de Flujo Completo (`tests/test_review_complete_flow.py`):
- Flujo: Crear usuario → Crear grupo → Crear libro → Crear reseña → Editar → Eliminar
- Validar cálculo de rating promedio
- Validar permisos entre grupos diferentes

### 8. Requisitos de Calidad de Código

#### Manejo de Errores:
- Usar HTTPException con códigos apropiados
- Mensajes de error descriptivos y específicos
- Nunca exponer información sensible en errores
- Formato consistente:
```python
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="No puedes editar reseñas de otros usuarios"
)
```

#### Logging:
- Log en puntos críticos:
  - Creación de reseña: `logger.info(f"Review created: {review.id} by user {user_id} for book {book_id}")`
  - Errores de permisos: `logger.warning(f"Permission denied: user {user_id} attempted to access review {review_id}")`
  - Eliminación: `logger.info(f"Review deleted: {review_id} by user {user_id}")`
- Usar logger configurado en `app/config.py`

#### Seguridad:
- Validar permisos en cada endpoint
- Sanitizar inputs (Pydantic lo hace automáticamente)
- Prevenir inyección SQL (SQLAlchemy ORM)
- Rate limiting en endpoints públicos (si aplica)

#### Optimización:
- Usar `selectinload` para evitar N+1 queries al cargar reseñas con usuario
- Indexes en columnas de búsqueda frecuente
- Limitar resultados con paginación

## Estructura de Archivos a Crear/Modificar

```
Crear:
├── app/models/review.py
├── app/schemas/review.py
├── app/api/reviews.py
├── app/services/review_service.py
├── tests/test_review_service_unit.py
├── tests/test_review_endpoints.py
└── tests/test_review_complete_flow.py

Modificar:
├── app/api/books.py (agregar include_reviews)
├── app/schemas/book.py (agregar BookWithReviews)
├── app/main.py (incluir router de reviews)
└── alembic/versions/XXXXX_add_reviews_table.py (nueva migración)
```

## Comandos para Ejecutar

```bash
# Crear migración
alembic revision --autogenerate -m "add_reviews_table"

# Aplicar migración
alembic upgrade head

# Ejecutar tests
pytest tests/test_review_service_unit.py -v
pytest tests/test_review_endpoints.py -v
pytest tests/test_review_complete_flow.py -v

# Coverage
pytest --cov=app/services/review_service --cov=app/api/reviews
```

## Criterios de Aceptación

✅ Todos los tests pasan (unitarios, integración, flujo completo)
✅ Coverage mínimo del 90% en código nuevo
✅ Migración de Alembic se aplica sin errores
✅ Endpoints documentados en Swagger (/docs)
✅ Manejo consistente de errores con códigos HTTP correctos
✅ Logs informativos en operaciones críticas
✅ Validaciones de permisos funcionan correctamente
✅ No se rompe ninguna funcionalidad existente
✅ Cálculo de rating promedio es preciso
✅ Una reseña por usuario por libro (constraint funciona)

## Notas Importantes

- **NO usar localStorage o sessionStorage** en el backend
- **Seguir convenciones del proyecto existente** (imports, naming, estructura)
- **Usar async/await** en todas las operaciones de base de datos
- **Documentar funciones con docstrings** explicando parámetros y returns
- **Respetar el estilo de código** del proyecto (type hints, PEP 8)
- **Probar manualmente en /docs** después de implementar

---

**Genera el código completo siguiendo estos requisitos exactamente. Pregunta si necesitas clarificación en algún punto.**
