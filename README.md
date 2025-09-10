# 📚 Book Sharing App

Una aplicación para compartir libros entre amigos, desarrollada con FastAPI y PostgreSQL.

## 🚀 Características

- Sistema de autenticación JWT
- Gestión de bibliotecas personales
- Grupos de amigos para compartir libros
- Sistema de préstamos con chat integrado
- OCR para extraer información de libros desde fotos
- Integración con APIs externas (OpenLibrary, Google Books)
- Caché con Redis para acelerar búsquedas externas

## 🛠️ Stack Tecnológico

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Autenticación**: JWT con Passlib
- **OCR**: EasyOCR
- **APIs Externas**: OpenLibrary, Google Books
- **Cache**: Redis
- **Testing**: Pytest

## 📁 Estructura del Proyecto

```
book_sharing_app/
├── app/
│   ├── models/          # Modelos SQLAlchemy
│   ├── schemas/         # Schemas Pydantic
│   ├── api/            # Endpoints FastAPI
│   ├── services/       # Lógica de negocio
│   └── utils/          # Utilidades
├── tests/              # Tests
├── alembic/            # Migraciones
└── uploads/            # Archivos temporales
```

## 🚀 Instalación

1. **Clonar el repositorio**
2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate   # Windows
   ```
3. **Instalar dependencias**
   - Con Poetry (recomendado):
     ```bash
     poetry install
     ```
   - O con pip:
     ```bash
     pip install -r requirements.txt
     ```
4. **Servicios Docker (Postgres y Redis)**
   ```bash
   docker compose up -d postgres redis
   ```
5. **Configurar variables de entorno**
   ```bash
   cp env.example .env
   # Editar .env con tus valores
   ```
   Variables relevantes:
   - `DATABASE_URL=postgresql://postgres:password@localhost:5432/book_sharing`
   - `SECRET_KEY=...`, `ALGORITHM=HS256`, `ACCESS_TOKEN_EXPIRE_MINUTES=30`
   - `OPENLIBRARY_BASE_URL=https://openlibrary.org`
   - `GOOGLE_BOOKS_API_KEY=...` (opcional)
   - `REDIS_URL=redis://localhost:6379/0`
   - `CACHE_TTL_SECONDS=21600` (opcional; por defecto 6h)
6. **Migraciones**
   ```bash
   poetry run alembic upgrade head
   ```
7. **Ejecutar la aplicación**
   ```bash
   poetry run python main.py
   # Abrir http://localhost:8000/docs
   ```

## 🔗 Endpoints Clave

- Autenticación
  - `POST /auth/register`
  - `POST /auth/login` (OAuth2 form)
  - `GET /auth/me`
- Libros
  - `POST /books/`, `GET /books/`, `GET /books/{id}`, `PUT /books/{id}`, `DELETE /books/{id}`
- Préstamos
  - `POST /loans/loan?book_id=&borrower_id=`
  - `POST /loans/return?book_id=`
- Búsqueda externa (OpenLibrary → fallback Google Books, con caché Redis)
  - `GET /search/books?q=<título_o_isbn>&limit=5`

## 📝 Roadmap

Este proyecto está diseñado para aprendizaje progresivo:

- **Semana 1**: Setup inicial y autenticación
- **Semana 2**: Gestión de libros y APIs externas
- **Semana 3**: Sistema de grupos
- **Semana 4**: Sistema de préstamos
- **Semana 5**: Chat y comunicación
- **Semana 6**: Testing y deployment

## 📚 Recursos de Aprendizaje

- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [OpenLibrary API](https://openlibrary.org/developers/api)

---

**¡Disfruta aprendiendo! 🎓**
