# Guía Rápida: Instalación de Node.js en Windows

## Opción 1: Instalador Oficial (Recomendado)

1. **Descargar**:
   - Ve a: https://nodejs.org/
   - Descarga la versión **LTS** (Long Term Support)
   - Actualmente la versión recomendada es **v20.x** o superior

2. **Instalar**:
   - Ejecuta el archivo `.msi` descargado
   - Sigue el asistente de instalación
   - ✅ **IMPORTANTE**: Asegúrate de marcar la opción "Add to PATH"
   - Acepta todas las opciones por defecto

3. **Verificar**:
   - Abre una **nueva** ventana de PowerShell o CMD
   - Ejecuta:
     ```powershell
     node --version
     npm --version
     ```
   - Deberías ver algo como:
     ```
     v20.11.0
     10.2.4
     ```

## Opción 2: Con Chocolatey (Si ya lo tienes)

```powershell
# Ejecutar como Administrador
choco install nodejs-lts -y
```

## Opción 3: Con Winget (Windows 11)

```powershell
winget install OpenJS.NodeJS.LTS
```

## Después de Instalar

1. **Reinicia tu terminal** (PowerShell o CMD)
2. **Verifica que funcione**:
   ```powershell
   node --version
   npm --version
   ```

3. **Actualizar npm** (opcional pero recomendado):
   ```powershell
   npm install -g npm@latest
   ```

## Solución de Problemas

### "node no se reconoce como comando"

1. Cierra y abre una nueva terminal
2. Si persiste, verifica que Node.js esté en el PATH:
   - Busca "Variables de entorno" en Windows
   - En "Variables del sistema", busca "Path"
   - Verifica que exista una entrada como: `C:\Program Files\nodejs\`

### Permisos de Ejecución

Si tienes problemas con permisos en PowerShell:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## Próximos Pasos

Una vez instalado Node.js, continúa con el **Paso 1** para crear el proyecto frontend:

```powershell
cd d:\IAs\book_sharing_app_friends
npx create-next-app@latest frontend
```

## Recursos Adicionales

- Documentación oficial: https://nodejs.org/docs/
- Guía de npm: https://docs.npmjs.com/
- Next.js: https://nextjs.org/docs
