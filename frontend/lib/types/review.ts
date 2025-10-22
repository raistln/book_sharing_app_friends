// Tipos para el sistema de reseñas

export interface Review {
  id: string;
  rating: number; // 1-5
  comment?: string;
  book_id: string;
  user_id: string;
  group_id?: string;
  created_at: string;
  updated_at?: string;
  
  // Datos enriquecidos (opcionales)
  book_title?: string;
  user_username?: string;
  group_name?: string;
}

export interface ReviewCreate {
  rating: number; // 1-5
  comment?: string;
  book_id: string;
  group_id?: string;
}

export interface ReviewUpdate {
  rating?: number; // 1-5
  comment?: string;
}

export interface ReviewFilters {
  book_id?: string;
  user_id?: string;
  group_id?: string;
  limit?: number;
  offset?: number;
}

export interface ReviewStats {
  total_reviews: number;
  average_rating: number;
  rating_distribution: {
    [key: number]: number; // { 1: 5, 2: 3, 3: 10, 4: 15, 5: 20 }
  };
}
