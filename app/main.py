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


# Importar y registrar routers aquí cuando los creemos
# from app.api import auth, users, books, groups, loans, messages
# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
# app.include_router(users.router, prefix="/api/users", tags=["users"])
# app.include_router(books.router, prefix="/api/books", tags=["books"])
# app.include_router(groups.router, prefix="/api/groups", tags=["groups"])
# app.include_router(loans.router, prefix="/api/loans", tags=["loans"])
# app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
