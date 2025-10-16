# Paso 4: Búsqueda y Exploración de Libros

## Objetivo
Implementar un sistema completo de búsqueda y exploración que permita a los usuarios descubrir libros de toda la comunidad con filtros avanzados.

## ✅ Lo que se ha Implementado

### 1. API Client de Búsqueda (`lib/api/search.ts`)

Cliente para interactuar con los endpoints de búsqueda del backend:

```typescript
- searchBooks(params): Búsqueda con filtros avanzados
- getSuggestions(query): Sugerencias de búsqueda
- getGenres(): Lista de géneros disponibles
- getLanguages(): Lista de idiomas
- getConditions(): Lista de condiciones de libros
```

**Características**:
- Construcción dinámica de query params
- Manejo de parámetros opcionales
- Fallback para metadata si falla el backend
- Debounce en sugerencias

### 2. Custom Hooks de Búsqueda (`lib/hooks/use-search.ts`)

Hooks especializados para búsqueda:

```typescript
// Búsqueda principal
const { books, pagination, isLoading } = useSearch(params);

// Sugerencias con debounce
const { suggestions, isLoading } = useSearchSuggestions(query);

// Metadata
const { genres } = useGenres();
const { languages } = useLanguages();
const { conditions } = useConditions();
```

**Características**:
- Integración con React Query
- Cache infinito para metadata
- Debounce automático (300ms) en sugerencias
- Invalidación inteligente de cache

### 3. Página de Búsqueda (`app/(dashboard)/search/page.tsx`)

Página completa de búsqueda y exploración con:

#### Barra de Búsqueda
- Input con icono de búsqueda
- Búsqueda al presionar Enter
- Botón de búsqueda
- Botón para mostrar/ocultar filtros

#### Panel de Filtros Avanzados
- **Género**: Dropdown con todos los géneros disponibles
- **Tipo de Libro**: Physical o Digital
- **Idioma**: Lista de idiomas del sistema
- **Condición**: New, Like New, Good, Fair, Poor
- **Ordenar por**: Date Added, Title, Author
- **Orden**: Ascending o Descending
- **Checkbox**: "Show only available books"
- **Botón**: Clear All Filters

#### Grid de Resultados
- Cards de libros con imagen
- Badges de estado (available, borrowed, reserved)
- Badges de género y tipo
- Información del propietario
- Botón "View Details"
- Hover effects

#### Paginación
- Botones Previous/Next
- Números de página (hasta 5 visibles)
- Indicador "..." para más páginas
- Deshabilitación en primera/última página

#### Estados
- **Loading**: Spinner con mensaje
- **Empty**: Mensaje "No books found" con sugerencia
- **Results**: Grid con libros encontrados
- **Error**: Manejo automático con toast

## 🎨 Características de Diseño

### Colores y Tema
- Mantiene el tema de cuento mágico
- Cards con hover effects
- Animaciones suaves (fade-in-up)
- Badges de colores según estado

### Layout
- Header sticky con navegación
- Barra de búsqueda prominente
- Panel de filtros colapsable
- Grid responsivo (1-4 columnas)

### Iconos
- **Search**: Búsqueda
- **Filter**: Filtros
- **SlidersHorizontal**: Filtros avanzados
- **X**: Limpiar filtros
- **Eye**: Ver detalles
- **Loader2**: Cargando

## 🔍 Funcionalidades de Búsqueda

### Búsqueda por Texto
- Busca en: título, autor, ISBN
- Case-insensitive
- Búsqueda parcial (LIKE)
- Resultados instantáneos

### Filtros Disponibles
1. **Género**: Fantasy, Science Fiction, Mystery, etc.
2. **Tipo**: Physical, Digital
3. **Idioma**: English, Spanish, French, etc.
4. **Condición**: New, Like New, Good, Fair, Poor
5. **Disponibilidad**: Solo libros disponibles
6. **Ordenamiento**: Por fecha, título o autor
7. **Dirección**: Ascendente o descendente

### Combinación de Filtros
- Todos los filtros son combinables
- Se aplican con lógica AND
- Actualización automática al cambiar filtro
- Reset a página 1 al cambiar filtros

## 🔄 Flujo de Búsqueda

### Búsqueda Simple
1. Usuario escribe en la barra de búsqueda
2. Presiona Enter o click en "Search"
3. GET a `/search/books?q=query`
4. Muestra resultados en grid

### Búsqueda con Filtros
1. Usuario click en "Filters"
2. Panel se expande con animación
3. Selecciona filtros deseados
4. Cada cambio actualiza resultados automáticamente
5. GET a `/search/books?q=query&genre=X&book_type=Y...`

### Ver Detalles
1. Usuario click en "View Details"
2. Navega a `/books/{id}`
3. Ve información completa del libro
4. Puede ver propietario
5. (Futuro) Puede solicitar préstamo

### Limpiar Filtros
1. Usuario click en "Clear All"
2. Todos los filtros se resetean
3. Búsqueda se limpia
4. Muestra todos los libros

## 📁 Estructura de Archivos Creados

```
frontend/
├── app/
│   └── (dashboard)/
│       └── search/
│           └── page.tsx              ✅ Página de búsqueda
├── lib/
│   ├── api/
│   │   └── search.ts                 ✅ Cliente API búsqueda
│   └── hooks/
│       └── use-search.ts             ✅ Hooks de búsqueda
```

## 🧪 Cómo Probar

### 1. Ir a la Página de Búsqueda
```
http://localhost:3000/search
```

### 2. Búsqueda Simple
1. Escribe "Harry" en la barra
2. Presiona Enter
3. Verás todos los libros con "Harry" en título o autor

### 3. Usar Filtros
1. Click en "Filters"
2. Selecciona:
   - **Genre**: Fantasy
   - **Book Type**: Physical
   - **Available Only**: ✓
3. Los resultados se actualizan automáticamente

### 4. Ordenar Resultados
1. En filtros, selecciona:
   - **Sort By**: Title
   - **Order**: Ascending
2. Los libros se ordenan alfabéticamente

### 5. Paginación
1. Si hay más de 12 libros
2. Usa los botones Previous/Next
3. O click en número de página

### 6. Limpiar Todo
1. Click en "Clear All"
2. Todos los filtros se resetean
3. Vuelve a mostrar todos los libros

## 🐛 Solución de Problemas

### No se muestran géneros/idiomas
**Causa**: Backend no tiene endpoint de metadata

**Solución**: El frontend tiene fallbacks hardcodeados:
```typescript
// En search.ts
return [
  { value: 'new', label: 'New' },
  // ...
];
```

### Búsqueda muy lenta
**Causa**: Muchos resultados o backend lento

**Solución**: 
- Reducir `per_page` en filtros
- Añadir más filtros para reducir resultados
- Backend tiene rate limiting (30 req/min)

### Filtros no se aplican
**Causa**: Cache de React Query

**Solución**: Los filtros están en la queryKey, se actualiza automáticamente

### Imágenes no cargan
**Causa**: CORS o URL incorrecta

**Solución**: Verifica `next.config.mjs` y que el backend esté corriendo

## 📊 Estado de Implementación

### ✅ Completado
- [x] Cliente API de búsqueda
- [x] Hooks personalizados
- [x] Página de búsqueda completa
- [x] Barra de búsqueda
- [x] Filtros avanzados
- [x] Panel colapsable de filtros
- [x] Grid de resultados
- [x] Paginación
- [x] Estados de loading/empty
- [x] Ordenamiento
- [x] Filtro de disponibilidad
- [x] Mostrar propietario del libro
- [x] Navegación integrada

### 🚧 Mejoras Futuras (Opcional)
- [ ] Autocompletado en búsqueda
- [ ] Búsqueda por voz
- [ ] Guardar búsquedas favoritas
- [ ] Historial de búsquedas
- [ ] Búsqueda avanzada por rango de fechas
- [ ] Filtro por rating/valoraciones
- [ ] Vista de mapa (libros cercanos)
- [ ] Exportar resultados

## 🎯 Próximo Paso: Sistema de Préstamos

En el **Paso 5** implementaremos:
- Solicitar préstamo de un libro
- Aprobar/rechazar solicitudes
- Ver mis préstamos (como prestador)
- Ver mis préstamos (como prestatario)
- Devolver libro
- Historial de préstamos
- Notificaciones de préstamos

## 💡 Notas Importantes

### Parámetros de Búsqueda

Todos los parámetros son opcionales:

```typescript
{
  q: string,              // Texto de búsqueda
  page: number,           // Página actual (default: 1)
  per_page: number,       // Items por página (default: 12)
  genre: string,          // Filtro por género
  book_type: string,      // 'physical' o 'digital'
  language: string,       // Filtro por idioma
  available_only: boolean,// Solo disponibles
  condition: string,      // Condición del libro
  sort_by: string,        // Campo para ordenar
  sort_order: string,     // 'asc' o 'desc'
}
```

### Performance

- **Cache**: React Query cachea resultados por 1 minuto
- **Debounce**: Sugerencias con 300ms de delay
- **Lazy Loading**: Imágenes con Next.js Image
- **Paginación**: Máximo 12 libros por página

### Seguridad

- Rate limiting en backend (30 req/min para búsqueda)
- Sanitización de inputs
- Validación de parámetros
- CORS configurado

### Accesibilidad

- Labels en todos los inputs
- Keyboard navigation (Enter para buscar)
- Estados de loading claros
- Mensajes de error descriptivos

## 🎨 Personalización

### Cambiar Número de Resultados por Página

En `search/page.tsx`:
```typescript
const [filters, setFilters] = useState({
  // ...
  per_page: 20, // Cambia de 12 a 20
});
```

### Añadir Más Filtros

1. Añade el campo en `SearchParams` en `search.ts`
2. Añade el filtro en el panel de filtros
3. Actualiza el estado `filters`

### Cambiar Ordenamiento por Defecto

```typescript
const [filters, setFilters] = useState({
  // ...
  sort_by: 'title',      // En vez de 'created_at'
  sort_order: 'asc',     // En vez de 'desc'
});
```

## 📚 Recursos

- [React Query Docs](https://tanstack.com/query/latest)
- [URL Search Params](https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams)
- [Debouncing in React](https://www.freecodecamp.org/news/debouncing-explained/)

## 🌟 Características Destacadas

### 1. Búsqueda Inteligente
- Busca en múltiples campos simultáneamente
- Case-insensitive
- Búsqueda parcial (no necesita coincidencia exacta)

### 2. Filtros Potentes
- Combinación de múltiples filtros
- Actualización en tiempo real
- Persistencia durante la sesión
- Fácil de limpiar

### 3. UX Excepcional
- Feedback visual inmediato
- Estados de carga claros
- Mensajes de error amigables
- Navegación intuitiva
- Panel de filtros colapsable

### 4. Performance Optimizada
- Cache inteligente
- Debounce en sugerencias
- Lazy loading de imágenes
- Paginación eficiente

---

**¡Búsqueda y Exploración completada! 🔍✨**

Ahora los usuarios pueden descubrir libros de toda la comunidad con filtros avanzados, ordenamiento personalizado y una experiencia de búsqueda fluida y mágica.

**Próximo paso**: Implementar el sistema de préstamos para que los usuarios puedan solicitar y gestionar préstamos de libros.
