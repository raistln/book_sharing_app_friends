## 📘 Paso 5: Autenticación JWT y Endpoints de Usuario

En este paso implementamos un sistema de autenticación con JWT sobre FastAPI y SQLAlchemy, añadiendo registro de usuarios, login con OAuth2 password flow y endpoints protegidos para obtener el perfil del usuario.

### 🎯 Objetivos
- Registrar usuarios con contraseña hasheada (bcrypt).
- Iniciar sesión para obtener un token JWT.
- Proteger rutas y obtener el usuario actual mediante dependencia.
- Exponer endpoints: `POST /auth/register`, `POST /auth/login`, `GET /auth/me`, `GET /users/me`.

---

### 🧱 Prerrequisitos
- FastAPI, SQLAlchemy, Alembic configurados.
- Modelo `User` y schemas Pydantic (`app/models/user.py`, `app/schemas/user.py`).
- Variables en `app/config.py` con `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`.

---

### 1) Utilidades de seguridad (hash y JWT)
Archivo: `app/utils/security.py`

- Hash de contraseñas con `passlib[bcrypt]`.
- Creación y decodificación de tokens con `python-jose`.

Puntos clave:
- `hash_password(plain)`, `verify_password(plain, hash)`.
- `create_access_token(subject, expires_minutes)` emite JWT con `sub` y `exp`.
- `decode_access_token(token)` devuelve el `subject` (id/username) o `None` si es inválido.

---

### 2) Servicio de autenticación
Archivo: `app/services/auth_service.py`

Responsabilidades:
- `register_user(db, user_in)`: valida duplicados y guarda `password_hash`.
- `authenticate_user(db, username, password)`: comprueba credenciales.
- `create_user_access_token(user)`: emite JWT con el `id` del usuario como `sub`.
- `get_current_user(db, token)`: dependencia para obtener el usuario a partir del JWT. Acepta `sub` como UUID (preferido) o `username` como respaldo.

También define `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")` para el flujo OAuth2.

---

### 3) Endpoints de autenticación y usuario
Archivos:
- `app/api/auth.py`: `/auth/register`, `/auth/login`, `/auth/me`.
- `app/api/users.py`: `/users/me`.

Detalles:
- `POST /auth/register`: recibe `UserCreate` (incluye `password`), devuelve `User` público.
- `POST /auth/login`: recibe formulario `username` + `password` (x-www-form-urlencoded), devuelve `{ access_token, token_type }`.
- `GET /auth/me`: requiere `Bearer <token>` y devuelve el usuario actual.
- `GET /users/me`: equivalente a `/auth/me` pero bajo prefijo `users`.

---

### 4) Registro de routers
Archivo: `app/main.py`

Se añadieron:
- `app.include_router(auth_router)`
- `app.include_router(users_router)`

La app ya exponía `GET /` y `GET /health`.

---

### 5) Variables de configuración relevantes
Archivo: `app/config.py`

- `SECRET_KEY`: clave secreta para firmar JWT.
- `ALGORITHM`: algoritmo (por defecto `HS256`).
- `ACCESS_TOKEN_EXPIRE_MINUTES`: minutos de expiración (por defecto 30).

En desarrollo pueden mantenerse valores por defecto; en producción, usa `.env`.

---

### 6) Cómo probar (Swagger y CLI)

Swagger: abre `/docs`.
1. `POST /auth/register` con `username`, `password`, `email` opcional.
2. `POST /auth/login` con `username` y `password` (form-data). Copia `access_token`.
3. Pulsa “Authorize” y pega `Bearer TU_TOKEN`.
4. Llama a `GET /auth/me` o `GET /users/me`.

CLI (ejemplos):
```bash
# Registro
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"SuperSegura123","email":"alice@example.com"}'

# Login (form-urlencoded)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=SuperSegura123"

# Con token
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/auth/me
```

---

### 7) Errores comunes y soluciones
- 401 en `/auth/me`: no se envió `Authorization: Bearer <token>` o token expirado.
- 400 en `/auth/register`: `username` o `email` ya en uso.
- DB no responde al migrar: asegurar Docker Desktop activo y `docker compose up -d postgres`.

---

### 8) Estructura resultante (resumen)
```
app/
  api/
    auth.py
    users.py
  services/
    auth_service.py
  utils/
    security.py
  main.py
```

---

### 9) Replicar en futuros proyectos (checklist)
- Añadir dependencias: `passlib[bcrypt]`, `python-jose[cryptography]`, `python-multipart`.
- Crear utilidades de seguridad (hash/JWT).
- Servicio de auth con registro, autenticación y dependencia `get_current_user`.
- Endpoints `/auth` y `/users` y registrar routers.
- Configurar claves/algoritmo en settings.
- Probar con Swagger y CLI.

---

### 10) Apéndice: Tipos y decisiones
- `sub` del token como `UUID` del usuario reduce ambigüedad vs username.
- `OAuth2PasswordBearer(tokenUrl="/auth/login")` permite integración automática en Swagger.
- `from_attributes=True` en schemas para serializar objetos SQLAlchemy.


