// Perfil de usuario extendido
export interface UserProfile {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  bio?: string;
  location?: string;
  avatar_url?: string;
  created_at: string;
  is_active: boolean;
  
  // Estadísticas
  stats?: {
    books_owned: number;
    books_borrowed: number;
    books_lent: number;
    groups_count: number;
    reviews_count: number;
  };
}

// Actualizar perfil
export interface UpdateProfile {
  full_name?: string;
  bio?: string;
  location?: string;
}

// Cambiar contraseña
export interface ChangePassword {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

// Estadísticas de usuario
export interface UserStats {
  books_owned: number;
  books_borrowed: number;
  books_lent: number;
  active_loans: number;
  groups_count: number;
  reviews_count: number;
  average_rating?: number;
}
