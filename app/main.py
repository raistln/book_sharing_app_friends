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


from app.api import books as books_router
from app.api import loans as loans_router

# Registro de routers
app.include_router(books_router.router, prefix="/api/books", tags=["books"])
app.include_router(loans_router.router, prefix="/api/loans", tags=["loans"])
