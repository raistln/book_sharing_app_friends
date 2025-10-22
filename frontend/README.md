# Book Sharing App - Frontend

Frontend de la aplicación Book Sharing App, construido con Next.js 14, TypeScript y Tailwind CSS con un tema visual mágico inspirado en cuentos.

## 🚀 Requisitos Previos

- Node.js 20.x o superior
- npm (viene con Node.js)
- Backend de Book Sharing App corriendo en `http://127.0.0.1:8000`

## 📦 Instalación

### 1. Instalar Node.js (si no lo tienes)

Ve a https://nodejs.org/ y descarga la versión LTS.

Verifica la instalación:
```powershell
node --version
npm --version
```

### 2. Instalar Dependencias

```powershell
cd frontend
npm install
```

Esto instalará todas las dependencias necesarias:
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- shadcn/ui components
- TanStack Query (React Query)
- Zustand (state management)
- Axios
- React Hook Form + Zod
- Lucide Icons

## 🎨 Tema Visual

El proyecto utiliza un tema visual inspirado en cuentos y libros mágicos:

- **Colores**: Tonos cálidos (marrones, dorados, crema)
- **Tipografía**: 
  - Cinzel (títulos)
  - Merriweather (cuerpo)
  - Dancing Script (decorativo)
- **Estilo**: Biblioteca mágica con texturas de papel antiguo

## 🏃 Desarrollo

### Iniciar el servidor de desarrollo

```powershell
npm run dev
```

La aplicación estará disponible en http://localhost:3000

### Build para producción

```powershell
npm run build
npm start
```

### Linting

```powershell
npm run lint
```

## 📁 Estructura del Proyecto

```
frontend/
├── app/                    # App Router de Next.js
│   ├── (auth)/            # Rutas de autenticación
│   ├── (dashboard)/       # Rutas protegidas
│   ├── layout.tsx         # Layout principal
│   ├── page.tsx           # Página de inicio
│   └── globals.css        # Estilos globales
├── components/
│   ├── ui/                # Componentes de shadcn/ui
│   ├── auth/              # Componentes de autenticación
│   ├── books/             # Componentes de libros
│   ├── layout/            # Header, Footer, Nav
│   └── shared/            # Componentes reutilizables
├── lib/
│   ├── api/               # Clientes API
│   │   └── client.ts      # Axios client configurado
│   ├── providers/         # React providers
│   │   └── query-provider.tsx
│   ├── store/             # Zustand stores
│   │   └── auth-store.ts
│   ├── types/             # TypeScript types
│   │   └── api.ts
│   └── utils.ts           # Utilidades
├── public/                # Assets estáticos
├── .env.local             # Variables de entorno
├── next.config.mjs        # Configuración de Next.js
├── tailwind.config.ts     # Configuración de Tailwind
└── tsconfig.json          # Configuración de TypeScript
```

## 🔧 Configuración

### Variables de Entorno

El archivo `.env.local` ya está configurado con:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_APP_NAME=Book Sharing App
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### Conexión con el Backend

El frontend se conecta automáticamente al backend en `http://127.0.0.1:8000`.

Asegúrate de que:
1. El backend esté corriendo
2. CORS esté configurado para permitir `http://localhost:3000`

## 📚 Características Implementadas

### Fase 1 (MVP)
- ✅ Configuración inicial del proyecto
- ✅ Tema visual estilo cuento
- ✅ Estructura de carpetas
- ✅ Cliente API configurado
- ✅ Sistema de autenticación (store)
- ✅ Página de inicio con diseño mágico
- 🚧 Login y Registro (próximo paso)
- 🚧 Gestión de libros (próximo paso)

### Próximas Fases
- Búsqueda y exploración
- Grupos y comunidades
- Chat y mensajería
- Préstamos entre usuarios

## 🎯 Próximos Pasos

1. **Implementar Autenticación**
   - Formularios de login y registro
   - Integración con endpoints del backend
   - Protección de rutas

2. **Gestión de Libros**
   - Listar libros
   - Añadir nuevo libro
   - Editar/eliminar libros propios
   - Subir imágenes de portada

## 🐛 Solución de Problemas

### Error: "Cannot find module"
Asegúrate de haber ejecutado `npm install`

### Error: "ECONNREFUSED"
Verifica que el backend esté corriendo en `http://127.0.0.1:8000`

### Errores de TypeScript
Son normales antes de instalar las dependencias. Ejecuta `npm install` primero.

## 📖 Documentación Adicional

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com)
- [TanStack Query](https://tanstack.com/query/latest)
- [Zustand](https://zustand-demo.pmnd.rs)

## 🎨 Tema y Diseño

Ver `docs/frontend/TEMA_VISUAL_CUENTO.md` para detalles completos del diseño.

## 📝 Licencia

Este proyecto es parte del Book Sharing App.

---

**¡Feliz lectura y codificación! 📚✨**
