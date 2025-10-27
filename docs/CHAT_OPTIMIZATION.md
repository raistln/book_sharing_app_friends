# Optimización del Sistema de Chat

## Problema Original

El sistema de chat tenía dos problemas principales:

1. **Polling ineficiente**: Cada 5 segundos se obtenían TODOS los mensajes del préstamo, incluso si no había mensajes nuevos
2. **Alto consumo de recursos**: Esto generaba tráfico innecesario y carga en el servidor y la base de datos

## Solución Implementada

Se implementó un sistema de **polling inteligente** que solo obtiene mensajes nuevos:

### Backend

1. **Endpoint optimizado** (`/chat/loan/{loan_id}`)
   - Nuevo parámetro opcional `since` (timestamp ISO 8601)
   - Solo devuelve mensajes posteriores al timestamp proporcionado
   - Mantiene compatibilidad con clientes que no usan el parámetro

2. **Servicio actualizado** (`MessageService.list_for_loan`)
   - Filtra mensajes por fecha usando `created_at > since`
   - Manejo robusto de errores en el parsing de fechas

3. **Nueva dependencia**: `python-dateutil` para parsear timestamps ISO 8601

### Frontend

1. **API actualizada** (`chatApi.getMessages`)
   - Soporte para parámetro opcional `since`
   - Envía el timestamp como query parameter

2. **Hook optimizado** (`useMessages`)
   - Mantiene referencia al timestamp del último mensaje
   - Primera carga: obtiene todos los mensajes
   - Polling subsecuente: solo obtiene mensajes nuevos
   - Combina mensajes existentes con nuevos automáticamente
   - Polling cada 3 segundos (más frecuente pero más eficiente)
   - No hace polling cuando la pestaña está en background

3. **Componente actualizado** (`ChatBox`)
   - Usa el nuevo hook con soporte para `resetTimestamp`
   - Auto-scroll al último mensaje

## Beneficios

- ✅ **Reducción de tráfico**: Solo se transfieren mensajes nuevos
- ✅ **Menor carga en BD**: Consultas más eficientes con filtro por fecha
- ✅ **Mejor UX**: Polling más frecuente (3s vs 5s) sin impacto en rendimiento
- ✅ **Ahorro de batería**: No hace polling en background
- ✅ **Escalabilidad**: El sistema escala mejor con más usuarios y mensajes

## Cómo Probar

### 1. Instalar dependencias y configurar base de datos

```bash
# Backend
poetry install

# Aplicar migraciones (crea la tabla messages)
alembic upgrade head

# Verificar que todo está correcto
poetry run python verify_database.py

# Frontend (si es necesario)
cd frontend
npm install
```

### 2. Iniciar el servidor

```bash
# Backend
python main.py

# Frontend (en otra terminal)
cd frontend
npm run dev
```

### 3. Probar el chat

1. Crear dos usuarios diferentes
2. Crear un préstamo entre ellos
3. Abrir el detalle del préstamo en ambas sesiones
4. Enviar mensajes desde ambos lados
5. Verificar que los mensajes aparecen en tiempo real

### 4. Verificar optimización

**En las DevTools del navegador (Network tab):**

1. Observar las peticiones a `/chat/loan/{loan_id}`
2. Primera petición: sin parámetro `since`
3. Peticiones subsecuentes: con parámetro `since=<timestamp>`
4. Cuando no hay mensajes nuevos: respuesta vacía `[]`
5. Cuando hay mensajes nuevos: solo los nuevos mensajes

**Ejemplo de peticiones:**

```
GET /chat/loan/123e4567-e89b-12d3-a456-426614174000
→ Devuelve todos los mensajes

GET /chat/loan/123e4567-e89b-12d3-a456-426614174000?since=2024-01-20T10:30:00Z
→ Devuelve solo mensajes posteriores a esa fecha
```

## Mejoras Futuras (Opcional)

Si el polling sigue siendo un problema a escala, considerar:

1. **WebSockets**: Para comunicación bidireccional en tiempo real
2. **Server-Sent Events (SSE)**: Para push de mensajes del servidor
3. **Long Polling**: Para reducir la frecuencia de peticiones
4. **Notificaciones Push**: Para alertar de mensajes nuevos

## Notas Técnicas

- El timestamp se guarda en un `useRef` para persistir entre renders
- Se usa `refetchIntervalInBackground: false` para no hacer polling cuando la pestaña no está activa
- El backend valida permisos antes de devolver mensajes (solo participantes del préstamo)
- Los timestamps usan formato ISO 8601 con timezone
