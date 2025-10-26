# 💬 Configuración del Sistema de Chat

## Resumen

El sistema de chat está completamente implementado y optimizado con:
- ✅ Polling inteligente (solo obtiene mensajes nuevos)
- ✅ Tabla `messages` en la base de datos
- ✅ Migraciones de Alembic configuradas
- ✅ Backend y frontend integrados

## Para Nuevas Instalaciones

Si estás configurando el proyecto en un **nuevo ordenador**:

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd book_sharing_app_friends
```

### 2. Instalar dependencias

```bash
# Backend
poetry install

# Frontend
cd frontend
npm install
cd ..
```

### 3. Configurar base de datos

```bash
# Crear archivo .env
cp .env.backend.example .env

# Editar .env y configurar DATABASE_URL
# DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/nombre_db
```

### 4. Crear base de datos y aplicar migraciones

```bash
# Conectar a PostgreSQL y crear la base de datos
psql -U postgres
CREATE DATABASE nombre_db;
\q

# Aplicar todas las migraciones (incluye la tabla messages)
alembic upgrade head
```

### 5. Verificar instalación

```bash
# Verificar que todas las tablas existen
poetry run python verify_database.py
```

Deberías ver:
```
✅ VERIFICACIÓN EXITOSA
   Todas las tablas necesarias están presentes
```

### 6. Iniciar servidores

```bash
# Terminal 1: Backend
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

## Para Instalaciones Existentes

Si ya tienes el proyecto configurado:

### 1. Actualizar código

```bash
git pull
```

### 2. Instalar nuevas dependencias

```bash
poetry install
```

### 3. Aplicar migraciones

```bash
alembic upgrade head
```

### 4. Verificar

```bash
poetry run python verify_database.py
```

## Estructura de la Tabla Messages

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

## Archivos Importantes

- **Migración**: `alembic/versions/fe_add_messages_table.py`
- **Modelo**: `app/models/message.py`
- **Servicio**: `app/services/message_service.py`
- **API Backend**: `app/api/chat.py`
- **API Frontend**: `frontend/lib/api/chat.ts`
- **Hook React**: `frontend/lib/hooks/use-chat.ts`
- **Componente**: `frontend/components/chat/chat-box.tsx`

## Documentación Adicional

- **Optimización del Chat**: `docs/CHAT_OPTIMIZATION.md`
- **Configuración de BD**: `docs/DATABASE_SETUP.md`

## Solución de Problemas

### Error: "relation 'messages' does not exist"

```bash
# Verificar estado de migraciones
alembic current

# Aplicar migraciones
alembic upgrade head

# Verificar
poetry run python verify_database.py
```

### Error: "No module named 'dateutil'"

```bash
poetry install
```

### El chat no muestra mensajes

1. Verificar que el backend está corriendo
2. Verificar que la tabla `messages` existe
3. Abrir DevTools del navegador y revisar la consola
4. Verificar que las peticiones a `/chat/loan/{id}` funcionan

## Características del Sistema de Chat

### Polling Optimizado

- **Primera carga**: Obtiene todos los mensajes del préstamo
- **Polling subsecuente**: Solo obtiene mensajes nuevos usando el parámetro `?since=<timestamp>`
- **Frecuencia**: Cada 3 segundos cuando la pestaña está activa
- **Background**: No hace polling cuando la pestaña está en background

### Ejemplo de Peticiones

```
# Primera petición
GET /chat/loan/123e4567-e89b-12d3-a456-426614174000
→ Devuelve todos los mensajes

# Peticiones subsecuentes
GET /chat/loan/123e4567-e89b-12d3-a456-426614174000?since=2024-01-20T10:30:00Z
→ Devuelve solo mensajes posteriores a esa fecha
```

### Seguridad

- Solo los participantes del préstamo pueden ver los mensajes
- Autenticación JWT requerida
- Validación de permisos en cada petición

## Pruebas

### Probar el chat manualmente

1. Crear dos usuarios diferentes
2. Usuario A crea un libro
3. Usuario B solicita el libro en préstamo
4. Usuario A aprueba el préstamo
5. Ambos usuarios abren el detalle del préstamo
6. Enviar mensajes desde ambos lados
7. Verificar que los mensajes aparecen en tiempo real

### Verificar optimización

En las DevTools del navegador (Network tab):

1. Observar las peticiones a `/chat/loan/{loan_id}`
2. Primera petición: sin parámetro `since`
3. Peticiones subsecuentes: con parámetro `since=<timestamp>`
4. Cuando no hay mensajes nuevos: respuesta vacía `[]`
5. Cuando hay mensajes nuevos: solo los nuevos mensajes

## Soporte

Si encuentras algún problema:

1. Ejecuta `poetry run python verify_database.py` para verificar la BD
2. Revisa los logs del backend
3. Revisa la consola del navegador
4. Verifica que las migraciones están aplicadas: `alembic current`
