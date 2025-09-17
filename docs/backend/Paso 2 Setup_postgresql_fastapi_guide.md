## Guía detallada: Setup de PostgreSQL con Docker y FastAPI (Hello World)

Esta guía documenta, paso a paso, lo que hicimos para preparar un entorno de desarrollo moderno con Docker + PostgreSQL y una API básica con FastAPI. El objetivo es que puedas repetir el proceso y entender el porqué de cada paso.

Contenido:
- Requisitos previos
- Configuración de WSL 2 y Docker Desktop en Windows
- Creación de variables de entorno (.env)
- Servicio de PostgreSQL con Docker Compose
- Verificación de salud y conexión a la base de datos
- Instalación de dependencias del proyecto (Poetry)
- Arranque de FastAPI (Hello World) y pruebas de endpoints
- Solución de problemas comunes (troubleshooting)

---

### Requisitos previos

- Windows 10/11 con virtualización habilitada en BIOS/UEFI (Intel VT-x / AMD-V).
- PowerShell (recomendado: PowerShell 7+).
- Git (opcional, para clonar repos).

Notas:
- Usamos WSL 2 como backend para Docker Desktop.
- Gestionamos dependencias Python con Poetry.

---

## 1) Habilitar WSL 2 y preparar Docker Desktop

En PowerShell como Administrador:

```powershell
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
wsl --install -d Ubuntu
```

- Reinicia Windows cuando se te solicite.
- Tras reiniciar, valida y actualiza WSL:

```powershell
wsl --status
wsl --update
wsl --set-default-version 2
```

Instala Docker Desktop para Windows desde `https://www.docker.com/products/docker-desktop/`.

En Docker Desktop:
- Settings → General: activa “Use the WSL 2 based engine”.
- Settings → Resources → WSL Integration: activa tu distro (p. ej., Ubuntu).

Verifica Docker y Compose:

```powershell
docker --version
docker compose version
```

Si ves versiones sin error, Docker está listo.

---

## 2) Variables de entorno (.env)

En la raíz del proyecto existe `env.example`. Crea `.env` a partir de esa plantilla:

```powershell
Copy-Item env.example .env -Force
```

Valores relevantes (por defecto):

```dotenv
DATABASE_URL=postgresql://postgres:password@localhost:5432/book_sharing
DEBUG=True
ENVIRONMENT=development
```

El proyecto carga estas variables con `pydantic-settings` en `app/config.py`.

---

## 3) Levantar PostgreSQL con Docker Compose

Archivo `docker-compose.yml` (resumen de lo importante):

```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: book_sharing
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

Arranca el servicio:

```powershell
docker compose up -d postgres
```

Verifica el estado:

```powershell
docker compose ps
docker ps --format "{{.Names}} {{.Status}}"
```

Deberías ver el contenedor `...-postgres-1` con estado `(healthy)`.

---

## 4) Verificar salud y conexión a PostgreSQL

Prueba un `SELECT 1` dentro del contenedor:

```powershell
docker exec -i book_sharing_app_friends-postgres-1 psql -U postgres -d book_sharing -c "SELECT 1;"
```

Salida esperada:

```text
 ?column?
----------
        1
(1 row)
```

Si obtienes esto, la base de datos está lista.

---

## 5) Instalar dependencias con Poetry

Este proyecto usa Poetry para manejar dependencias y entornos virtuales.

Verifica Poetry:

```powershell
poetry --version
```

Instala dependencias (según `pyproject.toml` / `poetry.lock`):

```powershell
poetry install --no-interaction --no-root
```

Prueba que la aplicación importa correctamente:

```powershell
poetry run python -c "from app.main import app; print('OK')"
```

---

## 6) Arrancar FastAPI (Hello World) y probar endpoints

Lanza el servidor Uvicorn:

```powershell
poetry run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

En otra terminal, prueba los endpoints:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/
Invoke-RestMethod http://127.0.0.1:8000/health
```

Respuestas esperadas:

```json
{
  "message": "¡Bienvenido a Book Sharing App! 📚",
  "version": "0.1.0",
  "docs": "/docs"
}
```

```json
{
  "status": "healthy",
  "environment": "development"
}
```

También puedes abrir `http://127.0.0.1:8000/docs` para la documentación interactiva.

---

## 7) Estructura relevante del proyecto

```text
app/
  main.py          # App FastAPI con CORS y endpoints / y /health
  config.py        # Carga de variables de entorno con pydantic-settings
  database.py      # Motor y sesión de SQLAlchemy
docker-compose.yml # Servicio PostgreSQL con healthcheck
.env               # Variables de entorno (local)
```

`app/main.py` expone los endpoints de verificación y bienvenida; `app/config.py` gestiona la configuración desde `.env`; y `app/database.py` prepara la conexión SQLAlchemy (usando `DATABASE_URL`).

---

## 8) Troubleshooting (problemas comunes)

- Docker: “no configuration file provided: not found”
  - Ejecuta `docker compose ...` desde la carpeta donde está `docker-compose.yml`.

- Error 500 Internal Server Error al hacer `docker pull`/`docker info`
  - Asegúrate de que WSL 2 está instalado y Docker Desktop está iniciado. Verifica:
    ```powershell
    wsl --status
    docker info
    ```

- WSL: `HCS_E_SERVICE_NOT_AVAILABLE` / “No se instaló una característica requerida”
  - Falta reiniciar tras habilitar “VirtualMachinePlatform” o WSL. Reinicia Windows.
  - Verifica virtualización en firmware:
    ```powershell
    systeminfo | findstr /i "Virtualization"
    ```

- Uvicorn no escucha en 8000 o el puerto está ocupado
  - Comprueba:
    ```powershell
    netstat -ano | findstr :8000
    ```
  - Prueba otro puerto:
    ```powershell
    poetry run uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
    ```

- Firewall bloquea solicitudes
  - Autoriza el proceso cuando Windows lo solicite o crea una excepción temporal para pruebas.

---

## 9) Qué sigue

- Inicializar migraciones con Alembic y crear la primera migración (tabla `users`).
- Añadir routers en `app/api` con prefijos (`/api/...`).
- Configurar `DATABASE_URL` por entorno (dev/test/prod). En contenedores, usa el hostname del servicio (`postgres`).

Con esto tienes un entorno base reproducible: base de datos lista con Docker y una API FastAPI funcional con endpoints de verificación.


