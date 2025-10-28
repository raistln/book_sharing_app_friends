# Guía de Despliegue - Book Sharing App

Render ha retirado la base de datos gratuita permanente, pero mantiene el plan gratuito para servicios web. Supabase sigue ofreciendo PostgreSQL gratis (con límites generosos). A fecha de 2025-10-28, la combinación más sencilla sin tarjeta es **Frontend en Vercel + Backend en Render + Base de datos en Supabase**.

## Variables de entorno necesarias

| Variable | Descripción |
| --- | --- |
| `DATABASE_URL` | Cadena Postgres (añade `?sslmode=require` si el proveedor lo requiere) |
| `SECRET_KEY` | Genera con `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |
| `ENVIRONMENT` | `production` |
| `OPENLIBRARY_BASE_URL` | `https://openlibrary.org` |
| `GOOGLE_BOOKS_API_KEY` | Tu API key (opcional, pero recomendable) |

> **Tip:** Crea primero un fichero `.env.backend` local con estas variables para facilitar el despliegue.

---

## Opción 1 (Recomendada): Frontend en **Vercel** + Backend en **Render** + Base de datos en **Supabase**

### 1. Crear la base de datos en Supabase
1. Ve a [https://supabase.com](https://supabase.com) y crea una cuenta (GitHub o email, sin tarjeta).
2. "New project" → completa:
   - **Organization**: crea una nueva (free tier).
   - **Name**: `book-sharing-db` (o similar).
   - **Database Password**: genera una contraseña segura (la necesitarás).
   - **Region**: `EU-West-1` (Irlanda) para menos latencia desde España.
3. Una vez aprovisionado, entra en *Settings → Database → Connection string* y copia la URL `postgresql://…`. Añade `?sslmode=require` si no aparece.
4. Opcional: en *Auth → Policies* puedes ajustar reglas si en el futuro usas Supabase Auth.

### 2. Backend en Render (FastAPI)
1. Ve a [https://render.com](https://render.com) y autentícate con GitHub.
2. "New +" → "Web Service" → selecciona este repositorio.
3. Configuración recomendada:
   - **Name**: `book-sharing-backend`
   - **Region**: `Frankfurt (EU Central)`
   - **Branch**: `main`
   - **Build Command**: `pip install poetry && poetry install --no-root`
   - **Start Command**: `poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free
4. Variables de entorno (*Environment → Add environment variable*):
   ```
   DATABASE_URL = <connection string de Supabase>
   SECRET_KEY = <python -c "import secrets; print(secrets.token_urlsafe(32))">
   ALGORITHM = HS256
   ACCESS_TOKEN_EXPIRE_MINUTES = 30
   ENVIRONMENT = production
   OPENLIBRARY_BASE_URL = https://openlibrary.org
   GOOGLE_BOOKS_API_KEY = <tu api key>
   ```
5. Crea el servicio y espera al primer deploy.
6. Ejecuta migraciones: en el servicio → *Shell* →
   ```bash
   poetry run alembic upgrade head
   ```
7. Guarda la URL pública (ej. `https://book-sharing-backend.onrender.com`).

### 3. Frontend en Vercel (Next.js)
1. Desde Vercel importa el repo (ya tienes cuenta):
   - **Framework**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output**: `.next`
2. Variables en *Settings → Environment Variables*:
   - `NEXT_PUBLIC_API_URL = https://book-sharing-backend.onrender.com`
3. Deploy y prueba la URL proporcionada. Si usas dominio personalizado, añade CORS en `.env.backend` (`CORS_ORIGINS`).

### Ventajas
- Todo el despliegue sin tarjeta.
- Supabase ofrece backups diarios, API SQL y panel gráfico.
- Render mantiene el backend siempre accesible (se "duerme" tras 15 min, demora 30-40 s en despertar).

### Inconvenientes
- Supabase free tier limita a 500 MB de almacenamiento y 200 MB de transferencia diaria.
- Render free puede experimentar cold start; considera pings periódicos.

---

## Opción 2: Frontend en **Vercel** + Backend en **Deta Space** + Base de datos en **Supabase**

> Deta Space (https://deta.space) ofrece hosting gratuito para microservicios Python (FastAPI incluido) sin requerir tarjeta.

### Pasos backend en Deta Space
1. Crea cuenta en Deta Space e instala [Space CLI](https://docs.deta.space/docs/getting_started/cli/setup/).
2. Desde la raíz del proyecto backend (puedes crear un subdirectorio `backend_space` si prefieres):
   ```bash
   space new
   ```
   Elige plantilla `Python` y responde las preguntas.
3. Ajusta `main.py`/`spacefile` para lanzar FastAPI (ejemplo):
   ```toml
   [app]
   engine = "python3.11"
   cmd = "poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000"
   ```
4. Define variables en `space push` → `Variables`:
   ```
   DATABASE_URL = <Supabase URL>
   SECRET_KEY = ...
   ALGORITHM = HS256
   ACCESS_TOKEN_EXPIRE_MINUTES = 30
   ENVIRONMENT = production
   OPENLIBRARY_BASE_URL = https://openlibrary.org
   GOOGLE_BOOKS_API_KEY = <tu api key>
   ```
5. Sube la app: `space push` y luego `space release`.
6. Obtén la URL pública (ej. `https://book-sharing-backend-USER.deta.app`).
7. Ejecuta migraciones manualmente usando `space shell` (o crea un endpoint `/admin/migrate` temporal si la shell no estuviera disponible):
   ```bash
   poetry run alembic upgrade head
   ```

### Frontend en Vercel
Repite los pasos de la opción 1 configurando `NEXT_PUBLIC_API_URL` con la URL de Deta.

### Ventajas / inconvenientes
- ✅ Deta no requiere tarjeta y mantiene la app encendida.
- ✅ Deploy muy rápido vía CLI.
- ⚠️ Límite de CPU/memoria de los micros (ideal para proyectos ligeros).
- ⚠️ Shell interactiva en beta: si falla, usa scripts propios para migraciones.

### Pasos backend en Railway
1. Crea cuenta en [https://railway.app](https://railway.app) y vincula GitHub.
2. "New Project" → "Deploy from GitHub repo" → selecciona este repositorio.
3. Configura variables en *Settings → Variables*:
   ```
   DATABASE_URL = <connection string de Neon>
   SECRET_KEY = ...
   ALGORITHM = HS256
   ACCESS_TOKEN_EXPIRE_MINUTES = 30
   ENVIRONMENT = production
   OPENLIBRARY_BASE_URL = https://openlibrary.org
   GOOGLE_BOOKS_API_KEY = <tu api key>
   ```
4. *Deploy Settings*:
   - **Root Directory**: `.`
   - **Build Command**: `pip install poetry && poetry install --no-root`
   - **Start Command**: `poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Tras el primer deploy, abre la consola → ejecuta `poetry run alembic upgrade head`.
6. Copia la URL pública (ej: `https://book-sharing-backend.up.railway.app`).

### Frontend en Vercel
Sigue los mismos pasos que en la opción 1, cambiando `NEXT_PUBLIC_API_URL` por la URL de Railway.

### Ventajas / inconvenientes
- ✅ Deploy súper sencillo (todo via dashboard). 
- ✅ Créditos gratuitos reiniciados cada mes.
- ⚠️ Requiere tarjeta y vigilar consumo para no superar los 5 USD.

---

## Opción 3: Frontend en **Vercel** + Backend en **Render** (Free) + Base de datos en **Railway** (créditos mensuales)

Si en algún momento necesitas más capacidad de base de datos que Supabase free pueda ofrecer, Railway permite crear PostgreSQL con los 5 USD de crédito mensual (requiere tarjeta). Configura Render como en la opción 1 y usa la cadena `DATABASE_URL` proporcionada por Railway.

---

## Generar `SECRET_KEY`

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

En PowerShell:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Consideraciones finales

- **Monitoring**: Fly.io, Vercel y Railway ofrecen logs en tiempo real desde su dashboard. Activa alertas por email si el servicio falla.
- **Migraciones futuras**: cada vez que merges a `main`, vuelve a ejecutar `alembic upgrade head` en el servicio backend.
- **Cold start**: Fly.io y Railway pueden necesitar unos segundos tras inactividad. Para eliminarlo, considera planes de pago o monitor con pings periódicos.
- **Buckets / ficheros**: si en el futuro subes imágenes, usa servicios como Cloudinary o S3 compatibles (Fly.io/Railway no tienen almacenamiento persistente).

Si en el futuro aparece un proveedor con tier gratuito permanente que incluya Postgres + Python + Node en un solo lugar, añade una nueva sección en este documento.

### Monitoreo:
- Render te envía emails si algo falla
- Puedes ver logs en tiempo real desde el dashboard
- Configura health checks para mantener servicios activos

---

## Troubleshooting

### El backend no arranca:
1. Verifica que `DATABASE_URL` esté configurada
2. Revisa los logs en el dashboard
3. Asegúrate de que las migraciones se ejecutaron

### El frontend no conecta con el backend:
1. Verifica que `NEXT_PUBLIC_API_URL` esté correcta (sin `/` al final)
2. Comprueba que el backend tenga CORS configurado
3. Revisa la consola del navegador para errores

### Base de datos no conecta:
1. Usa la "Internal Database URL" (no la externa)
2. Verifica que el servicio backend esté en la misma región que la DB
3. Comprueba que las credenciales sean correctas
