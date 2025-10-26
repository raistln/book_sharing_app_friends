# Cambios en el Sistema de Añadir Libros

## Resumen
Se ha simplificado completamente el proceso de añadir libros, permitiendo tres métodos de entrada:
1. **Búsqueda por Título/Autor**: Búsqueda manual en OpenLibrary y Google Books
2. **Búsqueda por ISBN**: Búsqueda automática por código ISBN
3. **Escaneo de Imagen**: OCR de portada o lectura de código de barras

## Cambios en el Backend

### 1. Modelo de Base de Datos (`app/models/book.py`)
- ✅ **Eliminado**: `BookType` enum y campo `book_type`
- ✅ **Agregado**: `BookCondition` enum con valores: new, like_new, good, fair, poor
- ✅ **Modificado**: Campo `author` ahora es nullable (opcional)
- ✅ **Agregados nuevos campos**:
  - `publisher` (String 200)
  - `published_date` (String 50)
  - `page_count` (String 10)
  - `language` (String 10)
  - `condition` (Enum BookCondition, default='good')

### 2. Schemas (`app/schemas/book.py`)
- ✅ Actualizado `BookBase` para incluir nuevos campos
- ✅ Actualizado `BookCreate` y `BookUpdate` con los nuevos campos
- ✅ `author` ahora es opcional
- ✅ `condition` tiene valor por defecto 'good'

### 3. API Endpoints (`app/api/books.py`)
- ✅ Actualizado endpoint de creación para manejar nuevos campos
- ✅ Eliminada lógica de `book_type`
- ✅ Agregada lógica para `condition` con valor por defecto

### 4. Migración de Base de Datos
- 📄 Creada migración: `zz_update_books_remove_book_type_add_fields.py`
- ⚠️ **IMPORTANTE**: Ejecutar antes de usar:
  ```bash
  poetry run alembic upgrade head
  ```

## Cambios en el Frontend

### 1. Nuevo Hook de Búsqueda (`lib/hooks/use-book-search.ts`)
- ✅ `useSearchBooks()`: Hook para buscar libros por título o ISBN
- ✅ `useScanBook()`: Hook para escanear imágenes (OCR + barcode)
- ✅ `useAutoSearch()`: Hook para búsqueda automática mientras se escribe

### 2. Componentes Nuevos

#### `components/books/AddBookForm.tsx`
- Componente principal con 3 tabs:
  - **Título/Autor**: Búsqueda manual
  - **ISBN**: Búsqueda por código
  - **Escanear**: Subir foto de portada o código de barras
- Maneja el flujo completo de búsqueda

#### `components/books/BookSearchResults.tsx`
- Muestra resultados de búsqueda de las APIs
- Permite seleccionar el libro correcto
- Muestra información: portada, título, autor, ISBN, fecha, idioma, páginas

#### `components/books/BookConfirmation.tsx`
- Pantalla de confirmación y edición de datos
- Permite al usuario revisar y modificar todos los campos
- Campos editables:
  - Título (obligatorio)
  - Autor (opcional)
  - ISBN
  - Editorial
  - Fecha de publicación
  - Número de páginas
  - Idioma
  - Estado del libro (condition)
  - Descripción

### 3. Componente UI Agregado
- ✅ `components/ui/tabs.tsx`: Componente de tabs de Radix UI

### 4. Página Actualizada
- ✅ `app/(dashboard)/books/new/page.tsx`: Simplificada para usar `AddBookForm`

## Flujo de Usuario

1. **Usuario accede a "Añadir Libro"**
2. **Elige método de entrada**:
   - Opción A: Escribe título (y opcionalmente autor) → Click "Buscar"
   - Opción B: Escribe ISBN → Click "Buscar por ISBN"
   - Opción C: Sube foto de portada o código de barras
3. **Sistema busca en APIs** (OpenLibrary → Google Books como fallback)
4. **Muestra resultados** con portadas, información completa
5. **Usuario selecciona el libro correcto**
6. **Pantalla de confirmación** muestra todos los datos
7. **Usuario revisa/edita** cualquier campo si es necesario
8. **Click "Confirmar y añadir"**
9. **Libro guardado** en la biblioteca del usuario

## Campos Guardados Automáticamente

Cuando se encuentra un libro en las APIs, se guardan:
- ✅ Título
- ✅ Autor(es)
- ✅ ISBN
- ✅ Portada (cover_url)
- ✅ Descripción
- ✅ Editorial
- ✅ Fecha de publicación
- ✅ Número de páginas
- ✅ Idioma
- ✅ Género (si está disponible)

## Campos Configurables por el Usuario

- **Condition** (Estado del libro): Siempre editable, default 'good'
- Todos los campos son editables antes de confirmar

## Dependencias Agregadas

```bash
npm install @radix-ui/react-tabs
```

## Problemas Resueltos

### ✅ Error de serialización en `/users/me/books`
- **Problema**: El endpoint devolvía objetos SQLAlchemy directamente
- **Solución**: Convertir a schemas Pydantic antes de devolver

### ✅ Datos incompletos de APIs
- **Problema**: Caché antiguo sin los nuevos campos
- **Solución**: Versión v2 de claves de caché + extracción mejorada de campos

### ✅ OpenLibrary con datos limitados
- **Problema**: API de búsqueda no devuelve detalles completos
- **Solución**: Enriquecimiento automático con endpoint de ISBN cuando está disponible

## Estado Actual

✅ **Backend**: Corriendo en http://127.0.0.1:8000
✅ **Frontend**: Corriendo en http://localhost:3001  
✅ **Base de datos**: Migrada correctamente
✅ **Sistema**: Completamente funcional

## Notas Técnicas

- **Solo libros físicos**: Por ahora solo se permiten libros físicos (no digitales) para evitar problemas de copyright
- **OCR Backend**: Ya implementado con EasyOCR
- **Barcode Backend**: Ya implementado con pyzbar
- **APIs**: OpenLibrary como principal, Google Books como fallback
- **Caché**: Redis caché para búsquedas (ya implementado)

## Compatibilidad

- ✅ Todos los libros existentes seguirán funcionando
- ✅ La migración es reversible (downgrade disponible)
- ⚠️ Los libros antiguos con `book_type` perderán ese campo (se elimina)
- ✅ Los libros sin `author` ahora son válidos
