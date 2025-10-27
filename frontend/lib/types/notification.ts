// Tipos de notificación
export type NotificationType = 
  | 'LOAN_REQUEST'        // Nueva solicitud de préstamo
  | 'LOAN_APPROVED'       // Préstamo aprobado
  | 'LOAN_REJECTED'       // Préstamo rechazado
  | 'LOAN_RETURNED'       // Libro devuelto
  | 'DUE_DATE_REMINDER'   // Recordatorio de fecha de devolución
  | 'OVERDUE'             // Préstamo vencido
  | 'NEW_MESSAGE'         // Nuevo mensaje en chat
  | 'GROUP_INVITATION'    // Invitación a grupo
  | 'GROUP_JOINED';       // Nuevo miembro en grupo

// Prioridad de la notificación
export type NotificationPriority = 'low' | 'medium' | 'high' | 'urgent';

// Notificación
export interface Notification {
  id: string;
  user_id: string;
  type: NotificationType;
  title: string;
  message: string;
  priority: NotificationPriority;
  is_read: boolean;
  created_at: string;
  read_at?: string;
  
  // Datos adicionales según el tipo
  data?: {
    loan_id?: string;
    book_id?: string;
    group_id?: string;
    group_name?: string;
    sender_id?: string;
    sender_name?: string;
    book_title?: string;
    due_date?: string;
    invitation_id?: string;
    invitation_code?: string;
    inviter_id?: string;
    inviter_name?: string;
    message?: string;
    message_preview?: string;
  };
}

// Crear notificación
export interface NotificationCreate {
  user_id: string;
  type: NotificationType;
  title: string;
  message: string;
  priority?: NotificationPriority;
  data?: Record<string, any>;
}

// Estadísticas de notificaciones
export interface NotificationStats {
  total: number;
  unread: number;
  by_type: Record<NotificationType, number>;
  by_priority: Record<NotificationPriority, number>;
}

// Filtros para notificaciones
export interface NotificationFilters {
  type?: NotificationType;
  priority?: NotificationPriority;
  is_read?: boolean;
  from_date?: string;
  to_date?: string;
}

// Configuración de notificaciones del usuario
export interface NotificationSettings {
  user_id: string;
  email_enabled: boolean;
  push_enabled: boolean;
  
  // Tipos de notificaciones habilitadas
  loan_requests: boolean;
  loan_updates: boolean;
  due_date_reminders: boolean;
  messages: boolean;
  group_updates: boolean;
  
  // Frecuencia de recordatorios (días antes)
  reminder_days_before: number;
}
