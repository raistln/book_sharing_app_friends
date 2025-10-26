import { apiClient } from './client';
import type { Message, MessageCreate } from '@/lib/types/chat';

export const chatApi = {
  // Enviar mensaje
  async sendMessage(data: MessageCreate): Promise<Message> {
    const response = await apiClient.post<Message>('/chat/send', data);
    return response.data;
  },

  // Obtener mensajes de un préstamo
  async getMessages(loanId: string, since?: string): Promise<Message[]> {
    const params = since ? { since } : {};
    const response = await apiClient.get<Message[]>(`/chat/loan/${loanId}`, { params });
    return response.data;
  },
};
