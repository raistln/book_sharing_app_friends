'use client';

import { useState } from 'react';
import { useNotifications, useUnreadNotifications, useMarkAsRead } from '@/lib/hooks/use-notifications';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { Bell, Check, CheckCheck, Copy } from 'lucide-react';
import { formatRelativeTime, notificationConfig } from '@/lib/utils/notifications';
import { toast } from '@/components/ui/use-toast';
import Link from 'next/link';

export function NotificationBell() {
  const { unreadCount } = useUnreadNotifications();
  const { notifications } = useNotifications();
  const { markAsRead, markAllAsRead } = useMarkAsRead();
  const [open, setOpen] = useState(false);

  const recentNotifications = notifications.slice(0, 5);

  const handleMarkAsRead = async (id: string) => {
    await markAsRead(id);
  };

  const handleMarkAllAsRead = async () => {
    await markAllAsRead();
  };

  const handleCopyCode = async (code: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await navigator.clipboard.writeText(code);
      toast({
        title: 'Código copiado',
        description: 'El código de invitación se ha copiado al portapapeles',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'No se pudo copiar el código',
        variant: 'destructive',
      });
    }
  };

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="relative rounded-full hover:bg-storybook-leather-dark"
        >
          <Bell className="h-5 w-5 text-storybook-cream" />
          {unreadCount > 0 && (
            <Badge
              className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 bg-red-500 text-white text-xs"
            >
              {unreadCount > 9 ? '9+' : unreadCount}
            </Badge>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80">
        <DropdownMenuLabel className="flex items-center justify-between">
          <span>Notificaciones</span>
          {unreadCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleMarkAllAsRead}
              className="h-auto p-1 text-xs"
            >
              <CheckCheck className="h-3 w-3 mr-1" />
              Marcar todas
            </Button>
          )}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />

        {recentNotifications.length === 0 ? (
          <div className="py-8 text-center text-sm text-storybook-ink-light">
            No tienes notificaciones
          </div>
        ) : (
          <div className="max-h-[400px] overflow-y-auto">
            {recentNotifications.map((notification) => {
              const config = notificationConfig[notification.type];
              return (
                <DropdownMenuItem
                  key={notification.id}
                  className={`flex flex-col items-start p-3 cursor-pointer ${
                    !notification.is_read ? 'bg-storybook-parchment' : ''
                  }`}
                  onClick={() => handleMarkAsRead(notification.id)}
                >
                  <div className="flex items-start gap-2 w-full">
                    <span className="text-xl flex-shrink-0">{config.icon}</span>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm text-storybook-ink">
                        {notification.title}
                      </p>
                      <p className="text-xs text-storybook-ink-light mt-1 line-clamp-2">
                        {notification.message}
                      </p>
                      
                      {/* Mostrar código de invitación si existe */}
                      {notification.type === 'GROUP_INVITATION' && notification.data?.invitation_code && (
                        <div className="mt-2 flex items-center gap-2 p-2 bg-storybook-cream rounded border border-storybook-gold-light">
                          <code className="text-xs font-mono text-storybook-leather flex-1">
                            {notification.data.invitation_code}
                          </code>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-6 w-6 p-0"
                            onClick={(e) => handleCopyCode(notification.data?.invitation_code || '', e)}
                          >
                            <Copy className="h-3 w-3" />
                          </Button>
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs text-storybook-ink-light">
                          {formatRelativeTime(notification.created_at)}
                        </span>
                        {!notification.is_read && (
                          <Badge variant="outline" className="text-xs">
                            Nueva
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                </DropdownMenuItem>
              );
            })}
          </div>
        )}

        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <Link
            href="/notifications"
            className="w-full text-center text-sm text-storybook-leather font-medium"
          >
            Ver todas las notificaciones
          </Link>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
