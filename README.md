@'
## Plantilla: FastAPI + PostgreSQL + Docker

Plantilla lista para arrancar proyectos con FastAPI, PostgreSQL (Docker) y Alembic.

### Requisitos
- Docker y Docker Compose
- (Opcional) Python 3.11+ y Poetry para desarrollo local

### Estructura
- `app/`: aplicación FastAPI (config, modelos, esquemas, etc.)
- `alembic/` y `alembic.ini`: migraciones de base de datos
- `docker-compose.yml`: servicios `app` y `db`
- `env.example`: variables de entorno de ejemplo

### Pasos rápidos (como template)
1. Crea tu repositorio con “Use this template”.
2. Copia `env.example` a `.env` y ajusta credenciales y `DATABASE_URL`.
3. Levanta servicios:
   ```bash
   docker compose up -d
   ```
4. Aplica migraciones (si hay):
   ```bash
   alembic upgrade head
   ```
5. Abre la documentación:
   - `http://localhost:8000/docs`

### Variables de entorno
- Crea `.env` a partir de `env.example`.
- Ajusta `DATABASE_URL` para la app y Alembic (Postgres en Docker).

### Migraciones (Alembic)
- Crear revisión:
  ```bash
  alembic revision --autogenerate -m "mensaje"
  ```
- Aplicar:
  ```bash
  alembic upgrade head
  ```
- Revertir:
  ```bash
  alembic downgrade -1
  ```

### Desarrollo
- Uvicorn con reload:
  ```bash
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ```

### Personalización
- Cambia nombre del proyecto y módulos en `app/`.
- Configura CORS, auth, logging, etc. según necesidades.

### Licencia
- Ver `LICENSE`.
'@ | Set-Content -NoNewline -Path README.md