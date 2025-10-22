'use client';

import { Loan } from '@/lib/types/loan';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Calendar, User, Book, Clock, MessageCircle } from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import Link from 'next/link';

interface LoanCardProps {
  loan: Loan;
  currentUserId: string;
  onApprove?: (loanId: string) => void;
  onReject?: (loanId: string) => void;
  onReturn?: (bookId: string) => void;
  showActions?: boolean;
}

const statusColors = {
  PENDING: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  APPROVED: 'bg-green-100 text-green-800 border-green-300',
  ACTIVE: 'bg-blue-100 text-blue-800 border-blue-300',
  RETURNED: 'bg-gray-100 text-gray-800 border-gray-300',
  REJECTED: 'bg-red-100 text-red-800 border-red-300',
  CANCELLED: 'bg-gray-100 text-gray-800 border-gray-300',
};

const statusLabels = {
  PENDING: 'Pendiente',
  APPROVED: 'Aprobado',
  ACTIVE: 'Activo',
  RETURNED: 'Devuelto',
  REJECTED: 'Rechazado',
  CANCELLED: 'Cancelado',
};

export function LoanCard({ loan, currentUserId, onApprove, onReject, onReturn, showActions = true }: LoanCardProps) {
  const isLender = loan.lender_id === currentUserId;
  const isBorrower = loan.borrower_id === currentUserId;
  const isPending = loan.status === 'PENDING';
  const isActive = loan.status === 'APPROVED' || loan.status === 'ACTIVE';
  const isOverdue = loan.due_date && new Date(loan.due_date) < new Date() && isActive;

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <Book className="h-4 w-4 text-storybook-leather" />
              <CardTitle className="text-lg">{loan.book?.title || 'Libro'}</CardTitle>
            </div>
            <CardDescription className="flex items-center gap-2">
              <User className="h-3 w-3" />
              {isLender ? (
                <span>Prestado a: <strong>{loan.borrower?.username}</strong></span>
              ) : (
                <span>Prestado por: <strong>{loan.lender?.username}</strong></span>
              )}
            </CardDescription>
          </div>
          <Badge className={statusColors[loan.status]}>
            {statusLabels[loan.status]}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Fechas */}
        <div className="space-y-2 text-sm text-storybook-ink-light">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            <span>Solicitado: {format(new Date(loan.requested_at), 'PPP', { locale: es })}</span>
          </div>
          
          {loan.approved_at && (
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              <span>Aprobado: {format(new Date(loan.approved_at), 'PPP', { locale: es })}</span>
            </div>
          )}
          
          {loan.due_date && (
            <div className={`flex items-center gap-2 ${isOverdue ? 'text-red-600 font-semibold' : ''}`}>
              <Clock className="h-4 w-4" />
              <span>
                Devolución: {format(new Date(loan.due_date), 'PPP', { locale: es })}
                {isOverdue && ' (¡Vencido!)'}
              </span>
            </div>
          )}
          
          {loan.returned_at && (
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              <span>Devuelto: {format(new Date(loan.returned_at), 'PPP', { locale: es })}</span>
            </div>
          )}
        </div>

        {/* Acciones */}
        {showActions && (
          <div className="flex gap-2 pt-2 border-t">
            {/* Acciones para el prestador (lender) */}
            {isLender && isPending && (
              <>
                <Button
                  size="sm"
                  onClick={() => onApprove?.(loan.id)}
                  className="flex-1"
                >
                  Aprobar
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => onReject?.(loan.id)}
                  className="flex-1"
                >
                  Rechazar
                </Button>
              </>
            )}

            {/* Acciones para el prestatario (borrower) */}
            {isBorrower && isActive && (
              <Button
                size="sm"
                onClick={() => onReturn?.(loan.book_id)}
                className="flex-1"
              >
                Marcar como devuelto
              </Button>
            )}

            {/* Chat disponible para ambos */}
            {(isActive || isPending) && (
              <Link href={`/loans/${loan.id}`} className="flex-1">
                <Button size="sm" variant="outline" className="w-full">
                  <MessageCircle className="h-4 w-4 mr-2" />
                  Chat
                </Button>
              </Link>
            )}

            {/* Ver detalles */}
            <Link href={`/loans/${loan.id}`}>
              <Button size="sm" variant="ghost">
                Ver detalles
              </Button>
            </Link>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
