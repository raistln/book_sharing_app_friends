# 📱 Frontend Development Guide - Book Sharing App

## 🎯 Visión General

Esta guía te ayudará a crear una interfaz web moderna y funcional para tu aplicación de intercambio de libros, aprovechando completamente el backend FastAPI existente.

## 🛠️ Stack Tecnológico Recomendado

### Opción 1: Next.js (Recomendado para principiantes)
```
Frontend: Next.js 14 + TypeScript
UI Framework: Tailwind CSS + shadcn/ui
Estado: Zustand (simple) o Redux Toolkit
HTTP Client: Axios + React Query
PWA: next-pwa
Testing: Jest + React Testing Library
```

**Ventajas para tu caso:**
- Excelente documentación y comunidad
- TypeScript integrado (ayuda con APIs)
- SSR/SSG para SEO
- Fácil deployment
- Perfecto para portfolios profesionales

### Opción 2: Vite + React (Más control)
```
Frontend: Vite + React 18 + TypeScript
UI Framework: Tailwind CSS + Headless UI
Estado: Zustand
HTTP Client: Axios + TanStack Query
PWA: Vite PWA Plugin
Testing: Vitest + React Testing Library
```

## 🏗️ Estructura de Proyecto Recomendada

```
book-sharing-frontend/
├── public/
│   ├── icons/              # PWA icons
│   ├── manifest.json       # PWA manifest
│   └── sw.js              # Service worker
├── src/
│   ├── components/         # Componentes reutilizables
│   │   ├── ui/            # Componentes base (botones, inputs)
│   │   ├── forms/         # Formularios específicos
│   │   ├── layout/        # Layout components
│   │   └── features/      # Componentes por feature
│   ├── pages/             # Páginas de la aplicación
│   │   ├── auth/          # Login, registro
│   │   ├── books/         # CRUD de libros
│   │   ├── loans/         # Gestión de préstamos
│   │   ├── groups/        # Grupos de amigos
│   │   └── chat/          # Chat integrado
│   ├── hooks/             # Custom hooks
│   ├── services/          # API calls y lógica de negocio
│   ├── stores/            # Estado global (Zustand)
│   ├── types/             # TypeScript types
│   ├── utils/             # Utilidades
│   └── constants/         # Constantes
├── docs/                  # Documentación
├── tests/                 # Tests
└── package.json
```

## 🚀 Configuración Inicial Paso a Paso

### 1. Crear el Proyecto

```bash
# Opción Next.js
npx create-next-app@latest book-sharing-frontend --typescript --tailwind --eslint --app

# Opción Vite
npm create vite@latest book-sharing-frontend -- --template react-ts
cd book-sharing-frontend
npm install
```

### 2. Instalar Dependencias Esenciales

```bash
# HTTP Client y Estado
npm install axios @tanstack/react-query zustand

# UI Components
npm install @headlessui/react @heroicons/react
npm install lucide-react # Iconos modernos

# Formularios y Validación
npm install react-hook-form @hookform/resolvers zod

# PWA y Offline
npm install workbox-webpack-plugin # Next.js
# o
npm install vite-plugin-pwa # Vite

# Utilidades
npm install clsx tailwind-merge date-fns
npm install @types/node # Para TypeScript
```

### 3. Configuración de Tailwind CSS

```javascript
// tailwind.config.js
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        secondary: {
          50: '#f8fafc',
          500: '#64748b',
          600: '#475569',
        }
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

### 4. Configuración de Variables de Entorno

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=BookShare
NEXT_PUBLIC_ENABLE_PWA=true
```

## 🔌 Integración con Backend

### 1. Configuración de Axios

```typescript
// src/services/api.ts
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para manejo de errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/auth/login';
    }
    return Promise.reject(error);
  }
);
```

### 2. Tipos TypeScript para el Backend

```typescript
// src/types/api.ts
export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  bio?: string;
  avatar_url?: string;
  is_active: boolean;
  created_at: string;
}

export interface Book {
  id: string;
  title: string;
  author: string;
  isbn?: string;
  cover_url?: string;
  description?: string;
  genre: string;
  book_type: 'physical' | 'digital';
  status: 'available' | 'loaned' | 'unavailable';
  owner_id: string;
  current_borrower_id?: string;
  created_at: string;
}

export interface Loan {
  id: string;
  book_id: string;
  borrower_id: string;
  lender_id: string;
  status: 'requested' | 'approved' | 'active' | 'returned';
  requested_at: string;
  approved_at?: string;
  due_date?: string;
  returned_at?: string;
}

export interface Group {
  id: string;
  name: string;
  description?: string;
  admin_id: string;
  is_public: boolean;
  created_at: string;
}
```

### 3. Servicios de API

```typescript
// src/services/auth.ts
import { api } from './api';
import { User } from '../types/api';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name: string;
}

export const authService = {
  async login(credentials: LoginCredentials) {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return response.data;
  },

  async register(data: RegisterData) {
    const response = await api.post('/auth/register', data);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/auth/me');
    return response.data;
  },

  logout() {
    localStorage.removeItem('access_token');
  }
};
```

## 🎨 Diseño y UX/UI

### Paleta de Colores Sugerida
```css
:root {
  --primary: #2563eb;      /* Azul profesional */
  --secondary: #64748b;    /* Gris neutro */
  --accent: #10b981;       /* Verde para éxito */
  --warning: #f59e0b;      /* Amarillo para alertas */
  --error: #ef4444;        /* Rojo para errores */
  --background: #f8fafc;   /* Fondo claro */
  --surface: #ffffff;      /* Superficie de cards */
  --text-primary: #1e293b; /* Texto principal */
  --text-secondary: #64748b; /* Texto secundario */
}
```

### Componentes Base Recomendados

1. **Button Component**
```typescript
// src/components/ui/Button.tsx
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'outline' | 'ghost';
  size: 'sm' | 'md' | 'lg';
  loading?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}
```

2. **Card Component**
```typescript
// Para mostrar libros, préstamos, etc.
interface CardProps {
  title?: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
}
```

3. **Modal Component**
```typescript
// Para formularios y confirmaciones
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}
```

## 📱 Configuración PWA

### 1. Manifest.json
```json
{
  "name": "BookShare - Intercambio de Libros",
  "short_name": "BookShare",
  "description": "Comparte libros con tus amigos",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#2563eb",
  "icons": [
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

### 2. Service Worker Básico
```javascript
// public/sw.js
const CACHE_NAME = 'bookshare-v1';
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});
```

## 🔒 Manejo de Autenticación

### 1. Hook de Autenticación
```typescript
// src/hooks/useAuth.ts
import { create } from 'zustand';
import { User } from '../types/api';
import { authService } from '../services/auth';

interface AuthStore {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuth = create<AuthStore>((set, get) => ({
  user: null,
  isLoading: false,
  isAuthenticated: false,

  login: async (credentials) => {
    set({ isLoading: true });
    try {
      const { access_token } = await authService.login(credentials);
      localStorage.setItem('access_token', access_token);
      const user = await authService.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: () => {
    authService.logout();
    set({ user: null, isAuthenticated: false });
  },

  checkAuth: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      const user = await authService.getCurrentUser();
      set({ user, isAuthenticated: true });
    } catch (error) {
      localStorage.removeItem('access_token');
    }
  },
}));
```

## 📊 Estado Global con Zustand

```typescript
// src/stores/booksStore.ts
import { create } from 'zustand';
import { Book } from '../types/api';

interface BooksStore {
  books: Book[];
  loading: boolean;
  fetchBooks: () => Promise<void>;
  addBook: (book: Book) => void;
  updateBook: (id: string, book: Partial<Book>) => void;
  deleteBook: (id: string) => void;
}

export const useBooksStore = create<BooksStore>((set, get) => ({
  books: [],
  loading: false,

  fetchBooks: async () => {
    set({ loading: true });
    try {
      const response = await api.get('/books/');
      set({ books: response.data, loading: false });
    } catch (error) {
      set({ loading: false });
      throw error;
    }
  },

  addBook: (book) => {
    set((state) => ({ books: [...state.books, book] }));
  },

  updateBook: (id, updatedBook) => {
    set((state) => ({
      books: state.books.map((book) =>
        book.id === id ? { ...book, ...updatedBook } : book
      ),
    }));
  },

  deleteBook: (id) => {
    set((state) => ({
      books: state.books.filter((book) => book.id !== id),
    }));
  },
}));
```

## 🧪 Testing Strategy

### 1. Configuración de Testing
```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest jsdom
```

### 2. Ejemplo de Test
```typescript
// src/components/__tests__/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '../ui/Button';

describe('Button Component', () => {
  it('renders correctly', () => {
    render(<Button variant="primary">Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = vi.fn();
    render(<Button variant="primary" onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

## 🚀 Deployment y Producción

### 1. Build Optimizado
```json
// package.json scripts
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "vitest",
    "test:coverage": "vitest --coverage"
  }
}
```

### 2. Configuración de Vercel (Recomendado)
```json
// vercel.json
{
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "env": {
    "NEXT_PUBLIC_API_URL": "https://your-backend-url.com"
  }
}
```

## 📈 Performance y Optimización

### 1. Lazy Loading
```typescript
// Lazy loading de páginas
const BooksPage = lazy(() => import('../pages/books/BooksPage'));
const LoansPage = lazy(() => import('../pages/loans/LoansPage'));
```

### 2. Optimización de Imágenes
```typescript
// Next.js Image component
import Image from 'next/image';

<Image
  src={book.cover_url || '/default-book-cover.jpg'}
  alt={book.title}
  width={200}
  height={300}
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,..."
/>
```

### 3. Caché de Datos
```typescript
// React Query para caché inteligente
import { useQuery } from '@tanstack/react-query';

export const useBooks = () => {
  return useQuery({
    queryKey: ['books'],
    queryFn: () => api.get('/books/').then(res => res.data),
    staleTime: 5 * 60 * 1000, // 5 minutos
    cacheTime: 10 * 60 * 1000, // 10 minutos
  });
};
```

## 🔧 Herramientas de Desarrollo

### 1. VS Code Extensions Recomendadas
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- TypeScript Importer
- Auto Rename Tag
- Prettier - Code formatter
- ESLint

### 2. Configuración de Prettier
```json
// .prettierrc
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2
}
```

## 🎯 Próximos Pasos

1. **Configurar el proyecto** siguiendo esta guía
2. **Implementar autenticación** como primera funcionalidad
3. **Crear componentes base** (Button, Card, Modal)
4. **Desarrollar páginas principales** según el roadmap
5. **Implementar PWA** para funcionalidad offline
6. **Optimizar performance** y testing
7. **Preparar para móvil** (React Native o Capacitor)

## 📚 Recursos Adicionales

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [React Query](https://tanstack.com/query/latest)
- [Zustand](https://github.com/pmndrs/zustand)
- [React Hook Form](https://react-hook-form.com/)

---

Esta guía te proporcionará una base sólida para crear una interfaz moderna y funcional. ¡Comienza con el MVP y ve expandiendo gradualmente las funcionalidades!
