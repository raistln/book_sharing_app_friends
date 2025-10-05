# 📋 Checklist Completa - Sistema de Reseñas

## 🎯 FASE 0: Preparación (5 min)
- [ ] Hacer backup de la base de datos
- [ ] Crear rama nueva en git: `git checkout -b feature/reviews-system`
- [ ] Asegurar que todos los tests actuales pasan: `pytest`
- [ ] Verificar que Redis y PostgreSQL están corriendo

---

## 📦 FASE 1: Modelos y Schemas (20 min)

### Modelo SQLAlchemy
- [ ] Crear archivo `app/models/review.py`
- [ ] Definir clase `Review` con todos los campos
- [ ] Agregar relaciones: `book`, `user`, `group`
- [ ] Crear constraint única: `(book_id, user_id)`
- [ ] Crear check constraint: `rating BETWEEN 1 AND 5`
- [ ] Agregar índices en `book_id` y `group_id`
- [ ] Importar modelo en `app/models/__init__.py`

### Schemas Pydantic
- [ ] Crear archivo `app/schemas/review.py`
- [ ] Implementar `ReviewBase` con validaciones
- [ ] Implementar `ReviewCreate`
- [ ] Implementar `ReviewUpdate`
- [ ] Implementar `ReviewResponse`
- [ ] Modificar `app/schemas/book.py`:
  - [ ] Crear `BookWithReviews` 
  - [ ] Agregar campos `average_rating` y `total_reviews`

### Verificación
- [ ] Los imports funcionan correctamente
- [ ] No hay errores de sintaxis: `python -m py_compile app/models/review.py`
- [ ] No hay errores en schemas: `python -m py_compile app/schemas/review.py`

---

## 🗄️ FASE 2: Migración de Base de Datos (15 min)

### Crear Migración
- [ ] Generar migración: `alembic revision --autogenerate -m "add_reviews_table"`
- [ ] Revisar archivo generado en `alembic/versions/`
- [ ] Verificar que incluye:
  - [ ] Tabla `reviews` con todas las columnas
  - [ ] Foreign keys con `ON DELETE CASCADE`
  - [ ] Índices en `book_id` y `group_id`
  - [ ] Unique constraint en `(book_id, user_id)`
  - [ ] Check constraint en `rating`

### Aplicar Migración
- [ ] Ejecutar: `alembic upgrade head`
- [ ] Verificar en PostgreSQL que la tabla existe:
  ```sql
  \dt reviews
  \d reviews
  ```
- [ ] Verificar constraints e índices

### Rollback de Prueba
- [ ] Probar rollback: `alembic downgrade -1`
- [ ] Volver a aplicar: `alembic upgrade head`

---

## 🔧 FASE 3: Servicio de Lógica de Negocio (30 min)

### Implementar Servicio
- [ ] Crear archivo `app/services/review_service.py`
- [ ] Implementar `create_review()` con:
  - [ ] Validación de libro existente
  - [ ] Validación de permisos de grupo
  - [ ] Validación de reseña duplicada
  - [ ] Logging de creación
- [ ] Implementar `get_book_reviews()` con:
  - [ ] Eager loading de usuario
  - [ ] Paginación (skip/limit)
  - [ ] Ordenamiento
  - [ ] Validación de permisos
- [ ] Implementar `update_review()` con:
  - [ ] Validación de propiedad
  - [ ] Actualización de `updated_at`
  - [ ] Logging de actualización
- [ ] Implementar `delete_review()` con:
  - [ ] Validación de propiedad
  - [ ] Hard delete
  - [ ] Logging de eliminación
- [ ] Implementar `calculate_book_rating()` con:
  - [ ] Cálculo de promedio
  - [ ] Conteo de reseñas
- [ ] Implementar `user_can_review_book()` con:
  - [ ] Validación de pertenencia a grupo

### Verificación
- [ ] Imports correctos
- [ ] Type hints en todas las funciones
- [ ] Docstrings completos
- [ ] Manejo de errores apropiado

---

## 🌐 FASE 4: Endpoints API (30 min)

### Crear Endpoints
- [ ] Crear archivo `app/api/reviews.py`
- [ ] Implementar `POST /reviews/`:
  - [ ] Validación de input
  - [ ] Llamada a servicio
  - [ ] Manejo de errores (400, 403, 404, 422)
  - [ ] Response 201 Created
  - [ ] Logging
- [ ] Implementar `GET /reviews/book/{book_id}`:
  - [ ] Query params (skip, limit, order_by)
  - [ ] Validación de permisos
  - [ ] Response 200 OK
  - [ ] Manejo de errores (403, 404)
- [ ] Implementar `GET /reviews/{review_id}`:
  - [ ] Validación de permisos
  - [ ] Response 200 OK
  - [ ] Manejo de errores (403, 404)
- [ ] Implementar `PUT /reviews/{review_id}`:
  - [ ] Validación de propiedad
  - [ ] Response 200 OK
  - [ ] Manejo de errores (403, 404)
- [ ] Implementar `DELETE /reviews/{review_id}`:
  - [ ] Validación de propiedad
  - [ ] Response 204 No Content
  - [ ] Manejo de errores (403, 404)
- [ ] Implementar `GET /reviews/my-reviews`:
  - [ ] Paginación
  - [ ] Response 200 OK

### Modificar Endpoint Existente
- [ ] Modificar `app/api/books.py`:
  - [ ] Agregar query param `include_reviews: bool = False`
  - [ ] Si True, incluir reseñas con eager loading
  - [ ] Calcular y agregar `average_rating`
  - [ ] Agregar `total_reviews`

### Registrar Router
- [ ] Agregar router en `app/main.py`:
  ```python
  from app.api import reviews
  app.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
  ```

### Verificación
- [ ] No hay errores de sintaxis
- [ ] Todos los endpoints tienen documentación (docstrings)
- [ ] Códigos HTTP correctos
- [ ] Mensajes de error claros

---

## 🧪 FASE 5: Tests Unitarios (45 min)

### Crear Archivo de Tests
- [ ] Crear `tests/test_review_service_unit.py`
- [ ] Setup de fixtures (mock db, usuarios, libros, grupos)

### Implementar Tests
- [ ] `test_create_review_success`:
  - [ ] Mock de db.execute y db.commit
  - [ ] Verificar que se crea correctamente
  - [ ] Verificar todos los campos
- [ ] `test_create_review_duplicate_fails`:
  - [ ] Simular reseña existente
  - [ ] Verificar que lanza excepción apropiada
- [ ] `test_create_review_invalid_rating_fails`:
  - [ ] Probar rating < 1 y rating > 5
  - [ ] Verificar ValidationError
- [ ] `test_create_review_user_not_in_group_fails`:
  - [ ] Usuario sin pertenencia al grupo
  - [ ] Verificar HTTPException 403
- [ ] `test_update_review_success`:
  - [ ] Mock de actualización
  - [ ] Verificar campos actualizados
- [ ] `test_update_review_not_owner_fails`:
  - [ ] Intentar actualizar reseña ajena
  - [ ] Verificar HTTPException 403
- [ ] `test_delete_review_success`:
  - [ ] Mock de eliminación
  - [ ] Verificar llamada a delete
- [ ] `test_delete_review_not_owner_fails`:
  - [ ] Intentar eliminar reseña ajena
  - [ ] Verificar HTTPException 403
- [ ] `test_calculate_book_rating`:
  - [ ] Mock de varias reseñas
  - [ ] Verificar cálculo correcto de promedio

### Ejecutar Tests
- [ ] Ejecutar: `pytest tests/test_review_service_unit.py -v`
- [ ] Verificar que todos pasan
- [ ] Verificar coverage: `pytest tests/test_review_service_unit.py --cov=app/services/review_service`

---

## 🔌 FASE 6: Tests de Integración (60 min)

### Crear Archivo de Tests
- [ ] Crear `tests/test_review_endpoints.py`
- [ ] Setup de TestClient y base de datos de prueba
- [ ] Fixtures para autenticación

### Implementar Tests de Endpoints
- [ ] `test_create_review_integration`:
  - [ ] Crear usuario, grupo, libro
  - [ ] POST /reviews/ con datos válidos
  - [ ] Verificar status 201
  - [ ] Verificar response
- [ ] `test_create_review_duplicate_integration`:
  - [ ] Crear reseña
  - [ ] Intentar crear otra del mismo usuario/libro
  - [ ] Verificar status 400
- [ ] `test_get_book_reviews_integration`:
  - [ ] Crear varias reseñas
  - [ ] GET /reviews/book/{book_id}
  - [ ] Verificar paginación
  - [ ] Verificar ordenamiento
- [ ] `test_get_review_by_id_integration`:
  - [ ] GET /reviews/{review_id}
  - [ ] Verificar datos correctos
- [ ] `test_update_review_integration`:
  - [ ] Crear reseña
  - [ ] PUT /reviews/{review_id}
  - [ ] Verificar actualización
- [ ] `test_delete_review_integration`:
  - [ ] Crear reseña
  - [ ] DELETE /reviews/{review_id}
  - [ ] Verificar status 204
  - [ ] Verificar que no existe
- [ ] `test_my_reviews_integration`:
  - [ ] Crear varias reseñas de un usuario
  - [ ] GET /reviews/my-reviews
  - [ ] Verificar que solo devuelve las propias
- [ ] `test_book_with_reviews_integration`:
  - [ ] GET /books/{book_id}?include_reviews=true
  - [ ] Verificar que incluye reseñas
  - [ ] Verificar average_rating
  - [ ] Verificar total_reviews
- [ ] `test_review_permissions_across_groups`:
  - [ ] Crear 2 grupos diferentes
  - [ ] Intentar acceder a reseña de otro grupo
  - [ ] Verificar status 403

### Ejecutar Tests
- [ ] Ejecutar: `pytest tests/test_review_endpoints.py -v`
- [ ] Verificar que todos pasan
- [ ] Verificar coverage: `pytest tests/test_review_endpoints.py --cov=app/api/reviews`

---

## 🔄 FASE 7: Tests de Flujo Completo (30 min)

### Crear Archivo de Tests
- [ ] Crear `tests/test_review_complete_flow.py`

### Implementar Test de Flujo
- [ ] `test_complete_review_flow`:
  - [ ] Paso 1: Registrar usuario
  - [ ] Paso 2: Crear grupo
  - [ ] Paso 3: Agregar libro
  - [ ] Paso 4: Crear reseña
  - [ ] Paso 5: Verificar en GET /books/{id}
  - [ ] Paso 6: Editar reseña
  - [ ] Paso 7: Verificar actualización
  - [ ] Paso 8: Crear segunda reseña (otro usuario)
  - [ ] Paso 9: Verificar rating promedio
  - [ ] Paso 10: Eliminar reseña
  - [ ] Paso 11: Verificar recalculo de rating

### Ejecutar Tests
- [ ] Ejecutar: `pytest tests/test_review_complete_flow.py -v`
- [ ] Verificar que todo el flujo funciona

---

## ✅ FASE 8: Verificación Final (30 min)

### Tests Completos
- [ ] Ejecutar todos los tests: `pytest -v`
- [ ] Verificar que no hay regresiones
- [ ] Verificar coverage total:
  ```bash
  pytest --cov=app --cov-report=html
  ```
- [ ] Revisar reporte HTML en `htmlcov/index.html`
- [ ] Coverage de código nuevo > 90%

### Pruebas Manuales en Swagger
- [ ] Iniciar aplicación: `python main.py`
- [ ] Abrir `http://localhost:8000/docs`
- [ ] Probar cada endpoint:
  - [ ] POST /auth/register (crear usuario de prueba)
  - [ ] POST /auth/login (obtener token)
  - [ ] POST /books/ (crear libro de prueba)
  - [ ] POST /reviews/ (crear reseña)
  - [ ] GET /reviews/book/{book_id} (ver reseñas)
  - [ ] GET /books/{book_id}?include_reviews=true
  - [ ] PUT /reviews/{review_id} (editar)
  - [ ] DELETE /reviews/{review_id} (eliminar)
- [ ] Verificar respuestas correctas
- [ ] Verificar códigos de error funcionan

### Validaciones de Seguridad
- [ ] Intentar crear reseña sin autenticación → 401
- [ ] Intentar editar reseña de otro usuario → 403
- [ ] Intentar ver reseñas de otro grupo → 403
- [ ] Intentar crear reseña duplicada → 400
- [ ] Intentar rating inválido (0, 6) → 422
- [ ] Intentar contenido > 1000 chars → 422

### Verificación de Base de Datos
- [ ] Conectar a PostgreSQL
- [ ] Verificar tabla `reviews` existe
- [ ] Crear reseña desde API
- [ ] Verificar registro en BD:
  ```sql
  SELECT * FROM reviews;
  ```
- [ ] Verificar foreign keys funcionan
- [ ] Verificar constraint única funciona
- [ ] Intentar insertar rating inválido manualmente → Error

---

## 📝 FASE 9: Documentación (15 min)

### Actualizar README
- [ ] Agregar sección "Sistema de Reseñas" en README.md
- [ ] Listar endpoints nuevos
- [ ] Agregar ejemplos de uso
- [ ] Actualizar estructura de archivos

### Documentación de Código
- [ ] Verificar que todos los docstrings están completos
- [ ] Verificar type hints en todas las funciones
- [ ] Agregar comentarios en código complejo

### Actualizar Changelog
- [ ] Crear entrada en CHANGELOG.md (si existe)
- [ ] Listar nuevas funcionalidades
- [ ] Mencionar migración de BD

---

## 🚀 FASE 10: Deploy (20 min)

### Preparación
- [ ] Revisar que `.env` no está en git
- [ ] Revisar variables de entorno necesarias
- [ ] Verificar que `requirements.txt` tiene todas las dependencias

### Git
- [ ] Revisar todos los cambios: `git status`
- [ ] Agregar archivos: `git add .`
- [ ] Commit: `git commit -m "feat: add reviews system with tests"`
- [ ] Push a rama: `git push origin feature/reviews-system`

### Merge a Main
- [ ] Crear Pull Request en GitHub
- [ ] Revisar diff completo
- [ ] Ejecutar CI/CD (si existe)
- [ ] Merge a `main`

### Deploy en Producción
- [ ] Hacer backup de BD de producción
- [ ] Ejecutar migraciones en producción:
  ```bash
  alembic upgrade head
  ```
- [ ] Verificar que la aplicación inicia correctamente
- [ ] Verificar logs: no hay errores
- [ ] Probar endpoints en producción

---

## 🎉 FASE 11: Validación Post-Deploy (15 min)

### Tests en Producción
- [ ] Crear usuario de prueba
- [ ] Crear libro de prueba
- [ ] Crear reseña de prueba
- [ ] Verificar GET /books/{id}?include_reviews=true
- [ ] Verificar cálculo de rating
- [ ] Eliminar datos de prueba

### Monitoreo
- [ ] Revisar logs de aplicación
- [ ] Verificar que no hay errores 500
- [ ] Verificar tiempos de respuesta
- [ ] Verificar uso de CPU/Memoria

### Comunicación
- [ ] Notificar a equipo (si aplica)
- [ ] Actualizar documentación de API
- [ ] Cerrar issues relacionados

---

## 📊 Resumen de Tiempo Estimado

| Fase | Tiempo Estimado | Acumulado |
|------|----------------|-----------|
| Preparación | 5 min | 5 min |
| Modelos y Schemas | 20 min | 25 min |
| Migración BD | 15 min | 40 min |
| Servicio | 30 min | 1h 10min |
| Endpoints API | 30 min | 1h 40min |
| Tests Unitarios | 45 min | 2h 25min |
| Tests Integración | 60 min | 3h 25min |
| Tests Flujo | 30 min | 3h 55min |
| Verificación | 30 min | 4h 25min |
| Documentación | 15 min | 4h 40min |
| Deploy | 20 min | 5h |
| Post-Deploy | 15 min | **5h 15min** |

---

## ⚠️ Troubleshooting Común

### Error: Migración falla
- [ ] Verificar que PostgreSQL está corriendo
- [ ] Verificar conexión en `.env`
- [ ] Revisar sintaxis de migración
- [ ] Hacer rollback y regenerar

### Error: Tests fallan
- [ ] Verificar base de datos de test
- [ ] Limpiar cache: `pytest --cache-clear`
- [ ] Verificar fixtures
- [ ] Revisar imports

### Error: 500 en producción
- [ ] Revisar logs: `tail -f logs/app.log`
- [ ] Verificar variables de entorno
- [ ] Verificar migración aplicada
- [ ] Verificar permisos de BD

---

## 🎯 Checklist de Calidad Final

- [ ] ✅ Todos los tests pasan (100%)
- [ ] ✅ Coverage > 90% en código nuevo
- [ ] ✅ No hay warnings en tests
- [ ] ✅ No hay errores en logs
- [ ] ✅ Documentación actualizada
- [ ] ✅ Código sigue convenciones del proyecto
- [ ] ✅ No hay código comentado innecesario
- [ ] ✅ No hay TODOs pendientes
- [ ] ✅ Performance aceptable (< 500ms por request)
- [ ] ✅ Seguridad validada (permisos funcionan)

---

**¡Listo para producción! 🚀**
