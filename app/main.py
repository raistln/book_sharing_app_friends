"""
Aplicación principal FastAPI
"""
from fastapi import FastAPI
import logging
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.books import router as books_router
from app.api.loans import router as loans_router
from app.api.search import router as search_router
from app.api.scan import router as scan_router
from app.api.groups import router as groups_router
from app.api.group_books import router as group_books_router
from app.api.chat import router as chat_router

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logging.getLogger("app.api").setLevel(logging.INFO)
logging.getLogger("app.services").setLevel(logging.INFO)

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

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],
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
