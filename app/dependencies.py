"""
Dependencias comunes para FastAPI
"""
from fastapi import Depends, HTTPException, status
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


# Ejemplo de dependencia para autenticación (se implementará más adelante)
async def require_user(user: User = Depends(get_current_user)) -> User:
    """Atajo para inyectar un usuario autenticado en endpoints."""
    return user
