"""
Script para limpiar y resetear la base de datos completamente.
Elimina todas las tablas y las recrea usando Alembic.
"""
import sys
import os
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text, inspect
from app.config import settings
from app.database import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def drop_all_tables():
    """Elimina todas las tablas de la base de datos"""
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        logger.info("🗑️  Eliminando todas las tablas y tipos...")
        
        # Obtener inspector para ver las tablas
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            logger.info("✅ No hay tablas para eliminar")
        else:
            logger.info(f"📋 Tablas encontradas: {', '.join(tables)}")
        
        # Eliminar todas las tablas y tipos ENUM usando DROP CASCADE
        with engine.connect() as conn:
            # Desactivar foreign key checks temporalmente
            conn.execute(text("SET session_replication_role = 'replica';"))
            
            # Eliminar cada tabla
            for table in tables:
                logger.info(f"   Eliminando tabla: {table}")
                conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
            
            # Eliminar la tabla de versiones de Alembic si existe
            conn.execute(text('DROP TABLE IF EXISTS "alembic_version" CASCADE'))
            
            # Eliminar tipos ENUM personalizados
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
                except Exception as e:
                    logger.debug(f"      - {enum_type} (no existe)")
            
            # Reactivar foreign key checks
            conn.execute(text("SET session_replication_role = 'origin';"))
            
            conn.commit()
        
        logger.info("✅ Todas las tablas y tipos eliminados correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error al eliminar tablas: {e}")
        raise
    finally:
        engine.dispose()


def recreate_with_alembic():
    """Recrea las tablas usando Alembic migrations"""
    import subprocess
    
    try:
        logger.info("\n🔄 Ejecutando migraciones de Alembic...")
        
        # Ejecutar alembic upgrade head
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            logger.info("✅ Migraciones aplicadas correctamente")
            logger.info(result.stdout)
        else:
            logger.error("❌ Error al aplicar migraciones:")
            logger.error(result.stderr)
            raise Exception("Fallo en migraciones de Alembic")
            
    except Exception as e:
        logger.error(f"❌ Error al ejecutar Alembic: {e}")
        raise


def verify_database():
    """Verifica que las tablas se hayan creado correctamente"""
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"\n📊 Tablas creadas ({len(tables)}):")
        for table in sorted(tables):
            logger.info(f"   ✓ {table}")
        
        return len(tables) > 0
        
    finally:
        engine.dispose()


def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🔄 RESET COMPLETO DE BASE DE DATOS")
    print("="*60)
    print(f"\n📍 Base de datos: {settings.DATABASE_URL.split('@')[-1]}")
    
    # Confirmar acción
    print("\n⚠️  ADVERTENCIA: Esta acción eliminará TODOS los datos.")
    response = input("¿Estás seguro de que quieres continuar? (escribe 'SI' para confirmar): ")
    
    if response.strip().upper() != "SI":
        print("\n❌ Operación cancelada")
        return
    
    try:
        # Paso 1: Eliminar todas las tablas
        drop_all_tables()
        
        # Paso 2: Recrear con Alembic
        recreate_with_alembic()
        
        # Paso 3: Verificar
        if verify_database():
            print("\n" + "="*60)
            print("✅ BASE DE DATOS RESETEADA EXITOSAMENTE")
            print("="*60)
            print("\n💡 La base de datos está limpia y lista para pruebas.")
            print("   Puedes iniciar el servidor y crear datos de prueba.\n")
        else:
            print("\n⚠️  Advertencia: No se encontraron tablas después del reset")
            
    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERROR AL RESETEAR BASE DE DATOS")
        print("="*60)
        print(f"\n{str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
