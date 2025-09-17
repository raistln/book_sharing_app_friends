# Paso 9: Sistema de Grupos e Invitaciones

## 📋 Resumen

Implementamos un sistema completo de grupos de usuarios que permite:
- Crear y gestionar grupos de amigos
- Sistema de roles (admin/member)
- Invitaciones por email
- Gestión de miembros
- Control de acceso basado en membresía

## 🎯 Funcionalidades Implementadas

### 1. Modelos de Base de Datos
- **Group**: Grupos de usuarios con creador y descripción
- **GroupMember**: Relación many-to-many con roles
- **Invitation**: Sistema de invitaciones por email

### 2. Sistema de Roles
- **ADMIN**: Puede gestionar miembros, crear invitaciones, modificar grupo
- **MEMBER**: Puede ver el grupo y sus miembros

### 3. Sistema de Invitaciones
- Invitaciones por email con mensaje personal
- Expiración automática (7 días)
- Respuesta aceptar/rechazar
- Prevención de invitaciones duplicadas

### 4. Control de Acceso
- Solo miembros pueden ver grupos
- Solo admins pueden gestionar miembros
- Solo el creador puede eliminar el grupo

## 📁 Archivos Creados

### Modelos
- `app/models/group.py` - Modelos Group y GroupMember
- `app/models/invitation.py` - Modelo Invitation

### Schemas
- `app/schemas/group.py` - Schemas para grupos y miembros
- `app/schemas/invitation.py` - Schemas para invitaciones

### Servicios
- `app/services/group_service.py` - Lógica de negocio para grupos

### API
- `app/api/groups.py` - Endpoints REST para grupos

### Tests
- `tests/test_groups.py` - Tests de integración

## 🗄️ **Modelos de Base de Datos**

### Group
```python
- id: UUID (primary key)
- name: str (nombre del grupo)
- description: str (descripción opcional)
- created_by: UUID (foreign key -> users)
- created_at: datetime
- updated_at: datetime
```

### GroupMember
```python
- id: UUID (primary key)
- group_id: UUID (foreign key -> groups)
- user_id: UUID (foreign key -> users)
- role: enum (admin, member)
- joined_at: datetime
- invited_by: UUID (foreign key -> users)
```

### Invitation
```python
- id: UUID (primary key)
- group_id: UUID (foreign key -> groups)
- email: str (email del invitado)
- message: str (mensaje personal opcional)
- invited_by: UUID (foreign key -> users)
- created_at: datetime
- expires_at: datetime
- is_accepted: bool (null = pendiente)
- responded_at: datetime
```

## 🌐 **Endpoints API**

### Grupos
```http
POST   /groups/                    # Crear grupo
GET    /groups/                    # Listar grupos del usuario
GET    /groups/{group_id}          # Obtener grupo específico
PUT    /groups/{group_id}          # Actualizar grupo (solo admins)
DELETE /groups/{group_id}          # Eliminar grupo (solo creador)
```

### Miembros
```http
GET    /groups/{group_id}/members           # Listar miembros
POST   /groups/{group_id}/members           # Añadir miembro (solo admins)
PUT    /groups/{group_id}/members/{member_id}  # Actualizar rol (solo admins)
DELETE /groups/{group_id}/members/{member_id}  # Remover miembro (solo admins)
```

### Invitaciones
```http
POST   /groups/{group_id}/invitations       # Crear invitación (solo admins)
GET    /groups/{group_id}/invitations       # Listar invitaciones (solo admins)
GET    /groups/invitations/pending          # Invitaciones pendientes del usuario
POST   /groups/invitations/{invitation_id}/respond  # Responder invitación
```

## 📖 **Uso de los Servicios**

### GroupService

```python
from app.services.group_service import GroupService

# Crear grupo
group = group_service.create_group(group_data, creator_id)

# Obtener grupos del usuario
groups = group_service.get_user_groups(user_id)

# Añadir miembro
member = group_service.add_member(group_id, admin_id, member_data)

# Crear invitación
invitation = group_service.create_invitation(group_id, admin_id, invitation_data)

# Responder invitación
member = group_service.respond_to_invitation(invitation_id, email, accept)
```

## 🔐 **Sistema de Permisos**

### Creador del Grupo
- Puede eliminar el grupo
- Es automáticamente admin
- Puede gestionar todos los aspectos

### Administradores
- Pueden añadir/remover miembros
- Pueden cambiar roles de miembros
- Pueden crear invitaciones
- Pueden actualizar información del grupo

### Miembros
- Pueden ver el grupo y sus miembros
- Pueden responder invitaciones
- No pueden gestionar el grupo

## 📧 **Sistema de Invitaciones**

### Flujo de Invitación
1. **Admin crea invitación** → Se envía email al invitado
2. **Usuario recibe invitación** → Ve invitaciones pendientes
3. **Usuario responde** → Acepta o rechaza
4. **Si acepta** → Se convierte en miembro automáticamente

### Validaciones
- No se pueden crear invitaciones duplicadas
- Las invitaciones expiran en 7 días
- Solo admins pueden crear invitaciones
- Solo el email correcto puede responder

## 🧪 **Testing**

### Tests Implementados
```bash
poetry run pytest tests/test_groups.py -v
```

### Casos de Prueba
- ✅ Crear grupo exitosamente
- ✅ Obtener grupos del usuario
- ✅ Acceso no autorizado
- ✅ Gestión de miembros
- ✅ Sistema de invitaciones
- ✅ Control de permisos

## 🔄 **Flujo de Trabajo Típico**

### 1. Crear Grupo
```http
POST /groups/
{
  "name": "Mi Grupo de Lectura",
  "description": "Compartimos libros de ciencia ficción"
}
```

### 2. Invitar Amigos
```http
POST /groups/{group_id}/invitations
{
  "email": "amigo@example.com",
  "message": "¡Únete a nuestro grupo!"
}
```

### 3. Aceptar Invitación
```http
POST /groups/invitations/{invitation_id}/respond
{
  "accept": true
}
```

### 4. Gestionar Miembros
```http
# Añadir miembro directamente
POST /groups/{group_id}/members
{
  "user_id": "uuid",
  "role": "member"
}

# Cambiar rol
PUT /groups/{group_id}/members/{member_id}
{
  "role": "admin"
}
```

## ⚡ **Características Avanzadas**

### Roles Dinámicos
- Los roles se pueden cambiar dinámicamente
- Solo admins pueden cambiar roles
- El creador siempre es admin

### Invitaciones Inteligentes
- Prevención de duplicados
- Expiración automática
- Mensajes personalizados

### Control de Acceso Granular
- Verificación de membresía en cada endpoint
- Diferentes permisos por rol
- Validación de propietario

## 🚀 **Próximos Pasos**

1. **Notificaciones**: Enviar emails reales de invitación
2. **Códigos de Invitación**: URLs públicas para unirse
3. **Estadísticas**: Métricas de actividad del grupo
4. **Configuración**: Ajustes de privacidad del grupo
5. **Historial**: Log de acciones del grupo

## 💡 **Casos de Uso**

### Grupo de Lectura
- Compartir bibliotecas personales
- Recomendar libros
- Organizar lecturas grupales

### Club de Libros
- Discutir libros específicos
- Votar por próximas lecturas
- Compartir reseñas

### Biblioteca Compartida
- Préstamos entre miembros
- Catálogo grupal
- Gestión de devoluciones

## ⚠️ **Limitaciones Actuales**

1. **Sin emails reales**: Las invitaciones no se envían por email
2. **Sin notificaciones**: No hay sistema de notificaciones
3. **Sin búsqueda**: No se puede buscar grupos públicos
4. **Sin límites**: No hay límite de miembros por grupo

## 🔧 **Configuración**

### Variables de Entorno
```env
# Ya configuradas en pasos anteriores
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

### Migraciones
```bash
# Aplicar migraciones
poetry run alembic upgrade head

# Crear nueva migración
poetry run alembic revision --autogenerate -m "Description"
```

## 📊 **Métricas del Sistema**

- **Grupos creados**: Contador por usuario
- **Miembros activos**: Por grupo
- **Invitaciones enviadas**: Por grupo
- **Tasa de aceptación**: Invitaciones aceptadas/total

## 🎉 **Resultado Final**

El sistema de grupos está completamente funcional y permite:
- ✅ Crear y gestionar grupos
- ✅ Sistema de roles y permisos
- ✅ Invitaciones por email
- ✅ Gestión de miembros
- ✅ Control de acceso granular
- ✅ Tests completos
- ✅ Documentación detallada

¡El sistema está listo para conectar amigos y compartir libros! 🚀
