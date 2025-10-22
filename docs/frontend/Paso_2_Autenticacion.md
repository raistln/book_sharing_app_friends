# Paso 2: Implementación de Autenticación

## Objetivo
Implementar el sistema completo de autenticación con login, registro y protección de rutas.

## ✅ Lo que se ha Implementado

### 1. API Client de Autenticación (`lib/api/auth.ts`)

Cliente para interactuar con los endpoints de autenticación del backend:

```typescript
- login(credentials): Inicia sesión con username/password
- register(data): Crea una nueva cuenta
- getCurrentUser(): Obtiene datos del usuario actual
- updateCurrentUser(data): Actualiza perfil del usuario
- logout(): Cierra sesión (client-side)
```

**Características**:
- Manejo de FormData para login (requerido por FastAPI)
- Integración con tokens JWT
- Manejo de errores automático

### 2. Custom Hook `useAuth` (`lib/hooks/use-auth.ts`)

Hook personalizado que encapsula toda la lógica de autenticación:

```typescript
const { 
  user,              // Usuario actual
  isAuthenticated,   // Estado de autenticación
  login,             // Función para login
  register,          // Función para registro
  logout,            // Función para logout
  isLoggingIn,       // Estado de carga login
  isRegistering      // Estado de carga registro
} = useAuth();
```

**Características**:
- Integración con React Query para cache
- Integración con Zustand store
- Notificaciones automáticas con toast
- Redirección automática después de login/registro
- Manejo de errores con mensajes amigables

### 3. Componentes UI

#### Button (`components/ui/button.tsx`)
- Variantes: default, destructive, outline, secondary, ghost, link
- Tamaños: default, sm, lg, icon
- Tema personalizado con colores storybook

#### Input (`components/ui/input.tsx`)
- Estilo personalizado con tema de cuento
- Focus con anillo dorado
- Placeholder con color ink-light

#### Label (`components/ui/label.tsx`)
- Basado en Radix UI
- Accesibilidad integrada

#### Card (`components/ui/card.tsx`)
- CardHeader, CardTitle, CardDescription
- CardContent, CardFooter
- Sombra estilo libro
- Bordes dorados sutiles

### 4. Páginas de Autenticación

#### Login (`app/(auth)/login/page.tsx`)

**Características**:
- Formulario con username y password
- Validación en tiempo real
- Estados de carga
- Animaciones mágicas
- Elementos decorativos flotantes
- Link a página de registro
- Redirección a dashboard después del login

**Diseño**:
- Fondo con gradiente de colores cálidos
- Card centrado con sombra de libro
- Iconos de Sparkles y Book flotantes
- Tipografía display para títulos

#### Register (`app/(auth)/register/page.tsx`)

**Características**:
- Formulario completo: username, email, full_name, password, confirmPassword
- Validación de formulario:
  - Username mínimo 3 caracteres
  - Email válido
  - Password mínimo 6 caracteres
  - Confirmación de password
- Mensajes de error específicos
- Estados de carga
- Animaciones y decoración
- Link a página de login
- Redirección a login después del registro

### 5. Dashboard (`app/(dashboard)/dashboard/page.tsx`)

**Características**:
- Protección de ruta (redirect si no autenticado)
- Header con información del usuario
- Botón de logout
- 3 cards de acciones rápidas:
  - My Books
  - Discover
  - Community
- Sección de estadísticas (placeholder)
- Footer con cita literaria

**Diseño**:
- Header con fondo leather
- Cards con hover effects
- Animaciones de entrada
- Iconos temáticos

## 🎨 Tema Visual Aplicado

### Colores Utilizados
- **Leather** (#8B4513): Botones primarios, headers
- **Gold** (#FFD700): Acentos, iconos, highlights
- **Parchment** (#FFF8E7): Fondos principales
- **Cream** (#FFFAF0): Cards, inputs
- **Ink** (#2C1810): Texto principal

### Animaciones
- **fade-in-up**: Entrada suave de elementos
- **float**: Iconos decorativos flotantes
- **spin**: Loaders durante carga

### Sombras
- **shadow-book**: Sombra estilo libro para cards
- **shadow-book-hover**: Elevación al hacer hover
- **shadow-magical**: Brillo dorado en elementos especiales

## 🔐 Flujo de Autenticación

### Registro
1. Usuario completa formulario en `/register`
2. Validación client-side
3. POST a `/auth/register`
4. Toast de éxito
5. Redirección a `/login`

### Login
1. Usuario ingresa credenciales en `/login`
2. POST a `/auth/login` (FormData)
3. Recibe `access_token`
4. GET a `/auth/me` para obtener datos del usuario
5. Guarda token en localStorage
6. Actualiza Zustand store
7. Toast de bienvenida
8. Redirección a `/dashboard`

### Protección de Rutas
1. useAuth hook verifica `isAuthenticated`
2. useEffect en componente protegido
3. Si no autenticado → redirect a `/login`
4. Si autenticado → muestra contenido

### Logout
1. Usuario click en botón logout
2. Limpia localStorage
3. Limpia Zustand store
4. Limpia cache de React Query
5. Toast de despedida
6. Redirección a `/`

## 📁 Estructura de Archivos Creados

```
frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx          ✅ Página de login
│   │   └── register/
│   │       └── page.tsx          ✅ Página de registro
│   └── (dashboard)/
│       └── dashboard/
│           └── page.tsx          ✅ Dashboard protegido
├── components/
│   └── ui/
│       ├── button.tsx            ✅ Componente Button
│       ├── input.tsx             ✅ Componente Input
│       ├── label.tsx             ✅ Componente Label
│       └── card.tsx              ✅ Componente Card
├── lib/
│   ├── api/
│   │   └── auth.ts               ✅ Cliente API auth
│   └── hooks/
│       └── use-auth.ts           ✅ Hook de autenticación
```

## 🧪 Cómo Probar

### 1. Iniciar el Frontend
```powershell
cd frontend
npm run dev
```

Abre: http://localhost:3000

### 2. Verificar Backend
Asegúrate de que el backend esté corriendo:
```powershell
curl http://127.0.0.1:8000/health
```

### 3. Probar Registro
1. Ve a http://localhost:3000/register
2. Completa el formulario:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `password123`
   - Confirm Password: `password123`
3. Click en "Create Account"
4. Deberías ver un toast de éxito
5. Serás redirigido a `/login`

### 4. Probar Login
1. En `/login`, ingresa:
   - Username: `testuser`
   - Password: `password123`
2. Click en "Sign In"
3. Deberías ver un toast de bienvenida
4. Serás redirigido a `/dashboard`

### 5. Probar Dashboard
1. En `/dashboard` verás:
   - Tu username en el header
   - 3 cards de acciones
   - Estadísticas (en 0 por ahora)
2. Click en "Logout"
3. Serás redirigido a `/`

## 🐛 Solución de Problemas

### Error: "CORS policy"
**Causa**: Backend no permite `localhost:3000`

**Solución**: En `app/main.py` del backend:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Error: "401 Unauthorized" después de login
**Causa**: Token no se está guardando correctamente

**Solución**: Verifica en DevTools → Application → Local Storage que existe `access_token`

### Error: "Cannot find module"
**Causa**: Falta instalar dependencias

**Solución**:
```powershell
cd frontend
npm install @radix-ui/react-label
```

### Página en blanco
**Causa**: Error de JavaScript

**Solución**: Abre DevTools → Console y revisa errores

## 📊 Estado de Implementación

### ✅ Completado
- [x] Cliente API de autenticación
- [x] Hook useAuth
- [x] Componentes UI (Button, Input, Label, Card)
- [x] Página de Login
- [x] Página de Registro
- [x] Dashboard básico
- [x] Protección de rutas
- [x] Manejo de errores
- [x] Notificaciones con toast
- [x] Tema visual aplicado

### 🚧 Pendiente (Próximos Pasos)
- [ ] Recuperación de contraseña
- [ ] Verificación de email
- [ ] Editar perfil
- [ ] Subir avatar
- [ ] Middleware de Next.js para protección de rutas
- [ ] Refresh token automático

## 🎯 Próximo Paso: Gestión de Libros

En el **Paso 3** implementaremos:
- Listar libros del usuario
- Añadir nuevo libro
- Editar libro
- Eliminar libro
- Subir imagen de portada
- Ver detalles de libro

## 💡 Notas Importantes

### Tokens JWT
- Se guardan en `localStorage` con key `access_token`
- Se añaden automáticamente a todas las peticiones via interceptor
- Si expiran (401), se redirige automáticamente a `/login`

### Zustand Store
- Persiste en localStorage con key `auth-storage`
- Se sincroniza automáticamente
- Se limpia al hacer logout

### React Query
- Cache de 1 minuto para datos del usuario
- Se invalida al hacer logout
- Retry automático 1 vez

### Validación
- Client-side: Formularios con validación básica
- Server-side: Backend valida con Pydantic
- Mensajes de error específicos y amigables

## 🎨 Personalización

### Cambiar Colores
Edita `tailwind.config.ts`:
```typescript
storybook: {
  leather: '#TU_COLOR',
  gold: '#TU_COLOR',
  // ...
}
```

### Cambiar Animaciones
Edita `app/globals.css`:
```css
@keyframes fadeInUp {
  /* Tu animación */
}
```

### Cambiar Textos
Edita directamente en los componentes o crea un archivo de i18n.

## 📚 Recursos

- [Next.js Authentication](https://nextjs.org/docs/authentication)
- [React Query](https://tanstack.com/query/latest)
- [Zustand](https://zustand-demo.pmnd.rs)
- [Radix UI](https://www.radix-ui.com)

---

**¡Autenticación completada! 🎉**

Ahora los usuarios pueden registrarse, iniciar sesión y acceder a su dashboard personalizado con el hermoso tema de cuento mágico.
