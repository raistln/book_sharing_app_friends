"""
Dependencias comunes para FastAPI
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db

# Aquí añadiremos más dependencias cuando implementemos autenticación
# from app.services.auth_service import get_current_user
# from app.models.user import User

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
