## Paso 13: Chat y Comunicación (Semana 5)

En este paso implementamos un chat básico entre prestamista (lender) y prestatario (borrower) vinculado a cada préstamo (Loan). Incluye modelo, migración, servicio, endpoints, tests y notas para limpieza automática.

### Objetivos
- Mensajería privada entre las dos partes de un préstamo.
- Endpoints para enviar y listar mensajes por `loan_id`.
- Control de acceso: solo lender o borrower pueden ver/enviar.
- Punto de extensión para limpieza automática de mensajes antiguos.

---

### Modelo y Migración
- Archivo: `app/models/message.py`
  - Campos: `id`, `loan_id`, `sender_id`, `content`, `created_at`.
  - FK a `loans.id` y `users.id` con `ondelete="CASCADE"`.
- Migración: `alembic/versions/fe_add_messages_table.py`
  - Crea tabla `messages` con índices por `loan_id` y `sender_id`.
  - Si aparecen múltiples heads, se crea una migración de merge y se ejecuta `alembic upgrade head`.

Aplicación de migraciones:
```bash
poetry run alembic heads
poetry run alembic merge -m "Merge heads invitations+messages" fe_add_invitation_code fe_add_messages_table
poetry run alembic upgrade head
```

---

### Schemas (Pydantic)
- Archivo: `app/schemas/message.py`
  - `MessageCreate`: `loan_id`, `content` (1..2000 chars).
  - `Message`: representación de salida con `from_attributes=True`.

---

### Servicio de Mensajes
- Archivo: `app/services/message_service.py`
  - `can_access(loan_id, user_id)`: lender o borrower del préstamo.
  - `send(loan_id, sender_id, content)`: valida acceso y persiste.
  - `list_for_loan(loan_id, user_id)`: valida acceso y lista en orden cronológico.
  - `cleanup_older_than(days)`: elimina mensajes anteriores al corte.

---

### Endpoints (FastAPI)
- Archivo: `app/api/chat.py` (prefix `/chat`)
  - `POST /chat/send` (body `MessageCreate`): envía mensaje.
  - `GET  /chat/loan/{loan_id}`: lista mensajes del préstamo.
- Registro en `app/main.py` con `app.include_router(chat_router)`.

Control de acceso:
- Ambos endpoints requieren autenticación; devuelven 403 si el usuario no es lender ni borrower del `loan_id`.

---

### Pruebas
- Archivo: `tests/test_chat.py`
  - `test_chat_send_and_receive`: crea préstamo, borrower envía, lender lee.
  - `test_chat_access_control`: un tercero no puede enviar/leer (403).

Ejecución selectiva:
```bash
poetry run pytest tests/test_chat.py -q
```

---

### Ejemplos rápidos (curl)
1) Enviar mensaje (como borrower/lender autenticado):
```bash
curl -X POST -H "Authorization: Bearer <TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"loan_id":"<LOAN_UUID>","content":"Hola"}' \
     http://localhost:8000/chat/send
```

2) Listar mensajes de un préstamo:
```bash
curl -H "Authorization: Bearer <TOKEN>" \
     http://localhost:8000/chat/loan/<LOAN_UUID>
```

---

### Limpieza automática (opcional)
- Usar `MessageService.cleanup_older_than(days)` por un job periódico (ej. cron externo o Celery/APS). 
- Recomendado: conservar últimos N días, p.ej. 30.

---

### Notas finales
- La lógica de acceso reutiliza la relación del `Loan` para validar usuarios.
- Fácil de extender con WebSockets/SSE para chat en tiempo real o con notificaciones.


