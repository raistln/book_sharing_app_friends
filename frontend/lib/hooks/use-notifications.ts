import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notificationsApi } from '@/lib/api/notifications';
import type { NotificationFilters } from '@/lib/types/notification';
import { requestNotificationPermission, createNotificationForType } from '@/lib/utils/notifications';
import { toast } from '@/components/ui/use-toast';

// Hook para obtener notificaciones del usuario
export function useNotifications(filters?: NotificationFilters) {
  const { data: notifications = [], isLoading, error, refetch } = useQuery({
    queryKey: ['notifications', filters],
    queryFn: () => notificationsApi.getNotifications(filters),
  });

  return { notifications, isLoading, error, refetch };
}

// Hook para obtener notificaciones no leídas
export function useUnreadNotifications() {
  const { notifications } = useNotifications({ is_read: false });
  return {
    unreadNotifications: notifications,
    unreadCount: notifications.length,
  };
}

// Hook para marcar notificación como leída
export function useMarkAsRead() {
  const queryClient = useQueryClient();

  const markAsReadMutation = useMutation({
    mutationFn: (notificationId: string) => notificationsApi.markAsRead(notificationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'No se pudo marcar como leída',
        variant: 'destructive',
      });
    },
  });

  const markAllAsReadMutation = useMutation({
    mutationFn: () => notificationsApi.markAllAsRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
      toast({
        title: 'Notificaciones marcadas',
        description: 'Todas las notificaciones han sido marcadas como leídas',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'No se pudieron marcar las notificaciones',
        variant: 'destructive',
      });
    },
  });

  return {
    markAsRead: (notificationId: string) => markAsReadMutation.mutate(notificationId),
    markAllAsRead: () => markAllAsReadMutation.mutate(),
  };
}

// Hook para solicitar permisos de notificaciones push
export function useNotificationPermission() {
  const [permission, setPermission] = useState<NotificationPermission>('default');

  useEffect(() => {
    if ('Notification' in window) {
      setPermission(Notification.permission);
    }
  }, []);

  const requestPermission = async () => {
    const granted = await requestNotificationPermission();
    setPermission(granted ? 'granted' : 'denied');
    return granted;
  };

  return { permission, requestPermission };
}
