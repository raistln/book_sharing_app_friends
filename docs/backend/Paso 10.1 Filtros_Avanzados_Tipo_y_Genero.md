# Paso 10.1: Filtros Avanzados - Tipo y Género

## 📋 Resumen

Hemos añadido filtros avanzados para tipo de libro y género, eliminando el filtro redundante de autor. Ahora los usuarios pueden filtrar libros por tipo (novela, cómic, manga, etc.) y género (ciencia ficción, fantasía, histórica, etc.).

## 🎯 Nuevas Funcionalidades

### 1. Filtro por Tipo de Libro
- **Novela**: Ficción narrativa larga
- **Cómic**: Historietas con viñetas
- **Manga**: Cómic japonés
- **Novela Gráfica**: Cómic de formato libro
- **Cuento**: Historia corta
- **Poesía**: Obra poética
- **Ensayo**: Texto argumentativo
- **Biografía**: Vida de una persona
- **Autobiografía**: Vida del autor
- **Otro**: Categoría miscelánea

### 2. Filtro por Género
#### Ficción
- **Ficción General**: Obras de ficción diversas
- **Ciencia Ficción**: Futuro, tecnología, espacio
- **Fantasía**: Magia, mundos imaginarios
- **Misterio**: Enigmas, crímenes
- **Thriller**: Suspenso, tensión
- **Horror**: Terror, sobrenatural
- **Romance**: Historias de amor
- **Ficción Histórica**: Ambientada en el pasado
- **Ficción Literaria**: Obras de calidad artística
- **Aventura**: Acción, exploración
- **Western**: Oeste americano
- **Distópica**: Sociedades futuras negativas
- **Realismo Mágico**: Elementos fantásticos en realidad

#### No Ficción
- **No Ficción General**: Obras informativas
- **Biografía**: Vida de personas
- **Autobiografía**: Vida del autor
- **Historia**: Eventos pasados
- **Filosofía**: Pensamiento, ética
- **Psicología**: Mente humana
- **Ciencia**: Conocimiento científico
- **Tecnología**: Innovación técnica
- **Negocios**: Empresa, economía
- **Autoayuda**: Desarrollo personal
- **Viajes**: Lugares, culturas
- **Cocina**: Gastronomía
- **Salud**: Bienestar físico
- **Religión**: Espiritualidad
- **Política**: Gobierno, sociedad
- **Economía**: Dinero, mercados
- **Educación**: Enseñanza, aprendizaje

#### Otros
- **Infantil**: Para niños
- **Juvenil**: Para adolescentes
- **Referencia**: Consulta, diccionarios
- **Académico**: Investigación, estudios
- **Otro**: Categoría miscelánea

## 📁 Archivos Modificados

### Modelos
- `app/models/book.py` - Añadidos campos `book_type` y `genre`

### Schemas
- `app/schemas/book.py` - Añadidos campos a schemas de libro
- `app/schemas/group_book.py` - Actualizado `GroupBookFilter`

### Servicios
- `app/services/group_book_service.py` - Añadidos filtros por tipo y género

### API
- `app/api/group_books.py` - Añadidos parámetros de filtro

### Base de Datos
- `alembic/versions/c4bcd84b18af_add_book_type_and_genre_fields_to_book_.py` - Migración

### Tests
- `tests/test_group_books.py` - Tests para nuevos filtros

## 🌐 **Endpoints Actualizados**

### Filtros Disponibles
```http
GET /groups/{group_id}/books?book_type=novel&genre=science_fiction&search=dune
```

### Parámetros de Filtro
- **search**: Búsqueda por título o autor (mantenido)
- **owner_id**: Filtrar por propietario (mantenido)
- **status**: Filtrar por estado (mantenido)
- **is_available**: Filtrar por disponibilidad (mantenido)
- **book_type**: Filtrar por tipo de libro (NUEVO)
- **genre**: Filtrar por género (NUEVO)
- **isbn**: Filtrar por ISBN (mantenido)
- ~~**author**: Eliminado (redundante con search)~~

## 📖 **Uso de los Nuevos Filtros**

### Ejemplos de Filtrado

#### Por Tipo de Libro
```http
# Solo novelas
GET /groups/{group_id}/books?book_type=novel

# Solo cómics
GET /groups/{group_id}/books?book_type=comic

# Solo manga
GET /groups/{group_id}/books?book_type=manga
```

#### Por Género
```http
# Solo ciencia ficción
GET /groups/{group_id}/books?genre=science_fiction

# Solo fantasía
GET /groups/{group_id}/books?genre=fantasy

# Solo ficción histórica
GET /groups/{group_id}/books?genre=historical_fiction
```

#### Combinando Filtros
```http
# Novelas de ciencia ficción
GET /groups/{group_id}/books?book_type=novel&genre=science_fiction

# Cómics de fantasía disponibles
GET /groups/{group_id}/books?book_type=comic&genre=fantasy&is_available=true

# Búsqueda + tipo + género
GET /groups/{group_id}/books?search=dune&book_type=novel&genre=science_fiction
```

## 🔍 **Casos de Uso Comunes**

### Club de Lectura de Ciencia Ficción
```http
GET /groups/{group_id}/books?genre=science_fiction&is_available=true
```

### Biblioteca de Cómics
```http
GET /groups/{group_id}/books?book_type=comic
```

### Novelas Históricas
```http
GET /groups/{group_id}/books?book_type=novel&genre=historical_fiction
```

### Manga y Anime
```http
GET /groups/{group_id}/books?book_type=manga
```

### No Ficción Educativa
```http
GET /groups/{group_id}/books?genre=education&is_available=true
```

## 📊 **Estadísticas Mejoradas**

### Género Más Común
Las estadísticas del grupo ahora incluyen el género más popular:
```json
{
  "total_books": 25,
  "available_books": 18,
  "loaned_books": 5,
  "reserved_books": 2,
  "total_owners": 8,
  "most_common_author": "Isaac Asimov",
  "most_common_genre": "science_fiction"
}
```

## 🧪 **Tests Actualizados**

### Nuevos Tests
- ✅ Filtro por tipo de libro
- ✅ Filtro por género
- ✅ Combinación de filtros
- ✅ Creación de libros con tipo y género
- ✅ Validación de enums

### Tests Modificados
- ✅ Eliminado test de filtro por autor redundante
- ✅ Actualizado test de filtros generales
- ✅ Añadido test específico para nuevos filtros

## 🔄 **Migración de Base de Datos**

### Campos Añadidos
```sql
ALTER TABLE books ADD COLUMN book_type book_type;
ALTER TABLE books ADD COLUMN genre book_genre;
```

### Tipos ENUM Creados
```sql
CREATE TYPE book_type AS ENUM (
    'novel', 'comic', 'manga', 'graphic_novel', 
    'short_story', 'poetry', 'essay', 'biography', 
    'autobiography', 'other'
);

CREATE TYPE book_genre AS ENUM (
    'fiction', 'science_fiction', 'fantasy', 'mystery',
    'thriller', 'horror', 'romance', 'historical_fiction',
    'literary_fiction', 'adventure', 'western', 'dystopian',
    'magical_realism', 'non_fiction', 'biography', 'autobiography',
    'history', 'philosophy', 'psychology', 'science',
    'technology', 'business', 'self_help', 'travel',
    'cooking', 'health', 'religion', 'politics',
    'economics', 'education', 'children', 'young_adult',
    'reference', 'academic', 'other'
);
```

## ⚡ **Mejoras de Rendimiento**

### Índices Añadidos
```sql
CREATE INDEX ix_books_book_type ON books (book_type);
CREATE INDEX ix_books_genre ON books (genre);
```

### Optimizaciones
- Filtros en base de datos (no en memoria)
- Índices para búsquedas rápidas
- Queries optimizadas con JOINs

## 🚀 **Próximas Mejoras**

1. **Filtros Múltiples**: Permitir seleccionar varios tipos/géneros
2. **Filtros Personalizados**: Guardar filtros favoritos
3. **Recomendaciones**: Sugerir libros basados en tipo/género
4. **Estadísticas Avanzadas**: Gráficos de distribución por tipo/género
5. **Búsqueda Inteligente**: Búsqueda por sinónimos de géneros

## 💡 **Casos de Uso Avanzados**

### Librería Especializada
```http
# Solo cómics de superhéroes
GET /groups/{group_id}/books?book_type=comic&search=superhéroe

# Novelas de terror
GET /groups/{group_id}/books?book_type=novel&genre=horror
```

### Biblioteca Académica
```http
# Libros de ciencia
GET /groups/{group_id}/books?genre=science&is_available=true

# Referencias académicas
GET /groups/{group_id}/books?genre=academic
```

### Club de Lectura Infantil
```http
# Libros para niños
GET /groups/{group_id}/books?genre=children&is_available=true
```

## ⚠️ **Consideraciones**

### Compatibilidad
- Los libros existentes tendrán `book_type` y `genre` como `NULL`
- Los filtros funcionan correctamente con valores `NULL`
- No se requiere migración de datos existentes

### Validación
- Los valores de tipo y género deben ser válidos según los enums
- FastAPI valida automáticamente los parámetros
- Respuesta 422 para valores inválidos

## 🎉 **Resultado Final**

Los filtros avanzados están completamente implementados:
- ✅ Filtro por tipo de libro (10 opciones)
- ✅ Filtro por género (30+ opciones)
- ✅ Eliminado filtro redundante de autor
- ✅ Estadísticas mejoradas con género más común
- ✅ Tests completos
- ✅ Migración de base de datos
- ✅ Documentación actualizada

¡Los usuarios ahora pueden encontrar libros de manera mucho más específica y eficiente! 📚✨
