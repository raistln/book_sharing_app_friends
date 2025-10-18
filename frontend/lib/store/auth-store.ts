import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '@/lib/types/api';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      setAuth: (user, token) => {
        if (typeof window !== 'undefined') {
          localStorage.setItem('access_token', token);
        }
        set({ user, token, isAuthenticated: true });
      },
      logout: () => {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token');
        }
        set({ user: null, token: null, isAuthenticated: false });
      },
      updateUser: (user) => {
        set({ user });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        // Verificar que el token en localStorage coincida con el del store
        if (typeof window !== 'undefined' && state) {
          const storedToken = localStorage.getItem('access_token');
          if (storedToken && state.token && storedToken !== state.token) {
            // Sincronizar si hay diferencia
            state.token = storedToken;
          } else if (!storedToken && state.isAuthenticated) {
            // Si no hay token pero el estado dice que está autenticado, limpiar
            state.user = null;
            state.token = null;
            state.isAuthenticated = false;
          }
        }
      },
    }
  )
);
