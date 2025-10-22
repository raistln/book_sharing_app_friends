import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { profileApi } from '@/lib/api/profile';
import { toast } from '@/components/ui/use-toast';
import type { UpdateProfile, ChangePassword } from '@/lib/types/profile';

// Hook para obtener el perfil del usuario actual
export function useMyProfile() {
  const { data: profile, isLoading, error } = useQuery({
    queryKey: ['myProfile'],
    queryFn: profileApi.getMyProfile,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });

  return { profile, isLoading, error };
}

// Hook para obtener perfil de otro usuario
export function useUserProfile(userId: string) {
  const { data: profile, isLoading, error } = useQuery({
    queryKey: ['userProfile', userId],
    queryFn: () => profileApi.getUserProfile(userId),
    enabled: !!userId,
  });

  return { profile, isLoading, error };
}

// Hook para obtener estadísticas
export function useMyStats() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['myStats'],
    queryFn: profileApi.getMyStats,
  });

  return { stats, isLoading, error };
}

// Hook para actualizar perfil
export function useUpdateProfile() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: profileApi.updateProfile,
    onSuccess: (updatedProfile) => {
      queryClient.invalidateQueries({ queryKey: ['myProfile'] });
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      toast({
        title: 'Perfil actualizado ✨',
        description: 'Tus cambios se han guardado correctamente',
      });
      router.push('/profile');
    },
    onError: (error: any) => {
      toast({
        title: 'Error al actualizar',
        description: error.response?.data?.detail || 'No se pudo actualizar el perfil',
        variant: 'destructive',
      });
    },
  });
}

// Hook para cambiar contraseña
export function useChangePassword() {
  return useMutation({
    mutationFn: profileApi.changePassword,
    onSuccess: () => {
      toast({
        title: 'Contraseña actualizada 🔒',
        description: 'Tu contraseña ha sido cambiada exitosamente',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al cambiar contraseña',
        description: error.response?.data?.detail || 'No se pudo cambiar la contraseña',
        variant: 'destructive',
      });
    },
  });
}

// Hook para subir avatar
export function useUploadAvatar() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: profileApi.uploadAvatar,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myProfile'] });
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      toast({
        title: 'Avatar actualizado 📸',
        description: 'Tu foto de perfil ha sido actualizada',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al subir imagen',
        description: error.response?.data?.detail || 'No se pudo subir la imagen',
        variant: 'destructive',
      });
    },
  });
}

// Hook para eliminar avatar
export function useDeleteAvatar() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: profileApi.deleteAvatar,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myProfile'] });
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      toast({
        title: 'Avatar eliminado',
        description: 'Tu foto de perfil ha sido eliminada',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al eliminar',
        description: error.response?.data?.detail || 'No se pudo eliminar la imagen',
        variant: 'destructive',
      });
    },
  });
}
