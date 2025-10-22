"""
Script simple para limpiar la base de datos usando SQLAlchemy.
Elimina todas las tablas y las recrea desde los modelos.
"""
import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text, inspect
from app.config import settings
from app.database import Base
import logging

# Importar todos los modelos para que SQLAlchemy los conozca
from app.models.user import User
from app.models.book import Book
from app.models.loan import Loan
from app.models.group import Group, GroupMember
from app.models.invitation import Invitation
from app.models.notification import Notification
from app.models.review import Review

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_database():
    """Elimina y recrea todas las tablas"""
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        # Obtener tablas existentes
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        logger.info("🗑️  Eliminando todas las tablas y tipos...")
        if existing_tables:
            logger.info(f"📋 Tablas a eliminar: {', '.join(existing_tables)}")
        
        # Eliminar tipos ENUM primero
        with engine.connect() as conn:
            logger.info("   Eliminando tipos ENUM...")
            enum_types = [
                'book_status',
                'book_condition',
                'book_type',
                'book_genre',
                'loan_status', 
                'grouprole',
                'notificationtype',
                'notificationpriority'
            ]
            
            for enum_type in enum_types:
                try:
                    conn.execute(text(f'DROP TYPE IF EXISTS {enum_type} CASCADE'))
                    logger.info(f"      ✓ {enum_type}")
                except Exception:
                    pass
            
            conn.commit()
        
        # Eliminar todas las tablas
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ Tablas eliminadas")
        
        # Recrear todas las tablas
        logger.info("\n🔨 Creando nuevas tablas...")
        Base.metadata.create_all(bind=engine)
        
        # Verificar tablas creadas
        inspector = inspect(engine)
        new_tables = inspector.get_table_names()
        
        logger.info(f"\n📊 Tablas creadas ({len(new_tables)}):")
        for table in sorted(new_tables):
            logger.info(f"   ✓ {table}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise
    finally:
        engine.dispose()


def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🔄 RESET SIMPLE DE BASE DE DATOS")
    print("="*60)
    print(f"\n📍 Base de datos: {settings.DATABASE_URL.split('@')[-1]}")
    
    # Confirmar acción
    print("\n⚠️  ADVERTENCIA: Esta acción eliminará TODOS los datos.")
    response = input("¿Estás seguro de que quieres continuar? (escribe 'SI' para confirmar): ")
    
    if response.strip().upper() != "SI":
        print("\n❌ Operación cancelada")
        return
    
    try:
        reset_database()
        
        print("\n" + "="*60)
        print("✅ BASE DE DATOS RESETEADA EXITOSAMENTE")
        print("="*60)
        print("\n💡 La base de datos está limpia y lista para pruebas.")
        print("   Puedes iniciar el servidor y crear datos de prueba.\n")
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERROR AL RESETEAR BASE DE DATOS")
        print("="*60)
        print(f"\n{str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
