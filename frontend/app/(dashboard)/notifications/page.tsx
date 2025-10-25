'use client';

import { useState } from 'react';
import { useNotifications, useMarkAsRead, useNotificationPermission } from '@/lib/hooks/use-notifications';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Bell, BellOff, Check, CheckCheck, Filter, Loader2 } from 'lucide-react';
import { formatRelativeTime, notificationConfig, groupNotificationsByDate } from '@/lib/utils/notifications';
import type { NotificationType } from '@/lib/types/notification';

export default function NotificationsPage() {
  const { notifications, isLoading } = useNotifications();
  const { markAsRead, markAllAsRead } = useMarkAsRead();
  const { permission, requestPermission } = useNotificationPermission();
  const [filter, setFilter] = useState<'all' | 'unread'>('all');

  const filteredNotifications = filter === 'unread' 
    ? notifications.filter(n => !n.is_read)
    : notifications;

  const groupedNotifications = groupNotificationsByDate(filteredNotifications);
  const unreadCount = notifications.filter(n => !n.is_read).length;

  const getTypeLabel = (type: NotificationType) => {
    switch (type) {
      case 'LOAN_REQUEST':
        return 'Préstamo solicitado';
      case 'LOAN_APPROVED':
        return 'Préstamo aprobado';
      case 'LOAN_REJECTED':
        return 'Préstamo rechazado';
      case 'LOAN_RETURNED':
        return 'Libro devuelto';
      case 'DUE_DATE_REMINDER':
        return 'Recordatorio de devolución';
      case 'OVERDUE':
        return 'Préstamo vencido';
      case 'NEW_MESSAGE':
        return 'Mensaje recibido';
      case 'GROUP_INVITATION':
        return 'Invitación a grupo';
      case 'GROUP_JOINED':
        return 'Nuevo miembro en grupo';
      default:
        return type;
    }
  };

  const handleRequestPermission = async () => {
    await requestPermission();
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-storybook-leather" />
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4 max-w-4xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-storybook-ink mb-2">Notificaciones</h1>
        <p className="text-storybook-ink-light">
          Mantente al día con tus préstamos y actividades
        </p>
      </div>

      {/* Permiso de notificaciones push */}
      {permission !== 'granted' && (
        <Card className="mb-6 border-storybook-gold">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              Activa las notificaciones
            </CardTitle>
            <CardDescription>
              Recibe alertas en tiempo real sobre tus préstamos y mensajes
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={handleRequestPermission}>
              Activar notificaciones push
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total</CardTitle>
            <Bell className="h-4 w-4 text-storybook-leather" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{notifications.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">No leídas</CardTitle>
            <BellOff className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{unreadCount}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Leídas</CardTitle>
            <CheckCheck className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{notifications.length - unreadCount}</div>
          </CardContent>
        </Card>
      </div>

      {/* Acciones */}
      <div className="flex items-center justify-between mb-6">
        <Tabs value={filter} onValueChange={(v) => setFilter(v as 'all' | 'unread')}>
          <TabsList>
            <TabsTrigger value="all">Todas ({notifications.length})</TabsTrigger>
            <TabsTrigger value="unread">No leídas ({unreadCount})</TabsTrigger>
          </TabsList>
        </Tabs>

        {unreadCount > 0 && (
          <Button variant="outline" size="sm" onClick={markAllAsRead}>
            <CheckCheck className="h-4 w-4 mr-2" />
            Marcar todas como leídas
          </Button>
        )}
      </div>

      {/* Lista de notificaciones */}
      {filteredNotifications.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Bell className="h-12 w-12 text-storybook-ink-light opacity-30 mb-3" />
            <p className="text-storybook-ink-light">
              {filter === 'unread' ? 'No tienes notificaciones sin leer' : 'No tienes notificaciones'}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {/* Hoy */}
          {groupedNotifications.today.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-storybook-ink-light mb-3">Hoy</h3>
              <div className="space-y-2">
                {groupedNotifications.today.map((notification) => {
                  const config = notificationConfig[notification.type];
                  return (
                    <Card
                      key={notification.id}
                      className={`cursor-pointer transition-colors ${
                        !notification.is_read ? 'bg-storybook-parchment border-storybook-gold' : ''
                      }`}
                      onClick={() => markAsRead(notification.id)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start gap-3">
                          <span className="text-2xl flex-shrink-0">{config.icon}</span>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-start justify-between gap-2">
                              <h4 className="font-semibold text-storybook-ink">
                                {notification.title}
                              </h4>
                              {!notification.is_read && (
                                <Badge variant="outline" className="flex-shrink-0">
                                  Nueva
                                </Badge>
                              )}
                            </div>
                            <p className="text-sm text-storybook-ink-light mt-1">
                              {notification.message}
                            </p>
                            <div className="flex items-center gap-2 mt-2">
                              <span className="text-xs text-storybook-ink-light">
                                {formatRelativeTime(notification.created_at)}
                              </span>
                              <Badge className={config.color} variant="outline">
                                {getTypeLabel(notification.type)}
                              </Badge>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>
          )}

          {/* Ayer */}
          {groupedNotifications.yesterday.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-storybook-ink-light mb-3">Ayer</h3>
              <div className="space-y-2">
                {groupedNotifications.yesterday.map((notification) => {
                  const config = notificationConfig[notification.type];
                  return (
                    <Card
                      key={notification.id}
                      className={`cursor-pointer transition-colors ${
                        !notification.is_read ? 'bg-storybook-parchment border-storybook-gold' : ''
                      }`}
                      onClick={() => markAsRead(notification.id)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start gap-3">
                          <span className="text-2xl flex-shrink-0">{config.icon}</span>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-start justify-between gap-2">
                              <h4 className="font-semibold text-storybook-ink">
                                {notification.title}
                              </h4>
                              {!notification.is_read && (
                                <Badge variant="outline" className="flex-shrink-0">
                                  Nueva
                                </Badge>
                              )}
                            </div>
                            <p className="text-sm text-storybook-ink-light mt-1">
                              {notification.message}
                            </p>
                            <div className="flex items-center gap-2 mt-2">
                              <span className="text-xs text-storybook-ink-light">
                                {formatRelativeTime(notification.created_at)}
                              </span>
                              <Badge className={config.color} variant="outline">
                                {notification.type.replace('_', ' ')}
                              </Badge>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>
          )}

          {/* Esta semana */}
          {groupedNotifications.thisWeek.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-storybook-ink-light mb-3">Esta semana</h3>
              <div className="space-y-2">
                {groupedNotifications.thisWeek.map((notification) => {
                  const config = notificationConfig[notification.type];
                  return (
                    <Card
                      key={notification.id}
                      className={`cursor-pointer transition-colors ${
                        !notification.is_read ? 'bg-storybook-parchment border-storybook-gold' : ''
                      }`}
                      onClick={() => markAsRead(notification.id)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start gap-3">
                          <span className="text-2xl flex-shrink-0">{config.icon}</span>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-start justify-between gap-2">
                              <h4 className="font-semibold text-storybook-ink">
                                {notification.title}
                              </h4>
                              {!notification.is_read && (
                                <Badge variant="outline" className="flex-shrink-0">
                                  Nueva
                                </Badge>
                              )}
                            </div>
                            <p className="text-sm text-storybook-ink-light mt-1">
                              {notification.message}
                            </p>
                            <div className="flex items-center gap-2 mt-2">
                              <span className="text-xs text-storybook-ink-light">
                                {formatRelativeTime(notification.created_at)}
                              </span>
                              <Badge className={config.color} variant="outline">
                                {notification.type.replace('_', ' ')}
                              </Badge>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>
          )}

          {/* Anteriores */}
          {groupedNotifications.older.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-storybook-ink-light mb-3">Anteriores</h3>
              <div className="space-y-2">
                {groupedNotifications.older.map((notification) => {
                  const config = notificationConfig[notification.type];
                  return (
                    <Card
                      key={notification.id}
                      className="cursor-pointer transition-colors"
                      onClick={() => markAsRead(notification.id)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start gap-3">
                          <span className="text-2xl flex-shrink-0">{config.icon}</span>
                          <div className="flex-1 min-w-0">
                            <h4 className="font-semibold text-storybook-ink">
                              {notification.title}
                            </h4>
                            <p className="text-sm text-storybook-ink-light mt-1">
                              {notification.message}
                            </p>
                            <div className="flex items-center gap-2 mt-2">
                              <span className="text-xs text-storybook-ink-light">
                                {formatRelativeTime(notification.created_at)}
                              </span>
                              <Badge className={config.color} variant="outline">
                                {notification.type.replace('_', ' ')}
                              </Badge>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
