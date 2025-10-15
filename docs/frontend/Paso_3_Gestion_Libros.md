# Paso 3: Gestión de Libros (CRUD Completo)

## Objetivo
Implementar el sistema completo de gestión de libros: crear, leer, actualizar, eliminar y subir portadas.

## ✅ Lo que se ha Implementado

### 1. API Client de Libros (`lib/api/books.ts`)

Cliente completo para interactuar con los endpoints de libros del backend:

```typescript
- getBooks(filters): Lista todos los libros con filtros
- getMyBooks(page, per_page): Lista mis libros con paginación
- getBook(id): Obtiene un libro específico
- createBook(data): Crea un nuevo libro
- updateBook(id, data): Actualiza un libro existente
- deleteBook(id): Elimina un libro
- uploadCover(bookId, file): Sube imagen de portada
- getCoverUrl(coverImage): Genera URL de la portada
```

**Características**:
- Soporte completo para filtros (género, tipo, idioma, estado)
- Paginación integrada
- Manejo de FormData para subida de archivos
- URLs de imágenes con fallback

### 2. Custom Hooks para Libros (`lib/hooks/use-books.ts`)

Hooks personalizados que encapsulan toda la lógica de libros:

```typescript
// Listar libros
const { books, pagination, isLoading } = useBooks(filters);
const { books, pagination, isLoading } = useMyBooks(page, per_page);

// Libro individual
const { book, isLoading, error } = useBook(id);

// Mutaciones
const createBook = useCreateBook();
const updateBook = useUpdateBook();
const deleteBook = useDeleteBook();
const uploadCover = useUploadCover();
```

**Características**:
- Integración con React Query para cache automático
- Invalidación de cache después de mutaciones
- Notificaciones toast automáticas
- Redirección después de crear/eliminar
- Manejo de errores con mensajes específicos

### 3. Componentes UI Adicionales

#### Textarea (`components/ui/textarea.tsx`)
- Área de texto para descripciones
- Estilo consistente con el tema
- Focus con anillo dorado

#### Select (`components/ui/select.tsx`)
- Dropdown basado en Radix UI
- Opciones para género, tipo, condición, estado
- Iconos de check para selección
- Animaciones suaves

#### Badge (`components/ui/badge.tsx`)
- Insignias para estado de libros
- Variantes: available (verde), borrowed (naranja), reserved (morado)
- También para género y tipo de libro

### 4. Páginas Implementadas

#### Lista de Libros (`app/(dashboard)/books/page.tsx`)

**Características**:
- Grid responsivo de libros (1-4 columnas según pantalla)
- Cards con imagen de portada
- Badges de estado y tipo
- Botones de acción: View, Edit
- Paginación completa
- Estado vacío con mensaje motivador
- Header con navegación
- Contador de libros totales

**Diseño**:
- Grid adaptativo
- Hover effects en cards
- Imágenes con fallback
- Skeleton loading

#### Añadir Libro (`app/(dashboard)/books/new/page.tsx`)

**Características**:
- Formulario completo con todos los campos
- Validación de campos requeridos
- Select para tipo de libro y condición
- Condición solo visible para libros físicos
- Estados de carga durante creación
- Cancelación con confirmación
- Redirección automática después de crear

**Campos**:
- **Requeridos**: Title, Author, Book Type
- **Opcionales**: Description, ISBN, Genre, Language, Condition

#### Detalles de Libro (`app/(dashboard)/books/[id]/page.tsx`)

**Características**:
- Layout de 2 columnas (portada + detalles)
- Imagen de portada grande
- Subida de nueva portada (solo propietario)
- Información completa del libro
- Badges de estado
- Iconos temáticos para cada campo
- Botones de edición y eliminación (solo propietario)
- Confirmación antes de eliminar
- Formato de fechas amigable

**Secciones**:
- Portada con opción de actualizar
- Título y autor con badge de estado
- Descripción completa
- Información detallada (género, tipo, idioma, condición, ISBN, fecha, propietario)

#### Editar Libro (`app/(dashboard)/books/[id]/edit/page.tsx`)

**Características**:
- Formulario prellenado con datos actuales
- Mismos campos que crear libro
- Campo adicional de estado (available, borrowed, reserved)
- Validación de propiedad (solo el dueño puede editar)
- Estados de carga durante actualización
- Cancelación que vuelve a detalles
- Actualización automática del cache

### 5. Componentes Compartidos

#### BookPlaceholder (`components/shared/book-placeholder.tsx`)
- Placeholder SVG para libros sin portada
- Icono de libro con gradiente leather
- Integrado automáticamente en Image onError

## 🎨 Tema Visual Aplicado

### Colores para Estados
- **Available** (Verde bosque): Libro disponible
- **Borrowed** (Naranja otoño): Libro prestado
- **Reserved** (Morado): Libro reservado

### Iconos Temáticos
- **Book**: Libros, biblioteca
- **Tag**: Género, ISBN
- **Package**: Tipo de libro
- **Globe**: Idioma
- **Calendar**: Fechas
- **User**: Propietario
- **Edit**: Editar
- **Trash**: Eliminar
- **Eye**: Ver detalles
- **Upload**: Subir imagen

## 🔄 Flujo de Gestión de Libros

### Crear Libro
1. Usuario va a `/books/new`
2. Completa formulario
3. Click en "Add Book"
4. POST a `/books/`
5. Toast de éxito
6. Redirección a `/books`
7. Cache invalidado automáticamente

### Ver Libros
1. Usuario va a `/books`
2. GET a `/users/me/books`
3. Muestra grid de libros
4. Paginación si hay más de 12 libros

### Ver Detalles
1. Click en "View" en un libro
2. Navega a `/books/{id}`
3. GET a `/books/{id}`
4. Muestra toda la información

### Editar Libro
1. En detalles, click en "Edit Book"
2. Navega a `/books/{id}/edit`
3. Formulario prellenado
4. Modifica campos
5. Click en "Save Changes"
6. PUT a `/books/{id}`
7. Toast de éxito
8. Cache invalidado
9. Vuelve a detalles

### Subir Portada
1. En detalles, selecciona archivo
2. Click en "Upload Cover"
3. POST a `/books/{id}/cover` con FormData
4. Toast de éxito
5. Imagen actualizada automáticamente

### Eliminar Libro
1. En detalles, click en "Delete"
2. Aparece confirmación
3. Click en "Yes, Delete"
4. DELETE a `/books/{id}`
5. Toast de confirmación
6. Redirección a `/books`
7. Cache invalidado

## 📁 Estructura de Archivos Creados

```
frontend/
├── app/
│   └── (dashboard)/
│       └── books/
│           ├── page.tsx              ✅ Lista de libros
│           ├── new/
│           │   └── page.tsx          ✅ Añadir libro
│           └── [id]/
│               ├── page.tsx          ✅ Detalles del libro
│               └── edit/
│                   └── page.tsx      ✅ Editar libro
├── components/
│   ├── ui/
│   │   ├── textarea.tsx              ✅ Componente Textarea
│   │   ├── select.tsx                ✅ Componente Select
│   │   └── badge.tsx                 ✅ Componente Badge
│   └── shared/
│       └── book-placeholder.tsx      ✅ Placeholder de libro
├── lib/
│   ├── api/
│   │   └── books.ts                  ✅ Cliente API libros
│   └── hooks/
│       └── use-books.ts              ✅ Hooks de libros
└── public/
    └── placeholder-book.jpg          ✅ Imagen placeholder
```

## 🧪 Cómo Probar

### 1. Verificar que el Frontend esté Corriendo
```powershell
# Debería estar en http://localhost:3000
# Si no, ejecuta:
cd frontend
npm run dev
```

### 2. Iniciar Sesión
1. Ve a http://localhost:3000/login
2. Inicia sesión con tu usuario

### 3. Ir a Mis Libros
1. En dashboard, click en "My Books"
2. O navega directamente a http://localhost:3000/books

### 4. Añadir un Libro
1. Click en "Add Book"
2. Completa el formulario:
   - **Title**: "El Quijote"
   - **Author**: "Miguel de Cervantes"
   - **Description**: "Las aventuras de Don Quijote de la Mancha"
   - **Genre**: "Clásico"
   - **Book Type**: Physical
   - **Language**: "Spanish"
   - **Condition**: Good
3. Click en "Add Book"
4. Deberías ver un toast y ser redirigido a la lista

### 5. Ver Detalles
1. Click en "View" en el libro que acabas de crear
2. Verás toda la información
3. Intenta subir una portada:
   - Click en "Choose File"
   - Selecciona una imagen
   - Click en "Upload Cover"

### 6. Editar Libro
1. En detalles, click en "Edit Book"
2. Modifica algún campo (ej: añade ISBN)
3. Click en "Save Changes"
4. Verás el cambio reflejado

### 7. Eliminar Libro
1. En detalles, click en "Delete"
2. Confirma la eliminación
3. Serás redirigido a la lista

## 🐛 Solución de Problemas

### Error: "Cannot find module @radix-ui/react-select"
**Solución**:
```powershell
cd frontend
npm install @radix-ui/react-select
```

### Error: "Failed to fetch books"
**Causa**: Backend no está corriendo o endpoint incorrecto

**Solución**: Verifica que el backend esté en http://127.0.0.1:8000
```powershell
curl http://127.0.0.1:8000/health
```

### Imágenes no se muestran
**Causa**: CORS o ruta incorrecta

**Solución**: Verifica `next.config.mjs`:
```javascript
images: {
  remotePatterns: [
    {
      protocol: 'http',
      hostname: '127.0.0.1',
      port: '8000',
      pathname: '/uploads/**',
    },
  ],
}
```

### Error al subir imagen
**Causa**: Tamaño de archivo o tipo no permitido

**Solución**: Verifica que:
- La imagen sea JPG, PNG o similar
- No exceda el tamaño máximo del backend

### Paginación no funciona
**Causa**: Cache de React Query

**Solución**: La paginación debería funcionar automáticamente. Si no, limpia el cache:
```typescript
queryClient.invalidateQueries({ queryKey: ['myBooks'] });
```

## 📊 Estado de Implementación

### ✅ Completado
- [x] Cliente API de libros
- [x] Hooks personalizados (useBooks, useMyBooks, useBook, etc.)
- [x] Componentes UI (Textarea, Select, Badge)
- [x] Lista de libros con paginación
- [x] Añadir nuevo libro
- [x] Ver detalles de libro
- [x] Editar libro
- [x] Eliminar libro con confirmación
- [x] Subir portada de libro
- [x] Placeholder para libros sin imagen
- [x] Filtrado por estado
- [x] Badges de estado
- [x] Protección de rutas (solo propietario puede editar/eliminar)

### 🚧 Mejoras Futuras (Opcional)
- [ ] Búsqueda de libros en la lista
- [ ] Filtros avanzados (género, tipo, condición)
- [ ] Ordenamiento (por título, fecha, autor)
- [ ] Vista de lista vs grid
- [ ] Exportar lista de libros
- [ ] Compartir libro en redes sociales
- [ ] Valoraciones y reseñas
- [ ] Historial de préstamos

## 🎯 Próximo Paso: Búsqueda y Exploración

En el **Paso 4** implementaremos:
- Página de búsqueda global
- Filtros avanzados (género, idioma, tipo, condición)
- Ordenamiento (título, autor, fecha, rating)
- Búsqueda por texto
- Ver libros de otros usuarios
- Solicitar préstamo de libros

## 💡 Notas Importantes

### Paginación
- Por defecto muestra 12 libros por página
- Botones Previous/Next
- Números de página clickeables
- Se deshabilitan botones en primera/última página

### Imágenes
- Se usa Next.js Image para optimización automática
- Fallback a placeholder si falla la carga
- Lazy loading automático
- Responsive images

### Cache
- React Query cachea durante 1 minuto
- Se invalida automáticamente después de mutaciones
- Optimistic updates en algunas operaciones

### Validación
- Client-side: Campos requeridos en formulario
- Server-side: Backend valida con Pydantic
- Mensajes de error específicos

### Permisos
- Solo el propietario puede editar/eliminar
- Verificación en frontend y backend
- Redirección si no es propietario

## 🎨 Personalización

### Cambiar Número de Libros por Página
En `app/(dashboard)/books/page.tsx`:
```typescript
const { books, pagination } = useMyBooks(page, 20); // Cambia 12 a 20
```

### Cambiar Colores de Estado
En `components/ui/badge.tsx`:
```typescript
available: "border-transparent bg-TU_COLOR text-white",
```

### Añadir Más Campos
1. Añade el campo en el formulario
2. Actualiza el tipo `CreateBookData` en `lib/api/books.ts`
3. Envía el campo en `handleSubmit`

## 📚 Recursos

- [React Query Mutations](https://tanstack.com/query/latest/docs/react/guides/mutations)
- [Next.js Image](https://nextjs.org/docs/api-reference/next/image)
- [Radix UI Select](https://www.radix-ui.com/docs/primitives/components/select)
- [FormData MDN](https://developer.mozilla.org/en-US/docs/Web/API/FormData)

---

**¡Gestión de libros completada! 📚✨**

Ahora puedes crear, ver, editar y eliminar libros con un hermoso diseño de cuento mágico. Los usuarios pueden gestionar completamente su biblioteca personal.
