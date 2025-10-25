/**
 * API client para reviews (reseñas)
 */
import { apiClient } from './client';
import type { Review, ReviewCreate, ReviewUpdate, ReviewFilters } from '../types/review';

const BASE_URL = '/reviews';

/**
 * Listar reseñas con filtros opcionales
 */
export async function listReviews(filters?: ReviewFilters): Promise<Review[]> {
  const params = new URLSearchParams();
  
  if (filters?.book_id) params.append('book_id', filters.book_id);
  if (filters?.user_id) params.append('user_id', filters.user_id);
  if (filters?.group_id) params.append('group_id', filters.group_id);
  if (filters?.limit) params.append('limit', filters.limit.toString());
  if (filters?.offset) params.append('offset', filters.offset.toString());
  
  const response = await apiClient.get<Review[]>(`${BASE_URL}/?${params.toString()}`);
  return response.data;
}

/**
 * Obtener mis reseñas
 */
export async function getMyReviews(): Promise<Review[]> {
  const response = await apiClient.get<Review[]>(`${BASE_URL}/my-reviews`);
  return response.data;
}

/**
 * Obtener una reseña por ID
 */
export async function getReview(reviewId: string): Promise<Review> {
  const response = await apiClient.get<Review>(`${BASE_URL}/${reviewId}`);
  return response.data;
}

/**
 * Crear una nueva reseña
 */
export async function createReview(data: ReviewCreate): Promise<Review> {
  const response = await apiClient.post<Review>(BASE_URL, data);
  return response.data;
}

/**
 * Actualizar una reseña existente
 */
export async function updateReview(reviewId: string, data: ReviewUpdate): Promise<Review> {
  const response = await apiClient.put<Review>(`${BASE_URL}/${reviewId}`, data);
  return response.data;
}

/**
 * Eliminar una reseña
 */
export async function deleteReview(reviewId: string): Promise<void> {
  await apiClient.delete(`${BASE_URL}/${reviewId}`);
}

/**
 * Obtener reseñas de un libro específico
 */
export async function getBookReviews(bookId: string): Promise<Review[]> {
  return listReviews({ book_id: bookId });
}

/**
 * Calcular estadísticas de reseñas
 */
export function calculateReviewStats(reviews: Review[]) {
  if (reviews.length === 0) {
    return {
      total_reviews: 0,
      average_rating: 0,
      rating_distribution: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 }
    };
  }

  const rating_distribution = reviews.reduce((acc, review) => {
    acc[review.rating] = (acc[review.rating] || 0) + 1;
    return acc;
  }, {} as { [key: number]: number });

  const average_rating = reviews.reduce((sum, review) => sum + review.rating, 0) / reviews.length;

  return {
    total_reviews: reviews.length,
    average_rating: Math.round(average_rating * 10) / 10, // Redondear a 1 decimal
    rating_distribution
  };
}
