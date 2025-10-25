// Estados del préstamo
export type LoanStatus = 'requested' | 'approved' | 'active' | 'returned' | 'cancelled';

// Usuario básico (para préstamos)
export interface LoanUser {
  id: string;
  username: string;
  avatar_url?: string;
}

// Libro básico (para préstamos)
export interface LoanBook {
  id: string;
  title: string;
  author: string;
  cover_url?: string;
}

// Préstamo completo
export interface Loan {
  id: string;
  book_id: string;
  borrower_id: string;
  lender_id: string;
  status: LoanStatus;
  requested_at: string;
  approved_at?: string;
  returned_at?: string;
  due_date?: string;
  
  // Relaciones (pueden venir del backend)
  book?: LoanBook;
  borrower?: LoanUser;
  lender?: LoanUser;
}

// Crear solicitud de préstamo
export interface LoanRequest {
  book_id: string;
  borrower_id: string;
}

// Aprobar préstamo
export interface ApproveLoanRequest {
  loan_id: string;
  lender_id: string;
  due_date?: string;
}

// Rechazar préstamo
export interface RejectLoanRequest {
  loan_id: string;
  lender_id: string;
}

// Devolver libro
export interface ReturnBookRequest {
  book_id: string;
}

// Cancelar préstamo
export interface CancelLoanRequest {
  loan_id: string;
  borrower_id: string;
}

// Establecer fecha de devolución
export interface SetDueDateRequest {
  loan_id: string;
  lender_id: string;
  due_date: string;
}

// Respuesta de solicitud de préstamo
export interface LoanRequestResponse {
  loan_id: string;
}

// Respuesta de aprobación
export interface ApproveLoanResponse {
  success: boolean;
  loan_id: string;
  status: string;
  message: string;
}

// Respuesta de rechazo
export interface RejectLoanResponse {
  success: boolean;
  message: string;
}

// Respuesta de devolución
export interface ReturnBookResponse {
  success: boolean;
  message: string;
}

// Respuesta de cancelación
export interface CancelLoanResponse {
  success: boolean;
  message: string;
}

// Respuesta de fecha de devolución
export interface SetDueDateResponse {
  success: boolean;
  loan_id: string;
  due_date: string;
  message: string;
}

// Filtros para lista de préstamos
export interface LoanFilters {
  status?: LoanStatus;
  role?: 'borrower' | 'lender' | 'all'; // Como prestatario, prestador o ambos
}

// Estadísticas de préstamos (para dashboard)
export interface LoanStats {
  total: number;
  pending: number;
  active: number;
  completed: number;
  as_borrower: number;
  as_lender: number;
}
