import React from 'react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { NotificationBell } from '@/components/notifications/notification-bell';
import * as notificationsHook from '@/lib/hooks/use-notifications';
import type { Notification } from '@/lib/types/notification';

vi.mock('@/lib/hooks/use-notifications', () => ({
  useNotifications: vi.fn(),
  useUnreadNotifications: vi.fn(),
  useMarkAsRead: vi.fn(),
}));

vi.mock('@radix-ui/react-dropdown-menu', async () => {
  const actual = await vi.importActual<typeof import('@radix-ui/react-dropdown-menu')>(
    '@radix-ui/react-dropdown-menu'
  );

  return {
    ...actual,
    DropdownMenu: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
    DropdownMenuTrigger: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
    DropdownMenuContent: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  };
});

const createWrapper = (ui: React.ReactElement) => {
  const queryClient = new QueryClient();
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
};

describe('NotificationBell', () => {
  const mockedHooks = vi.mocked(notificationsHook);

  const baseNotification = (overrides: Partial<Notification> = {}): Notification => ({
    id: '1',
    user_id: 'user-1',
    type: 'NEW_MESSAGE',
    title: 'Nuevo mensaje',
    message: 'Hola desde el chat',
    priority: 'medium',
    is_read: false,
    created_at: new Date().toISOString(),
    data: {},
    ...overrides,
  });

  beforeEach(() => {
    mockedHooks.useUnreadNotifications.mockReturnValue({ unreadNotifications: [], unreadCount: 0 });

    mockedHooks.useNotifications.mockReturnValue({
      notifications: [],
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    mockedHooks.useMarkAsRead.mockReturnValue({
      markAsRead: vi.fn(),
      markAllAsRead: vi.fn(),
    });
  });

  it('muestra el contador de notificaciones no leídas', () => {
    mockedHooks.useUnreadNotifications.mockReturnValue({
      unreadNotifications: [baseNotification()],
      unreadCount: 5,
    });
    mockedHooks.useNotifications.mockReturnValue({
      notifications: [baseNotification()],
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    createWrapper(<NotificationBell />);

    expect(screen.getByText('5')).toBeInTheDocument();
  });

  it('abre el dropdown y muestra notificaciones', async () => {
    mockedHooks.useNotifications.mockReturnValue({
      notifications: [baseNotification()],
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    const user = userEvent.setup();
    createWrapper(<NotificationBell />);

    await user.click(screen.getByRole('button'));

    await waitFor(() => {
      expect(screen.getByText('Nuevo mensaje')).toBeInTheDocument();
    });
  });

  it('marca todas las notificaciones como leídas', async () => {
    const markAll = vi.fn();
    mockedHooks.useNotifications.mockReturnValue({
      notifications: [baseNotification()],
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });
    mockedHooks.useUnreadNotifications.mockReturnValue({
      unreadNotifications: [baseNotification()],
      unreadCount: 1,
    });
    mockedHooks.useMarkAsRead.mockReturnValue({ markAsRead: vi.fn(), markAllAsRead: markAll });

    const user = userEvent.setup();
    createWrapper(<NotificationBell />);
    await user.click(screen.getByRole('button'));
    const markAllButton = await screen.findByText('Marcar todas');
    await user.click(markAllButton);

    expect(markAll).toHaveBeenCalled();
  });
});
