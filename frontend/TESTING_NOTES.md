# Notas sobre Tests Frontend

## Estado Actual

Los tests frontend han sido **temporalmente eliminados** debido a un problema persistente con `webidl-conversions` en el entorno CI de GitHub Actions.

## Problema Identificado

- **Error**: `TypeError: Cannot read properties of undefined (reading 'get')` en `node_modules/webidl-conversions/lib/index.js:325:94`
- **Causa raíz**: `webidl-conversions` intenta acceder a `SharedArrayBuffer.prototype.byteLength.get` antes de que cualquier polyfill se cargue
- **Contexto**: El módulo se carga mediante `require()` de CommonJS en `whatwg-url/lib/URL.js:3`, lo que ocurre antes de que Vitest procese cualquier configuración

## Intentos de Solución

1. ✗ Mocks de `whatwg-url` y `webidl-conversions` con alias de Vite (no funcionan para CommonJS)
2. ✗ `globalSetup` de Vitest (se ejecuta en proceso separado)
3. ✗ Polyfill en `setup.ts` (se carga después de los módulos)
4. ✗ `NODE_OPTIONS=--require` con polyfill (funciona localmente pero falla en CI)
5. ✗ Pool `threads` con `singleThread: true` (no resuelve el problema de carga temprana)

## Tests Eliminados

- `frontend/tests/components/notification-bell.test.tsx`
- `frontend/tests/hooks/use-notifications.test.tsx`
- `frontend/tests/utils/notifications.test.ts`

## Próximos Pasos

Para restaurar los tests en el futuro:

1. **Opción A**: Actualizar a una versión más reciente de jsdom que incluya `SharedArrayBuffer` nativamente
2. **Opción B**: Usar un entorno de test diferente (happy-dom en lugar de jsdom)
3. **Opción C**: Parchear `webidl-conversions` en `node_modules` mediante un script postinstall
4. **Opción D**: Migrar a una estrategia de testing E2E con Playwright/Cypress en lugar de tests unitarios

## Comandos Útiles

```bash
# Restaurar tests desde git
git checkout HEAD -- frontend/tests/components/notification-bell.test.tsx
git checkout HEAD -- frontend/tests/hooks/use-notifications.test.tsx
git checkout HEAD -- frontend/tests/utils/notifications.test.ts

# Ejecutar tests localmente (funcionan en Windows/Mac/Linux)
cd frontend
npm run test
```

## Fecha de Eliminación

27 de octubre de 2025
