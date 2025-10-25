'use client';

import { useState } from 'react';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ReviewCard } from './review-card';
import { ReviewForm } from './review-form';
import { ReviewStats } from './review-stats';
import { useBookReviews, useCreateReview, useUpdateReview, useDeleteReview } from '@/lib/hooks/use-reviews';
import { useAuthStore } from '@/lib/store/auth-store';
import type { Review, ReviewCreate, ReviewUpdate } from '@/lib/types/review';

interface BookReviewsSectionProps {
  bookId: string;
}

export function BookReviewsSection({ bookId }: BookReviewsSectionProps) {
  const { user } = useAuthStore();
  const { data: reviews = [], stats, isLoading, error } = useBookReviews(bookId);
  const createReview = useCreateReview();
  const updateReview = useUpdateReview();
  const deleteReview = useDeleteReview();

  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingReview, setEditingReview] = useState<Review | null>(null);

  // Verificar si el usuario ya ha reseñado este libro
  const userReview = reviews.find((r) => r.user_id === user?.id);
  const hasReviewed = !!userReview;

  const handleCreateReview = async (data: ReviewCreate) => {
    await createReview.mutateAsync(data);
    setIsDialogOpen(false);
  };

  const handleUpdateReview = async (data: ReviewUpdate) => {
    if (!editingReview) return;
    await updateReview.mutateAsync({ reviewId: editingReview.id, data });
    setEditingReview(null);
    setIsDialogOpen(false);
  };

  const handleDeleteReview = async (reviewId: string) => {
    if (!confirm('¿Estás seguro de que quieres eliminar esta reseña?')) return;
    await deleteReview.mutateAsync(reviewId);
  };

  const handleEditClick = (review: Review) => {
    setEditingReview(review);
    setIsDialogOpen(true);
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Reseñas</h2>
        <p className="text-muted-foreground">Cargando reseñas...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Reseñas</h2>
        <Alert variant="destructive">
          <AlertDescription>
            Error al cargar las reseñas. Por favor, intenta de nuevo.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Reseñas</h2>
        
        {user && !hasReviewed && (
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={() => setEditingReview(null)}>
                <Plus className="h-4 w-4 mr-2" />
                Escribir reseña
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>
                  {editingReview ? 'Editar reseña' : 'Escribir reseña'}
                </DialogTitle>
              </DialogHeader>
              <ReviewForm
                bookId={bookId}
                initialData={editingReview ? {
                  rating: editingReview.rating,
                  comment: editingReview.comment
                } : undefined}
                onSubmit={editingReview ? handleUpdateReview : handleCreateReview}
                onCancel={() => {
                  setIsDialogOpen(false);
                  setEditingReview(null);
                }}
                isLoading={createReview.isPending || updateReview.isPending}
                isEdit={!!editingReview}
              />
            </DialogContent>
          </Dialog>
        )}
      </div>

      {/* Stats */}
      {stats && (
        <ReviewStats
          totalReviews={stats.total_reviews}
          averageRating={stats.average_rating}
          ratingDistribution={stats.rating_distribution}
        />
      )}

      {/* Reviews list */}
      {reviews.length > 0 ? (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">
            Todas las reseñas ({reviews.length})
          </h3>
          <div className="space-y-3">
            {reviews.map((review) => (
              <ReviewCard
                key={review.id}
                review={review}
                currentUserId={user?.id}
                onEdit={handleEditClick}
                onDelete={handleDeleteReview}
              />
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-muted-foreground">
          <p>Aún no hay reseñas para este libro.</p>
          {user && (
            <p className="mt-2">¡Sé el primero en escribir una!</p>
          )}
        </div>
      )}
    </div>
  );
}
