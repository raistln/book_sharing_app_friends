# Corrección del Sistema de Chat

## Estado actual
- **Backend REST**: Los endpoints `POST /chat/send` y `GET /chat/loan/{loan_id}` definidos en `app/api/chat.py` funcionan sobre `MessageService` (`app/services/message_service.py`) y el modelo `Message` (`app/models/message.py`).
- **Control de acceso**: `MessageService.can_access()` valida que solo `borrower` y `lender` del préstamo interactúen con el chat.
- **Frontend**: `useMessages()` en `frontend/lib/hooks/use-chat.ts` usa React Query con `refetchInterval: 5000` y `ChatBox` (`frontend/components/chat/chat-box.tsx`) renderiza la conversación.
- **Cobertura de tests**: `tests/test_chat.py` garantiza envío y lectura básicos y verifica restricciones de acceso.

## Problemas detectados
- **Transferencia redundante**: Cada sondeo devuelve el historial completo del préstamo, generando sobrecarga innecesaria cuando crece el número de mensajes.
- **Latencia perceptible**: El intervalo fijo de 5 s retrasa la entrega y, si se reduce, incrementa la presión sobre el backend.
- **Falta de incrementalidad**: No existen filtros tipo `after_id` o `since`; el servicio no distingue mensajes ya descargados.
- **Orden débil**: Se ordena solo por `created_at`; si dos mensajes comparten timestamp, pueden aparecer desordenados.
- **Experiencia offline limitada**: No hay refresco automático al recuperar foco ni reintentos sobre errores de red.

## Plan de mejoras (fase inmediata sin WebSockets)
- **Filtro incremental**: Ampliar `MessageService.list_for_loan()` y `GET /chat/loan/{loan_id}` para aceptar `after_id` (o `since`) devolviendo solo mensajes nuevos; ordenar por `created_at` seguido de `id`.
- **Optimización de polling**: Ajustar `useMessages()` para enviar el `lastMessageId`, aplicar `refetchInterval` dinámico (rápido tras actividad, lento en reposo) y disparar `refetch` con `visibilitychange`.
- **Manejo de estado**: Consolidar invalidación en `useSendMessage()` eliminando `refetch` duplicado, añadir feedback en `ChatBox` para errores transitorios y mantener contador local mientras llega la respuesta.
- **Documentación y pruebas**: Extender `tests/test_chat.py` con casos para `after_id` y actualizar `docs/backend/Paso 13 Chat_y_Comunicacion.md` y `docs/SISTEMA_COMPLETO_Y_PRUEBAS.md` con el nuevo flujo.

## Escenario WebSocket (fase posterior)
- **Ventajas**: Push inmediato, menor transferencia (solo mensajes nuevos), posibilita estado "typing" y presencia.
- **Desafíos**: Autenticación en la conexión, gestión de salas por `loan_id`, necesidad de infraestructura compartida (Redis/pub-sub) y requisitos de despliegue asincrónico.
- **Recomendación**: Implementar primero las optimizaciones de polling y considerar WebSockets cuando el volumen o la UX requieran tiempo real pleno.
