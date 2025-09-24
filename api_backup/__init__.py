"""
API Package - Contains all API endpoints for the application.
"""
from fastapi import APIRouter

# Import all routers
from app.api.books import router as books_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.groups import router as groups_router
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.metadata import router as metadata_router
from app.api.loans import router as loans_router
from app.api.search import router as search_router
from app.api.scan import router as scan_router
# Importar group_books sin el prefijo para evitar duplicación
from app.api.group_books import router as group_books_router
from app.api.search_enhanced import router as search_enhanced_router

# Create main router
router = APIRouter()

# Include all routers
# Incluir auth_router sin prefijo ya que ya tiene su propio prefijo definido en auth.py
router.include_router(auth_router)
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(books_router, prefix="/books", tags=["books"])
router.include_router(loans_router, prefix="/loans", tags=["loans"])
router.include_router(search_router, prefix="/search", tags=["search"])
router.include_router(scan_router, prefix="/scan", tags=["scan"])
router.include_router(groups_router, prefix="/groups", tags=["groups"])
# Incluir group_books_router sin prefijo ya que ya tiene su propio prefijo definido
router.include_router(group_books_router, tags=["group-books"])
router.include_router(chat_router, prefix="/chat", tags=["chat"])
router.include_router(health_router, prefix="/health", tags=["health"])
router.include_router(metadata_router, prefix="/metadata", tags=["metadata"])
router.include_router(search_enhanced_router, prefix="/search-enhanced", tags=["search-enhanced"])

__all__ = ["router"]
