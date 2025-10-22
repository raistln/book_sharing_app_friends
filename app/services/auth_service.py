"""
Servicio de autenticación: registro, validación de credenciales y obtención de usuario actual
"""
from typing import Optional
import logging
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
logger = logging.getLogger(__name__)


def register_user(*, db: Session, user_in: UserCreate) -> User:
    """Crea un nuevo usuario con contraseña hasheada.

    Lanza 400 si username o email ya existen.
    """
    logger.info("register_user username=%s email=%s", user_in.username, user_in.email)
    exists_username = db.query(User).filter(User.username == user_in.username).first()
    if exists_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username ya está en uso")
    if user_in.email:
        exists_email = db.query(User).filter(User.email == user_in.email).first()
        if exists_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email ya está en uso")

    user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        bio=user_in.bio,
        avatar_url=user_in.avatar_url,
        password_hash=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(*, db: Session, username: str, password: str) -> Optional[User]:
    """Devuelve el usuario si las credenciales son válidas, None en caso contrario."""
    logger.info("authenticate_user identifier=%s", username)

    # Intentar buscar por username primero
    user: Optional[User] = db.query(User).filter(User.username == username).first()
    logger.info("authenticate_user search by username=%s found=%s", username, user is not None)

    # Si no se encuentra por username, intentar por email
    if not user:
        user = db.query(User).filter(User.email == username).first()
        if user:
            logger.info("authenticate_user found user by email=%s", username)

    if not user:
        logger.info("authenticate_user no user found for identifier=%s", username)
        return None

    logger.info("authenticate_user checking password for user=%s", user.username)
    if not verify_password(password, user.password_hash):
        logger.info("authenticate_user invalid password for user=%s", user.username)
        return None

    if not user.is_active:
        logger.info("authenticate_user user inactive=%s", user.username)
        return None

    logger.info("authenticate_user authentication successful for user=%s", user.username)
    return user


def create_user_access_token(user: User) -> str:
    """Genera un token de acceso para el usuario."""
    # Usamos el id como subject para evitar colisiones si cambia el username
    return create_access_token(subject=str(user.id))


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """Dependencia para obtener el usuario autenticado a partir del JWT."""
    subject = decode_access_token(token)
    logger.debug("get_current_user subject=%s", subject)
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudieron validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user: Optional[User] = None
    # Intentar interpretar el subject como UUID (id del usuario)
    try:
        user_id = UUID(subject)
        user = db.query(User).filter(User.id == user_id).first()
    except ValueError:
        # Si no es UUID válido, intentar tratarlo como username
        user = db.query(User).filter(User.username == subject).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")
    return user


