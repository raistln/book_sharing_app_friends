import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { loansApi } from '@/lib/api/loans';
import { toast } from '@/components/ui/use-toast';
import type {
  LoanRequest,
  ApproveLoanRequest,
  RejectLoanRequest,
  ReturnBookRequest,
  SetDueDateRequest,
  LoanFilters,
  CancelLoanRequest,
} from '@/lib/types/loan';

// Hook para obtener préstamos del usuario
export function useUserLoans(userId?: string, filters?: LoanFilters) {
  const { data: loans = [], isLoading, error, refetch } = useQuery({
    queryKey: ['loans', userId, filters],
    queryFn: () => loansApi.listUserLoans(userId),
    select: (data) => {
      let filtered = data;

      // Filtrar por estado
      if (filters?.status) {
        filtered = filtered.filter((loan) => loan.status === filters.status);
      }

      // Filtrar por rol
      if (filters?.role && userId) {
        if (filters.role === 'borrower') {
          filtered = filtered.filter((loan) => loan.borrower_id === userId);
        } else if (filters.role === 'lender') {
          filtered = filtered.filter((loan) => loan.lender_id === userId);
        }
      }

      return filtered;
    },
  });

  return { loans, isLoading, error, refetch };
}

// Hook para obtener un préstamo específico
export function useLoan(loanId: string) {
  const { data: loan, isLoading, error, refetch } = useQuery({
    queryKey: ['loan', loanId],
    queryFn: () => loansApi.getLoan(loanId),
    enabled: !!loanId,
  });

  return { loan, isLoading, error, refetch };
}

// Hook para obtener historial de préstamos de un libro
export function useBookLoanHistory(bookId: string) {
  const { data: history = [], isLoading, error } = useQuery({
    queryKey: ['loan-history', bookId],
    queryFn: () => loansApi.getBookHistory(bookId),
    enabled: !!bookId,
  });

  return { history, isLoading, error };
}

// Hook para solicitar préstamo
export function useRequestLoan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: LoanRequest) => loansApi.requestLoan(data),
    onSuccess: (response, variables) => {
      toast({
        title: '¡Solicitud enviada!',
        description: 'El propietario del libro recibirá tu solicitud de préstamo.',
      });
      
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({ queryKey: ['loans'] });
      queryClient.invalidateQueries({ queryKey: ['loan-history', variables.book_id] });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al solicitar préstamo',
        description: error.response?.data?.detail || 'No se pudo enviar la solicitud',
        variant: 'destructive',
      });
    },
  });
}

// Hook para aprobar préstamo
export function useApproveLoan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ApproveLoanRequest) => loansApi.approveLoan(data),
    onSuccess: (response) => {
      toast({
        title: '¡Préstamo aprobado!',
        description: 'El libro ha sido prestado exitosamente.',
      });
      
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({ queryKey: ['loans'] });
      queryClient.invalidateQueries({ queryKey: ['loan', response.loan_id] });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al aprobar préstamo',
        description: error.response?.data?.detail || 'No se pudo aprobar el préstamo',
        variant: 'destructive',
      });
    },
  });
}

// Hook para rechazar préstamo
export function useRejectLoan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: RejectLoanRequest) => loansApi.rejectLoan(data),
    onSuccess: () => {
      toast({
        title: 'Préstamo rechazado',
        description: 'La solicitud de préstamo ha sido rechazada.',
      });
      
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({ queryKey: ['loans'] });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al rechazar préstamo',
        description: error.response?.data?.detail || 'No se pudo rechazar el préstamo',
        variant: 'destructive',
      });
    },
  });
}

// Hook para devolver libro
export function useReturnBook() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ReturnBookRequest) => loansApi.returnBook(data),
    onSuccess: () => {
      toast({
        title: '¡Libro devuelto!',
        description: 'El libro ha sido marcado como devuelto.',
      });
      
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({ queryKey: ['loans'] });
      queryClient.invalidateQueries({ queryKey: ['loan-history'] });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al devolver libro',
        description: error.response?.data?.detail || 'No se pudo marcar el libro como devuelto',
        variant: 'destructive',
      });
    },
  });
}

// Hook para establecer fecha de devolución
export function useSetDueDate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SetDueDateRequest) => loansApi.setDueDate(data),
    onSuccess: (response) => {
      toast({
        title: 'Fecha actualizada',
        description: 'La fecha de devolución ha sido establecida.',
      });
      
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({ queryKey: ['loans'] });
      queryClient.invalidateQueries({ queryKey: ['loan', response.loan_id] });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al establecer fecha',
        description: error.response?.data?.detail || 'No se pudo establecer la fecha de devolución',
        variant: 'destructive',
      });
    },
  });
}

// Hook para cancelar préstamo
export function useCancelLoan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CancelLoanRequest) => loansApi.cancelLoan(data),
    onSuccess: (_response, variables) => {
      toast({
        title: 'Préstamo cancelado',
        description: 'El préstamo ha sido cancelado.',
      });
      
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({ queryKey: ['loans'] });
      queryClient.invalidateQueries({ queryKey: ['loan', variables.loan_id] });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al cancelar préstamo',
        description: error.response?.data?.detail || 'No se pudo cancelar el préstamo',
        variant: 'destructive',
      });
    },
  });
}

// Hook para obtener estadísticas de préstamos
export function useLoanStats(userId?: string) {
const { loans, isLoading } = useUserLoans(userId);

const pendingLoans = loans.filter((loan) => loan.status === 'requested');
const activeLoans = loans.filter(
(loan) => loan.status === 'approved' || loan.status === 'active'
);
const stats = {
total: loans.length,
pending: pendingLoans.length,
active: activeLoans.length,
completed: loans.filter((l) => l.status === 'returned').length,
as_borrower: userId ? loans.filter((l) => l.borrower_id === userId).length : 0,
as_lender: userId ? loans.filter((l) => l.lender_id === userId).length : 0,
};

return { stats, isLoading };
}
