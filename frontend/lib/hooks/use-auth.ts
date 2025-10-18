import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/api/auth';
import { useAuthStore } from '@/lib/store/auth-store';
import { toast } from '@/components/ui/use-toast';
import type { LoginRequest, RegisterRequest } from '@/lib/types/api';

export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { setAuth, logout: logoutStore, user, isAuthenticated } = useAuthStore();

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: authApi.login,
    onSuccess: async (data) => {
      try {
        console.log('✅ Login exitoso, token recibido');
        
        // PRIMERO: Guardar el token en localStorage
        if (typeof window !== 'undefined') {
          localStorage.setItem('access_token', data.access_token);
          console.log('💾 Token guardado en localStorage');
        }
        
        // SEGUNDO: Obtener datos del usuario (ahora el token ya está disponible)
        console.log('📡 Obteniendo datos del usuario...');
        const userData = await authApi.getCurrentUser();
        console.log('✅ Datos del usuario obtenidos:', userData.username);
        
        // TERCERO: Actualizar el estado de Zustand
        setAuth(userData, data.access_token);

        // Verificar que el estado se guardó correctamente
        console.log('🔍 Verificando estado después del login:', {
          isAuthenticated: useAuthStore.getState().isAuthenticated,
          hasToken: !!useAuthStore.getState().token,
          hasUser: !!useAuthStore.getState().user
        });

        // Pequeña pausa para asegurar que el estado se actualice completamente
        await new Promise(resolve => setTimeout(resolve, 100));

        toast({
          title: '¡Bienvenido! 📚',
          description: `Hola ${userData.username}, ¡feliz lectura!`,
        });

        console.log('🔄 Redirigiendo a dashboard...');
        router.push('/dashboard');
      } catch (error) {
        console.error('❌ Error después del login:', error);
        toast({
          title: 'Error',
          description: 'No se pudo completar el inicio de sesión',
          variant: 'destructive',
        });
        // Limpiar el estado si hubo un error después del login
        logoutStore();
      }
    },
    onError: (error: any) => {
      console.error('❌ Error en login mutation:', error);
      toast({
        title: 'Error de autenticación',
        description: error.response?.data?.detail || 'Credenciales inválidas',
        variant: 'destructive',
      });
    },
  });

  // Register mutation
  const registerMutation = useMutation({
    mutationFn: authApi.register,
    onSuccess: async (userData) => {
      toast({
        title: '¡Cuenta creada! ✨',
        description: 'Ahora puedes iniciar sesión',
      });
      
      router.push('/login');
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail || 'Error al crear la cuenta';
      toast({
        title: 'Error de registro',
        description: errorMessage,
        variant: 'destructive',
      });
    },
  });

  // Get current user query - solo si está autenticado y tiene token
  const { data: currentUser, isLoading: isLoadingUser } = useQuery({
    queryKey: ['currentUser'],
    queryFn: authApi.getCurrentUser,
    enabled: isAuthenticated && !!user && typeof window !== 'undefined' && !!localStorage.getItem('access_token'),
    retry: (failureCount, error: any) => {
      // No reintentar si es error de autenticación (token inválido)
      if (error?.response?.status === 401) {
        return false;
      }
      // Reintentar hasta 2 veces para otros errores
      return failureCount < 2;
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
  });

  // Logout function
  const logout = () => {
    logoutStore();
    queryClient.clear();
    authApi.logout();
    toast({
      title: 'Sesión cerrada',
      description: '¡Hasta pronto! 👋',
    });
    router.push('/');
  };

  return {
    // State
    user: currentUser || user,
    isAuthenticated,
    isLoadingUser,

    // Mutations
    login: (data: LoginRequest) => loginMutation.mutate(data),
    register: (data: RegisterRequest) => registerMutation.mutate(data),
    logout,

    // Loading states
    isLoggingIn: loginMutation.isPending,
    isRegistering: registerMutation.isPending,

    // Error states
    loginError: loginMutation.error,
  };
}
