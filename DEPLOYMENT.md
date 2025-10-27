# Guía de Despliegue - Book Sharing App

## Opción 1: Render.com (Recomendado - Gratuito)

### Requisitos previos
- Cuenta en [Render.com](https://render.com)
- Repositorio en GitHub (ya lo tienes)

### Pasos:

#### 1. Crear cuenta en Render
1. Ve a https://render.com
2. Regístrate con tu cuenta de GitHub
3. Autoriza el acceso a tu repositorio

#### 2. Crear la base de datos PostgreSQL
1. En el dashboard de Render, haz clic en "New +"
2. Selecciona "PostgreSQL"
3. Configura:
   - **Name**: `book-sharing-db`
   - **Database**: `book_sharing`
   - **User**: `book_sharing_user`
   - **Region**: Frankfurt (más cercano a España)
   - **Plan**: Free
4. Haz clic en "Create Database"
5. **Guarda la "Internal Database URL"** (la necesitarás)

#### 3. Desplegar el Backend
1. En el dashboard, haz clic en "New +" → "Web Service"
2. Conecta tu repositorio `book_sharing_app_friends`
3. Configura:
   - **Name**: `book-sharing-backend`
   - **Region**: Frankfurt
   - **Branch**: `main`
   - **Root Directory**: (dejar vacío)
   - **Runtime**: Python 3
   - **Build Command**: `pip install poetry && poetry install --no-root`
   - **Start Command**: `poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

4. **Variables de entorno** (Add Environment Variable):
   ```
   DATABASE_URL=<pega aquí la Internal Database URL>
   SECRET_KEY=<genera una clave aleatoria segura>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ENVIRONMENT=production
   GOOGLE_BOOKS_API_KEY=<tu API key de Google Books>
   OPEN_LIBRARY_API_URL=https://openlibrary.org
   ```

5. Haz clic en "Create Web Service"
6. **Guarda la URL del backend** (ej: `https://book-sharing-backend.onrender.com`)

#### 4. Ejecutar migraciones de base de datos
Una vez desplegado el backend:
1. Ve al servicio backend en Render
2. Haz clic en "Shell" (terminal)
3. Ejecuta:
   ```bash
   poetry run alembic upgrade head
   ```

#### 5. Desplegar el Frontend
1. En el dashboard, haz clic en "New +" → "Web Service"
2. Conecta el mismo repositorio
3. Configura:
   - **Name**: `book-sharing-frontend`
   - **Region**: Frankfurt
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Runtime**: Node
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`
   - **Plan**: Free

4. **Variables de entorno**:
   ```
   NEXT_PUBLIC_API_URL=<URL del backend sin / al final>
   NODE_ENV=production
   ```

5. Haz clic en "Create Web Service"

#### 6. Verificar el despliegue
1. Espera a que ambos servicios estén "Live" (verde)
2. Visita la URL del frontend (ej: `https://book-sharing-frontend.onrender.com`)
3. Prueba el registro/login

---

## Opción 2: Railway.app (Alternativa)

### Ventajas
- Más rápido para despertar
- Mejor experiencia de desarrollo
- $5 de crédito gratis al mes

### Desventajas
- Requiere tarjeta de crédito (aunque no cobran si no excedes el tier gratuito)
- Tier gratuito más limitado que Render

### Pasos:

#### 1. Crear cuenta
1. Ve a https://railway.app
2. Regístrate con GitHub
3. Añade método de pago (no te cobrarán si te mantienes en el tier gratuito)

#### 2. Crear nuevo proyecto
1. Haz clic en "New Project"
2. Selecciona "Deploy from GitHub repo"
3. Selecciona tu repositorio

#### 3. Añadir PostgreSQL
1. Haz clic en "+ New"
2. Selecciona "Database" → "PostgreSQL"
3. Railway creará automáticamente la variable `DATABASE_URL`

#### 4. Configurar Backend
1. Selecciona el servicio del backend
2. Ve a "Settings" → "Environment"
3. Añade variables:
   ```
   SECRET_KEY=<genera una clave aleatoria>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   GOOGLE_BOOKS_API_KEY=<tu API key>
   ```
4. En "Settings" → "Deploy":
   - **Build Command**: `pip install poetry && poetry install --no-root`
   - **Start Command**: `poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `/`

5. Haz clic en "Generate Domain" para obtener una URL pública

#### 5. Ejecutar migraciones
1. Ve a la pestaña del servicio backend
2. Haz clic en los tres puntos → "Shell"
3. Ejecuta: `poetry run alembic upgrade head`

#### 6. Configurar Frontend
1. Haz clic en "+ New" → "GitHub Repo" (mismo repo)
2. En "Settings":
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`
3. Variables de entorno:
   ```
   NEXT_PUBLIC_API_URL=<URL del backend>
   ```
4. Genera dominio público

---

## Opción 3: Vercel (Frontend) + Render (Backend)

**Mejor opción para producción:**
- Frontend en Vercel (gratis, ultra rápido, sin sleep)
- Backend + DB en Render (gratis)

### Frontend en Vercel:
1. Ve a https://vercel.com
2. Importa tu repositorio
3. Configura:
   - **Framework**: Next.js
   - **Root Directory**: `frontend`
   - **Environment Variables**: `NEXT_PUBLIC_API_URL=<backend URL>`
4. Deploy automático

### Backend en Render:
Sigue los pasos de la Opción 1 (solo backend + DB)

---

## Generar SECRET_KEY segura

En tu terminal local:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

O en PowerShell:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Notas importantes

### Limitaciones del tier gratuito:
- **Render**: Servicios se duermen tras 15 min de inactividad
- **Railway**: $5/mes de crédito (suficiente para uso personal)
- **Vercel**: Sin limitaciones significativas para el frontend

### Recomendación final:
**Para empezar**: Render.com (todo en uno, gratis, fácil)
**Para mejor rendimiento**: Vercel (frontend) + Render (backend)
**Si tienes tarjeta**: Railway (mejor experiencia)

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
