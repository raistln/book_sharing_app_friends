'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/hooks/use-auth';
import { useRequestLoan } from '@/lib/hooks/use-loans';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { BookOpen, Loader2 } from 'lucide-react';

interface RequestLoanButtonProps {
  bookId: string;
  bookTitle: string;
  ownerId: string;
  ownerName: string;
  isAvailable?: boolean;
  variant?: 'default' | 'outline' | 'ghost';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  className?: string;
}

export function RequestLoanButton({
  bookId,
  bookTitle,
  ownerId,
  ownerName,
  isAvailable = true,
  variant = 'default',
  size = 'default',
  className,
}: RequestLoanButtonProps) {
  const { user } = useAuth();
  const requestLoan = useRequestLoan();
  const [open, setOpen] = useState(false);

  const isOwnBook = user?.id === ownerId;

  const handleRequest = async () => {
    if (!user?.id) return;

    await requestLoan.mutateAsync({
      book_id: bookId,
      borrower_id: user.id,
    });

    setOpen(false);
  };

  // No mostrar el botón si es el dueño del libro
  if (isOwnBook) {
    return null;
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          variant={variant}
          size={size}
          disabled={!isAvailable || !user}
          className={className}
        >
          <BookOpen className="h-4 w-4 mr-2" />
          {isAvailable ? 'Solicitar préstamo' : 'No disponible'}
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Solicitar préstamo</DialogTitle>
          <DialogDescription>
            Estás a punto de solicitar el préstamo de este libro.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <p className="text-sm font-medium">Libro:</p>
            <p className="text-sm text-storybook-ink-light">{bookTitle}</p>
          </div>

          <div className="space-y-2">
            <p className="text-sm font-medium">Propietario:</p>
            <p className="text-sm text-storybook-ink-light">{ownerName}</p>
          </div>

          <div className="rounded-lg bg-storybook-parchment p-4 text-sm">
            <p className="text-storybook-ink-light">
              El propietario recibirá tu solicitud y podrá aprobarla o rechazarla.
              Una vez aprobada, podrás coordinar la entrega del libro.
            </p>
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => setOpen(false)}
            disabled={requestLoan.isPending}
          >
            Cancelar
          </Button>
          <Button
            onClick={handleRequest}
            disabled={requestLoan.isPending}
          >
            {requestLoan.isPending ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Enviando...
              </>
            ) : (
              'Confirmar solicitud'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
