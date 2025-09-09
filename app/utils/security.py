"""
Utilidades de seguridad: hashing de contraseñas y manejo de JWT
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Genera el hash seguro de una contraseña en texto plano."""
    return password_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verifica que la contraseña coincida con el hash almacenado."""
    return password_context.verify(plain_password, password_hash)


def create_access_token(subject: str, expires_delta_minutes: Optional[int] = None) -> str:
    """Crea un JWT de acceso con expiración configurable.

    subject: identificador del usuario (por ejemplo, str(user.id) o username)
    """
    if expires_delta_minutes is None:
        expires_delta_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=expires_delta_minutes)
    to_encode = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """Decodifica un JWT y devuelve el subject si es válido, None si no lo es."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        subject: str = payload.get("sub")
        if subject is None:
            return None
        return subject
    except JWTError:
        return None


