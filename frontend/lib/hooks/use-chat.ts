import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { chatApi } from '@/lib/api/chat';
import { toast } from '@/components/ui/use-toast';
import type { Message, MessageCreate } from '@/lib/types/chat';
import { useRef, useCallback } from 'react';

// Hook para obtener mensajes de un préstamo con polling optimizado
export function useMessages(loanId: string) {
  const queryClient = useQueryClient();
  const lastMessageTimeRef = useRef<string | null>(null);

  const { data: messages = [], isLoading, error, refetch } = useQuery({
    queryKey: ['messages', loanId],
    queryFn: async () => {
      // En la primera carga, obtener todos los mensajes
      if (!lastMessageTimeRef.current) {
        const allMessages = await chatApi.getMessages(loanId);
        
        // Guardar el timestamp del último mensaje
        if (allMessages.length > 0) {
          lastMessageTimeRef.current = allMessages[allMessages.length - 1].created_at;
        }
        
        return allMessages;
      }
      
      // En polling subsecuente, solo obtener mensajes nuevos
      const newMessages = await chatApi.getMessages(loanId, lastMessageTimeRef.current);
      
      if (newMessages.length > 0) {
        // Actualizar el timestamp del último mensaje
        lastMessageTimeRef.current = newMessages[newMessages.length - 1].created_at;
        
        // Combinar mensajes existentes con los nuevos
        const existingMessages = queryClient.getQueryData<Message[]>(['messages', loanId]) || [];
        return [...existingMessages, ...newMessages];
      }
      
      // Si no hay mensajes nuevos, devolver los existentes
      return queryClient.getQueryData<Message[]>(['messages', loanId]) || [];
    },
    enabled: !!loanId,
    refetchInterval: 3000, // Polling cada 3 segundos (más frecuente pero más eficiente)
    refetchIntervalInBackground: false, // No hacer polling cuando la pestaña está en background
  });

  // Función para resetear el timestamp (útil cuando se envía un mensaje)
  const resetTimestamp = useCallback(() => {
    if (messages.length > 0) {
      lastMessageTimeRef.current = messages[messages.length - 1].created_at;
    }
  }, [messages]);

  return { messages, isLoading, error, refetch, resetTimestamp };
}

// Hook para enviar mensaje
export function useSendMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: chatApi.sendMessage,
    onSuccess: (newMessage) => {
      // Actualizar la lista de mensajes del préstamo
      queryClient.invalidateQueries({ queryKey: ['messages', newMessage.loan_id] });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al enviar mensaje',
        description: error.response?.data?.detail || 'No se pudo enviar el mensaje',
        variant: 'destructive',
      });
    },
  });
}
