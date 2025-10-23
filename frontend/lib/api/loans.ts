import { apiClient } from './client';
import type {
  Loan,
  LoanRequest,
  LoanRequestResponse,
  ApproveLoanRequest,
  ApproveLoanResponse,
  RejectLoanRequest,
  RejectLoanResponse,
  ReturnBookRequest,
  ReturnBookResponse,
  CancelLoanRequest,
  CancelLoanResponse,
  SetDueDateRequest,
  SetDueDateResponse,
} from '@/lib/types/loan';

export const loansApi = {
  // Solicitar préstamo
  async requestLoan(data: LoanRequest): Promise<LoanRequestResponse> {
    const response = await apiClient.post<LoanRequestResponse>(
      '/loans/request',
      null,
      {
        params: {
          book_id: data.book_id,
          borrower_id: data.borrower_id,
        },
      }
    );
    return response.data;
  },

  // Aprobar préstamo
  async approveLoan(data: ApproveLoanRequest): Promise<ApproveLoanResponse> {
    const response = await apiClient.post<ApproveLoanResponse>(
      `/loans/${data.loan_id}/approve`,
      null,
      {
        params: {
          lender_id: data.lender_id,
          due_date: data.due_date,
        },
      }
    );
    return response.data;
  },

  // Rechazar préstamo
  async rejectLoan(data: RejectLoanRequest): Promise<RejectLoanResponse> {
    const response = await apiClient.post<RejectLoanResponse>(
      `/loans/${data.loan_id}/reject`,
      null,
      {
        params: {
          lender_id: data.lender_id,
        },
      }
    );
    return response.data;
  },

  // Cancelar préstamo
  async cancelLoan(data: CancelLoanRequest): Promise<CancelLoanResponse> {
    const response = await apiClient.post<CancelLoanResponse>(
      `/loans/${data.loan_id}/cancel`,
      null,
      {
        params: {
          borrower_id: data.borrower_id,
        },
      }
    );
    return response.data;
  },

  // Devolver libro
  async returnBook(data: ReturnBookRequest): Promise<ReturnBookResponse> {
    const response = await apiClient.post<ReturnBookResponse>(
      '/loans/return',
      null,
      {
        params: {
          book_id: data.book_id,
        },
      }
    );
    return response.data;
  },

  // Establecer fecha de devolución
  async setDueDate(data: SetDueDateRequest): Promise<SetDueDateResponse> {
    const response = await apiClient.post<SetDueDateResponse>(
      `/loans/${data.loan_id}/due-date`,
      null,
      {
        params: {
          lender_id: data.lender_id,
          due_date: data.due_date,
        },
      }
    );
    return response.data;
  },

  // Listar préstamos del usuario
  async listUserLoans(userId?: string): Promise<Loan[]> {
    const response = await apiClient.get<Loan[]>('/loans/', {
      params: userId ? { user_id: userId } : undefined,
    });
    return response.data;
  },

  // Obtener historial de préstamos de un libro
  async getBookHistory(bookId: string): Promise<Loan[]> {
    const response = await apiClient.get<Loan[]>(`/loans/history/book/${bookId}`);
    return response.data;
  },

  // Obtener un préstamo específico por ID
  async getLoan(loanId: string): Promise<Loan> {
    // Este endpoint no existe en el backend, pero lo podemos simular
    // obteniendo todos los préstamos y filtrando
    const loans = await this.listUserLoans();
    const loan = loans.find((l) => l.id === loanId);
    if (!loan) {
      throw new Error('Préstamo no encontrado');
    }
    return loan;
  },
};
