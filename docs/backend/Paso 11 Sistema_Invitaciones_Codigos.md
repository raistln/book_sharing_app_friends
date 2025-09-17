## Día 19-21: Sistema de Invitaciones con códigos únicos

Este tutorial explica cómo quedó implementado el sistema de invitaciones para grupos, incluyendo la generación de códigos únicos, los endpoints para consultar y aceptar invitaciones por código, validaciones y ejemplos de uso.

### Objetivo
- Permitir a un administrador de grupo invitar a usuarios mediante email.
- Generar un `code` único por invitación para poder compartir un enlace directo de acceso.
- Exponer endpoints para consultar una invitación por `code` y aceptarla sin conocer su `id`.

---

### Cambios en modelos (SQLAlchemy)
- Archivo: `app/models/invitation.py`
  - Se añadió el campo `code` único y con índice:
    - `code = Column(String(64), unique=True, index=True, nullable=False, default=lambda: uuid.uuid4().hex)`
  - Se mantienen los campos ya existentes: `id`, `group_id`, `email`, `message`, `invited_by`, `created_at`, `expires_at`, `is_accepted`, `responded_at`.
  - Relaciones: `group` y `inviter` (con `User.sent_group_invitations`).

- Archivo: `app/models/group.py`
  - La relación `invitations` del modelo `Group` referencia a `Invitation` y realiza cascade delete-orphan.

---

### Migración Alembic
- Archivo: `alembic/versions/fe_add_invitation_code.py`
  - `upgrade()`: agrega columna `code` (String(64)) e índice único `ix_invitations_code`.
  - `downgrade()`: elimina índice y columna.

Aplicación de migraciones:
```bash
docker compose up -d  # Asegurar Postgres/Redis
poetry run alembic upgrade head
```

---

### Schemas (Pydantic)
- Archivo: `app/schemas/invitation.py`
  - El schema `Invitation` incluye explícitamente `code: str` y está configurado con `model_config = ConfigDict(from_attributes=True)` para mapear desde ORM.

---

### Servicio de Grupos
- Archivo: `app/services/group_service.py`
  - `create_invitation(group_id, user_id, invitation_data)`:
    - Solo admin puede crear invitaciones.
    - Evita duplicados: si ya existe una invitación pendiente vigente para el mismo email, no crea otra.
    - Genera `code` único (`uuid4().hex`).
    - Expiración por defecto: 7 días.
  - `get_group_invitations(group_id, user_id)`:
    - Solo admin puede listar invitaciones del grupo.
  - `get_user_invitations(email)`:
    - Lista invitaciones pendientes vigentes para un email.
  - `respond_to_invitation(invitation_id, email, accept)`:
    - Valida que esté pendiente y vigente.
    - Si `accept=True`, añade al usuario como `GroupRole.MEMBER`.

---

### Endpoints (FastAPI)
- Archivo: `app/api/groups.py`
  - `POST /groups/{group_id}/invitations` → Crea invitación (solo admin). Responde con la invitación incluyendo `code`.
  - `GET /groups/{group_id}/invitations` → Lista invitaciones del grupo (solo admin). Responde con cada invitación incluyendo `code`.
  - `GET /groups/invitations/by-code/{code}` → Obtiene una invitación por `code` (no requiere autenticación para previsualizar).
  - `POST /groups/invitations/accept/{code}` → Acepta una invitación por `code` (requiere autenticación del usuario que acepta).

Notas de serialización:
- Se añadió lógica para asegurar que `code` esté presente en las respuestas de creación y de listado, incluso si el ORM todavía no hubiera materializado el atributo en el objeto (consulta directa a la tabla para enriquecer la respuesta cuando es necesario).

---

### Ejemplos de uso (curl)
1) Crear una invitación (como admin):
```bash
curl -X POST \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"email":"invitee@example.com","message":"¡Únete!"}' \
  http://localhost:8000/groups/<GROUP_ID>/invitations
```
Respuesta (ejemplo):
```json
{
  "id": "<invitation-uuid>",
  "group_id": "<group-uuid>",
  "email": "invitee@example.com",
  "message": "¡Únete!",
  "invited_by": "<admin-uuid>",
  "created_at": "2025-09-12T14:00:00Z",
  "expires_at": "2025-09-19T14:00:00Z",
  "is_accepted": null,
  "responded_at": null,
  "code": "a1b2c3..."
}
```

2) Consultar una invitación por código (sin token):
```bash
curl http://localhost:8000/groups/invitations/by-code/<CODE>
```

3) Aceptar una invitación por código (usuario autenticado):
```bash
curl -X POST \
  -H "Authorization: Bearer <USER_TOKEN>" \
  http://localhost:8000/groups/invitations/accept/<CODE>
```

---

### Validaciones y errores frecuentes
- Crear invitación duplicada pendiente (mismo email, no expirada) → 400.
- Responder a invitación expirada o inexistente → 400/404.
- Listar invitaciones del grupo sin ser admin → 404 (según diseño actual; no expone existencia del recurso).

---

### Tests añadidos (resumen)
- Archivo: `tests/test_invitations_extra.py`
  - `test_create_duplicate_pending_invitation_returns_400`
  - `test_respond_to_expired_invitation_returns_400`
  - `test_respond_to_nonexistent_invitation_returns_404`
  - `test_get_group_invitations_non_admin_returns_404`
  - `test_invitation_by_code_and_accept` (flujo con `code`)

Ejecución selectiva:
```bash
poetry run pytest tests/test_invitations_extra.py::test_invitation_by_code_and_accept -q
```

---

### Registro y depuración
- Se añadieron logs informativos en `GroupService` y endpoints de grupos para auditar creación y aceptación de invitaciones.
- Si hay problemas de serialización del `code`, revisar los logs del endpoint y que las migraciones estén aplicadas.

---

### Requisitos de entorno
- `pydantic>=2` y FastAPI actualizados (Poetry gestiona dependencias).
- Asegurar que el editor usa el intérprete del virtualenv de Poetry si aparece un warning de import.

---

### Conclusión
El sistema de invitaciones permite invitar por email, compartir un código único y aceptar la invitación con un solo endpoint. Las respuestas de la API incluyen el `code`, lo que habilita flujos de invitación por enlace y facilita pruebas automatizadas y depuración.


