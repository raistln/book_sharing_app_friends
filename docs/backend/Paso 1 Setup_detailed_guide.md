# 📚 Guía Detallada: Configuración Inicial del Proyecto Book Sharing App

## 🎯 **Objetivo de esta guía**

Esta guía explica paso a paso todo lo que hemos configurado en el proyecto, desde la estructura de carpetas hasta la configuración de base de datos. Cada sección incluye:
- **¿Qué es?** - Explicación del concepto
- **¿Por qué se hace así?** - Justificación de las decisiones
- **¿Cómo funciona?** - Detalles técnicos
- **Ejemplo práctico** - Código y configuración

---

## 📁 **1. Estructura del Proyecto**

### **¿Qué es la estructura de carpetas?**

La estructura de carpetas es la organización de archivos y directorios que sigue las mejores prácticas de Python y FastAPI.

### **¿Por qué esta estructura?**

```
book_sharing_app/
├── app/                    # Código principal de la aplicación
│   ├── __init__.py        # Hace que 'app' sea un paquete Python
│   ├── main.py            # Punto de entrada de FastAPI
│   ├── config.py          # Configuración y variables de entorno
│   ├── database.py        # Configuración de base de datos
│   ├── dependencies.py    # Dependencias comunes (auth, db)
│   │
│   ├── models/            # Modelos SQLAlchemy (tablas de BD)
│   │   ├── __init__.py
│   │   └── user.py
│   │
│   ├── schemas/           # Modelos Pydantic (validación de datos)
│   │   ├── __init__.py
│   │   └── user.py
│   │
│   ├── api/               # Endpoints de la API
│   │   ├── __init__.py
│   │   ├── auth.py        # Login, registro
│   │   ├── users.py       # CRUD usuarios
│   │   └── ...
│   │
│   ├── services/          # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   └── ...
│   │
│   └── utils/             # Utilidades y helpers
│       ├── __init__.py
│       └── ...
│
├── tests/                 # Tests unitarios y de integración
├── alembic/               # Migraciones de base de datos
├── uploads/               # Archivos subidos por usuarios
├── requirements.txt       # Dependencias (alternativo a Poetry)
├── pyproject.toml         # Configuración de Poetry
├── docker-compose.yml     # PostgreSQL local
├── alembic.ini           # Configuración de Alembic
└── main.py               # Punto de entrada para ejecutar
```

### **¿Por qué separar en carpetas?**

1. **Separación de responsabilidades**: Cada carpeta tiene un propósito específico
2. **Escalabilidad**: Fácil añadir nuevas funcionalidades
3. **Mantenibilidad**: Código organizado y fácil de encontrar
4. **Convenciones**: Sigue estándares de la industria

---

## 🔧 **2. Gestión de Dependencias con Poetry**

### **¿Qué es Poetry?**

Poetry es una herramienta moderna para gestionar dependencias y empaquetado de proyectos Python.

### **¿Por qué Poetry en lugar de pip?**

- **Gestión de dependencias**: Resuelve automáticamente conflictos
- **Entornos virtuales**: Crea y gestiona automáticamente
- **Lock file**: Garantiza versiones exactas
- **Publicación**: Facilita publicar paquetes

### **Configuración en `pyproject.toml`**

```toml
[project]
name = "book-sharing-app-friends"
version = "0.1.0"
description = ""
authors = [
    {name = "raistln", email = "samumarfon@gmail.com"}
]
readme = "README.md"
requires-python = ">=3.13"

# Dependencias principales
dependencies = [
    "fastapi[all]>=0.104.1",           # Framework web
    "uvicorn[standard]>=0.24.0",       # Servidor ASGI
    "sqlalchemy>=2.0.23",              # ORM para base de datos
    "psycopg2-binary>=2.9.9",          # Driver PostgreSQL
    "alembic>=1.12.1",                 # Migraciones de BD
    "passlib[bcrypt]>=1.7.4",          # Hashing de contraseñas
    "python-jose[cryptography]>=3.3.0", # JWT tokens
    "python-multipart>=0.0.6",         # Manejo de archivos
    "httpx>=0.25.2",                   # Cliente HTTP
    "pillow>=10.1.0",                  # Procesamiento de imágenes
    "pydantic>=2.5.0",                 # Validación de datos
    "python-dotenv>=1.0.0",            # Variables de entorno
    "pytest>=7.4.3",                   # Testing
    "pytest-asyncio>=0.21.1",          # Testing asíncrono
]

# Dependencias de desarrollo
[project.optional-dependencies]
dev = [
    "black>=23.0.0",                   # Formateador de código
    "isort>=5.12.0",                   # Ordenar imports
    "flake8>=6.0.0",                   # Linter
    "mypy>=1.5.0",                     # Type checker
]

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
package-mode = false  # No empaquetar como librería
```

### **Comandos básicos de Poetry**

```bash
# Instalar dependencias
poetry install

# Añadir nueva dependencia
poetry add nombre-paquete

# Ejecutar comando en el entorno virtual
poetry run python main.py

# Activar entorno virtual
poetry shell
```

---

## ⚙️ **3. Configuración con Pydantic Settings**

### **¿Qué es Pydantic Settings?**

Pydantic Settings es una extensión de Pydantic que facilita la gestión de configuración y variables de entorno.

### **¿Por qué usar Pydantic Settings?**

- **Validación automática**: Valida tipos y formatos
- **Variables de entorno**: Carga automáticamente desde `.env`
- **Valores por defecto**: Configuración segura
- **Type hints**: Autocompletado en IDEs

### **Archivo `app/config.py`**

```python
"""
Configuración del proyecto usando Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Configuración de la base de datos
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/book_sharing"
    
    # Configuración de seguridad
    SECRET_KEY: str = "your-secret-key-here-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # APIs externas
    OPENLIBRARY_BASE_URL: str = "https://openlibrary.org"
    GOOGLE_BOOKS_API_KEY: Optional[str] = None
    
    # Configuración de la aplicación
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Configuración de archivos
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"        # Cargar desde archivo .env
        case_sensitive = True    # Sensible a mayúsculas/minúsculas


# Instancia global de configuración
settings = Settings()
```

### **¿Cómo funciona?**

1. **Carga automática**: Busca variables en `.env` o variables de entorno del sistema
2. **Validación**: Verifica tipos y formatos automáticamente
3. **Valores por defecto**: Si no encuentra la variable, usa el valor por defecto
4. **Type hints**: Proporciona autocompletado y verificación de tipos

### **Archivo `.env` (ejemplo)**

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/book_sharing

# Security
SECRET_KEY=tu-clave-secreta-aqui-cambiala-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs
OPENLIBRARY_BASE_URL=https://openlibrary.org
GOOGLE_BOOKS_API_KEY=tu-api-key-de-google-books

# App Settings
DEBUG=True
ENVIRONMENT=development
```

---

## 🗄️ **4. Configuración de Base de Datos con SQLAlchemy**

### **¿Qué es SQLAlchemy?**

SQLAlchemy es un ORM (Object Relational Mapper) que permite trabajar con bases de datos usando objetos Python en lugar de SQL directo.

### **¿Por qué SQLAlchemy?**

- **ORM**: Trabaja con objetos Python en lugar de SQL
- **Multiplataforma**: Soporta múltiples bases de datos
- **Migraciones**: Integración con Alembic
- **Type safety**: Verificación de tipos
- **Performance**: Conexiones pool y optimizaciones

### **Archivo `app/database.py`**

```python
"""
Configuración de la base de datos con SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Crear el motor de base de datos
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,        # Mostrar SQL en consola en modo debug
    pool_pre_ping=True,         # Verificar conexión antes de usar
    pool_recycle=300            # Reciclar conexiones cada 5 minutos
)

# Crear la sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


def get_db():
    """
    Dependency para obtener la sesión de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### **Explicación detallada:**

#### **1. Engine (Motor)**
```python
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,        # Muestra SQL en consola si DEBUG=True
    pool_pre_ping=True,         # Verifica conexión antes de usar
    pool_recycle=300            # Recicla conexiones cada 5 minutos
)
```

- **`echo=True`**: Muestra todas las consultas SQL en la consola (útil para debug)
- **`pool_pre_ping=True`**: Verifica que la conexión esté activa antes de usarla
- **`pool_recycle=300`**: Recicla conexiones cada 5 minutos para evitar timeouts

#### **2. SessionMaker**
```python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

- **`autocommit=False`**: Los cambios no se guardan automáticamente
- **`autoflush=False`**: No ejecuta consultas automáticamente
- **`bind=engine`**: Conecta con el motor de base de datos

#### **3. Base para modelos**
```python
Base = declarative_base()
```

Esta es la clase base que heredarán todos nuestros modelos SQLAlchemy.

#### **4. Dependency para FastAPI**
```python
def get_db():
    db = SessionLocal()
    try:
        yield db          # Entrega la sesión a FastAPI
    finally:
        db.close()        # Cierra la sesión al terminar
```

Esta función es una **dependency** de FastAPI que:
- Crea una nueva sesión de base de datos
- La entrega al endpoint que la necesite
- Cierra la sesión automáticamente al terminar

---

## 🏗️ **5. Modelos SQLAlchemy**

### **¿Qué son los modelos SQLAlchemy?**

Los modelos son clases Python que representan tablas en la base de datos. Cada instancia de la clase representa una fila.

### **¿Por qué usar modelos?**

- **Mapeo objeto-relacional**: Cada clase = una tabla
- **Validación**: Validación automática de tipos
- **Relaciones**: Fácil definir relaciones entre tablas
- **Migraciones**: Alembic puede generar migraciones automáticamente

### **Archivo `app/models/user.py`**

```python
"""
Modelo de Usuario
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    # Campos principales
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Campos de estado
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Campos de auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Campos opcionales
    full_name = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
```

### **Explicación detallada de cada campo:**

#### **1. ID (Identificador único)**
```python
id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
```

- **`UUID(as_uuid=True)`**: Tipo UUID de PostgreSQL, se maneja como objeto UUID de Python
- **`primary_key=True`**: Clave primaria de la tabla
- **`default=uuid.uuid4`**: Genera automáticamente un UUID único

#### **2. Campos de texto**
```python
username = Column(String(50), unique=True, nullable=False, index=True)
email = Column(String(100), unique=True, nullable=True, index=True)
```

- **`String(50)`**: Campo de texto con máximo 50 caracteres
- **`unique=True`**: No puede haber valores duplicados
- **`nullable=False`**: No puede ser NULL (obligatorio)
- **`index=True`**: Crea un índice para búsquedas rápidas

#### **3. Campos de estado**
```python
is_active = Column(Boolean, default=True)
is_verified = Column(Boolean, default=False)
```

- **`Boolean`**: Campo booleano (True/False)
- **`default=True`**: Valor por defecto si no se especifica

#### **4. Campos de auditoría**
```python
created_at = Column(DateTime(timezone=True), server_default=func.now())
updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

- **`DateTime(timezone=True)`**: Fecha y hora con zona horaria
- **`server_default=func.now()`**: PostgreSQL establece la fecha actual al crear
- **`onupdate=func.now()`**: PostgreSQL actualiza la fecha al modificar

#### **5. Método `__repr__`**
```python
def __repr__(self):
    return f"<User(id={self.id}, username='{self.username}')>"
```

Este método define cómo se muestra el objeto cuando se imprime (útil para debug).

---

## 📋 **6. Schemas Pydantic**

### **¿Qué son los schemas Pydantic?**

Los schemas son clases que definen la estructura y validación de los datos que entran y salen de la API.

### **¿Por qué usar schemas?**

- **Validación**: Valida automáticamente los datos de entrada
- **Serialización**: Convierte objetos a JSON automáticamente
- **Documentación**: FastAPI genera documentación automática
- **Type safety**: Verificación de tipos en tiempo de ejecución

### **Archivo `app/schemas/user.py`**

```python
"""
Schemas Pydantic para Usuario
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """Schema base para usuario"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    """Schema para crear usuario"""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema para actualizar usuario"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """Schema para usuario en base de datos"""
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class User(UserInDB):
    """Schema para respuesta de usuario (sin datos sensibles)"""
    pass


class UserLogin(BaseModel):
    """Schema para login"""
    username: str
    password: str


class UserPasswordChange(BaseModel):
    """Schema para cambio de contraseña"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
```

### **Explicación de cada schema:**

#### **1. UserBase (Schema base)**
```python
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
```

- **`Field(...)`**: Campo obligatorio (los `...` significan "requerido")
- **`min_length=3, max_length=50`**: Validación de longitud
- **`Optional[EmailStr]`**: Campo opcional que debe ser un email válido

#### **2. UserCreate (Para crear usuarios)**
```python
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
```

Hereda de `UserBase` y añade el campo `password` obligatorio.

#### **3. UserUpdate (Para actualizar usuarios)**
```python
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
```

Todos los campos son opcionales porque en una actualización no necesitas enviar todos los campos.

#### **4. UserInDB (Usuario en base de datos)**
```python
class UserInDB(UserBase):
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
```

- **`from_attributes = True`**: Permite crear el schema desde un objeto SQLAlchemy
- Incluye todos los campos que vienen de la base de datos

#### **5. User (Respuesta pública)**
```python
class User(UserInDB):
    pass
```

Hereda de `UserInDB` pero no incluye campos sensibles como `password_hash`.

---

## 🚀 **7. Aplicación FastAPI**

### **¿Qué es FastAPI?**

FastAPI es un framework moderno para crear APIs con Python que se basa en type hints y Pydantic.

### **¿Por qué FastAPI?**

- **Rendimiento**: Muy rápido, comparable a NodeJS
- **Type hints**: Verificación de tipos automática
- **Documentación automática**: Genera Swagger/OpenAPI automáticamente
- **Validación automática**: Con Pydantic
- **Async/await**: Soporte nativo para programación asíncrona

### **Archivo `app/main.py`**

```python
"""
Aplicación principal FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Crear la aplicación FastAPI
app = FastAPI(
    title="Book Sharing App",
    description="Una aplicación para compartir libros entre amigos",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "¡Bienvenido a Book Sharing App! 📚",
        "version": "0.1.0",
        "docs": "/docs" if settings.DEBUG else None
    }


@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud"""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}
```

### **Explicación detallada:**

#### **1. Creación de la aplicación**
```python
app = FastAPI(
    title="Book Sharing App",
    description="Una aplicación para compartir libros entre amigos",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)
```

- **`title`**: Título de la API (aparece en la documentación)
- **`description`**: Descripción de la API
- **`version`**: Versión de la API
- **`docs_url`**: URL para la documentación Swagger (solo en desarrollo)
- **`redoc_url`**: URL para la documentación ReDoc (solo en desarrollo)

#### **2. Middleware CORS**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**CORS** (Cross-Origin Resource Sharing) permite que tu API sea accesible desde otros dominios:
- **`allow_origins=["*"]`**: Permite acceso desde cualquier dominio (solo en desarrollo)
- **`allow_credentials=True`**: Permite cookies y headers de autenticación
- **`allow_methods=["*"]`**: Permite todos los métodos HTTP (GET, POST, etc.)
- **`allow_headers=["*"]`**: Permite todos los headers

#### **3. Endpoints**
```python
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "¡Bienvenido a Book Sharing App! 📚",
        "version": "0.1.0",
        "docs": "/docs" if settings.DEBUG else None
    }
```

- **`@app.get("/")`**: Decorador que define un endpoint GET en la ruta raíz
- **`async def`**: Función asíncrona (mejor rendimiento)
- **`return`**: FastAPI convierte automáticamente el diccionario a JSON

---

## 🔄 **8. Migraciones con Alembic**

### **¿Qué es Alembic?**

Alembic es una herramienta de migraciones para SQLAlchemy que permite versionar los cambios en la base de datos.

### **¿Por qué usar migraciones?**

- **Versionado**: Control de versiones para la base de datos
- **Colaboración**: Múltiples desarrolladores pueden sincronizar cambios
- **Rollback**: Puedes deshacer cambios si algo sale mal
- **Producción**: Despliegue seguro de cambios de base de datos

### **Archivo `alembic.ini`**

```ini
# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = alembic

# template used to generate migration file names
file_template = %%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
prepend_sys_path = .

# URL de la base de datos (se sobrescribe en env.py)
sqlalchemy.url = postgresql://postgres:password@localhost:5432/book_sharing

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### **Archivo `alembic/env.py`**

```python
"""
Alembic environment configuration
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from app.database import Base
from app.models import user  # Importar todos los modelos aquí
from app.config import settings

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def get_url():
    """Get database URL from settings"""
    return settings.DATABASE_URL


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### **Archivo `alembic/script.py.mako`**

```mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
```

### **Comandos de Alembic**

```bash
# Inicializar Alembic (solo la primera vez)
alembic init alembic

# Crear una nueva migración
alembic revision --autogenerate -m "Create users table"

# Ejecutar migraciones pendientes
alembic upgrade head

# Ver estado de migraciones
alembic current

# Ver historial de migraciones
alembic history

# Revertir última migración
alembic downgrade -1
```

---

## 📦 **9. Archivos `__init__.py`**

### **¿Qué son los archivos `__init__.py`?**

Los archivos `__init__.py` hacen que un directorio sea reconocido como un paquete Python.

### **¿Por qué son necesarios?**

- **Paquetes Python**: Sin `__init__.py`, Python no reconoce el directorio como paquete
- **Imports**: Permite hacer `from app.models import user`
- **Inicialización**: Puede contener código de inicialización del paquete

### **Ejemplos de `__init__.py`**

```python
# app/__init__.py
# Book Sharing App - Main Package

# app/models/__init__.py
# SQLAlchemy Models Package

# app/schemas/__init__.py
# Pydantic Schemas Package

# app/api/__init__.py
# FastAPI Endpoints Package

# app/services/__init__.py
# Business Logic Services Package

# app/utils/__init__.py
# Utility Functions Package

# tests/__init__.py
# Tests Package
```

---

## 🔧 **10. Dependencias de FastAPI**

### **¿Qué son las dependencias?**

Las dependencias son funciones que se ejecutan antes de los endpoints y pueden proporcionar datos o realizar validaciones.

### **Archivo `app/dependencies.py`**

```python
"""
Dependencias comunes para FastAPI
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db

def get_current_db(db: Session = Depends(get_db)) -> Session:
    """Dependency para obtener la sesión de base de datos"""
    return db


# Ejemplo de dependencia para autenticación (se implementará más adelante)
# async def get_current_user(
#     db: Session = Depends(get_db),
#     token: str = Depends(oauth2_scheme)
# ) -> User:
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     # Lógica de validación de token aquí
#     return user
```

### **¿Cómo usar dependencias?**

```python
from app.dependencies import get_current_db

@app.get("/users/")
async def get_users(db: Session = Depends(get_current_db)):
    # db es una sesión de base de datos
    users = db.query(User).all()
    return users
```

---

## 🐳 **11. Docker y PostgreSQL**

### **¿Qué es Docker Compose?**

Docker Compose permite definir y ejecutar aplicaciones multi-contenedor.

### **Archivo `docker-compose.yml`**

```yaml
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

volumes:
  postgres_data:
```

### **Explicación:**

- **`image: postgres:15`**: Usa PostgreSQL versión 15
- **`environment`**: Variables de entorno para configurar la BD
- **`ports`**: Mapea puerto 5432 del contenedor al puerto 5432 del host
- **`volumes`**: Persiste los datos de la base de datos

### **Comandos de Docker Compose**

```bash
# Levantar servicios
docker-compose up -d

# Ver logs
docker-compose logs

# Parar servicios
docker-compose down

# Ver estado
docker-compose ps
```

---

## 🎯 **12. Punto de Entrada**

### **Archivo `main.py` (en la raíz)**

```python
"""
Punto de entrada para ejecutar la aplicación
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Recargar automáticamente en desarrollo
        log_level="info"
    )
```

### **Explicación:**

- **`"app.main:app"`**: Ruta al objeto app (módulo app.main, variable app)
- **`host="0.0.0.0"`**: Escucha en todas las interfaces de red
- **`port=8000`**: Puerto donde se ejecutará la aplicación
- **`reload=True`**: Recarga automáticamente cuando cambias el código
- **`log_level="info"`**: Nivel de logging

---

## 🚀 **13. Próximos Pasos**

### **Orden recomendado de implementación:**

1. **Probar la aplicación básica**
   ```bash
   poetry run python main.py
   ```

2. **Configurar PostgreSQL**
   ```bash
   docker-compose up -d
   ```

3. **Crear primera migración**
   ```bash
   alembic revision --autogenerate -m "Create users table"
   alembic upgrade head
   ```

4. **Implementar autenticación**
   - Crear `app/services/auth_service.py`
   - Crear `app/api/auth.py`

5. **Crear endpoints CRUD**
   - Crear `app/api/users.py`
   - Implementar operaciones básicas

### **Conceptos que aprenderás:**

- **FastAPI**: Decoradores, dependencias, routers
- **SQLAlchemy**: Consultas, relaciones, sesiones
- **Pydantic**: Validación, serialización, configuración
- **Alembic**: Migraciones, versionado de BD
- **Testing**: Tests unitarios y de integración

---

## 📚 **Recursos Adicionales**

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Poetry Documentation](https://python-poetry.org/docs/)

---

**¡Ahora tienes una base sólida para continuar con el desarrollo! 🎓**
