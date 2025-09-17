## Paso 12: Sistema de Préstamos (Días 22-28)

Este documento describe la implementación del sistema de préstamos: solicitud, aprobación/rechazo, activación, devolución, fechas de vencimiento e historial. Incluye rutas, reglas de negocio y ejemplos de uso.

### Objetivos
- Modelo Loan con estados: requested, approved, active, returned.
- Endpoints para solicitar y gestionar préstamos.
- Actualización automática de disponibilidad del libro.
- Historial de préstamos por libro.
- Asignación de fecha de vencimiento (due_date).

Nota: Las notificaciones/recordatorios quedan como mejora futura (se dejaron trazas en logs y puntos de extensión para integrar un emisor de notificaciones).

---

### Modelo y Migración
- Archivo: `app/models/loan.py`
  - `LoanStatus = {requested, approved, active, returned}`
  - Campos: `book_id`, `borrower_id`, `lender_id`, `group_id?`, `status`, `requested_at`, `approved_at`, `due_date`, `returned_at`.
  - Relaciones: `book`, `borrower`, `lender`, `group`.

- Migración: `alembic/versions/e301a10327c7_add_loans_table.py`
  - Crea la tabla `loans` con índices por `book_id`, `borrower_id`, `lender_id`, `group_id`.

---

### Servicio de Préstamos
- Archivo: `app/services/loan_service.py`
  - `request_loan(book_id, borrower_id)`
    - Rechaza si el libro está archivado o prestado.
    - Evita solicitudes duplicadas activas (requested/approved/active) del mismo usuario para el mismo libro.
  - `approve_loan(loan_id, lender_id, due_date?)`
    - Solo el dueño del libro (lender) puede aprobar.
    - Pone `status=active`, fija `approved_at` y actualiza el libro a `loaned` con `current_borrower_id`.
  - `reject_loan(loan_id, lender_id)`
    - Solo el dueño. Borra la solicitud (flujo simple de rechazo).
  - `return_book(book_id)`
    - Cambia el préstamo activo a `returned` y actualiza el libro a `available`.
  - `set_due_date(loan_id, lender_id, due_date)`
    - Solo dueño. Permite ajustar la fecha de vencimiento para préstamos `approved/active`.
  - `get_user_loans(user_id)` y `get_book_history(book_id)`
    - Listados ordenados por `requested_at`.

---

### Endpoints (FastAPI)
- Archivo: `app/api/loans.py` (con `prefix="/loans"`)
  - `POST /loans/request` (params: `book_id`, `borrower_id`)
  - `POST /loans/{loan_id}/approve` (params: `lender_id`, `due_date?`)
  - `POST /loans/{loan_id}/reject` (params: `lender_id`)
  - `POST /loans/return` (params: `book_id`)
  - `POST /loans/{loan_id}/due-date` (params: `lender_id`, `due_date`)
  - `GET  /loans/history/book/{book_id}`

Integración en app:
- Archivo: `app/main.py`
  - `app.include_router(loans_router)` sin doble prefijo.

---

### Reglas y Validaciones Clave
- No se puede aprobar si no es el dueño del libro.
- No se pueden crear solicitudes duplicadas mientras exista una en `requested/approved/active` para el mismo libro/usuario.
- Aprobar un préstamo actualiza el estado del libro a `loaned` y asigna `current_borrower_id`.
- Devolver un libro solo es válido si está en estado `loaned` y existe un préstamo `active`.

---

### Ejemplos (curl)
1) Solicitar préstamo:
```bash
curl -X POST "http://localhost:8000/loans/request?book_id=<BOOK_ID>&borrower_id=<BORR_ID>"
```

2) Aprobar préstamo:
```bash
curl -X POST "http://localhost:8000/loans/<LOAN_ID>/approve?lender_id=<OWNER_ID>"
```

3) Devolver libro:
```bash
curl -X POST "http://localhost:8000/loans/return?book_id=<BOOK_ID>"
```

4) Historial por libro:
```bash
curl "http://localhost:8000/loans/history/book/<BOOK_ID>"
```

---

### Tests
- Archivo: `tests/test_loans_extra.py`
  - `test_loan_flow_request_approve_return`
  - `test_double_loan_should_fail`
  - `test_return_when_not_loaned_returns_400`

Ejecución:
```bash
poetry run pytest tests/test_loans_extra.py -q
```

---

### Próximos pasos (opcional)
- Notificaciones básicas y recordatorios (ej. vía email o webhook) usando eventos del servicio.
- Restricciones de due_date (no fechas pasadas) y extensiones.
- Auditoría completa por usuario/libro.


