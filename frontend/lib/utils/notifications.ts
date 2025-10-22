import type { NotificationType, NotificationPriority } from '@/lib/types/notification';

// Configuración de iconos y colores por tipo
export const notificationConfig: Record<
  NotificationType,
  { icon: string; color: string; priority: NotificationPriority }
> = {
  LOAN_REQUEST: {
    icon: '📚',
    color: 'bg-blue-100 text-blue-800',
    priority: 'high',
  },
  LOAN_APPROVED: {
    icon: '✅',
    color: 'bg-green-100 text-green-800',
    priority: 'high',
  },
  LOAN_REJECTED: {
    icon: '❌',
    color: 'bg-red-100 text-red-800',
    priority: 'medium',
  },
  LOAN_RETURNED: {
    icon: '📖',
    color: 'bg-gray-100 text-gray-800',
    priority: 'medium',
  },
  DUE_DATE_REMINDER: {
    icon: '⏰',
    color: 'bg-yellow-100 text-yellow-800',
    priority: 'medium',
  },
  OVERDUE: {
    icon: '⚠️',
    color: 'bg-red-100 text-red-800',
    priority: 'urgent',
  },
  NEW_MESSAGE: {
    icon: '💬',
    color: 'bg-purple-100 text-purple-800',
    priority: 'low',
  },
  GROUP_INVITATION: {
    icon: '👥',
    color: 'bg-indigo-100 text-indigo-800',
    priority: 'medium',
  },
  GROUP_JOINED: {
    icon: '🎉',
    color: 'bg-green-100 text-green-800',
    priority: 'low',
  },
};

// Solicitar permiso para notificaciones push
export async function requestNotificationPermission(): Promise<boolean> {
  if (!('Notification' in window)) {
    console.warn('Este navegador no soporta notificaciones');
    return false;
  }

  if (Notification.permission === 'granted') {
    return true;
  }

  if (Notification.permission !== 'denied') {
    const permission = await Notification.requestPermission();
    return permission === 'granted';
  }

  return false;
}

// Mostrar notificación push del navegador
export function showBrowserNotification(
  title: string,
  options?: NotificationOptions
): void {
  if (Notification.permission === 'granted') {
    new Notification(title, {
      icon: '/icon-192x192.png',
      badge: '/icon-192x192.png',
      ...options,
    });
  }
}

// Crear notificación push para un tipo específico
export function createNotificationForType(
  type: NotificationType,
  data: {
    title: string;
    message: string;
    bookTitle?: string;
    senderName?: string;
  }
): void {
  const config = notificationConfig[type];
  
  showBrowserNotification(data.title, {
    body: data.message,
    icon: '/icon-192x192.png',
    badge: '/icon-192x192.png',
    tag: type,
    requireInteraction: config.priority === 'urgent',
  });
}

// Formatear fecha relativa
export function formatRelativeTime(date: string): string {
  const now = new Date();
  const then = new Date(date);
  const diffMs = now.getTime() - then.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Ahora';
  if (diffMins < 60) return `Hace ${diffMins} min`;
  if (diffHours < 24) return `Hace ${diffHours}h`;
  if (diffDays < 7) return `Hace ${diffDays}d`;
  
  return then.toLocaleDateString('es-ES', {
    day: 'numeric',
    month: 'short',
  });
}

// Agrupar notificaciones por fecha
export function groupNotificationsByDate<T extends { created_at: string }>(
  notifications: T[]
): Record<string, T[]> {
  const groups: Record<string, T[]> = {
    today: [],
    yesterday: [],
    thisWeek: [],
    older: [],
  };

  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  const weekAgo = new Date(today);
  weekAgo.setDate(weekAgo.getDate() - 7);

  notifications.forEach((notification) => {
    const date = new Date(notification.created_at);
    
    if (date >= today) {
      groups.today.push(notification);
    } else if (date >= yesterday) {
      groups.yesterday.push(notification);
    } else if (date >= weekAgo) {
      groups.thisWeek.push(notification);
    } else {
      groups.older.push(notification);
    }
  });

  return groups;
}
