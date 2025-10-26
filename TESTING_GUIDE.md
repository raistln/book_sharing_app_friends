# 🧪 Guía de Testing

Esta guía explica cómo ejecutar y escribir tests para el proyecto Book Sharing App.

## 📋 Tabla de Contenidos

- [Backend Tests (Python/Pytest)](#backend-tests)
- [Frontend Tests (TypeScript/Vitest)](#frontend-tests)
- [Cobertura de Tests](#cobertura)
- [Escribir Nuevos Tests](#escribir-tests)

---

## 🐍 Backend Tests

### Configuración

El backend usa **pytest** con cobertura de código. La configuración está en `pytest.ini`.

### Ejecutar Tests

```bash
# 1. Configurar variables de entorno para testing
$env:TESTING="true"
$env:DISABLE_RATE_LIMITING="true"

# 2. Ejecutar todos los tests
poetry run pytest -v

# 3. Ejecutar tests con cobertura
poetry run pytest --cov=app --cov-report=term-missing --cov-report=html -v

# 4. Ejecutar un archivo específico
poetry run pytest tests/test_notifications.py -v

# 5. Ejecutar un test específico
poetry run pytest tests/test_book_flow.py -v
poetry run pytest tests/test_loan_flow.py -v
poetry run pytest tests/test_chat_flow.py -v
poetry run pytest tests/test_notifications_flow.py -v
poetry run pytest tests/test_notification_service.py -v
poetry run pytest tests/test_notifications.py::TestNotificationService::test_create_notification -v
```

### Estructura de Tests Backend

```
tests/
├── conftest.py                    # Fixtures compartidas
├── test_auth.py                   # Autenticación
├── test_books.py                  # Gestión de libros
├── test_loans.py                  # Sistema de préstamos
├── test_groups.py                 # Grupos y miembros
├── test_chat.py                   # Sistema de chat
├── test_notifications.py          # Sistema de notificaciones (NUEVO)
├── test_search.py                 # Búsqueda de libros
├── test_book_flow.py              # Flujo principal de libros incluyendo duplicados y errores de autenticación
├── test_loan_flow.py              # Flujo de préstamos con casos negativos
├── test_chat_flow.py              # Envío/recepción, polling y control de acceso en chat
├── test_notifications_flow.py     # Generación desde chat, contador y marcado masivo de notificaciones
├── test_notification_service.py   # Pruebas unitarias completas del servicio de notificaciones
└── test_complete_flow.py          # Tests de integración
```

### Tests Principales

#### ✅ Autenticación (`test_auth.py`)
- Registro de usuarios
- Login y tokens JWT
- Refresh tokens
- Validación de permisos

#### ✅ Libros (`test_books.py`)
- CRUD de libros
- Búsqueda y filtrado
- Soft delete (archivado)
- Validaciones

#### ✅ Préstamos (`test_loans.py`)
- Solicitud de préstamos
- Aprobación/rechazo
- Devolución de libros
- Estados de préstamos

#### ✅ Chat (`test_chat.py`)
- Envío de mensajes
- Polling optimizado con `since`
- Control de acceso
- Notificaciones de mensajes

#### ✅ Notificaciones (`test_notifications.py`)
- Creación de notificaciones
- Filtrado por tipo/prioridad
- Marcar como leída
- Contador de no leídas
- Estadísticas

#### ✅ Grupos (`test_groups.py`)
- Creación de grupos
- Invitaciones
- Gestión de miembros
- Permisos de admin

### Fixtures Disponibles

```python
# En conftest.py
def test_user(db):           # Usuario de prueba
def test_user2(db):          # Segundo usuario
def test_book(db, test_user): # Libro de prueba
def auth_headers(client, test_user): # Headers con token
```

### Ejemplo de Test

```python
def test_create_notification(db: Session, test_user):
    """Test crear notificación"""
    service = NotificationService(db)
    
    notification = service.create_notification(
        user_id=test_user.id,
        notification_type=NotificationType.LOAN_REQUEST,
        title="Test",
        message="Test message",
        priority=NotificationPriority.HIGH
    )
    
    assert notification.id is not None
    assert notification.user_id == test_user.id
    assert notification.is_read is False
```

---

## ⚛️ Frontend Tests

### Configuración

El frontend usa **Vitest** + **React Testing Library**. La configuración está en `vitest.config.ts`.

### Instalar Dependencias

```bash
cd frontend

# Instalar dependencias de testing
npm install -D vitest @vitejs/plugin-react jsdom
npm install -D @testing-library/react @testing-library/jest-dom @testing-library/user-event
npm install -D @vitest/ui @vitest/coverage-v8
```

### Ejecutar Tests

```bash
cd frontend

# Ejecutar todos los tests
npm run test

# Ejecutar con UI interactiva
npm run test:ui

# Ejecutar con cobertura
npm run test:coverage

# Watch mode (re-ejecuta al guardar)
npm run test:watch
```

### Agregar Scripts a package.json

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest run --coverage"
  }
}
```

### Estructura de Tests Frontend

```
frontend/
├── tests/
│   ├── setup.ts                   # Configuración global
│   ├── components/
│   │   ├── NotificationBell.test.tsx
│   │   ├── BookCard.test.tsx
│   │   └── ChatMessage.test.tsx
│   ├── hooks/
│   │   ├── use-auth.test.ts
│   │   ├── use-notifications.test.ts
│   │   └── use-books.test.ts
│   └── utils/
│       ├── notifications.test.ts
│       └── api.test.ts
└── vitest.config.ts
```

### Ejemplo de Test de Componente

```typescript
// tests/components/NotificationBell.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { NotificationBell } from '@/components/notifications/notification-bell';

describe('NotificationBell', () => {
  it('muestra el contador de notificaciones no leídas', async () => {
    render(<NotificationBell />);
    
    // Esperar a que carguen las notificaciones
    await waitFor(() => {
      expect(screen.getByText('3')).toBeInTheDocument();
    });
  });
  
  it('abre el dropdown al hacer click', async () => {
    const user = userEvent.setup();
    render(<NotificationBell />);
    
    const bell = screen.getByRole('button');
    await user.click(bell);
    
    expect(screen.getByText('Notificaciones')).toBeInTheDocument();
  });
});
```

### Ejemplo de Test de Hook

```typescript
// tests/hooks/use-notifications.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { useNotifications } from '@/lib/hooks/use-notifications';

describe('useNotifications', () => {
  it('obtiene notificaciones del usuario', async () => {
    const { result } = renderHook(() => useNotifications());
    
    await waitFor(() => {
      expect(result.current.notifications).toHaveLength(5);
    });
  });
});
```

---

## 📊 Cobertura de Tests

### Backend

```bash
# Generar reporte de cobertura
poetry run pytest --cov=app --cov-report=html

# Ver reporte en navegador
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac/Linux
```

**Objetivo de cobertura**: 80% (configurado en `pytest.ini`)

### Frontend

```bash
cd frontend

# Generar reporte de cobertura
npm run test:coverage

# Ver reporte en navegador
start coverage/index.html  # Windows
open coverage/index.html   # Mac/Linux
```

### Áreas Críticas con Cobertura

✅ **Backend (>80%)**:
- Autenticación y autorización
- CRUD de libros
- Sistema de préstamos
- Chat y mensajes
- Notificaciones
- Grupos e invitaciones

✅ **Frontend (Objetivo >70%)**:
- Componentes principales (Header, NotificationBell, BookCard)
- Hooks de datos (use-auth, use-notifications, use-books)
- Utilidades (formatters, validators)
- API clients

---

## ✍️ Escribir Nuevos Tests

### Principios

1. **AAA Pattern**: Arrange, Act, Assert
2. **Un test, un concepto**: Cada test debe probar una sola cosa
3. **Tests independientes**: No deben depender del orden de ejecución
4. **Nombres descriptivos**: El nombre debe explicar qué se prueba

### Backend: Agregar Test para Nuevo Endpoint

```python
# tests/test_my_feature.py
import pytest
from fastapi.testclient import TestClient

def test_my_new_endpoint(client: TestClient, auth_headers):
    """Test descripción de lo que hace"""
    # Arrange
    data = {"field": "value"}
    
    # Act
    response = client.post("/my-endpoint", json=data, headers=auth_headers)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["field"] == "value"
```

### Frontend: Agregar Test para Nuevo Componente

```typescript
// tests/components/MyComponent.test.tsx
import { render, screen } from '@testing-library/react';
import { MyComponent } from '@/components/MyComponent';

describe('MyComponent', () => {
  it('renderiza correctamente', () => {
    render(<MyComponent title="Test" />);
    expect(screen.getByText('Test')).toBeInTheDocument();
  });
});
```

---

## 🚀 CI/CD

### GitHub Actions (Ejemplo)

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install poetry
      - run: poetry install
      - run: poetry run pytest --cov=app

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd frontend && npm ci
      - run: cd frontend && npm run test:coverage
```

---

## 📝 Checklist para PR

Antes de hacer un Pull Request, asegúrate de:

- [ ] Todos los tests pasan (`pytest` y `npm test`)
- [ ] La cobertura no ha bajado
- [ ] Has agregado tests para el nuevo código
- [ ] Los tests son claros y descriptivos
- [ ] No hay tests comentados o skipped sin razón

---

## 🔧 Troubleshooting

### Backend

**Error: "Database is locked"**
```bash
# Asegúrate de que TESTING=true esté configurado
$env:TESTING="true"
```

**Error: "Rate limit exceeded"**
```bash
# Deshabilita rate limiting para tests
$env:DISABLE_RATE_LIMITING="true"
```

### Frontend

**Error: "Cannot find module"**
```bash
# Reinstala dependencias
cd frontend
rm -rf node_modules
npm install
```

**Error: "window is not defined"**
- Asegúrate de que `environment: 'jsdom'` esté en `vitest.config.ts`

---

## 📚 Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

## 🎯 Próximos Pasos

1. **Aumentar cobertura frontend** a >70%
2. **Tests E2E** con Playwright
3. **Tests de performance** con Locust
4. **Tests de seguridad** con OWASP ZAP
