import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Interceptor para añadir token de autenticación
apiClient.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    console.error('❌ Error en interceptor de request:', error);
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const url = error.config?.url || '';
      // No redirigir si es login, register o cualquier endpoint de auth público
      const isAuthEndpoint = url.includes('/auth/login') || 
                            url.includes('/auth/register') ||
                            url.includes('/auth/verify');
      
      if (!isAuthEndpoint) {
        // Token expirado o inválido en otras operaciones
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token');
          // Solo redirigir si no estamos ya en login o register
          const currentPath = window.location.pathname;
          if (currentPath !== '/login' && currentPath !== '/register') {
            window.location.href = '/login';
          }
        }
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
