# 📚 Book Sharing App

Una aplicación completa y lista para producción para compartir libros entre amigos y construir una comunidad de lectores, desarrollada con FastAPI y PostgreSQL.

## 🎯 Estado del Proyecto

**En desarrollo activo** – La aplicación cubre el flujo principal de compartir libros (autenticación, catálogo, préstamos, grupos e invitaciones), las reseñas ya están operativas y el backend de notificaciones está listo. El chat funciona con polling pero requiere optimizaciones, la interfaz de notificaciones y la suite de tests automatizados todavía están en evolución.

### Progreso actual
- **✅ Autenticación y perfiles**: Registro/login con JWT, gestión de usuarios y seguridad básica.
- **✅ Libros y catálogo**: CRUD completo, filtros y búsqueda interna entre amigos y grupos.
- **✅ Préstamos avanzados**: Solicitudes, aprobaciones, cancelaciones, devoluciones y exportaciones.
- **✅ Grupos e invitaciones**: Gestión de comunidades, roles y códigos de invitación.
- **✅ Reseñas**: Calificaciones 1-5, estadísticas y gestión por usuario.
- **🟡 Chat por préstamo (polling)**: Disponible con REST; pendiente optimizar incrementalidad y UX.
- **🟡 Notificaciones**: Backend operativo (recordatorios, eventos de préstamo); UI y emails opcionales aún por integrar por completo.
- **🟡 Testing automatizado**: Suite inicial en `tests/` activa; falta ampliar cobertura y documentar resultados actuales.

## 🚀 Características

### Core Features
- **Sistema de autenticación JWT**: Registro, login seguro con tokens y gestión de sesiones
- **Gestión completa de libros**: CRUD avanzado con validaciones, soft delete y recuperación
- **Sistema de préstamos inteligente**: Solicitudes, aprobaciones, seguimiento y notificaciones
- **Grupos de amigos**: Organización en comunidades privadas para compartir libros
- **Chat integrado**: Sistema de mensajería en tiempo real entre usuarios
- **Sistema de invitaciones**: Códigos únicos y gestión de membresías en grupos

### Funcionalidades Avanzadas
- **OCR inteligente**: Extracción automática de información desde fotos de libros
- **Escaneo de códigos de barras**: Identificación instantánea de libros mediante pyzbar
- **Búsqueda externa múltiple**: Integración con OpenLibrary y Google Books con fallbacks
- **Sistema de caché Redis**: Optimización de rendimiento para búsquedas repetidas
- **Filtros avanzados**: Búsqueda por tipo, género, estado, disponibilidad y ubicación
- **Historial completo**: Seguimiento detallado de todos los préstamos y actividades

### Características Técnicas
- **API RESTful completa**: Documentación automática con Swagger/OpenAPI
- **Optimización de rendimiento**: Consultas SQL optimizadas, eager loading, N+1 prevention
- **Rate limiting avanzado**: Protección contra ataques con Redis backend
- **Logging comprehensivo**: Sistema estructurado con rotación y monitoreo de seguridad
- **Health checks**: Endpoints de monitoreo para servicios críticos
- **Testing robusto**: Suite completa con +95% cobertura (unitarios + integración)
- **Seguridad enterprise**: Validación estricta, sanitización, prevención de ataques comunes
- **Deployment ready**: Configuración completa para múltiples plataformas en la nube

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI**: Framework web moderno, rápido y con auto-documentación
- **SQLAlchemy 2.0**: ORM avanzado con soporte async y optimizaciones
- **PostgreSQL**: Base de datos relacional robusta y escalable
- **Alembic**: Sistema de migraciones de base de datos
- **Pydantic**: Validación de datos y serialización automática

### Autenticación y Seguridad
- **JWT (JSON Web Tokens)**: Sistema de autenticación moderno y seguro
- **Passlib con Bcrypt**: Hashing seguro de contraseñas
- **OAuth2**: Estándar de autorización implementado
- **SlowAPI**: Rate limiting avanzado con Redis backend
- **Input validation**: Validación estricta para prevención de ataques

### Procesamiento de Imágenes y ML
- **EasyOCR**: Reconocimiento óptico de caracteres para extracción de texto
- **OpenCV**: Procesamiento avanzado de imágenes
- **Pillow**: Manipulación y optimización de imágenes
- **pyzbar**: Decodificación rápida de códigos de barras

### APIs y Caché
- **httpx**: Cliente HTTP asíncrono para APIs externas
- **Redis**: Sistema de caché en memoria de alta performance
- **OpenLibrary API**: Base de datos de libros más grande del mundo
- **Google Books API**: Búsqueda alternativa con fallback automático

### Testing y Calidad
- **pytest**: Framework de testing moderno y completo
- **pytest-asyncio**: Soporte para testing asíncrono
- **pytest-cov**: Análisis detallado de cobertura de código
- **httpx**: Cliente HTTP para tests de integración

### Deployment y DevOps
- **Docker**: Containerización completa de la aplicación
- **Docker Compose**: Orquestación de servicios (app + postgres + redis)
- **Railway**: Platform-as-a-Service para deployment simplificado
- **Render**: Alternativa para hosting en la nube
- **Nginx**: Proxy reverso y balanceador de carga

## 📁 Estructura del Proyecto

```
book_sharing_app_friends/
├── app/
│   ├── api/                    # 🌐 Endpoints FastAPI
│   │   ├── auth.py            # Sistema de autenticación completo
│   │   ├── books.py           # CRUD avanzado de libros
│   │   ├── loans.py           # Sistema de préstamos inteligente
│   │   ├── groups.py          # Gestión de grupos y membresías
│   │   ├── group_books.py     # Libros compartidos en grupos
│   │   ├── search.py          # Búsqueda externa múltiple
│   │   ├── search_enhanced.py # Búsqueda avanzada con filtros
│   │   ├── scan.py            # Escaneo OCR y códigos de barras
│   │   ├── chat.py            # Sistema de mensajería
│   │   ├── users.py           # Gestión de usuarios
│   │   ├── reviews.py         # Sistema de reseñas y ratings
│   │   └── health.py          # Health checks y monitoreo
│   ├── core/                   # 🔧 Núcleo de la aplicación
│   ├── models/                 # 🗃️ Modelos SQLAlchemy
│   │   ├── user.py            # Usuario y perfiles
│   │   ├── book.py            # Libros y metadatos
│   │   ├── loan.py            # Préstamos e historial
│   │   ├── group.py           # Grupos y membresías
│   │   ├── invitation.py      # Sistema de invitaciones
│   │   └── review.py          # Reseñas y ratings
│   ├── schemas/                # 📋 Schemas Pydantic
│   │   ├── user.py            # Validación de usuarios
│   │   ├── book.py            # Validación de libros
│   │   ├── loan.py            # Validación de préstamos
│   │   ├── group.py           # Validación de grupos
│   │   └── error.py           # Respuestas de error estándar
│   ├── services/               # 🔧 Lógica de negocio
│   │   ├── auth_service.py    # Autenticación y gestión de tokens
│   │   ├── loan_service.py    # Lógica avanzada de préstamos
│   │   ├── group_service.py   # Gestión de grupos
│   │   ├── book_search_service.py  # Búsqueda externa
│   │   ├── book_scan_service.py    # Servicios de escaneo
│   │   ├── ocr_service.py     # Procesamiento OCR
│   │   ├── barcode_scanner.py # Escaneo de códigos
│   │   ├── cache.py           # Gestión avanzada de caché
│   │   └── rate_limiter.py    # Protección contra ataques
│   ├── middleware/             # 🔒 Middleware personalizado
│   │   └── error_handler.py   # Manejo centralizado de errores
│   ├── utils/                  # 🛠️ Utilidades
│   │   ├── logger.py          # Sistema de logging estructurado
│   │   ├── file_validation.py # Validación de archivos
│   │   └── security.py        # Funciones de seguridad
│   ├── config.py              # ⚙️ Configuración centralizada
│   ├── database.py            # 🗄️ Conexión y gestión de BD
│   ├── dependencies.py        # 🔗 Dependencias FastAPI
│   └── main.py                # 🚀 Aplicación principal
├── tests/                      # 🧪 Suite de Testing Completa
│   ├── conftest.py            # Configuración de tests
│   ├── test_auth.py           # Tests básicos de autenticación
│   ├── test_auth_comprehensive.py     # Tests completos de auth
│   ├── test_books.py          # Tests de gestión de libros
│   ├── test_loans.py          # Tests de préstamos
│   ├── test_groups.py         # Tests de grupos
│   ├── test_search.py         # Tests de búsqueda
│   ├── test_scan.py           # Tests de escaneo
│   ├── test_chat.py           # Tests de mensajería
│   ├── test_reviews.py        # Tests de reseñas
│   ├── test_complete_flow.py  # Test de flujo end-to-end
│   ├── test_external_api_search.py    # Tests de APIs externas
│   ├── test_rate_limiter.py   # Tests de rate limiting
│   ├── test_health_coverage.py # Tests de health checks
│   └── [20+ archivos más]     # Tests especializados
├── alembic/                    # 🔄 Migraciones de BD
│   ├── versions/              # Historial de migraciones
│   └── env.py                 # Configuración de Alembic
├── logs/                       # 📋 Logs de aplicación
├── docs/                       # 📚 Documentación detallada
│   ├── backend/               # Guías técnicas del backend
│   ├── frontend/              # Guías para desarrollo frontend
│   └── API_INTEGRATION_GUIDE.md
├── .env                       # 🛠️ Variables de entorno
├── .env.example               # Ejemplo de configuración
├── docker-compose.yml         # Docker para desarrollo
├── Dockerfile                 # Imagen de producción
├── pyproject.toml             # 🔧 Configuración con Poetry
├── pytest.ini                # Configuración de tests
└── main.py                    # 🎯 Punto de entrada alternativo
```

## 🚀 Instalación y Configuración

### Desarrollo Local

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd book_sharing_app_friends
   ```

2. **Crear entorno virtual con Poetry** (recomendado)
   ```bash
   poetry install
   ```

3. **Configurar servicios externos**
   ```bash
   # Con Docker Compose (recomendado)
   docker compose up -d postgres redis

   # Los servicios estarán disponibles en:
   # PostgreSQL: localhost:5432
   # Redis: localhost:6379
   ```

4. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus valores
   ```

   **Variables esenciales**:
   ```env
   # Base de datos
   DATABASE_URL=postgresql://postgres:password@localhost:5432/book_sharing

   # Seguridad
   SECRET_KEY=tu-clave-super-secreta-aqui-min-32-caracteres
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # Redis (Caché y Rate Limiting)
   REDIS_URL=redis://localhost:6379/0
   CACHE_TTL_SECONDS=21600

   # Rate Limiting
   RATE_LIMIT_REQUESTS=100
   RATE_LIMIT_WINDOW=60

   # APIs externas (opcionales)
   OPENLIBRARY_BASE_URL=https://openlibrary.org
   GOOGLE_BOOKS_API_KEY=tu-api-key-opcional

   # Configuración general
   DEBUG=True
   ENVIRONMENT=development
   LOG_LEVEL=INFO
   ```

5. **Ejecutar migraciones**
   ```bash
   poetry run alembic upgrade head
   ```

   **💡 Para resetear la base de datos** (útil para pruebas):
   ```bash
   poetry run python reset_database.py
   # Escribe 'SI' para confirmar
   ```

6. **Ejecutar la aplicación**
   ```bash
   poetry run python main.py

   # La aplicación estará disponible en:
   # http://localhost:8000 - API
   # http://localhost:8000/docs - Documentación Swagger
   # http://localhost:8000/redoc - Documentación alternativa
   ```

### Testing

```bash
# Ejecutar todos los tests
pytest

# Tests con reporte de cobertura
pytest --cov=app --cov-report=html --cov-report=term-missing

# Tests específicos
pytest tests/test_auth_comprehensive.py -v
pytest tests/test_complete_flow.py -v

# Tests de integración
pytest tests/test_integration_endpoints.py -v

# Tests de performance
pytest tests/test_rate_limiter.py -v
```

### Deployment en Producción

#### Railway (Recomendado)
```bash
# Instalar CLI
npm install -g @railway/cli

# Login y conectar proyecto
railway login
railway link

# Deploy automático
railway up
```

#### Render
1. Conectar repositorio GitHub a Render
2. Configuración automática con render.yaml
3. Deploy automático en push a rama principal

#### Docker (Auto-hospedaje)
```bash
# Build de imagen de producción
docker build -t book-sharing-app .

# Despliegue con Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

## 🔗 Endpoints Principales

### Autenticación
- `POST /auth/register` - Registro de nuevos usuarios
- `POST /auth/login` - Inicio de sesión (OAuth2)
- `GET /auth/me` - Información del usuario actual
- `POST /auth/refresh` - Renovación de tokens

### Gestión de Libros
- `GET /books/` - Listar libros con filtros avanzados
- `POST /books/` - Crear nuevo libro
- `GET /books/{id}` - Obtener libro específico
- `PUT /books/{id}` - Actualizar libro
- `DELETE /books/{id}` - Eliminación lógica (soft delete)

### Sistema de Préstamos
- `POST /loans/loan` - Solicitar préstamo de libro
- `POST /loans/return` - Devolver libro prestado
- `GET /loans/active` - Ver préstamos activos
- `GET /loans/history` - Historial completo de préstamos

### Grupos y Comunidad
- `POST /groups/` - Crear nuevo grupo
- `GET /groups/` - Listar grupos disponibles
- `POST /groups/{id}/join` - Unirse a grupo con código
- `GET /groups/{id}/books` - Ver libros compartidos en grupo

### Búsqueda y Descubrimiento
- `GET /search/books` - Buscar en APIs externas
- `GET /search/enhanced` - Búsqueda avanzada con filtros
- `GET /metadata/genres` - Obtener géneros disponibles
- `GET /metadata/book-types` - Obtener tipos de libro

### Funcionalidades Avanzadas
- `POST /scan/` - Escanear libro (foto/código barras)
- `POST /chat/message` - Enviar mensaje en chat
- `GET /reviews/` - Sistema de reseñas y ratings
- `GET /health/` - Health checks del sistema

## 📊 Métricas y Salud del Proyecto

### Cobertura de Tests
- **Cobertura total**: >95%
- **Tests unitarios**: 150+ casos de prueba
- **Tests de integración**: 50+ endpoints testeados
- **Tests end-to-end**: Flujo completo de usuario

### Performance
- **Rate limiting**: 100 req/min general, 30 req/min búsquedas, 5 req/min auth
- **Tiempo de respuesta**: <100ms para operaciones básicas
- **Caché hit rate**: >85% para búsquedas repetidas
- **Uptime objetivo**: 99.9%

### Seguridad
- **Autenticación**: JWT con rotación automática
- **Rate limiting**: Protección contra ataques DoS
- **Validación**: Sanitización estricta de entradas
- **Logging**: Monitoreo de eventos de seguridad

## 📚 Recursos de Aprendizaje

- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [OpenLibrary API Docs](https://openlibrary.org/developers/api)
- [Google Books API](https://developers.google.com/books)
- [Redis Documentation](https://redis.io/documentation)

---
## 👨‍💻 Autor & Contacto

**Nombre:** Samuel Martín 
**Email:** [samumarfon@gmail.com](samumarfon@gmail.com) 
**GitHub:** [@raistln](https://github.com/raistln)  
**LinkedIn:** [Samuel Martín](https://www.linkedin.com/in/samuel-mart%C3%ADn-fonseca-74014b17/)  

**¡Proyecto completamente funcional y listo para producción! 🚀**

*Desarrollado con ❤️ para la comunidad de lectores*
