import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { chatApi } from '@/lib/api/chat';
import { toast } from '@/components/ui/use-toast';
import type { MessageCreate } from '@/lib/types/chat';

// Hook para obtener mensajes de un préstamo
export function useMessages(loanId: string) {
  const { data: messages = [], isLoading, error, refetch } = useQuery({
    queryKey: ['messages', loanId],
    queryFn: () => chatApi.getMessages(loanId),
    enabled: !!loanId,
    refetchInterval: 5000, // Refrescar cada 5 segundos para simular tiempo real
  });

  return { messages, isLoading, error, refetch };
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
