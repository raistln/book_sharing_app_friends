# 🗑️ Cómo Resetear la Base de Datos

## ✅ Resumen Rápido

Para limpiar completamente la base de datos y empezar desde cero:

```bash
cd d:/IAs/book_sharing_app_friends
poetry run python reset_database.py
```

Escribe **SI** cuando te pida confirmación.

---

## 📋 ¿Qué hace el script?

1. **Elimina todas las tablas** de la base de datos
2. **Elimina todos los tipos ENUM** personalizados
3. **Recrea las tablas** usando migraciones de Alembic
4. **Verifica** que todo se creó correctamente

---

## 🎯 Resultado

Después de ejecutar el script verás:

```
============================================================
✅ BASE DE DATOS RESETEADA EXITOSAMENTE
============================================================

📊 Tablas creadas (9):
   ✓ alembic_version
   ✓ books
   ✓ group_members
   ✓ groups
   ✓ invitations
   ✓ loans
   ✓ notifications
   ✓ reviews
   ✓ users

💡 La base de datos está limpia y lista para pruebas.
```

---

## 🚀 Siguiente Paso

Después de resetear, inicia el servidor:

```bash
poetry run uvicorn app.main:app --reload
```

Y el frontend:

```bash
cd frontend
npm run dev
```

---

## 📝 Notas Importantes

- ⚠️ **Todos los datos se perderán** (usuarios, libros, préstamos, etc.)
- ✅ El script pide confirmación antes de ejecutar
- ✅ Los archivos subidos NO se eliminan (solo la BD)
- ✅ Las migraciones de Alembic se mantienen actualizadas

---

## 🔄 Alternativa Rápida

Si prefieres un reset más rápido sin Alembic:

```bash
poetry run python reset_database_simple.py
```

---

**Última actualización:** 22 de Octubre, 2025
