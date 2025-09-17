# 📘 Guía paso a paso: Modelos y Base de Datos (User y Book) + Alembic

Esta guía documenta de forma práctica lo realizado para crear los modelos, configurar Alembic y aplicar la primera migración en el proyecto.

---

## 1) Prerrequisitos

- Python y Poetry instalados.
- Docker Desktop instalado y en ejecución.
- Proyecto clonado en `D:/IAs/book_sharing_app_friends` (Windows).

Comprobación rápida:
```bash
poetry --version
docker --version
```

---

## 2) Variables de entorno

Crear un archivo `.env` en la raíz del proyecto con el siguiente contenido (o usar `env.example` como base):
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/book_sharing
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENLIBRARY_BASE_URL=https://openlibrary.org
GOOGLE_BOOKS_API_KEY=
DEBUG=True
ENVIRONMENT=development
```

Notas:
- `DATABASE_URL` debe apuntar a tu instancia local de PostgreSQL (en Docker Compose ya está configurado ese usuario/contraseña por defecto).

---

## 3) Levantar PostgreSQL con Docker

Desde la carpeta del proyecto:
```bash
# Levantar solo el servicio de postgres
docker compose up -d postgres
```

Verificar que el contenedor está corriendo:
```bash
docker ps
```

---

## 4) Configuración de SQLAlchemy y Alembic

Ya existen los archivos base:
- `app/config.py` (carga variables `.env`)
- `app/database.py` (engine/SessionLocal/Base)
- `alembic/env.py` (config de Alembic)
- `alembic.ini`

Ajustes realizados:
- En `alembic.ini` se corrigió el formato de versión para evitar error de interpolación:
```ini
version_num_format = %%04d
```
- En `alembic/env.py` se aseguró que Alembic use `sqlalchemy.url` del `alembic.ini` si está presente:
```python
def get_url():
    ini_url = config.get_main_option("sqlalchemy.url")
    return ini_url or settings.DATABASE_URL
```
- En `alembic/env.py` se importan los modelos para soportar autogenerate:
```python
from app.models import user
from app.models import book
```

---

## 5) Modelo User (existente)

Archivo: `app/models/user.py`
- Tabla: `users`
- Campos: `id (UUID)`, `username`, `email`, `password_hash`, `is_active`, `is_verified`, `created_at`, `updated_at`, `full_name`, `bio`, `avatar_url`.

Schemas Pydantic en `app/schemas/user.py`.

---

## 6) Modelo Book (nuevo)

Archivo creado: `app/models/book.py`
- Tabla: `books`
- Enum de estado: `available | loaned | reserved`
- FK: `owner_id -> users.id`
- Índices: `title`, `author`, `isbn`, `owner_id`

Schemas Pydantic creados en `app/schemas/book.py`:
- `BookBase`, `BookCreate`, `BookUpdate`, `BookInDB`, `Book`.

---

## 7) Generar migración con Alembic

1) Asegúrate de tener la carpeta de versiones (si no existe, crearla):
```bash
mkdir alembic/versions
```

2) Generar la revisión autogenerada (usando Poetry):
```bash
poetry run alembic revision --autogenerate -m "create users and books tables"
```

Esto debe crear un archivo parecido a:
- `alembic/versions/<hash>_create_users_and_books_tables.py`

---

## 8) Aplicar la migración

```bash
poetry run alembic upgrade head
```

---

## 9) Verificar tablas creadas

Usando psql dentro del contenedor Docker:
```bash
docker compose exec -T postgres psql -U postgres -d book_sharing -c "\\dt"
```
Debes ver al menos:
- `public | users`
- `public | books`

---

## 10) Errores frecuentes y soluciones

- Error: InterpolationSyntaxError en `alembic.ini` con `%04d`.
  - Causa: ConfigParser interpreta `%`.
  - Solución: usar `version_num_format = %%04d`.

- Error: `FileNotFoundError` por falta de `alembic/versions/`.
  - Solución: crear la carpeta `alembic/versions` antes de generar la migración.

- Error: `OperationalError: connection refused` al autogenerar/aplicar migraciones.
  - Causa: PostgreSQL no está corriendo.
  - Solución: `docker compose up -d postgres` y reintentar.

- Error: `password authentication failed for user ...`.
  - Causa: Usuario/contraseña distintos a los de `DATABASE_URL` o `alembic.ini`.
  - Solución: Alinear credenciales. Por defecto: `postgres:password`.

- Error en Windows/PowerShell con tuberías o PSReadLine al usar `| cat`.
  - Causa: Peculiaridades de la consola.
  - Solución: Ejecutar el comando sin la tubería adicional; usar `poetry run ...` directamente.

- Error: `WSL ... execvpe(/bin/bash) failed` al intentar usar comandos Linux.
  - Causa: El entorno no es WSL.
  - Solución: En Windows, ejecutar directamente con Poetry y Docker Desktop, sin `bash -lc`.

---

## 11) Comandos rápidos (Windows + Poetry)

- Levantar PostgreSQL:
```bash
docker compose up -d postgres
```
- Generar migración:
```bash
poetry run alembic revision --autogenerate -m "create users and books tables"
```
- Aplicar migración:
```bash
poetry run alembic upgrade head
```
- Ver tablas:
```bash
docker compose exec -T postgres psql -U postgres -d book_sharing -c "\\dt"
```

---

## 12) Qué quedó implementado

- Modelo `User` (existente) y modelo `Book` (nuevo) con relación `User -> Book` (owner).
- Schemas Pydantic de `Book`.
- Alembic configurado y primera migración aplicada.
- Tablas `users` y `books` creadas en PostgreSQL.

---

## 13) Próximos pasos sugeridos

- Implementar registro/login con JWT y hashing de contraseña.
- CRUD de libros (endpoints `books`).
- Tests básicos de integración de usuarios y libros.
