import { apiClient } from './client';
import type {
  Notification,
  NotificationFilters,
  NotificationStats,
} from '@/lib/types/notification';

export const notificationsApi = {
  // Obtener notificaciones del usuario
  async getNotifications(filters?: NotificationFilters): Promise<Notification[]> {
    const params: Record<string, any> = {};
    
    if (filters?.type) params.notification_type = filters.type;
    if (filters?.is_read !== undefined) params.is_read = filters.is_read;
    if (filters?.from_date) params.from_date = filters.from_date;
    if (filters?.to_date) params.to_date = filters.to_date;
    
    const response = await apiClient.get<Notification[]>('/notifications/', { params });
    return response.data;
  },

  // Obtener cantidad de notificaciones no leídas
  async getUnreadCount(): Promise<number> {
    const response = await apiClient.get<{ unread_count: number }>('/notifications/unread/count');
    return response.data.unread_count;
  },

  // Obtener estadísticas
  async getStats(): Promise<NotificationStats> {
    const response = await apiClient.get<NotificationStats>('/notifications/stats');
    return response.data;
  },

  // Obtener una notificación específica
  async getNotification(notificationId: string): Promise<Notification> {
    const response = await apiClient.get<Notification>(`/notifications/${notificationId}`);
    return response.data;
  },

  // Marcar como leída
  async markAsRead(notificationId: string): Promise<Notification> {
    const response = await apiClient.patch<Notification>(`/notifications/${notificationId}/read`);
    return response.data;
  },

  // Marcar todas como leídas
  async markAllAsRead(): Promise<number> {
    const response = await apiClient.post<{ marked_as_read: number }>('/notifications/read-all');
    return response.data.marked_as_read;
  },

  // Eliminar notificación
  async deleteNotification(notificationId: string): Promise<void> {
    await apiClient.delete(`/notifications/${notificationId}`);
  },
};
