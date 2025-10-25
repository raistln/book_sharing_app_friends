'use client';

import { Star, Trash2, Edit } from 'lucide-react';
import { Review } from '@/lib/types/review';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

interface ReviewCardProps {
  review: Review;
  currentUserId?: string;
  onEdit?: (review: Review) => void;
  onDelete?: (reviewId: string) => void;
  showBookTitle?: boolean;
}

export function ReviewCard({ 
  review, 
  currentUserId, 
  onEdit, 
  onDelete,
  showBookTitle = false 
}: ReviewCardProps) {
  const isOwner = currentUserId === review.user_id;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="font-semibold">{review.user_username || 'Usuario'}</span>
              <span className="text-sm text-muted-foreground">
                {formatDistanceToNow(new Date(review.created_at), { 
                  addSuffix: true,
                  locale: es 
                })}
              </span>
            </div>
            {showBookTitle && review.book_title && (
              <p className="text-sm text-muted-foreground">
                Libro: {review.book_title}
              </p>
            )}
          </div>
          
          {/* Rating */}
          <div className="flex items-center gap-1">
            {[1, 2, 3, 4, 5].map((star) => (
              <Star
                key={star}
                className={`h-4 w-4 ${
                  star <= review.rating
                    ? 'fill-yellow-400 text-yellow-400'
                    : 'text-gray-300'
                }`}
              />
            ))}
          </div>
        </div>
      </CardHeader>

      {review.comment && (
        <CardContent className="pb-3">
          <p className="text-sm text-muted-foreground whitespace-pre-wrap">
            {review.comment}
          </p>
        </CardContent>
      )}

      {isOwner && (onEdit || onDelete) && (
        <CardFooter className="pt-0 gap-2">
          {onEdit && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => onEdit(review)}
            >
              <Edit className="h-4 w-4 mr-1" />
              Editar
            </Button>
          )}
          {onDelete && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => onDelete(review.id)}
              className="text-destructive hover:text-destructive"
            >
              <Trash2 className="h-4 w-4 mr-1" />
              Eliminar
            </Button>
          )}
        </CardFooter>
      )}
    </Card>
  );
}
