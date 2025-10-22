'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/hooks/use-auth';
import { useUserLoans, useApproveLoan, useRejectLoan, useReturnBook } from '@/lib/hooks/use-loans';
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

  // Filtrar préstamos por rol
  const borrowedLoans = loans.filter((loan) => loan.borrower_id === currentUserId);
  const lentLoans = loans.filter((loan) => loan.lender_id === currentUserId);
  const pendingLoans = loans.filter((loan) => loan.status === 'PENDING');
  const activeLoans = loans.filter(
    (loan) => loan.status === 'APPROVED' || loan.status === 'ACTIVE'
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
        {loans.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <BookOpen className="h-12 w-12 text-storybook-ink-light opacity-30 mb-3" />
              <p className="text-storybook-ink-light">No hay préstamos</p>
            </CardContent>
          </Card>
        ) : (
          loans.map((loan) => (
            <LoanCard
              key={loan.id}
              loan={loan}
              currentUserId={currentUserId}
              onApprove={handleApprove}
              onReject={handleReject}
              onReturn={handleReturn}
            />
          ))
        )}
      </div>
    );
  }

  return (
    <Tabs defaultValue="all" className="w-full">
      <TabsList className="grid w-full grid-cols-4">
        <TabsTrigger value="all">
          Todos ({loans.length})
        </TabsTrigger>
        <TabsTrigger value="pending">
          Pendientes ({pendingLoans.length})
        </TabsTrigger>
        <TabsTrigger value="active">
          Activos ({activeLoans.length})
        </TabsTrigger>
        <TabsTrigger value="borrowed">
          Prestados ({borrowedLoans.length})
        </TabsTrigger>
      </TabsList>

      <TabsContent value="all" className="space-y-4 mt-4">
        {loans.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <BookOpen className="h-12 w-12 text-storybook-ink-light opacity-30 mb-3" />
              <p className="text-storybook-ink-light">No tienes préstamos aún</p>
            </CardContent>
          </Card>
        ) : (
          loans.map((loan) => (
            <LoanCard
              key={loan.id}
              loan={loan}
              currentUserId={currentUserId}
              onApprove={handleApprove}
              onReject={handleReject}
              onReturn={handleReturn}
            />
          ))
        )}
      </TabsContent>

      <TabsContent value="pending" className="space-y-4 mt-4">
        {pendingLoans.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Package className="h-12 w-12 text-storybook-ink-light opacity-30 mb-3" />
              <p className="text-storybook-ink-light">No hay préstamos pendientes</p>
            </CardContent>
          </Card>
        ) : (
          pendingLoans.map((loan) => (
            <LoanCard
              key={loan.id}
              loan={loan}
              currentUserId={currentUserId}
              onApprove={handleApprove}
              onReject={handleReject}
              onReturn={handleReturn}
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
            />
          ))
        )}
      </TabsContent>

      <TabsContent value="borrowed" className="space-y-4 mt-4">
        {borrowedLoans.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <BookOpen className="h-12 w-12 text-storybook-ink-light opacity-30 mb-3" />
              <p className="text-storybook-ink-light">No has prestado libros</p>
            </CardContent>
          </Card>
        ) : (
          borrowedLoans.map((loan) => (
            <LoanCard
              key={loan.id}
              loan={loan}
              currentUserId={currentUserId}
              onApprove={handleApprove}
              onReject={handleReject}
              onReturn={handleReturn}
            />
          ))
        )}
      </TabsContent>
    </Tabs>
  );
}
