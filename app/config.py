"""
Configuración del proyecto usando Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


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
    
    # Configuración de archivos
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()
