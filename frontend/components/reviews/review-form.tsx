'use client';

import { useState } from 'react';
import { Star } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { ReviewCreate, ReviewUpdate } from '@/lib/types/review';

interface ReviewFormProps {
  bookId?: string;
  initialData?: { rating: number; comment?: string };
  onSubmit: ((data: ReviewCreate) => void) | ((data: ReviewUpdate) => void);
  onCancel?: () => void;
  isLoading?: boolean;
  isEdit?: boolean;
}

export function ReviewForm({ 
  bookId, 
  initialData, 
  onSubmit, 
  onCancel, 
  isLoading = false,
  isEdit = false 
}: ReviewFormProps) {
  const [rating, setRating] = useState(initialData?.rating || 0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [comment, setComment] = useState(initialData?.comment || '');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (rating === 0) {
      return; // No permitir enviar sin rating
    }

    if (isEdit) {
      (onSubmit as (data: ReviewUpdate) => void)({ 
        rating, 
        comment: comment.trim() || undefined 
      });
    } else {
      if (!bookId) return;
      (onSubmit as (data: ReviewCreate) => void)({ 
        book_id: bookId, 
        rating, 
        comment: comment.trim() || undefined 
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Rating selector */}
      <div className="space-y-2">
        <Label>Calificación *</Label>
        <div className="flex items-center gap-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              onClick={() => setRating(star)}
              onMouseEnter={() => setHoveredRating(star)}
              onMouseLeave={() => setHoveredRating(0)}
              className="focus:outline-none transition-transform hover:scale-110"
            >
              <Star
                className={`h-8 w-8 ${
                  star <= (hoveredRating || rating)
                    ? 'fill-yellow-400 text-yellow-400'
                    : 'text-gray-300'
                }`}
              />
            </button>
          ))}
          {rating > 0 && (
            <span className="ml-2 text-sm text-muted-foreground">
              {rating} de 5 estrellas
            </span>
          )}
        </div>
      </div>

      {/* Comment */}
      <div className="space-y-2">
        <Label htmlFor="comment">Comentario (opcional)</Label>
        <Textarea
          id="comment"
          placeholder="Comparte tu opinión sobre este libro..."
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          rows={4}
          maxLength={500}
        />
        <p className="text-xs text-muted-foreground text-right">
          {comment.length}/500 caracteres
        </p>
      </div>

      {/* Actions */}
      <div className="flex gap-2 justify-end">
        {onCancel && (
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isLoading}
          >
            Cancelar
          </Button>
        )}
        <Button type="submit" disabled={rating === 0 || isLoading}>
          {isLoading ? 'Guardando...' : isEdit ? 'Actualizar reseña' : 'Publicar reseña'}
        </Button>
      </div>
    </form>
  );
}
