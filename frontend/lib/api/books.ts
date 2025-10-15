import { apiClient } from './client';
import type { Book, PaginatedResponse } from '@/lib/types/api';

export interface CreateBookData {
  title: string;
  author: string;
  description?: string;
  isbn?: string;
  genre?: string;
  book_type: 'physical' | 'digital';
  language?: string;
  condition?: 'new' | 'like_new' | 'good' | 'fair' | 'poor';
}

export interface UpdateBookData extends Partial<CreateBookData> {
  status?: 'available' | 'borrowed' | 'reserved';
}

export interface BookFilters {
  page?: number;
  per_page?: number;
  genre?: string;
  book_type?: string;
  language?: string;
  status?: string;
  owner_id?: string;
}

export const booksApi = {
  // Get all books with filters
  async getBooks(filters?: BookFilters): Promise<PaginatedResponse<Book>> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    const response = await apiClient.get<PaginatedResponse<Book>>(`/books/?${params.toString()}`);
    return response.data;
  },

  // Get my books
  async getMyBooks(page: number = 1, per_page: number = 10): Promise<PaginatedResponse<Book>> {
    const response = await apiClient.get<PaginatedResponse<Book>>('/users/me/books', {
      params: { page, per_page },
    });
    return response.data;
  },

  // Get single book
  async getBook(id: string): Promise<Book> {
    const response = await apiClient.get<Book>(`/books/${id}`);
    return response.data;
  },

  // Create book
  async createBook(data: CreateBookData): Promise<Book> {
    const response = await apiClient.post<Book>('/books/', data);
    return response.data;
  },

  // Update book
  async updateBook(id: string, data: UpdateBookData): Promise<Book> {
    const response = await apiClient.put<Book>(`/books/${id}`, data);
    return response.data;
  },

  // Delete book
  async deleteBook(id: string): Promise<void> {
    await apiClient.delete(`/books/${id}`);
  },

  // Upload book cover
  async uploadCover(bookId: string, file: File): Promise<Book> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post<Book>(`/books/${bookId}/cover`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get book cover URL
  getCoverUrl(coverImage?: string): string {
    if (!coverImage) return '/placeholder-book.jpg';
    if (coverImage.startsWith('http')) return coverImage;
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
    return `${baseUrl}${coverImage}`;
  },
};
