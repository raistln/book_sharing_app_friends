import { apiClient } from './client';
import type { UserProfile, UpdateProfile, ChangePassword, UserStats } from '@/lib/types/profile';

export const profileApi = {
  // Obtener perfil del usuario actual
  async getMyProfile(): Promise<UserProfile> {
    const response = await apiClient.get<UserProfile>('/users/me');
    return response.data;
  },

  // Obtener perfil de otro usuario
  async getUserProfile(userId: string): Promise<UserProfile> {
    const response = await apiClient.get<UserProfile>(`/users/${userId}`);
    return response.data;
  },

  // Actualizar perfil
  async updateProfile(data: UpdateProfile): Promise<UserProfile> {
    const response = await apiClient.put<UserProfile>('/users/me', data);
    return response.data;
  },

  // Cambiar contraseña
  async changePassword(data: ChangePassword): Promise<void> {
    await apiClient.post('/users/me/change-password', data);
  },

  // Obtener estadísticas del usuario
  async getMyStats(): Promise<UserStats> {
    const response = await apiClient.get<UserStats>('/users/me/stats');
    return response.data;
  },

  // Subir avatar
  async uploadAvatar(file: File): Promise<{ avatar_url: string }> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post<{ avatar_url: string }>(
      '/users/me/avatar',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  // Eliminar avatar
  async deleteAvatar(): Promise<void> {
    await apiClient.delete('/users/me/avatar');
  },
};
