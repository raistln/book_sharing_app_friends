import { describe, it, expect } from 'vitest';
import { formatRelativeTime } from '@/lib/utils/notifications';

describe('formatRelativeTime', () => {
  it('formatea tiempo hace menos de 1 minuto', () => {
    const now = new Date();
    const result = formatRelativeTime(now.toISOString());
    expect(result).toBe('Ahora');
  });

  it('formatea tiempo hace varios minutos', () => {
    const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
    const result = formatRelativeTime(fiveMinutesAgo.toISOString());
    expect(result).toBe('Hace 5 min');
  });

  it('formatea tiempo hace una hora', () => {
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
    const result = formatRelativeTime(oneHourAgo.toISOString());
    expect(result).toBe('Hace 1h');
  });

  it('formatea tiempo hace varios días', () => {
    const threeDaysAgo = new Date(Date.now() - 3 * 24 * 60 * 60 * 1000);
    const result = formatRelativeTime(threeDaysAgo.toISOString());
    expect(result).toBe('Hace 3d');
  });
});
