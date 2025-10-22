# Resumen del Proyecto Frontend - Book Sharing App

## Estado Actual

### ✅ Documentación Completada
1. **Paso 1**: Configuración inicial con Next.js, TypeScript y Tailwind
2. **Guía de instalación**: Node.js para Windows
3. **Tema visual**: Diseño estilo cuento/storybook mágico

### ⏳ Pendiente de Instalación
- Node.js (requerido para continuar)

## Roadmap de Desarrollo

### Fase 1: MVP (Versión Mínima Viable) 🎯
**Prioridad Alta - Implementar primero**

1. **Autenticación** ✨
   - Login
   - Registro
   - Gestión de sesión con JWT
   - Protección de rutas

2. **Gestión de Libros** 📚
   - Listar libros
   - Ver detalles de un libro
   - Añadir nuevo libro
   - Editar libro propio
   - Eliminar libro propio
   - Subir imagen de portada

### Fase 2: Funcionalidades Sociales 🌟
**Prioridad Media**

3. **Búsqueda y Exploración** 🔍
   - Barra de búsqueda
   - Filtros avanzados (género, idioma, condición)
   - Paginación
   - Ordenamiento
   - Sugerencias de búsqueda

4. **Grupos y Comunidades** 👥
   - Crear grupo
   - Unirse a grupo
   - Biblioteca de grupo
   - Gestión de miembros

### Fase 3: Interacciones Avanzadas 💬
**Prioridad Baja - Futuras mejoras**

5. **Chat y Mensajería** 💬
   - Conversaciones privadas
   - Notificaciones en tiempo real

6. **Préstamos entre Usuarios** 🤝
   - Solicitar préstamo
   - Aprobar/rechazar préstamo
   - Gestión de devoluciones
   - Historial de préstamos

## Stack Tecnológico

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Lenguaje**: TypeScript
- **Estilos**: Tailwind CSS + shadcn/ui
- **Estado**: Zustand
- **Datos**: TanStack Query (React Query)
- **Formularios**: React Hook Form + Zod
- **HTTP**: Axios
- **Iconos**: Lucide React

### Backend (Ya existente)
- **Framework**: FastAPI
- **Base de datos**: PostgreSQL
- **Cache**: Redis
- **Autenticación**: JWT

## Tema Visual: Storybook Mágico 📖✨

### Concepto
Diseño que evoca la magia de los libros de cuentos con:
- Colores cálidos (marrones, dorados, crema)
- Tipografía elegante (Cinzel, Merriweather)
- Texturas de papel antiguo
- Animaciones mágicas sutiles
- Iconografía temática de libros

### Paleta Principal
- **Leather**: #8B4513 (Cuero de libro)
- **Gold**: #FFD700 (Dorado mágico)
- **Parchment**: #FFF8E7 (Papel antiguo)
- **Ink**: #2C1810 (Tinta oscura)

## Estructura del Proyecto

```
frontend/
├── app/
│   ├── (auth)/              # Rutas de autenticación
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/         # Rutas protegidas
│   │   ├── books/           # Gestión de libros
│   │   ├── search/          # Búsqueda
│   │   ├── loans/           # Préstamos
│   │   ├── groups/          # Grupos
│   │   └── profile/         # Perfil de usuario
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── ui/                  # shadcn components
│   ├── auth/                # Componentes de auth
│   ├── books/               # Componentes de libros
│   ├── layout/              # Header, Footer, Nav
│   └── shared/              # Componentes reutilizables
├── lib/
│   ├── api/                 # Clientes API
│   ├── hooks/               # Custom hooks
│   ├── store/               # Zustand stores
│   ├── types/               # TypeScript types
│   └── utils.ts             # Utilidades
└── public/
    ├── textures/            # Texturas de fondo
    └── patterns/            # Patrones decorativos
```

## Endpoints del Backend

### Autenticación
- `POST /auth/register` - Registrar usuario
- `POST /auth/login` - Iniciar sesión
- `GET /auth/me` - Obtener usuario actual

### Libros
- `GET /books/` - Listar libros
- `POST /books/` - Crear libro
- `GET /books/{id}` - Ver libro
- `PUT /books/{id}` - Actualizar libro
- `DELETE /books/{id}` - Eliminar libro

### Búsqueda
- `GET /search/books` - Búsqueda avanzada
- `GET /search/suggestions` - Sugerencias

### Usuarios
- `GET /users/me` - Perfil actual
- `PUT /users/me` - Actualizar perfil
- `GET /users/me/favorites` - Favoritos

### Préstamos
- `GET /loans/` - Listar préstamos
- `POST /loans/` - Crear préstamo
- `PUT /loans/{id}` - Actualizar préstamo

### Grupos
- `GET /groups/` - Listar grupos
- `POST /groups/` - Crear grupo
- `POST /groups/{id}/join` - Unirse a grupo

### Metadatos
- `GET /metadata/genres` - Lista de géneros
- `GET /metadata/languages` - Lista de idiomas
- `GET /metadata/conditions` - Condiciones de libros

## Próximos Pasos

### Inmediato
1. **Instalar Node.js** siguiendo `INSTALACION_NODEJS.md`
2. **Verificar instalación**: `node --version` y `npm --version`
3. **Crear proyecto**: Ejecutar comandos del Paso 1

### Después de la Instalación
1. Configurar proyecto Next.js
2. Instalar dependencias
3. Configurar tema visual
4. Implementar autenticación (Paso 2)
5. Implementar gestión de libros (Paso 3)

## Comandos Útiles

### Backend (Python/Poetry)
```powershell
# Activar entorno
poetry shell

# Iniciar servidor
poetry run uvicorn app.main:app --reload
```

### Frontend (Node/npm)
```powershell
# Desarrollo
npm run dev

# Build
npm run build

# Producción
npm start
```

## Notas Importantes

### CORS
El backend debe permitir `http://localhost:3000` en la configuración de CORS.

### Variables de Entorno
Crear `.env.local` en el frontend con:
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### Autenticación
- Tokens JWT guardados en localStorage
- Interceptores de Axios para añadir token automáticamente
- Redirección a login si token expira

## Recursos

### Documentación
- Next.js: https://nextjs.org/docs
- Tailwind CSS: https://tailwindcss.com/docs
- shadcn/ui: https://ui.shadcn.com
- React Query: https://tanstack.com/query/latest
- Zustand: https://zustand-demo.pmnd.rs

### Diseño
- Tema visual: `TEMA_VISUAL_CUENTO.md`
- Paleta de colores: Ver archivo de tema
- Tipografía: Cinzel, Merriweather, Dancing Script

## Contacto y Soporte

Si tienes dudas durante la implementación:
1. Revisa la documentación del paso correspondiente
2. Consulta los ejemplos de código
3. Verifica que el backend esté corriendo
4. Comprueba las variables de entorno

---

**Última actualización**: 15 de octubre de 2025
**Versión**: 1.0.0
**Estado**: En desarrollo - Fase de configuración
