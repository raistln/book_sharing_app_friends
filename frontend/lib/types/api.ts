// User Types
export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Book Types
export interface Book {
  id: string;
  title: string;
  author: string;
  description?: string;
  isbn?: string;
  genre?: string;
  book_type: 'physical' | 'digital';
  language?: string;
  status: 'available' | 'borrowed' | 'reserved';
  condition?: 'new' | 'like_new' | 'good' | 'fair' | 'poor';
  owner_id: string;
  owner?: User;
  current_borrower?: User;
  cover_image?: string;
  created_at: string;
  updated_at: string;
  average_rating?: number;
  total_reviews?: number;
}

// Auth Types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in?: number;
}

// Search Types
export interface SearchParams {
  q?: string;
  page?: number;
  per_page?: number;
  genre?: string;
  book_type?: string;
  language?: string;
  available_only?: boolean;
  condition?: string;
  min_rating?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Loan Types
export interface Loan {
  id: string;
  book_id: string;
  book?: Book;
  borrower_id: string;
  borrower?: User;
  lender_id: string;
  lender?: User;
  status: 'pending' | 'active' | 'returned' | 'cancelled';
  start_date?: string;
  due_date?: string;
  return_date?: string;
  created_at: string;
  updated_at: string;
}

// Group Types
export interface Group {
  id: string;
  name: string;
  description?: string;
  is_public: boolean;
  member_count: number;
  created_at: string;
  updated_at: string;
}

// Review Types
export interface Review {
  id: string;
  book_id: string;
  user_id: string;
  user?: User;
  rating: number;
  comment?: string;
  created_at: string;
  updated_at: string;
}

// Metadata Types
export interface Genre {
  value: string;
  label: string;
}

export interface Language {
  code: string;
  name: string;
}

export interface Condition {
  value: string;
  label: string;
  description?: string;
}

// API Error Response
export interface APIError {
  detail: string;
  status_code?: number;
}
