"""
Aplicación principal FastAPI
"""
from fastapi import FastAPI
import logging
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.utils.rate_limiter import limiter, rate_limit_handler, SLOWAPI_AVAILABLE
try:
    from slowapi.errors import RateLimitExceeded
except ImportError:
    RateLimitExceeded = Exception
from app.utils.logger import setup_logging
from app.middleware.error_handler import (
    http_exception_handler, validation_exception_handler, 
    general_exception_handler, business_logic_exception_handler,
    database_exception_handler, auth_exception_handler,
    BusinessLogicError, DatabaseError, AuthenticationError, AuthorizationError
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import HTTPException
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.books import router as books_router
from app.api.loans import router as loans_router
from app.api.search import router as search_router
from app.api.scan import router as scan_router
from app.api.groups import router as groups_router
from app.api.group_books import router as group_books_router
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.metadata import router as metadata_router
from app.api.search_enhanced import router as search_enhanced_router

# Initialize comprehensive logging system
setup_logging(log_level=settings.LOG_LEVEL, enable_file_logging=settings.ENABLE_FILE_LOGGING)

# Crear la aplicación FastAPI
app = FastAPI(
    title="Book Sharing App",
    description="""
    ## 📚 Book Sharing App

    Una aplicación completa para compartir libros entre amigos y construir una comunidad de lectores.

    ### Características principales:
    - **Autenticación JWT**: Sistema seguro de registro y login
    - **Gestión de libros**: CRUD completo con soporte para OCR y códigos de barras
    - **Sistema de préstamos**: Solicitud, aprobación y seguimiento de préstamos
    - **Grupos de amigos**: Organización en grupos para compartir bibliotecas
    - **Búsqueda externa**: Integración con OpenLibrary y Google Books
    - **Chat integrado**: Comunicación entre usuarios
    - **Caché inteligente**: Redis para optimizar búsquedas externas

    ### Flujo típico:
    1. **Registro/Login** → Crear cuenta o iniciar sesión
    2. **Añadir libros** → Escanear código de barras o añadir manualmente
    3. **Unirse a grupos** → Conectar con amigos
    4. **Solicitar préstamos** → Pedir libros prestados
    5. **Gestionar préstamos** → Aprobar/rechazar solicitudes
    6. **Comunicarse** → Chat con otros usuarios

    ### Tecnologías:
    - **Backend**: FastAPI + SQLAlchemy + PostgreSQL
    - **Autenticación**: JWT + Passlib
    - **OCR**: EasyOCR para reconocimiento de texto
    - **Caché**: Redis para rendimiento
    - **APIs externas**: OpenLibrary, Google Books
    """,
    version="1.0.0",
    contact={
        "name": "Book Sharing App Team",
        "email": "support@booksharing.app",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_tags=[
        {
            "name": "auth",
            "description": "Operaciones de autenticación: registro, login, gestión de usuarios"
        },
        {
            "name": "books",
            "description": "Gestión de libros: CRUD, búsqueda, categorización"
        },
        {
            "name": "loans",
            "description": "Sistema de préstamos: solicitudes, aprobaciones, devoluciones"
        },
        {
            "name": "groups",
            "description": "Gestión de grupos de amigos y bibliotecas compartidas"
        },
        {
            "name": "search",
            "description": "Búsqueda en APIs externas (OpenLibrary, Google Books)"
        },
        {
            "name": "scan",
            "description": "Escaneo de códigos de barras y OCR para libros"
        },
        {
            "name": "chat",
            "description": "Sistema de mensajería entre usuarios"
        },
        {
            "name": "invitations",
            "description": "Sistema de invitaciones a grupos"
        }
    ]
)

# Add rate limiter to app (if available and not in testing mode)
import os
if SLOWAPI_AVAILABLE and limiter and not (os.getenv("TESTING") == "true" or os.getenv("DISABLE_RATE_LIMITING") == "true"):
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Configure comprehensive error handling
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(BusinessLogicError, business_logic_exception_handler)
app.add_exception_handler(DatabaseError, database_exception_handler)
app.add_exception_handler(AuthenticationError, auth_exception_handler)
app.add_exception_handler(AuthorizationError, auth_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Configure CORS with production security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(books_router, prefix="/books", tags=["books"])
app.include_router(loans_router)
app.include_router(search_router)
app.include_router(scan_router)
app.include_router(groups_router)
app.include_router(group_books_router)
app.include_router(chat_router)
app.include_router(health_router)
app.include_router(metadata_router)
app.include_router(search_enhanced_router)

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


from app.api import books as books_router  # noqa: F401 (compat)
