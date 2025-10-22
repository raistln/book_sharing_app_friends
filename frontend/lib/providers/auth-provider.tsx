'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/lib/store/auth-store';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isHydrated, setIsHydrated] = useState(false);

  useEffect(() => {
    // Esperar a que Zustand se hidrate desde localStorage
    const unsubscribe = useAuthStore.persist.onFinishHydration(() => {
      console.log('🔄 Zustand hydrated');
      setIsHydrated(true);
    });

    // Si ya está hidratado, marcarlo inmediatamente
    if (useAuthStore.persist.hasHydrated()) {
      console.log('✅ Zustand already hydrated');
      setIsHydrated(true);
    }

    return unsubscribe;
  }, []);

  // Mostrar un loader mínimo mientras se hidrata
  if (!isHydrated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-storybook-parchment via-storybook-cream to-storybook-gold-light flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-storybook-leather"></div>
      </div>
    );
  }

  return <>{children}</>;
}
