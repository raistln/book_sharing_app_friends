'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/hooks/use-auth';
import { useUserLoans, useApproveLoan, useRejectLoan, useReturnBook, useCancelLoan } from '@/lib/hooks/use-loans';
import { LoanCard } from './loan-card';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Loader2, BookOpen, Package } from 'lucide-react';
import type { LoanStatus } from '@/lib/types/loan';

interface LoanListProps {
  userId?: string;
  showTabs?: boolean;
}

export function LoanList({ userId, showTabs = true }: LoanListProps) {
  const { user } = useAuth();
  const currentUserId = userId || user?.id || '';
  
  const [statusFilter, setStatusFilter] = useState<LoanStatus | undefined>();
  const { loans, isLoading, refetch } = useUserLoans(currentUserId, { status: statusFilter });
  
  const approveLoan = useApproveLoan();
  const rejectLoan = useRejectLoan();
  const returnBook = useReturnBook();
  const cancelLoan = useCancelLoan();

  const handleApprove = async (loanId: string) => {
    await approveLoan.mutateAsync({
      loan_id: loanId,
      lender_id: currentUserId,
    });
    refetch();
  };

  const handleReject = async (loanId: string) => {
    await rejectLoan.mutateAsync({
      loan_id: loanId,
      lender_id: currentUserId,
    });
    refetch();
  };

  const handleReturn = async (bookId: string) => {
    await returnBook.mutateAsync({ book_id: bookId });
    refetch();
  };

  const handleCancel = async (loanId: string) => {
    await cancelLoan.mutateAsync({
      loan_id: loanId,
      borrower_id: currentUserId,
    });
    refetch();
  };

  const visibleLoans = loans.filter(
    (loan) => loan.status !== 'cancelled' && loan.status !== 'returned'
  );

  // Listas principales
  const pendingBorrowedLoans = visibleLoans.filter(
    (loan) => loan.status === 'requested' && loan.borrower_id === currentUserId
  );
  const pendingLentLoans = visibleLoans.filter(
    (loan) => loan.status === 'requested' && loan.lender_id === currentUserId
  );
  const activeLoans = visibleLoans.filter(
    (loan) => loan.status === 'approved' || loan.status === 'active'
  );

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-storybook-leather" />
      </div>
    );
  }

  if (!showTabs) {
    return (
      <div className="space-y-4">
        {visibleLoans.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <BookOpen className="h-12 w-12 text-storybook-ink-light opacity-30 mb-3" />
              <p className="text-storybook-ink-light">No hay préstamos</p>
            </CardContent>
          </Card>
        ) : (
          visibleLoans.map((loan) => (
            <LoanCard
              key={loan.id}
              loan={loan}
              currentUserId={currentUserId}
              onApprove={handleApprove}
              onReject={handleReject}
              onReturn={handleReturn}
              onCancel={handleCancel}
            />
          ))
        )}
      </div>
    );
  }

  return (
    <Tabs defaultValue="pending-borrowed" className="w-full">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="pending-borrowed">
          Pendientes (solicitados) ({pendingBorrowedLoans.length})
        </TabsTrigger>
        <TabsTrigger value="pending-lent">
          Pendientes (por aprobar) ({pendingLentLoans.length})
        </TabsTrigger>
        <TabsTrigger value="active">
          Activos ({activeLoans.length})
        </TabsTrigger>
      </TabsList>

      <TabsContent value="pending-borrowed" className="space-y-4 mt-4">
        {pendingBorrowedLoans.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Package className="h-12 w-12 text-storybook-ink-light opacity-30 mb-3" />
              <p className="text-storybook-ink-light">No has solicitado libros pendientes</p>
            </CardContent>
          </Card>
        ) : (
          pendingBorrowedLoans.map((loan) => (
            <LoanCard
              key={loan.id}
              loan={loan}
              currentUserId={currentUserId}
              onApprove={handleApprove}
              onReject={handleReject}
              onReturn={handleReturn}
              onCancel={handleCancel}
            />
          ))
        )}
      </TabsContent>

      <TabsContent value="pending-lent" className="space-y-4 mt-4">
        {pendingLentLoans.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Package className="h-12 w-12 text-storybook-ink-light opacity-30 mb-3" />
              <p className="text-storybook-ink-light">No tienes solicitudes por aprobar</p>
            </CardContent>
          </Card>
        ) : (
          pendingLentLoans.map((loan) => (
            <LoanCard
              key={loan.id}
              loan={loan}
              currentUserId={currentUserId}
              onApprove={handleApprove}
              onReject={handleReject}
              onReturn={handleReturn}
              onCancel={handleCancel}
            />
          ))
        )}
      </TabsContent>

      <TabsContent value="active" className="space-y-4 mt-4">
        {activeLoans.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <BookOpen className="h-12 w-12 text-storybook-ink-light opacity-30 mb-3" />
              <p className="text-storybook-ink-light">No hay préstamos activos</p>
            </CardContent>
          </Card>
        ) : (
          activeLoans.map((loan) => (
            <LoanCard
              key={loan.id}
              loan={loan}
              currentUserId={currentUserId}
              onApprove={handleApprove}
              onReject={handleReject}
              onReturn={handleReturn}
              onCancel={handleCancel}
            />
          ))
        )}
      </TabsContent>
    </Tabs>
  );
}
