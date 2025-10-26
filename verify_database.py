"""
Script para verificar que la base de datos está correctamente configurada
"""
from app.database import engine
from sqlalchemy import inspect, text

def verify_database():
    """Verifica que todas las tablas necesarias existen"""
    
    required_tables = [
        'users',
        'books',
        'loans',
        'groups',
        'group_members',
        'invitations',
        'messages',  # Tabla del sistema de chat
        'reviews',
        'notifications',
        'alembic_version'
    ]
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print("=" * 60)
    print("VERIFICACIÓN DE BASE DE DATOS")
    print("=" * 60)
    
    # Verificar tablas
    print("\n📋 Verificando tablas...")
    missing_tables = []
    for table in required_tables:
        if table in existing_tables:
            print(f"  ✅ {table}")
        else:
            print(f"  ❌ {table} - FALTA")
            missing_tables.append(table)
    
    # Verificar migración actual
    print("\n📦 Verificando migraciones...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        versions = [row[0] for row in result]
        if versions:
            print(f"  ✅ Migración actual: {versions[0]}")
        else:
            print("  ❌ No hay migraciones aplicadas")
    
    # Verificar estructura de tabla messages
    if 'messages' in existing_tables:
        print("\n💬 Verificando estructura de tabla 'messages'...")
        columns = inspector.get_columns('messages')
        column_names = [col['name'] for col in columns]
        
        required_columns = ['id', 'loan_id', 'sender_id', 'content', 'created_at']
        for col in required_columns:
            if col in column_names:
                print(f"  ✅ Columna '{col}'")
            else:
                print(f"  ❌ Columna '{col}' - FALTA")
        
        # Verificar índices
        indexes = inspector.get_indexes('messages')
        print(f"\n  📊 Índices encontrados: {len(indexes)}")
        for idx in indexes:
            print(f"    - {idx['name']}: {idx['column_names']}")
    
    # Resumen
    print("\n" + "=" * 60)
    if missing_tables:
        print("❌ VERIFICACIÓN FALLIDA")
        print(f"   Faltan {len(missing_tables)} tabla(s): {', '.join(missing_tables)}")
        print("\n💡 Solución: Ejecuta 'alembic upgrade head'")
    else:
        print("✅ VERIFICACIÓN EXITOSA")
        print("   Todas las tablas necesarias están presentes")
    print("=" * 60)

if __name__ == "__main__":
    verify_database()
