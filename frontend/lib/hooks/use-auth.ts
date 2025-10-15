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
      // Get user data
      try {
        const userData = await authApi.getCurrentUser();
        setAuth(userData, data.access_token);
        
        toast({
          title: '¡Bienvenido! 📚',
          description: `Hola ${userData.username}, ¡feliz lectura!`,
        });
        
        router.push('/dashboard');
      } catch (error) {
        toast({
          title: 'Error',
          description: 'No se pudo obtener la información del usuario',
          variant: 'destructive',
        });
      }
    },
    onError: (error: any) => {
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

  // Get current user query
  const { data: currentUser, isLoading: isLoadingUser } = useQuery({
    queryKey: ['currentUser'],
    queryFn: authApi.getCurrentUser,
    enabled: isAuthenticated && !!user,
    retry: false,
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
  };
}
