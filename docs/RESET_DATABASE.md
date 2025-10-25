# 🗑️ Guía para Limpiar la Base de Datos

## 📋 Descripción

Estos scripts te permiten resetear completamente la base de datos, eliminando todos los datos y recreando las tablas desde cero. Son útiles para:

- 🧪 Empezar pruebas desde cero
- 🐛 Resolver problemas de migración
- 🔄 Limpiar datos de desarrollo
- 🎯 Preparar demos limpias

---

## 🚀 Uso Rápido

### **Opción 1: Reset con Alembic (Recomendado)**

```bash
cd d:/IAs/book_sharing_app_friends
python reset_database.py
```

**Ventajas:**
- ✅ Usa migraciones de Alembic
- ✅ Mantiene historial de versiones
- ✅ Más robusto para producción
- ✅ Elimina tabla `alembic_version` también

**Cuándo usar:**
- Cuando quieras mantener el historial de migraciones
- Para resetear en entornos de staging/producción
- Cuando tengas problemas con migraciones

---

### **Opción 2: Reset Simple**

```bash
cd d:/IAs/book_sharing_app_friends
python reset_database_simple.py
```

**Ventajas:**
- ✅ Más rápido
- ✅ Usa directamente SQLAlchemy
- ✅ No depende de Alembic
- ✅ Ideal para desarrollo

**Cuándo usar:**
- Para desarrollo local rápido
- Cuando no te importa el historial de migraciones
- Para pruebas rápidas

---

## ⚙️ Cómo Funcionan

### **reset_database.py (Alembic)**

1. **Conecta a la base de datos** usando `DATABASE_URL` de `.env.backend`
2. **Lista todas las tablas** existentes
3. **Elimina todas las tablas** usando `DROP TABLE CASCADE`
4. **Elimina tabla alembic_version** para resetear historial
5. **Ejecuta `alembic upgrade head`** para recrear todo
6. **Verifica** que las tablas se crearon correctamente

### **reset_database_simple.py (SQLAlchemy)**

1. **Conecta a la base de datos** usando `DATABASE_URL`
2. **Importa todos los modelos** (User, Book, Loan, etc.)
3. **Ejecuta `Base.metadata.drop_all()`** para eliminar tablas
4. **Ejecuta `Base.metadata.create_all()`** para recrearlas
5. **Verifica** las tablas creadas

---

## 🔒 Seguridad

Ambos scripts incluyen medidas de seguridad:

1. **Confirmación requerida:** Debes escribir "SI" para continuar
2. **Información clara:** Muestra qué base de datos se va a limpiar
3. **Logs detallados:** Muestra cada paso del proceso
4. **Manejo de errores:** Captura y muestra errores claramente

---

## 📊 Ejemplo de Ejecución

```bash
$ python reset_database.py

============================================================
🔄 RESET COMPLETO DE BASE DE DATOS
============================================================

📍 Base de datos: localhost:5432/book_sharing

⚠️  ADVERTENCIA: Esta acción eliminará TODOS los datos.
¿Estás seguro de que quieres continuar? (escribe 'SI' para confirmar): SI

🗑️  Eliminando todas las tablas...
📋 Tablas encontradas: users, books, loans, groups, group_members, invitations, notifications, reviews, alembic_version
   Eliminando tabla: users
   Eliminando tabla: books
   Eliminando tabla: loans
   Eliminando tabla: groups
   Eliminando tabla: group_members
   Eliminando tabla: invitations
   Eliminando tabla: notifications
   Eliminando tabla: reviews
   Eliminando tabla: alembic_version
✅ Todas las tablas eliminadas correctamente

🔄 Ejecutando migraciones de Alembic...
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> abc123, create users table
INFO  [alembic.runtime.migration] Running upgrade abc123 -> def456, create books table
...
✅ Migraciones aplicadas correctamente

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

============================================================
✅ BASE DE DATOS RESETEADA EXITOSAMENTE
============================================================

💡 La base de datos está limpia y lista para pruebas.
   Puedes iniciar el servidor y crear datos de prueba.
```

---

## 🐛 Troubleshooting

### **Error: "No module named 'app'"**

**Solución:** Ejecuta desde la raíz del proyecto:
```bash
cd d:/IAs/book_sharing_app_friends
python reset_database.py
```

### **Error: "Could not connect to database"**

**Solución:** Verifica que PostgreSQL está corriendo:
```bash
# Windows
net start postgresql-x64-14

# O verifica el servicio en Services
```

### **Error: "alembic: command not found"**

**Solución:** Usa Poetry:
```bash
poetry run alembic upgrade head
```

O instala Alembic:
```bash
poetry install
```

### **Error: "Permission denied"**

**Solución:** Verifica que tu usuario tiene permisos en la base de datos:
```sql
-- Conectar como superusuario
psql -U postgres

-- Dar permisos
GRANT ALL PRIVILEGES ON DATABASE book_sharing TO tu_usuario;
```

---

## 🔄 Flujo Completo de Pruebas

### **1. Limpiar base de datos**
```bash
python reset_database.py
```

### **2. Iniciar backend**
```bash
poetry run uvicorn app.main:app --reload
```

### **3. Iniciar frontend**
```bash
cd frontend
npm run dev
```

### **4. Crear datos de prueba**
- Registrar usuarios
- Crear grupos
- Agregar libros
- Solicitar préstamos
- etc.

---

## 📝 Notas Importantes

1. **Backup:** Si tienes datos importantes, haz backup ANTES de resetear:
   ```bash
   pg_dump -U postgres book_sharing > backup.sql
   ```

2. **Restaurar backup:**
   ```bash
   psql -U postgres book_sharing < backup.sql
   ```

3. **Variables de entorno:** Los scripts usan `.env.backend` automáticamente

4. **No afecta archivos:** Solo limpia la base de datos, no elimina archivos subidos

---

## 🎯 Casos de Uso

### **Desarrollo diario:**
```bash
# Reset rápido
python reset_database_simple.py
```

### **Antes de demo:**
```bash
# Reset completo con Alembic
python reset_database.py
```

### **Problemas de migración:**
```bash
# Reset con Alembic para recrear historial
python reset_database.py
```

### **Testing automatizado:**
```python
# En tus tests
import subprocess
subprocess.run(["python", "reset_database_simple.py"], input="SI\n", text=True)
```

---

## ✅ Checklist Post-Reset

Después de resetear la base de datos:

- [ ] Verificar que el backend inicia sin errores
- [ ] Verificar que puedes registrar un usuario
- [ ] Verificar que puedes hacer login
- [ ] Verificar que las migraciones están actualizadas: `alembic current`
- [ ] Verificar que todas las tablas existen en la BD

---

## 📞 Soporte

Si tienes problemas:

1. Revisa los logs del script (son muy detallados)
2. Verifica tu archivo `.env.backend`
3. Verifica que PostgreSQL está corriendo
4. Consulta la documentación de Alembic: https://alembic.sqlalchemy.org/

---

**Última actualización:** 22 de Octubre, 2025
