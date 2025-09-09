"""
Configuración de la base de datos con SQLAlchemy
"""
from sqlalchemy import create_engine
import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Log de conexión
logging.getLogger(__name__).info(f"Usando DATABASE_URL: {settings.DATABASE_URL}")

# Crear el motor de base de datos
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Mostrar SQL en consola en modo debug
    pool_pre_ping=True,   # Verificar conexión antes de usar
    pool_recycle=300      # Reciclar conexiones cada 5 minutos
)

# Crear la sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


def get_db():
    """
    Dependency para obtener la sesión de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
