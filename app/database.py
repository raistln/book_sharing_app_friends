"""
Configuración de la base de datos con SQLAlchemy
"""
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# Log de conexión
logging.getLogger(__name__).info(f"Usando DATABASE_URL: {settings.DATABASE_URL}")

# Permitir URL alternativa en entornos de test
database_url = settings.DATABASE_URL

if os.getenv("TESTING") == "true":
    database_url = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")

connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}

# Crear el motor de base de datos
engine = create_engine(
    database_url,
    echo=settings.DEBUG,  # Mostrar SQL en consola en modo debug
    pool_pre_ping=True,   # Verificar conexión antes de usar
    pool_recycle=300,      # Reciclar conexiones cada 5 minutos
    connect_args=connect_args,
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
