# Paso 1: Configuración Inicial del Frontend

## Objetivo
Configurar un proyecto Next.js con TypeScript, Tailwind CSS y las herramientas necesarias para conectar con el backend de Book Sharing App.

## Pre-requisitos (Windows con Poetry)

### Instalar Node.js y npm

1. **Descargar Node.js**:
   - Ve a https://nodejs.org/
   - Descarga la versión LTS (Long Term Support) - recomendado v20.x o superior
   - Ejecuta el instalador y sigue los pasos (asegúrate de marcar "Add to PATH")

2. **Verificar instalación**:
   ```powershell
   node --version
   npm --version
   ```

3. **Alternativa con Chocolatey** (si lo tienes instalado):
   ```powershell
   choco install nodejs-lts
   ```

### Nota sobre Poetry
Poetry es para el backend Python. Para el frontend usaremos npm (que viene con Node.js).

## Stack Tecnológico
- **Framework**: Next.js 14 (App Router)
- **Lenguaje**: TypeScript
- **Estilos**: Tailwind CSS + shadcn/ui
- **Estado Global**: Zustand
- **API Client**: Axios + TanStack Query (React Query)
- **Formularios**: React Hook Form + Zod
- **Iconos**: Lucide React

## 1. Crear el Proyecto Next.js

```bash
# Navegar a la raíz del proyecto
cd d:\IAs\book_sharing_app_friends

# Crear el proyecto Next.js con TypeScript
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir --import-alias "@/*"
```

### Opciones seleccionadas:
- ✅ TypeScript
- ✅ ESLint
- ✅ Tailwind CSS
- ✅ App Router (recomendado)
- ❌ src/ directory (para simplicidad)
- ✅ Import alias (@/*)

## 2. Instalar Dependencias Principales

```bash
cd frontend

# Cliente HTTP y manejo de estado
npm install axios @tanstack/react-query zustand

# Formularios y validación
npm install react-hook-form zod @hookform/resolvers

# UI Components (shadcn/ui)
npm install class-variance-authority clsx tailwind-merge lucide-react

# Utilidades
npm install date-fns
```

## 3. Configurar shadcn/ui

```bash
# Inicializar shadcn/ui
npx shadcn-ui@latest init
```

### Configuración recomendada:
- Style: **Default**
- Base color: **Slate**
- CSS variables: **Yes**

### Instalar componentes básicos:
```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add form
npx shadcn-ui@latest add avatar
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add skeleton
```

## 4. Estructura de Carpetas

Crear la siguiente estructura en el directorio `frontend/`:

```
frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       └── page.tsx
│   ├── (dashboard)/
│   │   ├── books/
│   │   │   ├── page.tsx
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   ├── search/
│   │   │   └── page.tsx
│   │   ├── loans/
│   │   │   └── page.tsx
│   │   ├── groups/
│   │   │   └── page.tsx
│   │   └── profile/
│   │       └── page.tsx
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── ui/           # shadcn components
│   ├── auth/
│   ├── books/
│   ├── layout/
│   └── shared/
├── lib/
│   ├── api/
│   │   ├── client.ts
│   │   ├── auth.ts
│   │   ├── books.ts
│   │   ├── search.ts
│   │   └── loans.ts
│   ├── hooks/
│   ├── store/
│   │   └── auth-store.ts
│   ├── types/
│   │   └── api.ts
│   └── utils.ts
├── public/
├── .env.local
├── next.config.js
├── tailwind.config.ts
└── tsconfig.json
```

## 5. Configurar Variables de Entorno

Crear archivo `.env.local`:

```env
# API Backend URL
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

# App Configuration
NEXT_PUBLIC_APP_NAME=Book Sharing App
NEXT_PUBLIC_APP_VERSION=1.0.0
```

## 6. Configurar Cliente API Base

Crear `lib/api/client.ts`:

```typescript
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para añadir token de autenticación
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

## 7. Configurar React Query Provider

Crear `lib/providers/query-provider.tsx`:

```typescript
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode, useState } from 'react';

export function QueryProvider({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minuto
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
```

## 8. Configurar Store de Autenticación (Zustand)

Crear `lib/store/auth-store.ts`:

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      setAuth: (user, token) => {
        localStorage.setItem('access_token', token);
        set({ user, token, isAuthenticated: true });
      },
      logout: () => {
        localStorage.removeItem('access_token');
        set({ user: null, token: null, isAuthenticated: false });
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);
```

## 9. Actualizar Layout Principal

Modificar `app/layout.tsx`:

```typescript
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { QueryProvider } from '@/lib/providers/query-provider';
import { Toaster } from '@/components/ui/toaster';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Book Sharing App',
  description: 'Share books with friends and build a reading community',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <QueryProvider>
          {children}
          <Toaster />
        </QueryProvider>
      </body>
    </html>
  );
}
```

## 10. Crear Tipos TypeScript para la API

Crear `lib/types/api.ts`:

```typescript
// User Types
export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Book Types
export interface Book {
  id: string;
  title: string;
  author: string;
  description?: string;
  isbn?: string;
  genre?: string;
  book_type: 'physical' | 'digital';
  language?: string;
  status: 'available' | 'borrowed' | 'reserved';
  condition?: 'new' | 'like_new' | 'good' | 'fair' | 'poor';
  owner_id: string;
  created_at: string;
  updated_at: string;
}

// Auth Types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

// Search Types
export interface SearchParams {
  q?: string;
  page?: number;
  per_page?: number;
  genre?: string;
  book_type?: string;
  language?: string;
  available_only?: boolean;
  condition?: string;
  min_rating?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Loan Types
export interface Loan {
  id: string;
  book_id: string;
  borrower_id: string;
  lender_id: string;
  status: 'pending' | 'active' | 'returned' | 'cancelled';
  start_date?: string;
  due_date?: string;
  return_date?: string;
  created_at: string;
}

// Group Types
export interface Group {
  id: string;
  name: string;
  description?: string;
  is_public: boolean;
  member_count: number;
  created_at: string;
}
```

## 11. Verificar la Configuración

Ejecutar el servidor de desarrollo:

```bash
npm run dev
```

Abrir http://localhost:3000 en el navegador para verificar que todo funciona correctamente.

## 12. Crear Página de Inicio Temporal

Modificar `app/page.tsx`:

```typescript
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center space-y-6">
        <h1 className="text-4xl font-bold">📚 Book Sharing App</h1>
        <p className="text-xl text-muted-foreground">
          Share books with friends and build a reading community
        </p>
        <div className="flex gap-4 justify-center">
          <Button asChild>
            <Link href="/login">Login</Link>
          </Button>
          <Button asChild variant="outline">
            <Link href="/register">Register</Link>
          </Button>
        </div>
      </div>
    </main>
  );
}
```

## Resumen del Paso 1

✅ **Completado:**
- Proyecto Next.js con TypeScript configurado
- Tailwind CSS y shadcn/ui instalados
- Cliente API con Axios configurado
- React Query para manejo de datos
- Zustand para estado global de autenticación
- Estructura de carpetas organizada
- Tipos TypeScript para la API
- Variables de entorno configuradas

## Próximos Pasos

En el **Paso 2**, implementaremos:
- Formularios de login y registro
- Integración con endpoints de autenticación del backend
- Protección de rutas privadas
- Manejo de sesiones y tokens JWT

## Comandos Útiles

```bash
# Desarrollo
npm run dev

# Build para producción
npm run build

# Iniciar en producción
npm start

# Linting
npm run lint

# Añadir componentes de shadcn/ui
npx shadcn-ui@latest add [component-name]
```

## Notas Importantes

1. **CORS**: El backend ya tiene CORS configurado, pero asegúrate de que `http://localhost:3000` esté en la lista de orígenes permitidos.

2. **Tokens JWT**: Los tokens se guardan en `localStorage` y se añaden automáticamente a las peticiones mediante interceptores de Axios.

3. **Rutas Protegidas**: En el siguiente paso implementaremos middleware para proteger rutas que requieren autenticación.

4. **Estilos**: Tailwind CSS está configurado con las variables de color de shadcn/ui para mantener consistencia visual.
