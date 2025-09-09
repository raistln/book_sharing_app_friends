"""
Configuración del proyecto usando Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
import configparser
import os


class Settings(BaseSettings):
    # Configuración de la base de datos
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/book_sharing"
    
    # Configuración de seguridad
    SECRET_KEY: str = "your-secret-key-here-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # APIs externas
    OPENLIBRARY_BASE_URL: str = "https://openlibrary.org"
    GOOGLE_BOOKS_API_KEY: Optional[str] = None
    
    # Configuración de la aplicación
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    PREFER_ALEMBIC_DB_URL: bool = True
    
    # Configuración de archivos
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True


def _maybe_override_db_url_with_alembic(settings: Settings) -> Settings:
    if not settings.PREFER_ALEMBIC_DB_URL:
        return settings
    try:
        config = configparser.ConfigParser()
        ini_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic.ini")
        if os.path.exists(ini_path):
            config.read(ini_path)
            ini_url = config.get("alembic", "sqlalchemy.url", fallback=None)
            if ini_url:
                settings.DATABASE_URL = ini_url
    except Exception:
        pass
    return settings


# Instancia global de configuración
settings = _maybe_override_db_url_with_alembic(Settings())
