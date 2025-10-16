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
}

export const searchApi = {
  // Search books
  async searchBooks(params: SearchParams): Promise<PaginatedResponse<Book>> {
    const searchParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        searchParams.append(key, value.toString());
      }
    });

    const response = await apiClient.get<PaginatedResponse<Book>>(
      `/search/books?${searchParams.toString()}`
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
      const response = await apiClient.get<{ genres: string[] }>('/metadata/genres');
      return response.data.genres || [];
    } catch (error) {
      return [];
    }
  },

  // Get available languages
  async getLanguages(): Promise<Array<{ code: string; name: string }>> {
    try {
      const response = await apiClient.get<{ languages: Array<{ code: string; name: string }> }>(
        '/metadata/languages'
      );
      return response.data.languages || [];
    } catch (error) {
      return [];
    }
  },

  // Get book conditions
  async getConditions(): Promise<Array<{ value: string; label: string; description?: string }>> {
    try {
      const response = await apiClient.get<{
        conditions: Array<{ value: string; label: string; description?: string }>;
      }>('/metadata/conditions');
      return response.data.conditions || [];
    } catch (error) {
      return [
        { value: 'new', label: 'New' },
        { value: 'like_new', label: 'Like New' },
        { value: 'good', label: 'Good' },
        { value: 'fair', label: 'Fair' },
        { value: 'poor', label: 'Poor' },
      ];
    }
  },
};
