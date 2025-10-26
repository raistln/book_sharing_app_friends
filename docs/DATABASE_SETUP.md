# Configuración de Base de Datos

## Para Nuevas Instalaciones

Si estás configurando el proyecto por primera vez en un nuevo ordenador:

### 1. Configurar variables de entorno

Crea un archivo `.env` basado en `.env.backend.example`:

```bash
cp .env.backend.example .env
```

Edita `.env` y configura tu conexión a PostgreSQL:

```env
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/nombre_db
```

### 2. Crear la base de datos

```bash
# Conectar a PostgreSQL
psql -U postgres

# Crear la base de datos
CREATE DATABASE nombre_db;

# Salir
\q
```

### 3. Ejecutar migraciones

```bash
# Aplicar todas las migraciones
alembic upgrade head
```

Esto creará todas las tablas necesarias, incluyendo:
- `users`
- `books`
- `loans`
- `groups`
- `group_members`
- `invitations`
- `messages` ← Tabla del sistema de chat
- `reviews`
- `notifications`

### 4. Verificar instalación

```bash
# Verificar que todas las tablas existen
poetry run python -c "from app.database import engine; from sqlalchemy import inspect; print('Tablas:', inspect(engine).get_table_names())"
```

## Para Desarrollo

### Ver estado actual de migraciones

```bash
alembic current
```

### Ver historial de migraciones

```bash
alembic history
```

### Crear una nueva migración

```bash
# Autogenerar migración basada en cambios en los modelos
alembic revision --autogenerate -m "descripción del cambio"

# Revisar el archivo generado en alembic/versions/
# Editar si es necesario

# Aplicar la migración
alembic upgrade head
```

### Revertir una migración

```bash
# Revertir una migración
alembic downgrade -1

# Revertir a una versión específica
alembic downgrade <revision_id>
```

## Solución de Problemas

### Error: "relation 'messages' does not exist"

Si ves este error, significa que la tabla `messages` no se creó. Solución:

```bash
# Verificar estado de migraciones
alembic current

# Si no muestra 'add_cancelled_status (head)', ejecutar:
alembic upgrade head
```

### Error: "alembic_version table not found"

La base de datos no está inicializada. Ejecutar:

```bash
alembic upgrade head
```

### Resetear la base de datos (CUIDADO: Borra todos los datos)

```bash
# Opción 1: Usar el script de reset
python reset_database.py

# Opción 2: Manual
psql -U postgres
DROP DATABASE nombre_db;
CREATE DATABASE nombre_db;
\q

# Luego ejecutar migraciones
alembic upgrade head
```

## Estructura de la Tabla Messages

La tabla `messages` tiene la siguiente estructura:

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_id UUID NOT NULL REFERENCES loans(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX ix_messages_loan_id ON messages(loan_id);
CREATE INDEX ix_messages_sender_id ON messages(sender_id);
```

### Campos:

- `id`: Identificador único del mensaje (UUID generado automáticamente)
- `loan_id`: Referencia al préstamo asociado
- `sender_id`: Referencia al usuario que envió el mensaje
- `content`: Contenido del mensaje (máximo 2000 caracteres según validación del backend)
- `created_at`: Fecha y hora de creación (con timezone)

### Relaciones:

- Un mensaje pertenece a un préstamo (`loan_id` → `loans.id`)
- Un mensaje pertenece a un usuario (`sender_id` → `users.id`)
- Si se elimina un préstamo, se eliminan todos sus mensajes (CASCADE)
- Si se elimina un usuario, se eliminan todos sus mensajes (CASCADE)

## Notas Importantes

1. **PostgreSQL requerido**: El proyecto usa características específicas de PostgreSQL como `UUID` y `gen_random_uuid()`
2. **Migraciones en orden**: Alembic aplica las migraciones en orden cronológico
3. **No editar migraciones aplicadas**: Una vez aplicada una migración, no la edites. Crea una nueva migración para cambios adicionales
4. **Backup antes de migrar**: En producción, siempre haz backup antes de ejecutar migraciones
