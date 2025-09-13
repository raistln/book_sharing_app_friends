# 📚 Book Sharing App

Una aplicación completa para compartir libros entre amigos y construir una comunidad de lectores, desarrollada con FastAPI y PostgreSQL.

## 🎯 Estado del Proyecto

**✅ SEMANA 6 COMPLETADA** - Proyecto listo para producción con testing comprehensivo, optimizaciones de rendimiento y configuración de deployment.

### Checklist Semana 6:
- [x] Tests unitarios para servicios críticos
- [x] Tests de integración para endpoints principales  
- [x] Test de flujo completo: registro → añadir libro → préstamo
- [x] Tests para sistema de escaneo (códigos de barras + OCR)
- [x] Tests para sistema de autenticación
- [x] Tests para búsqueda en APIs externas
- [x] Optimización de consultas SQL (N+1 queries)
- [x] Caching básico para APIs externas (Redis)
- [x] Documentación automática con Swagger
- [x] Configuración de variables de entorno para producción
- [x] Configuración para deploy en Railway/Render
- [x] Configuración de PostgreSQL en la nube

## 🚀 Características

### Core Features
- **Sistema de autenticación JWT**: Registro, login seguro con tokens
- **Gestión completa de libros**: CRUD con validaciones y soft delete
- **Sistema de préstamos avanzado**: Solicitudes, aprobaciones, seguimiento
- **Grupos de amigos**: Organización en comunidades para compartir
- **Chat integrado**: Comunicación entre usuarios del sistema
- **Sistema de invitaciones**: Códigos únicos para unirse a grupos

### Funcionalidades Avanzadas
- **OCR inteligente**: Extracción de información desde fotos de libros
- **Escaneo de códigos de barras**: Identificación automática de libros
- **Búsqueda externa**: Integración con OpenLibrary y Google Books
- **Caché inteligente**: Redis para optimizar búsquedas repetidas
- **Filtros avanzados**: Por tipo, género, estado y disponibilidad
- **Historial completo**: Seguimiento de todos los préstamos

### Características Técnicas
- **API RESTful completa**: Documentación automática con Swagger
- **Optimización de rendimiento**: Consultas SQL optimizadas, eager loading
- **Logging comprehensivo**: Monitoreo en puntos críticos
- **Testing robusto**: +95% cobertura con tests unitarios e integración
- **Seguridad avanzada**: Validación de entrada, prevención de ataques
- **Deployment ready**: Configuración para Railway, Render y Docker

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy 2.0**: ORM avanzado con soporte async
- **PostgreSQL**: Base de datos relacional robusta
- **Alembic**: Migraciones de base de datos
- **Pydantic**: Validación de datos y serialización

### Autenticación y Seguridad
- **JWT**: Tokens seguros con Passlib
- **Bcrypt**: Hashing seguro de contraseñas
- **OAuth2**: Estándar de autenticación
- **Rate Limiting**: Protección contra ataques

### Procesamiento de Imágenes
- **EasyOCR**: Reconocimiento óptico de caracteres
- **OpenCV**: Procesamiento de imágenes
- **Pillow**: Manipulación de imágenes
- **pyzbar**: Decodificación de códigos de barras

### APIs y Caché
- **httpx**: Cliente HTTP asíncrono
- **Redis**: Caché en memoria para rendimiento
- **OpenLibrary API**: Búsqueda de libros
- **Google Books API**: Búsqueda alternativa

### Testing y Calidad
- **pytest**: Framework de testing
- **pytest-asyncio**: Testing asíncrono
- **httpx**: Cliente para tests de integración
- **coverage**: Análisis de cobertura de código

### Deployment y DevOps
- **Docker**: Containerización
- **Nginx**: Proxy reverso y balanceador
- **Railway**: Platform-as-a-Service
- **Render**: Alternativa de deployment

## 📁 Estructura del Proyecto

```
book_sharing_app_friends/
├── app/
│   ├── api/                    # 🌐 Endpoints FastAPI
│   │   ├── auth.py            # Autenticación (registro, login)
│   │   ├── books.py           # CRUD de libros
│   │   ├── loans.py           # Sistema de préstamos
│   │   ├── groups.py          # Gestión de grupos
│   │   ├── group_books.py     # Libros compartidos en grupos
│   │   ├── search.py          # Búsqueda externa (APIs)
│   │   ├── scan.py            # Escaneo OCR y códigos de barras
│   │   ├── chat.py            # Sistema de mensajería
│   │   └── users.py           # Gestión de usuarios
│   ├── models/                 # 🗃️ Modelos SQLAlchemy
│   │   ├── user.py            # Usuario y autenticación
│   │   ├── book.py            # Libros y metadatos
│   │   ├── loan.py            # Préstamos y historial
│   │   ├── group.py           # Grupos y membresías
│   │   └── invitation.py      # Invitaciones a grupos
│   ├── schemas/                # 📋 Schemas Pydantic
│   │   ├── user.py            # Validación de usuarios
│   │   ├── book.py            # Validación de libros
│   │   ├── loan.py            # Validación de préstamos
│   │   └── group.py           # Validación de grupos
│   ├── services/               # 🔧 Lógica de negocio
│   │   ├── auth_service.py    # Autenticación y JWT
│   │   ├── loan_service.py    # Lógica de préstamos
│   │   ├── group_service.py   # Lógica de grupos
│   │   ├── book_search_service.py  # Búsqueda externa
│   │   ├── book_scan_service.py    # Escaneo de libros
│   │   ├── ocr_service.py     # Reconocimiento de texto
│   │   ├── barcode_scanner.py # Escaneo de códigos
│   │   ├── cache.py           # Gestión de caché Redis
│   │   └── message_service.py # Mensajería
│   ├── utils/                  # 🛠️ Utilidades
│   │   └── security.py        # Funciones de seguridad
│   ├── config.py              # ⚙️ Configuración
│   ├── database.py            # 🗄️ Conexión a BD
│   ├── dependencies.py        # 🔗 Dependencias FastAPI
│   └── main.py                # 🚀 Aplicación principal
├── tests/                      # 🧪 Suite de Testing
│   ├── test_services_unit.py          # Tests unitarios
│   ├── test_integration_endpoints.py  # Tests de integración
│   ├── test_complete_flow.py          # Tests de flujo completo
│   ├── test_auth_comprehensive.py     # Tests de autenticación
│   ├── test_external_api_search.py    # Tests de APIs externas
│   ├── test_scan.py                   # Tests de escaneo
│   └── [15+ archivos de tests]        # Tests específicos
├── alembic/                    # 🔄 Migraciones de BD
│   └── versions/              # Historial de migraciones
├── .env                       # 🛠️ Variables de desarrollo
├── docker-compose.yml         # Docker para desarrollo
├── Dockerfile                 # Imagen Docker
├── docs/                       # 📚 Documentación
│   └── SEMANA_6_TESTING_DEPLOYMENT_GUIDE.md
├── requirements.txt            # 📦 Dependencias Python
├── pyproject.toml             # 🔧 Configuración del proyecto
└── main.py                    # 🎯 Punto de entrada
```

## 🚀 Instalación y Configuración

### Desarrollo Local

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd book_sharing_app_friends
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate   # Windows
   ```

3. **Instalar dependencias**
   ```bash
   # Con Poetry (recomendado)
   poetry install
   
   # O con pip
   pip install -r requirements.txt
   ```

4. **Configurar servicios (PostgreSQL y Redis)**
   ```bash
   # Opción 1: Docker Compose (recomendado)
   docker compose up -d postgres redis
   
   # Opción 2: Instalación local
   # Instalar PostgreSQL y Redis en tu sistema
   ```

5. **Configurar variables de entorno**
   ```bash
   cp env.example .env
   # Editar .env con tus valores
   ```

   **Variables esenciales**:
   ```env
   # Base de datos
   DATABASE_URL=postgresql://postgres:password@localhost:5432/book_sharing
   
   # Autenticación
   SECRET_KEY=tu-clave-super-secreta-aqui
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # Redis
   REDIS_URL=redis://localhost:6379/0
   CACHE_TTL_SECONDS=21600
   
   # APIs externas
   OPENLIBRARY_BASE_URL=https://openlibrary.org
   GOOGLE_BOOKS_API_KEY=tu-api-key-opcional
   
   # Desarrollo
   DEBUG=True
   ENVIRONMENT=development
   ```

6. **Ejecutar migraciones**
   ```bash
   # Con Poetry
   poetry run alembic upgrade head
   
   # Con pip
   alembic upgrade head
   ```

7. **Ejecutar la aplicación**
   ```bash
   # Con Poetry
   poetry run python main.py
   
   # Con pip
   python main.py
   
   # La aplicación estará disponible en:
   # http://localhost:8000 - API
   # http://localhost:8000/docs - Documentación Swagger
   # http://localhost:8000/redoc - Documentación ReDoc
   ```

### Testing

```bash
# Ejecutar todos los tests
pytest

# Tests con cobertura
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/test_auth_comprehensive.py
pytest tests/test_complete_flow.py

# Tests unitarios solamente
pytest tests/test_services_unit.py
```

### Deployment en Producción

#### Railway
```bash
# Instalar CLI
npm install -g @railway/cli

# Login y conectar
railway login
railway link

# Deploy
railway up
```

#### Render
1. Conectar repositorio GitHub a Render
2. Render detecta automáticamente `render.yaml`
3. Deploy automático en push a `main`

#### Docker
```bash
# Build local
docker build -t book-sharing-app .

# Run con Docker Compose
docker-compose -f docker-compose.prod.yml up -d
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
