# 🔔 Sistema de Notificaciones

## Resumen

El sistema de notificaciones está completamente implementado y ahora **funcional**:
- ✅ Tabla `notifications` en la base de datos
- ✅ Backend con endpoints completos
- ✅ Notificaciones automáticas en eventos de préstamos
- ✅ Frontend con componente NotificationBell integrado
- ✅ Polling automático de notificaciones

## Arquitectura

### Backend

**Modelo**: `app/models/notification.py`
- Tipos de notificaciones: LOAN_REQUEST, LOAN_APPROVED, LOAN_REJECTED, etc.
- Prioridades: low, medium, high, urgent
- Campos: title, message, is_read, created_at, read_at, data (JSONB)

**Servicio**: `app/services/notification_service.py`
- `create_notification()`: Crear notificación
- `get_user_notifications()`: Obtener notificaciones con filtros
- `mark_as_read()`: Marcar como leída
- `mark_all_as_read()`: Marcar todas como leídas
- `get_unread_count()`: Contador de no leídas
- Funciones helper para cada tipo de evento

**API**: `app/api/notifications.py`
- `GET /notifications/`: Obtener notificaciones
- `GET /notifications/unread/count`: Contador de no leídas
- `GET /notifications/stats`: Estadísticas
- `GET /notifications/{id}`: Obtener una específica
- `PATCH /notifications/{id}/read`: Marcar como leída
- `POST /notifications/read-all`: Marcar todas como leídas
- `DELETE /notifications/{id}`: Eliminar notificación

### Frontend

**Componente**: `components/notifications/notification-bell.tsx`
- Icono de campana en el header
- Badge con contador de no leídas
- Dropdown con últimas 5 notificaciones
- Botón "Marcar todas como leídas"
- Link a página completa de notificaciones

**Hook**: `lib/hooks/use-notifications.ts`
- `useNotifications()`: Obtener notificaciones con filtros
- `useUnreadNotifications()`: Solo no leídas
- `useMarkAsRead()`: Marcar como leída/todas

**API Client**: `lib/api/notifications.ts`
- Funciones para consumir todos los endpoints

## Eventos que Generan Notificaciones

### 1. Solicitud de Préstamo (LOAN_REQUEST)
**Cuándo**: Un usuario solicita un libro prestado
**Destinatario**: Dueño del libro (lender)
**Prioridad**: HIGH
**Datos**: loan_id, book_title, sender_name

### 2. Préstamo Aprobado (LOAN_APPROVED)
**Cuándo**: El dueño aprueba una solicitud
**Destinatario**: Usuario que solicitó (borrower)
**Prioridad**: HIGH
**Datos**: loan_id, book_title, sender_name

### 3. Préstamo Rechazado (LOAN_REJECTED)
**Cuándo**: El dueño rechaza una solicitud
**Destinatario**: Usuario que solicitó (borrower)
**Prioridad**: MEDIUM
**Datos**: loan_id, book_title, sender_name

### 4. Nuevo Mensaje (NEW_MESSAGE)
**Cuándo**: Alguien envía un mensaje en el chat del préstamo
**Destinatario**: El otro usuario del préstamo
**Prioridad**: MEDIUM
**Datos**: loan_id, sender_id, sender_name, message_preview

### 5. Invitación a Grupo (GROUP_INVITATION)
**Cuándo**: Alguien te invita a unirte a un grupo
**Destinatario**: Usuario invitado (si está registrado)
**Prioridad**: MEDIUM
**Datos**: group_id, group_name, invitation_id, invitation_code, inviter_id, inviter_name, message
**Características especiales**:
- Muestra el código de invitación directamente en la notificación
- Botón de copiar para copiar el código al portapapeles
- Permite unirse al grupo sin buscar el código

### 6. Recordatorio de Devolución (DUE_DATE_REMINDER)
**Cuándo**: Scheduler automático (días antes del vencimiento)
**Destinatario**: Usuario que tiene el libro (borrower)
**Prioridad**: MEDIUM
**Datos**: loan_id, book_title, due_date

### 5. Préstamo Vencido (OVERDUE)
**Cuándo**: Scheduler automático (después del vencimiento)
**Destinatario**: Usuario que tiene el libro (borrower)
**Prioridad**: URGENT
**Datos**: loan_id, book_title

## Integración en el Código

### Crear Notificación en un Evento

```python
from app.services.notification_service import create_loan_request_notification

# En el servicio de préstamos
create_loan_request_notification(
    db=self.db,
    lender_id=lender.id,
    borrower_name=borrower.username,
    book_title=book.title,
    loan_id=loan.id
)
```

### Usar en el Frontend

```tsx
import { NotificationBell } from '@/components/notifications/notification-bell';

// En el Header
<NotificationBell />
```

## Configuración

### Variables de Entorno (Opcional)

Para notificaciones por email (futuro):
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-contraseña
EMAIL_FROM=noreply@booksharing.app
```

## Cómo Probar

### 1. Verificar que la tabla existe

```bash
poetry run python verify_database.py
```

Debe mostrar la tabla `notifications` en la lista.

### 2. Probar flujo completo

1. **Usuario A** crea un libro
2. **Usuario B** solicita el libro
   - ✅ Usuario A recibe notificación "Nueva solicitud de préstamo"
3. **Usuario A** aprueba el préstamo
   - ✅ Usuario B recibe notificación "¡Préstamo aprobado!"
4. **Usuario A** rechaza una solicitud
   - ✅ Usuario B recibe notificación "Préstamo rechazado"

### 3. Verificar en el frontend

1. Abrir la aplicación
2. Buscar el icono de campana 🔔 en el header
3. Si hay notificaciones no leídas, aparece un badge rojo con el número
4. Click en la campana para ver las notificaciones
5. Click en una notificación para marcarla como leída
6. Click en "Marcar todas" para marcar todas como leídas

### 4. Verificar en la base de datos

```sql
-- Ver todas las notificaciones
SELECT * FROM notifications ORDER BY created_at DESC;

-- Ver notificaciones no leídas
SELECT * FROM notifications WHERE is_read = false;

-- Ver notificaciones por usuario
SELECT * FROM notifications WHERE user_id = 'UUID-DEL-USUARIO';
```

## Mejoras Futuras (Opcional)

### 1. Notificaciones en Tiempo Real
Actualmente usa polling. Para tiempo real:
- WebSockets con Socket.IO
- Server-Sent Events (SSE)
- Firebase Cloud Messaging

### 2. Notificaciones Push del Navegador
```typescript
// Solicitar permiso
const permission = await Notification.requestPermission();

// Mostrar notificación
new Notification('Título', {
  body: 'Mensaje',
  icon: '/icon.png',
});
```

### 3. Notificaciones por Email
Ya está parcialmente implementado en `email_service.py`. Solo falta configurar SMTP.

### 4. Notificaciones Programadas
El scheduler ya está configurado para:
- Recordatorios de devolución (X días antes)
- Alertas de préstamos vencidos

### 5. Configuración de Usuario
Permitir que cada usuario configure:
- Qué tipos de notificaciones recibir
- Frecuencia de recordatorios
- Canal preferido (app, email, push)

## Solución de Problemas

### No aparecen notificaciones

1. **Verificar que el backend está corriendo**
   ```bash
   python main.py
   ```

2. **Verificar que la tabla existe**
   ```bash
   poetry run python verify_database.py
   ```

3. **Verificar logs del backend**
   Buscar líneas como:
   ```
   INFO - Notification created for loan request: loan_id=...
   ```

4. **Verificar en DevTools del navegador**
   - Network tab: Buscar peticiones a `/notifications/`
   - Console: Buscar errores

### El contador no se actualiza

El hook `useNotifications` hace polling automático cada cierto tiempo. Si no se actualiza:

1. Verificar que React Query está configurado
2. Refrescar manualmente: `refetch()`
3. Verificar que el token de autenticación es válido

### Error 403 Forbidden

El usuario no tiene permiso para ver esas notificaciones. Las notificaciones solo son visibles para su destinatario.

## Archivos Importantes

**Backend:**
- `app/models/notification.py` - Modelo
- `app/services/notification_service.py` - Lógica de negocio
- `app/services/loan_service.py` - Integración con préstamos
- `app/api/notifications.py` - Endpoints REST
- `app/schemas/notification.py` - Schemas Pydantic

**Frontend:**
- `components/notifications/notification-bell.tsx` - Componente principal
- `lib/hooks/use-notifications.ts` - Hooks React
- `lib/api/notifications.ts` - Cliente API
- `lib/types/notification.ts` - Tipos TypeScript
- `lib/utils/notifications.ts` - Utilidades

**Migraciones:**
- `alembic/versions/add_notifications_table.py` - Crea la tabla

## Documentación Adicional

- **API Endpoints**: Ver `/docs` en el backend (Swagger UI)
- **Tipos de Notificaciones**: Ver `NotificationType` enum en el modelo
- **Prioridades**: Ver `NotificationPriority` enum en el modelo
