"""
Configuración del proyecto usando Pydantic Settings
"""
from pydantic import Field, PostgresDsn, validator, ConfigDict
from pydantic_settings import BaseSettings
from typing import Optional
import configparser
import os


class Settings(BaseSettings):
    # Configuración de la base de datos
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/book_sharing"
    
    # Configuración de seguridad
    SECRET_KEY: str = "your-development-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # APIs externas
    OPENLIBRARY_BASE_URL: str = "https://openlibrary.org"
    GOOGLE_BOOKS_API_KEY: Optional[str] = None
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CACHE_TTL_SECONDS: int = 6 * 60 * 60  # 6 horas
    
    # Configuración de la aplicación
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    PREFER_ALEMBIC_DB_URL: bool = True
    
    # Configuración de archivos
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    
    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 30
    AUTH_RATE_LIMIT_PER_MINUTE: int = 5
    UPLOAD_RATE_LIMIT_PER_MINUTE: int = 10
    
    # Logging
    LOG_LEVEL: str = "INFO"
    ENABLE_FILE_LOGGING: bool = True
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    @property
    def cors_origins_list(self):
        """Convert CORS origins string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    model_config = ConfigDict(env_file=".env", case_sensitive=True)


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
