import { apiClient } from './client';
import type { Book, PaginatedResponse } from '@/lib/types/api';

export interface SearchParams {
  q?: string;
  page?: number;
  per_page?: number;
  genre?: string;
  book_type?: 'physical' | 'digital';
  language?: string;
  available_only?: boolean;
  condition?: string;
  min_rating?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  group_id?: string;
}

export const searchApi = {
  // Search books in database (from group members) - for Discover page
  async searchBooks(params: SearchParams): Promise<PaginatedResponse<Book>> {
    const searchParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        searchParams.append(key, value.toString());
      }
    });

    const response = await apiClient.get<PaginatedResponse<Book>>(
      `/discover/books?${searchParams.toString()}`  // Changed from /search/books to /discover/books
    );
    return response.data;
  },

  // Get search suggestions
  async getSuggestions(query: string): Promise<string[]> {
    if (!query || query.length < 2) return [];
    
    try {
      const response = await apiClient.get<string[]>('/search/suggestions', {
        params: { q: query },
      });
      return response.data;
    } catch (error) {
      return [];
    }
  },

  // Get available genres
  async getGenres(): Promise<string[]> {
    try {
      const response = await apiClient.get<string[]>('/metadata/genres');
      return response.data || [];
    } catch (error) {
      console.error('Error fetching genres:', error);
      return [];
    }
  },

  // Get available languages
  async getLanguages(): Promise<Array<{ code: string; name: string }>> {
    try {
      const response = await apiClient.get<Array<{ code: string; name: string }>>(
        '/metadata/languages'
      );
      return response.data || [];
    } catch (error) {
      console.error('Error fetching languages:', error);
      return [];
    }
  },

  // Get book conditions
  async getConditions(): Promise<Array<{ value: string; label: string; description?: string }>> {
    try {
      const response = await apiClient.get<Array<{ value: string; label: string }>>(
        '/metadata/book-conditions'
      );
      return response.data || [];
    } catch (error) {
      console.error('Error fetching conditions:', error);
      return [
        { value: 'excellent', label: 'Excelente' },
        { value: 'good', label: 'Bueno' },
        { value: 'fair', label: 'Regular' },
        { value: 'poor', label: 'Malo' },
      ];
    }
  },
};
