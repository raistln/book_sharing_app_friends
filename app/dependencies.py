"""
Dependencias comunes para FastAPI
"""
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import get_current_user, oauth2_scheme
from app.models.user import User

# Aquí añadiremos más dependencias cuando implementemos autenticación
# from app.services.auth_service import get_current_user
# from app.models.user import User

def get_current_db(db: Session = Depends(get_db)) -> Session:
    """Dependency para obtener la sesión de base de datos"""
    return db


async def require_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """Atajo para inyectar un usuario autenticado en endpoints."""
    return await get_current_user(db=db, token=token)


async def optional_current_user(
    request: Request,
    db: Session = Depends(get_current_db),
) -> User | None:
    """Devuelve el usuario autenticado si hay Bearer token válido; si no, None."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    try:
        # Reusar la lógica de get_current_user pasando dependencias manualmente
        return await get_current_user(db=db, token=token)  # type: ignore[arg-type]
    except HTTPException:
        return None
