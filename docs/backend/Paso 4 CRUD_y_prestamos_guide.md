# 🧩 Paso 4 — CRUD de Libros y Préstamos (Swagger + ejemplos)

Esta guía te explica, paso a paso, cómo usar el CRUD básico de libros y el MVP de préstamos (prestar/devolver) que hemos implementado. Sigue la secuencia para aprender y comprobar que todo funciona.

---

## 1) Requisitos previos

- PostgreSQL en Docker corriendo:
```bash
docker compose up -d postgres
```
- Migraciones aplicadas (ya generadas en pasos previos):
```bash
poetry run alembic upgrade head
```
- Servidor FastAPI levantado:
```bash
poetry run uvicorn app.main:app --port 8001 --reload
```

Swagger UI: `http://127.0.0.1:8001/docs`

---

## 2) Modelos y rutas relevantes

- Modelos SQLAlchemy:
  - `app/models/book.py`
  - `app/models/loan.py`
- Schemas Pydantic:
  - `app/schemas/book.py`
  - `app/schemas/loan.py`
- Routers FastAPI:
  - Libros: `app/api/books.py` → prefijo `/api/books`
  - Préstamos: `app/api/loans.py` → prefijo `/api/loans`
- Registro de rutas: `app/main.py`

---

## 3) Preparar datos: crear un usuario de prueba

Los libros necesitan un `owner_id` (UUID) de un usuario existente. Crea un usuario y copia su `id`:
```bash
docker compose exec -T postgres psql -U postgres -d book_sharing -c "INSERT INTO users (id, username, email, password_hash, is_active, is_verified) VALUES (gen_random_uuid(), 'tester', 'tester@example.com', 'hash', true, false) RETURNING id, username;"
```
Ejemplo de salida:
```
                  id                  | username
--------------------------------------+---------
09b008fd-aba8-4b07-a4d7-e630361253b0 | tester
```
Usaremos ese `id` como `owner_id`.

---

## 4) CRUD de Libros en Swagger

Abre `http://127.0.0.1:8001/docs` y busca el grupo `books`.

### 4.1 Crear libro (POST /api/books/)
Body mínimo recomendado:
```json
{
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "owner_id": "09b008fd-aba8-4b07-a4d7-e630361253b0"
}
```
Campos opcionales: `isbn`, `cover_url`, `description`.

Respuesta esperada (201): objeto del libro con `id`, `status: "available"`, `created_at`, etc.

### 4.2 Listar libros (GET /api/books/)
Devuelve los libros no archivados (`is_archived == false`).

### 4.3 Obtener detalle (GET /api/books/{id})
Proporciona un `id` válido devuelto por el POST o el listado.

### 4.4 Actualizar libro (PUT /api/books/{id})
Ejemplos de body:
- Cambiar estado:
```json
{ "status": "reserved" }
```
- Añadir descripción/ISBN:
```json
{ "description": "Edición revisada", "isbn": "9780132350884" }
```

### 4.5 Borrado lógico (DELETE /api/books/{id})
Marca `is_archived = true`. El libro ya no aparecerá en listados normales.

---

## 5) MVP de Préstamos en Swagger

Abre el grupo `loans`.

### 5.1 Prestar un libro (POST /api/loans/loan)
Parámetros (query params):
- `book_id`: UUID del libro
- `borrower_id`: UUID del usuario que recibe el libro

Efectos:
- Crea un `Loan` con estado `active`.
- Cambia el `Book.status` a `loaned` y fija `current_borrower_id`.

Ejemplo (valores de ejemplo):
```
book_id = d2ba952f-0a88-4e7f-82cb-b6dece608743
borrower_id = 09b008fd-aba8-4b07-a4d7-e630361253b0
```

### 5.2 Devolver un libro (POST /api/loans/return)
Parámetro (query param):
- `book_id`: UUID del libro

Efectos:
- Cambia el `Loan` activo a `returned` (pone `returned_at`).
- Marca el libro como `available` y limpia `current_borrower_id`.

---

## 6) Buenas prácticas y notas

- Soft delete en `Book`:
  - `DELETE /api/books/{id}` no borra físicamente. Útil para conservar historial.
- Estados de `Book` (`BookStatus`): `available`, `loaned`, `reserved`.
- `current_borrower_id`: campo práctico para saber “quién lo tiene ahora” (MVP). Más adelante, la fuente de verdad será `Loan`.

---

## 7) Errores comunes y soluciones (Troubleshooting)

- 422 uuid_parsing (`owner_id` inválido):
  - Causa: UUID con espacios o incompleto.
  - Solución: usa un UUID completo, sin espacios. Ejemplo: `"09b008fd-aba8-4b07-a4d7-e630361253b0"`.

- 422 json_invalid:
  - Causa: JSON mal formateado (comillas “curvas”, caracteres ocultos, comas sobrantes).
  - Solución: reescribe el JSON a mano, usa comillas rectas, sin comas finales.

- 500 Internal Server Error por base de datos (credenciales):
  - Causa: URL de BD con usuario/clave incorrectos.
  - Verifica `alembic.ini` → `sqlalchemy.url = postgresql://postgres:password@localhost:5432/book_sharing`
  - Reinicia el servidor para que tome la configuración.

- No conecta al servidor (`/health` no responde):
  - Asegúrate de tener el servidor en el puerto correcto (ej. 8001).
  - Reintenta:
    ```bash
    poetry run uvicorn app.main:app --port 8001 --reload
    ```

---

## 8) Secuencia de prueba sugerida (resumen)

1. Levantar Docker PostgreSQL y el servidor FastAPI.
2. Crear usuario de prueba y copiar el UUID.
3. Crear libro (POST /api/books/).
4. Listar libros (GET /api/books/).
5. Prestar libro (POST /api/loans/loan) → comprobar `status=loaned` y `current_borrower_id`.
6. Devolver libro (POST /api/loans/return) → comprobar `status=available` y `current_borrower_id=null`.
7. Borrado lógico del libro (DELETE /api/books/{id}).

---

## 9) Qué has aprendido

- Diseñar y exponer un CRUD con FastAPI, SQLAlchemy y Pydantic.
- Modelar un flujo básico de préstamos con mínimo de endpoints.
- Usar Swagger para probar rápidamente la API.
- Diagnosticar errores típicos (422, 500) y solucionarlos.

> Consulta también las guías previas en `app_information/` (Paso 1, Paso 2, Paso 3) para contexto de setup y base de datos.

