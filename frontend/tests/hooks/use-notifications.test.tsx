import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import * as notificationsApi from '@/lib/api/notifications';
import { useNotifications, useUnreadNotifications, useMarkAsRead } from '@/lib/hooks/use-notifications';
import type { Notification } from '@/lib/types/notification';

vi.mock('@/components/ui/use-toast', () => ({
  toast: vi.fn(),
}));

const createWrapper = () => {
  const queryClient = new QueryClient();
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
  return { wrapper, queryClient };
};

const buildNotification = (overrides: Partial<Notification> = {}): Notification => ({
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

describe('useNotifications hooks', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('fetches notifications', async () => {
    vi.spyOn(notificationsApi.notificationsApi, 'getNotifications').mockResolvedValue([
      buildNotification(),
    ]);

    const { wrapper } = createWrapper();
    const { result } = renderHook(() => useNotifications(), { wrapper });

    await waitFor(() => {
      expect(result.current.notifications).toHaveLength(1);
    });
  });

  it('returns unread count', async () => {
    vi.spyOn(notificationsApi.notificationsApi, 'getNotifications').mockResolvedValue([
      {
        id: '1',
        type: 'NEW_MESSAGE',
        title: 'Nuevo mensaje',
        message: 'Hola desde el chat',
        created_at: new Date().toISOString(),
        is_read: false,
        data: {},
      },
    ]);

    const { wrapper } = createWrapper();
    const { result } = renderHook(() => useUnreadNotifications(), { wrapper });

    await waitFor(() => {
      expect(result.current.unreadCount).toBe(1);
    });
  });

  it('marks notification as read', async () => {
    const markAsReadMock = vi.spyOn(notificationsApi.notificationsApi, 'markAsRead').mockResolvedValue(buildNotification({ is_read: true }));
    vi.spyOn(notificationsApi.notificationsApi, 'getNotifications').mockResolvedValue([
      buildNotification(),
    ]);

    const { wrapper, queryClient } = createWrapper();
    const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');
    const { result } = renderHook(() => useMarkAsRead(), { wrapper });

    await act(async () => {
      await result.current.markAsRead('1');
    });

    expect(markAsReadMock).toHaveBeenCalledWith('1');
    expect(invalidateSpy).toHaveBeenCalled();
  });

  it('marks all notifications as read', async () => {
    const markAllMock = vi.spyOn(notificationsApi.notificationsApi, 'markAllAsRead').mockResolvedValue(1);
    vi.spyOn(notificationsApi.notificationsApi, 'getNotifications').mockResolvedValue([]);

    const { wrapper, queryClient } = createWrapper();
    const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');
    const { result } = renderHook(() => useMarkAsRead(), { wrapper });

    await act(async () => {
      await result.current.markAllAsRead();
    });

    expect(markAllMock).toHaveBeenCalled();
    expect(invalidateSpy).toHaveBeenCalled();
  });
});
