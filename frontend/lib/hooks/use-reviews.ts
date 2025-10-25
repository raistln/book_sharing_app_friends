/**
 * Hooks personalizados para reviews usando React Query
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  listReviews, 
  getMyReviews, 
  getReview, 
  createReview, 
  updateReview, 
  deleteReview,
  getBookReviews,
  calculateReviewStats
} from '../api/reviews';
import type { ReviewCreate, ReviewUpdate, ReviewFilters } from '../types/review';
import { toast } from '@/components/ui/use-toast';

// Query keys
export const reviewKeys = {
  all: ['reviews'] as const,
  lists: () => [...reviewKeys.all, 'list'] as const,
  list: (filters?: ReviewFilters) => [...reviewKeys.lists(), filters] as const,
  myReviews: () => [...reviewKeys.all, 'my-reviews'] as const,
  details: () => [...reviewKeys.all, 'detail'] as const,
  detail: (id: string) => [...reviewKeys.details(), id] as const,
  bookReviews: (bookId: string) => [...reviewKeys.all, 'book', bookId] as const,
};

/**
 * Hook para listar reseñas con filtros
 */
export function useReviews(filters?: ReviewFilters) {
  return useQuery({
    queryKey: reviewKeys.list(filters),
    queryFn: () => listReviews(filters),
  });
}

/**
 * Hook para obtener mis reseñas
 */
export function useMyReviews() {
  return useQuery({
    queryKey: reviewKeys.myReviews(),
    queryFn: getMyReviews,
  });
}

/**
 * Hook para obtener una reseña específica
 */
export function useReview(reviewId: string) {
  return useQuery({
    queryKey: reviewKeys.detail(reviewId),
    queryFn: () => getReview(reviewId),
    enabled: !!reviewId,
  });
}

/**
 * Hook para obtener reseñas de un libro
 */
export function useBookReviews(bookId: string) {
  const query = useQuery({
    queryKey: reviewKeys.bookReviews(bookId),
    queryFn: () => getBookReviews(bookId),
    enabled: !!bookId,
  });

  const stats = query.data ? calculateReviewStats(query.data) : null;

  return {
    ...query,
    stats,
  };
}

/**
 * Hook para crear una reseña
 */
export function useCreateReview() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ReviewCreate) => createReview(data),
    onSuccess: (newReview) => {
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({ queryKey: reviewKeys.lists() });
      queryClient.invalidateQueries({ queryKey: reviewKeys.myReviews() });
      queryClient.invalidateQueries({ queryKey: reviewKeys.bookReviews(newReview.book_id) });
      
      toast({
        title: 'Éxito',
        description: 'Reseña creada exitosamente',
      });
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Error al crear la reseña';
      toast({
        title: 'Error',
        description: message,
        variant: 'destructive',
      });
    },
  });
}

/**
 * Hook para actualizar una reseña
 */
export function useUpdateReview() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ reviewId, data }: { reviewId: string; data: ReviewUpdate }) =>
      updateReview(reviewId, data),
    onSuccess: (updatedReview) => {
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({ queryKey: reviewKeys.lists() });
      queryClient.invalidateQueries({ queryKey: reviewKeys.myReviews() });
      queryClient.invalidateQueries({ queryKey: reviewKeys.detail(updatedReview.id) });
      queryClient.invalidateQueries({ queryKey: reviewKeys.bookReviews(updatedReview.book_id) });
      
      toast({
        title: 'Éxito',
        description: 'Reseña actualizada exitosamente',
      });
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Error al actualizar la reseña';
      toast({
        title: 'Error',
        description: message,
        variant: 'destructive',
      });
    },
  });
}

/**
 * Hook para eliminar una reseña
 */
export function useDeleteReview() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (reviewId: string) => deleteReview(reviewId),
    onSuccess: () => {
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({ queryKey: reviewKeys.all });
      
      toast({
        title: 'Éxito',
        description: 'Reseña eliminada exitosamente',
      });
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Error al eliminar la reseña';
      toast({
        title: 'Error',
        description: message,
        variant: 'destructive',
      });
    },
  });
}
