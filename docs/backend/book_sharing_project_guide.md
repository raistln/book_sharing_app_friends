# 📚 Proyecto: App de Intercambio de Libros entre Amigos
## Guía Completa de Desarrollo y Aprendizaje

---

## 🎯 **OBJETIVOS DEL PROYECTO**

### Técnicos:
- Dominar FastAPI y desarrollo de APIs REST
- Aprender SQLAlchemy y diseño de bases de datos relacionales
- Integrar APIs externas (OpenLibrary, Google Books, OCR)
- Implementar sistemas de autenticación JWT
- Practicar testing y deployment

### Funcionales:
- Sistema de catalogación personal de libros físicos
- OCR para extraer datos de libros fotografiados
- Grupos de amigos para compartir bibliotecas
- Sistema de préstamos y chat básico

---

## 🛠️ **STACK TECNOLÓGICO**

### Backend:
```
- FastAPI (framework web moderno)
- SQLAlchemy (ORM para base de datos)
- PostgreSQL (base de datos relacional)
- Pydantic (validación de datos)
- JWT (autenticación sin sesiones)
- Uvicorn (servidor ASGI)
```

### Librerías Adicionales:
```
- EasyOCR (reconocimiento de texto en imágenes)
- httpx (cliente HTTP para APIs externas)
- Pillow (procesamiento de imágenes)
- python-multipart (manejo de archivos)
- passlib (hashing de contraseñas)
- pyzbar (escaneo de códigos de barras)
- opencv-python (procesamiento de imágenes)
- redis (caching en memoria)
```

### APIs Externas:
```
- OpenLibrary API (base de datos de libros)
- Google Books API (fallback para libros)
- Google Vision API (OCR inicial para pruebas)
```

---

## 📁 **ESTRUCTURA DEL PROYECTO**

```
book_sharing_app/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada FastAPI
│   ├── config.py              # Configuración y variables de entorno
│   ├── database.py            # Configuración de base de datos
│   ├── dependencies.py        # Dependencias comunes (auth, db)
│   │
│   ├── models/                # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── book.py
│   │   ├── group.py
│   │   ├── loan.py
│   │   └── message.py
│   │
│   ├── schemas/               # Modelos Pydantic (serialización)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── book.py
│   │   ├── group.py
│   │   ├── loan.py
│   │   └── message.py
│   │
│   ├── api/                   # Endpoints organizados
│   │   ├── __init__.py
│   │   ├── auth.py            # Login, registro
│   │   ├── users.py           # Gestión de usuarios
│   │   ├── books.py           # CRUD libros
│   │   ├── groups.py          # Gestión de grupos
│   │   ├── loans.py           # Sistema de préstamos
│   │   ├── messages.py        # Chat básico
│   │   ├── search.py          # Búsqueda en APIs externas
│   │   └── scan.py            # Escaneo de códigos de barras y OCR
│   │
│   ├── services/              # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── auth_service.py    # JWT, hashing
│   │   ├── book_service.py    # OCR, APIs externas
│   │   ├── group_service.py   # Lógica de grupos
│   │   ├── notification_service.py
│   │   ├── barcode_scanner.py # Escaneo de códigos de barras
│   │   ├── ocr_service.py     # Reconocimiento óptico de caracteres
│   │   ├── book_scan_service.py # Servicio unificado de escaneo
│   │   ├── book_search_service.py # Búsqueda en APIs externas
│   │   ├── openlibrary_client.py # Cliente OpenLibrary
│   │   ├── googlebooks_client.py # Cliente Google Books
│   │   └── cache.py           # Cliente Redis para caching
│   │
│   └── utils/                 # Utilidades
│       ├── __init__.py
│       ├── ocr.py            # EasyOCR integration
│       ├── book_apis.py      # OpenLibrary/Google Books
│       └── image_processing.py
│
├── tests/                     # Tests unitarios y de integración
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_auth_extra.py
│   ├── test_basic.py
│   ├── test_books_loans.py
│   ├── test_search.py
│   ├── test_scan.py
│   └── test_groups.py
│
├── alembic/                   # Migraciones de BD
├── uploads/                   # Imágenes temporales
├── requirements.txt           # Dependencias
├── .env                       # Variables de entorno
├── .gitignore
├── README.md
└── docker-compose.yml         # PostgreSQL y Redis local
```

---

## 🗄️ **DISEÑO DE BASE DE DATOS**

### Modelos Principales:

```python
# users table
- id: UUID (primary key)
- username: str (unique)
- email: str (optional, unique)
- password_hash: str
- created_at: datetime
- is_active: bool

# books table
- id: UUID (primary key)
- title: str
- author: str
- isbn: str (optional)
- cover_url: str (optional)
- description: text (optional)
- owner_id: UUID (foreign key -> users)
- status: enum (available, loaned, reserved)
- created_at: datetime

# groups table
- id: UUID (primary key)
- name: str
- description: str (optional)
- created_by: UUID (foreign key -> users)
- created_at: datetime

# group_members table (many-to-many)
- group_id: UUID (foreign key -> groups)
- user_id: UUID (foreign key -> users)
- joined_at: datetime
- role: enum (admin, member)

# loans table
- id: UUID (primary key)
- book_id: UUID (foreign key -> books)
- borrower_id: UUID (foreign key -> users)
- lender_id: UUID (foreign key -> users)
- group_id: UUID (foreign key -> groups)
- status: enum (requested, approved, active, returned)
- requested_at: datetime
- approved_at: datetime (optional)
- due_date: datetime (optional)
- returned_at: datetime (optional)

# messages table
- id: UUID (primary key)
- loan_id: UUID (foreign key -> loans)
- sender_id: UUID (foreign key -> users)
- content: text
- sent_at: datetime
- expires_at: datetime (auto-delete)
```

---

## 🚀 **ROADMAP DE DESARROLLO (6 semanas)**

### **SEMANA 1: Base del Proyecto**
#### Día 1-2: Setup inicial
- [x] Crear estructura de carpetas
- [x] Configurar entorno virtual y dependencias
- [x] Setup PostgreSQL con Docker
- [x] Configurar FastAPI básico con "Hello World"

#### Día 3-4: Modelos y Base de Datos
- [x] Crear modelos SQLAlchemy (User, Book)
- [x] Configurar Alembic para migraciones
- [x] Crear primera migración
- [x] Testear conexión a BD

#### Día 5-7: Sistema de Autenticación
- [x] Implementar registro de usuarios
- [x] Sistema login con JWT
- [x] Middleware de autenticación
- [x] Endpoints básicos de usuario

**Checkpoint Semana 1**: Usuario se puede registrar, hacer login y obtener su perfil

---

### **SEMANA 2: Gestión de Libros**
#### Día 8-9: CRUD Básico de Libros
- [x] Schemas Pydantic para libros
- [x] Endpoints: crear, listar, editar, eliminar libros
- [x] Relación usuario-libros funcionando

#### Día 10-11: Integración APIs Externas
- [x] Cliente para OpenLibrary API
- [x] Cliente para Google Books API como fallback
- [x] Servicio que busque libro por título/ISBN
- [x] Endpoint para búsqueda automática

#### Día 12-14: OCR y Códigos de Barras
- [x] Integrar EasyOCR para reconocimiento de texto
- [x] Integrar pyzbar para escaneo de códigos de barras
- [x] Servicio unificado de escaneo (códigos + OCR)
- [x] Endpoint para subir imagen de libro
- [x] Extraer título/autor de la imagen
- [x] Combinar escaneo + búsqueda en APIs
- [x] Implementar caching con Redis

**Checkpoint Semana 2**: Usuario puede añadir libros manualmente, por búsqueda, por foto y por escaneo de códigos de barras

---

### **SEMANA 3: Sistema de Grupos**
#### Día 15-16: Modelos de Grupos
- [x] Implementar modelos Group y GroupMember
- [x] Endpoints para crear y gestionar grupos
- [x] Sistema de invitaciones básico

#### Día 17-18: Bibliotecas Compartidas
- [x] Endpoint para ver libros de un grupo
- [x] Filtros y búsqueda dentro del grupo
- [x] Permisos: solo miembros pueden ver libross   

#### Día 19-21: Sistema de Invitaciones
- [x] Generar códigos de invitación únicos
- [x] Endpoint para enviar invitación por email
- [x] Aceptar/rechazar invitaciones

**Checkpoint Semana 3**: Usuarios pueden crear grupos e invitar amigos

---

### **SEMANA 4: Sistema de Préstamos**
#### Día 22-23: Modelo de Préstamos
- [x] Implementar modelo Loan con estados
- [x] Endpoints para solicitar préstamo
- [x] Lógica de aprobación/rechazo

#### Día 24-25: Estados de Libros
- [x] Actualizar disponibilidad automáticamente
- [x] Historial de préstamos
- [x] Notificaciones básicas

#### Día 26-28: Gestión Avanzada
- [x] Fechas de devolución
- [x] Recordatorios automáticos
- [x] Marcar como devuelto

**Checkpoint Semana 4**: Sistema completo de préstamos funcionando

---

### **SEMANA 5: Chat y Comunicación**
#### Día 29-30: Sistema de Mensajes
- [x] Modelo Message vinculado a préstamos
- [x] Endpoints para enviar/recibir mensajes
- [x] Chat privado entre prestamista y prestatario

#### Día 31-32: Auto-limpieza
- [x] Tarea automática para borrar mensajes viejos
- [x] Configurar expiración de conversaciones
- [x] Optimizar consultas de mensajes

#### Día 33-35: Polish del Backend
- [x] Manejo de errores mejorado
- [x] Logging estructurado
- [x] Validaciones adicionales

**Checkpoint Semana 5**: Chat funcional con auto-limpieza

---

### **SEMANA 6: Testing y Deployment**
#### Día 36-37: Testing
- [] Tests unitarios para servicios críticos
- [] Tests de integración para endpoints principales
- [] Test de flujo completo: registro → añadir libro → préstamo
- [] Tests para sistema de escaneo (códigos de barras + OCR)
- [] Tests para sistema de autenticación
- [] Tests para búsqueda en APIs externas

#### Día 38-39: Optimización
- [ ] Optimizar consultas SQL (N+1 queries)
- [x] Caching básico para APIs externas (Redis)
- [ ] Documentación automática con Swagger

#### Día 40-42: Deployment
- [ ] Configurar variables de entorno para producción
- [ ] Deploy en Railway/Render
- [ ] Configurar PostgreSQL en la nube
- [ ] Probar en producción

**Checkpoint Final**: API desplegada y funcionando en producción

---

## 🧪 **CHECKLIST DE APRENDIZAJE**

### Conceptos Técnicos a Dominar:
- [ ] **FastAPI**: Decoradores, dependencias, middleware
- [ ] **SQLAlchemy**: ORM, relaciones, lazy loading
- [ ] **Pydantic**: Validación, serialización, tipos
- [ ] **JWT**: Generación, validación, middleware
- [ ] **Async/Await**: Programación asíncrona en Python
- [ ] **APIs REST**: Diseño, códigos de estado, buenas prácticas
- [ ] **Base de Datos**: Relaciones, índices, migraciones
- [ ] **OCR**: Procesamiento de imágenes, extracción de texto
- [ ] **Testing**: Unitarios, integración, mocking

### Buenas Prácticas:
- [ ] Separación de responsabilidades (models/schemas/services)
- [ ] Manejo de errores consistente
- [ ] Logging estructurado
- [ ] Variables de entorno para configuración
- [ ] Validación de datos de entrada
- [ ] Documentación automática
- [ ] Control de versiones con Git

---

## 🔧 **COMANDOS INICIALES**

### Setup del proyecto:
```bash
# Crear directorio y entorno virtual
mkdir book_sharing_app && cd book_sharing_app
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install fastapi[all] sqlalchemy psycopg2-binary alembic
pip install easyocr pillow httpx passlib python-jose python-multipart
pip freeze > requirements.txt

# Crear estructura de carpetas
mkdir -p app/{models,schemas,api,services,utils} tests alembic uploads
```

### Docker para PostgreSQL y Redis:
```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: book_sharing
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Variables de entorno (.env):
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/book_sharing
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENLIBRARY_BASE_URL=https://openlibrary.org
GOOGLE_BOOKS_API_KEY=your-google-books-api-key
REDIS_URL=redis://localhost:6379
CACHE_TTL_SECONDS=3600
```

---

## ✅ **FUNCIONALIDADES IMPLEMENTADAS**

### 🔐 **Sistema de Autenticación (Paso 5)**
- [x] Registro de usuarios con validación
- [x] Login con JWT tokens
- [x] Middleware de autenticación
- [x] Endpoints de perfil de usuario
- [x] Validación de tokens y usuarios inactivos
- [x] Tests completos de autenticación

### 📚 **Gestión de Libros (Paso 4)**
- [x] CRUD completo de libros
- [x] Relación usuario-libros
- [x] Sistema de préstamos básico
- [x] Estados de libros (disponible, prestado, archivado)
- [x] Tests de flujo completo de préstamos

### 🔍 **Búsqueda en APIs Externas (Paso 6)**
- [x] Cliente OpenLibrary API
- [x] Cliente Google Books API (fallback)
- [x] Servicio unificado de búsqueda
- [x] Búsqueda por título e ISBN
- [x] Endpoint REST para búsqueda
- [x] Tests de integración con APIs

### 📸 **Sistema de Escaneo (Paso 8)**
- [x] Escaneo de códigos de barras (pyzbar + OpenCV)
- [x] Reconocimiento óptico de caracteres (EasyOCR)
- [x] Servicio unificado de escaneo
- [x] Endpoints para subir imágenes
- [x] Extracción automática de títulos y autores
- [x] Integración con búsqueda en APIs
- [x] Tests unitarios del sistema de escaneo

### ⚡ **Caching con Redis (Paso 7)**
- [x] Cliente Redis para caching
- [x] Cache de resultados de búsqueda
- [x] Configuración de TTL
- [x] Integración con Docker Compose
- [x] Métricas de cache hit/miss
- [x] Tests de caching

### 🧪 **Testing**
- [x] Tests unitarios para servicios críticos
- [x] Tests de integración para endpoints
- [x] Tests de autenticación (casos edge)
- [x] Tests de escaneo (mocks y casos reales)
- [x] Tests de búsqueda en APIs
- [x] Tests de flujo completo

---

## 📝 **PRÓXIMOS PASOS**

1. **Crear estructura de carpetas** según el esquema propuesto
2. **Configurar entorno virtual** e instalar dependencias
3. **Levantar PostgreSQL** con Docker
4. **Implementar primer modelo** (User) y migración
5. **Crear endpoint básico** de registro/login

---

## 💡 **RECURSOS ADICIONALES**

- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [OpenLibrary API Docs](https://openlibrary.org/developers/api)
- [EasyOCR Documentation](https://github.com/JaidedAI/EasyOCR)

---

**¡Empezamos cuando quieras! 🚀**

*Este proyecto está diseñado para ser un aprendizaje progresivo donde cada semana construyes sobre lo anterior, dominando nuevos conceptos técnicos mientras desarrollas una aplicación funcional.*