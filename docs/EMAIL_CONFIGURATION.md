# 📧 Configuración de Notificaciones por Email

El sistema de notificaciones por email es **completamente opcional** y está desactivado por defecto. Puedes activarlo cuando lo desees configurando las variables de entorno.

## 🎯 ¿Cuándo se envían emails?

Cuando está activado, el sistema envía emails automáticamente en estos casos:

1. **Nueva solicitud de préstamo** - Al dueño del libro
2. **Préstamo aprobado** - Al solicitante
3. **Recordatorio de devolución** - 3 días antes del vencimiento
4. **Préstamo vencido** - Cuando se pasa la fecha límite

## ⚙️ Configuración

### 1. Editar archivo `.env.backend`

Copia el archivo de ejemplo si no existe:
```bash
cp .env.backend.example .env.backend
```

### 2. Activar notificaciones por email

En `.env.backend`, cambia:
```env
ENABLE_EMAIL_NOTIFICATIONS=True
```

### 3. Configurar SMTP según tu proveedor

#### 📮 Gmail

1. **Habilitar "Verificación en 2 pasos"** en tu cuenta de Google
2. **Crear una "Contraseña de aplicación"**:
   - Ve a: https://myaccount.google.com/apppasswords
   - Selecciona "Correo" y "Otro (nombre personalizado)"
   - Copia la contraseña generada (16 caracteres)

3. **Configurar en `.env.backend`**:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-contraseña-de-aplicacion
SMTP_FROM_EMAIL=tu-email@gmail.com
SMTP_FROM_NAME=Book Sharing App
SMTP_USE_TLS=True
```

#### 📮 Outlook/Hotmail

```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=tu-email@outlook.com
SMTP_PASSWORD=tu-contraseña
SMTP_FROM_EMAIL=tu-email@outlook.com
SMTP_FROM_NAME=Book Sharing App
SMTP_USE_TLS=True
```

#### 📮 Yahoo Mail

```env
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USER=tu-email@yahoo.com
SMTP_PASSWORD=tu-contraseña-de-aplicacion
SMTP_FROM_EMAIL=tu-email@yahoo.com
SMTP_FROM_NAME=Book Sharing App
SMTP_USE_TLS=True
```

#### 📮 SendGrid (Recomendado para producción)

1. Crea una cuenta en https://sendgrid.com
2. Genera una API Key
3. Configura:

```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=tu-api-key-de-sendgrid
SMTP_FROM_EMAIL=noreply@tudominio.com
SMTP_FROM_NAME=Book Sharing App
SMTP_USE_TLS=True
```

#### 📮 Mailgun

```env
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@tudominio.mailgun.org
SMTP_PASSWORD=tu-contraseña-mailgun
SMTP_FROM_EMAIL=noreply@tudominio.com
SMTP_FROM_NAME=Book Sharing App
SMTP_USE_TLS=True
```

## 🧪 Probar la configuración

1. **Reinicia el servidor**:
```bash
poetry run uvicorn app.main:app --reload
```

2. **Verifica los logs**:
Al iniciar, deberías ver:
```
INFO: Email service is configured and enabled
```

3. **Prueba enviando una solicitud de préstamo**:
- El dueño del libro debería recibir un email
- Si no llega, revisa los logs para ver errores

## 🔍 Troubleshooting

### Email no se envía

1. **Verifica que está activado**:
```env
ENABLE_EMAIL_NOTIFICATIONS=True
```

2. **Revisa los logs del servidor**:
```bash
# Busca errores como:
# "Failed to send email to..."
# "Email service is not configured or disabled"
```

3. **Problemas comunes**:

**Gmail bloquea el acceso:**
- Asegúrate de usar una "Contraseña de aplicación", no tu contraseña normal
- Verifica que la verificación en 2 pasos esté activada

**Outlook/Hotmail bloquea:**
- Verifica que tu cuenta no esté bloqueada
- Intenta iniciar sesión desde un navegador primero

**Error de conexión:**
- Verifica el puerto (587 para TLS, 465 para SSL)
- Asegúrate de que tu firewall no bloquee el puerto

**Error de autenticación:**
- Verifica usuario y contraseña
- Para Gmail, usa la contraseña de aplicación de 16 caracteres

## 🔒 Seguridad

### ⚠️ IMPORTANTE:

1. **NUNCA** subas el archivo `.env.backend` a Git
2. **NUNCA** compartas tus contraseñas de aplicación
3. **USA** variables de entorno en producción
4. **ROTA** las contraseñas periódicamente

### Buenas prácticas:

- En desarrollo: Usa Gmail con contraseña de aplicación
- En producción: Usa SendGrid, Mailgun o AWS SES
- Limita el rate de emails para evitar spam
- Monitorea los logs de envío

## 📊 Monitoreo

El sistema registra todos los intentos de envío:

```python
# Logs exitosos:
INFO: Email sent successfully to user@example.com

# Logs de error:
ERROR: Failed to send email to user@example.com: [razón]
```

## 🎨 Personalización

Los templates de email están en `app/services/email_service.py`. Puedes personalizarlos editando:

- `send_loan_request_email()` - Solicitud de préstamo
- `send_loan_approved_email()` - Préstamo aprobado
- `send_due_date_reminder_email()` - Recordatorio

## 🚀 Desactivar emails

Para desactivar temporalmente sin borrar la configuración:

```env
ENABLE_EMAIL_NOTIFICATIONS=False
```

El sistema seguirá creando notificaciones en la app, pero no enviará emails.

## 📝 Notas

- Los emails se envían de forma **asíncrona** para no bloquear las peticiones
- Si falla el envío, se registra en los logs pero **no afecta** la funcionalidad principal
- Las notificaciones en la app **siempre** se crean, independientemente del email
- Los recordatorios automáticos se envían mediante APScheduler (diariamente a las 9:00 AM)
