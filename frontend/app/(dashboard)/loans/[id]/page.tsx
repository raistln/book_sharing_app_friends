'use client';

import { useMemo, useState } from 'react';
import { useAuth } from '@/lib/hooks/use-auth';
import { useLoan, useApproveLoan, useRejectLoan, useReturnBook, useSetDueDate, useCancelLoan } from '@/lib/hooks/use-loans';
import { ChatBox } from '@/components/chat/chat-box';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Calendar, User, Book, Clock, Loader2, ArrowLeft } from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const statusColors: Record<string, string> = {
  requested: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  approved: 'bg-green-100 text-green-800 border-green-300',
  active: 'bg-blue-100 text-blue-800 border-blue-300',
  returned: 'bg-gray-100 text-gray-800 border-gray-300',
  cancelled: 'bg-gray-100 text-gray-800 border-gray-300',
};

const statusLabels: Record<string, string> = {
  requested: 'Pendiente',
  approved: 'Aprobado',
  active: 'Activo',
  returned: 'Devuelto',
  cancelled: 'Cancelado',
};

type LoanPageParams = { params: { id: string } };

export default function LoanDetailPage({ params }: LoanPageParams) {
  const id = params.id;
  const { user } = useAuth();
  const router = useRouter();
  const { loan, isLoading, refetch } = useLoan(id);
  const approveLoan = useApproveLoan();
  const rejectLoan = useRejectLoan();
  const returnBook = useReturnBook();
  const setDueDate = useSetDueDate();
  const cancelLoan = useCancelLoan();

  const [dueDate, setDueDateValue] = useState('');
  const [showDueDateInput, setShowDueDateInput] = useState(false);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-storybook-leather" />
      </div>
    );
  }

  if (!loan) {
    return (
      <div className="container mx-auto py-8 px-4 max-w-4xl">
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <p className="text-storybook-ink-light">Préstamo no encontrado</p>
            <Link href="/loans">
              <Button className="mt-4">Volver a préstamos</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  const isLender = loan.lender_id === user?.id;
  const isBorrower = loan.borrower_id === user?.id;
  const isPending = loan.status === 'requested';
  const isActive = loan.status === 'approved' || loan.status === 'active';
  const isOverdue = loan.due_date && new Date(loan.due_date) < new Date() && isActive;

  const otherUser = isLender ? loan.borrower : loan.lender;

  const handleApprove = async () => {
    if (!user?.id) return;
    await approveLoan.mutateAsync({
      loan_id: loan.id,
      lender_id: user.id,
      due_date: dueDate || undefined,
    });
    refetch();
  };

  const handleReject = async () => {
    if (!user?.id) return;
    await rejectLoan.mutateAsync({
      loan_id: loan.id,
      lender_id: user.id,
    });
    router.push('/loans');
  };

  const handleCancel = async () => {
    if (!user?.id) return;
    await cancelLoan.mutateAsync({
      loan_id: loan.id,
      borrower_id: user.id,
    });
    router.push('/loans');
  };

  const handleReturn = async () => {
    await returnBook.mutateAsync({ book_id: loan.book_id });
    refetch();
  };

  const handleSetDueDate = async () => {
    if (!user?.id || !dueDate) return;
    await setDueDate.mutateAsync({
      loan_id: loan.id,
      lender_id: user.id,
      due_date: dueDate,
    });
    setShowDueDateInput(false);
    setDueDateValue('');
    refetch();
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-6xl">
      {/* Header */}
      <div className="mb-6">
        <Link href="/loans">
          <Button variant="ghost" size="sm" className="mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver a préstamos
          </Button>
        </Link>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-storybook-ink mb-2">
              Detalle del Préstamo
            </h1>
            <p className="text-storybook-ink-light">
              {isLender ? 'Has prestado este libro' : 'Has solicitado este libro'}
            </p>
          </div>
          <Badge className={statusColors[loan.status] ?? 'bg-gray-100 text-gray-800 border-gray-300'}>
            {statusLabels[loan.status] ?? loan.status}
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Información del préstamo */}
        <div className="lg:col-span-2 space-y-6">
          {/* Información del libro */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Book className="h-5 w-5" />
                Información del Libro
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm font-medium text-storybook-ink-light">Título</p>
                <p className="text-lg font-semibold">{loan.book?.title}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-storybook-ink-light">Autor</p>
                <p>{loan.book?.author}</p>
              </div>
              {loan.book?.cover_url && (
                <img
                  src={loan.book.cover_url}
                  alt={loan.book.title}
                  className="w-32 h-48 object-cover rounded-lg"
                />
              )}
            </CardContent>
          </Card>

          {/* Fechas importantes */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Fechas
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-storybook-ink-light">Solicitado</span>
                <span className="font-medium">
                  {format(new Date(loan.requested_at), 'PPP', { locale: es })}
                </span>
              </div>

              {loan.approved_at && (
                <>
                  <Separator />
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-storybook-ink-light">Aprobado</span>
                    <span className="font-medium">
                      {format(new Date(loan.approved_at), 'PPP', { locale: es })}
                    </span>
                  </div>
                </>
              )}

              {loan.due_date && (
                <>
                  <Separator />
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-storybook-ink-light">Fecha de devolución</span>
                    <span className={`font-medium ${isOverdue ? 'text-red-600' : ''}`}>
                      {format(new Date(loan.due_date), 'PPP', { locale: es })}
                      {isOverdue && ' (¡Vencido!)'}
                    </span>
                  </div>
                </>
              )}

              {loan.returned_at && (
                <>
                  <Separator />
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-storybook-ink-light">Devuelto</span>
                    <span className="font-medium">
                      {format(new Date(loan.returned_at), 'PPP', { locale: es })}
                    </span>
                  </div>
                </>
              )}

              {/* Establecer fecha de devolución */}
              {isLender && isActive && !loan.due_date && (
                <>
                  <Separator />
                  {!showDueDateInput ? (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setShowDueDateInput(true)}
                      className="w-full"
                    >
                      <Clock className="h-4 w-4 mr-2" />
                      Establecer fecha de devolución
                    </Button>
                  ) : (
                    <div className="space-y-2">
                      <Label htmlFor="due-date">Fecha de devolución</Label>
                      <div className="flex gap-2">
                        <Input
                          id="due-date"
                          type="date"
                          value={dueDate}
                          onChange={(e) => setDueDateValue(e.target.value)}
                          min={new Date().toISOString().split('T')[0]}
                        />
                        <Button
                          size="sm"
                          onClick={handleSetDueDate}
                          disabled={!dueDate || setDueDate.isPending}
                        >
                          Guardar
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => {
                            setShowDueDateInput(false);
                            setDueDateValue('');
                          }}
                        >
                          Cancelar
                        </Button>
                      </div>
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>

          {/* Acciones */}
          {(isPending || isActive) && (
            <Card>
              <CardHeader>
                <CardTitle>Acciones</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {isLender && isPending && (
                  <div className="flex gap-2">
                    <Button
                      onClick={handleApprove}
                      disabled={approveLoan.isPending}
                      className="flex-1"
                    >
                      {approveLoan.isPending ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Aprobando...
                        </>
                      ) : (
                        'Aprobar préstamo'
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      onClick={handleReject}
                      disabled={rejectLoan.isPending}
                      className="flex-1"
                    >
                      {rejectLoan.isPending ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Rechazando...
                        </>
                      ) : (
                        'Rechazar'
                      )}
                    </Button>
                  </div>
                )}

                {isBorrower && isPending && (
                  <Button
                    onClick={handleCancel}
                    disabled={cancelLoan.isPending}
                    className="w-full"
                    variant="outline"
                  >
                    {cancelLoan.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Cancelando...
                      </>
                    ) : (
                      'Cancelar solicitud'
                    )}
                  </Button>
                )}

                {isLender && isActive && (
                  <Button
                    onClick={handleReturn}
                    disabled={returnBook.isPending}
                    className="w-full"
                  >
                    {returnBook.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Confirmando devolución...
                      </>
                    ) : (
                      'Confirmar devolución'
                    )}
                  </Button>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Chat */}
        <div className="lg:col-span-1">
          {otherUser && (isPending || isActive) && (
            <ChatBox loanId={loan.id} otherUser={otherUser} />
          )}
        </div>
      </div>
    </div>
  );
}
