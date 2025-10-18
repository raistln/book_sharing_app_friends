import { apiClient } from './client';
import type { LoginRequest, RegisterRequest, AuthResponse, User } from '@/lib/types/api';

export const authApi = {
  // Login
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
    return response.data;
  },

  // Register
  async register(data: RegisterRequest): Promise<User> {
    const response = await apiClient.post<User>('/auth/register', data);
    return response.data;
  },

  // Get current user
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  // Update current user
  async updateCurrentUser(data: Partial<User>): Promise<User> {
    const response = await apiClient.put<User>('/auth/me', data);
    return response.data;
  },

  // Logout (client-side only, backend doesn't have logout endpoint)
  logout(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
    }
  },
};
