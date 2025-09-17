## ⚡ Paso 7: Caching con Redis

En este paso integramos una capa de caché con Redis para acelerar las búsquedas de libros contra APIs externas, reduciendo latencia, llamadas redundantes y evitando límites de tasa.

### 🎯 Objetivos
- Añadir Redis en Docker Compose.
- Configurar variables `REDIS_URL` y TTL.
- Implementar un cliente de caché sencillo.
- Integrar caché en el servicio de búsqueda (`BookSearchService`).
- Probar end-to-end que todo funciona.

---

### 1) Servicio Redis en Docker
Archivo: `docker-compose.yml`

Se añadió el servicio:
- Imagen: `redis:7-alpine`
- Puerto: `6379`
- Healthcheck y modo append-only

Arranque:
```bash
docker compose up -d redis
```

---

### 2) Configuración en la app
Archivos: `env.example` y `app/config.py`

- `REDIS_URL=redis://localhost:6379/0`
- `CACHE_TTL_SECONDS=21600` (6 horas por defecto)

`app/config.py` expone ambas variables para usarlas en servicios.

---

### 3) Dependencia
Archivo: `pyproject.toml`

- Se añadió la librería `redis` (cliente oficial de Python).

Instalación:
```bash
poetry lock
poetry install
```

---

### 4) Cliente de caché
Archivo: `app/services/cache.py`

Interfaz mínima:
- `get_json(key)` → devuelve dict/list o `None`.
- `set_json(key, value, ttl_seconds)` → guarda JSON con expiración.

Usa `Redis.from_url(REDIS_URL, decode_responses=True)` para manejar strings.

---

### 5) Integración en la búsqueda de libros
Archivo: `app/services/book_search_service.py`

Claves de caché empleadas:
- Por ISBN: `search:isbn:{isbn}:{limit}`
- Por título: `search:title:{slug_titulo}:{limit}` (slug simple en minúsculas, espacios → '+')

Flujo:
1. Intentar leer de caché.
2. Si no hay datos, consultar OpenLibrary; si falla o no devuelve resultados, usar Google Books.
3. Normalizar resultados y guardarlos en caché.
4. Devolver la lista al cliente.

Beneficios:
- Respuestas casi instantáneas en búsquedas repetidas.
- Protección ante fallos temporales de APIs externas.

---

### 6) Pruebas end-to-end

- Reinicio limpio: `docker compose down -v && docker compose up -d postgres redis`
- Migraciones: `poetry run alembic upgrade head`
- App: `poetry run python main.py`
- Suite: `poetry run pytest -q` → 9 tests pasando.

Puedes observar en logs que búsquedas repetidas responden más rápido gracias a la caché.

---

### 7) Mejores prácticas y siguientes pasos
- Añadir invalidación selectiva si incorporas escritura de datos externos (no aplica aquí).
- Monitorizar tasa de aciertos (metrics) y latencias.
- Proteger Redis si se despliega fuera de red local (auth, TLS, red privada).
- Opcional: usar `aioredis`/`fastapi-cache2` para caché a nivel de endpoints.


