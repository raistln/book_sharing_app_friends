import { useMutation, useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { toast } from '@/components/ui/use-toast';

export interface BookSearchResult {
  title: string;
  authors: string[];
  isbn?: string;
  cover_url?: string;
  description?: string;
  publisher?: string;
  published_date?: string;
  page_count?: number;
  language?: string;
  source: string;
}

export interface ScanResult {
  method: 'barcode' | 'ocr' | null;
  isbn?: string;
  title?: string;
  author?: string;
  search_results: BookSearchResult[];
  success: boolean;
  error?: string;
}

// Hook para buscar libros por título o ISBN
export function useSearchBooks() {
  return useMutation({
    mutationFn: async ({ query, limit = 5 }: { query: string; limit?: number }) => {
      const response = await apiClient.get<BookSearchResult[]>('/search/books', {
        params: { q: query, limit },
      });
      return response.data;
    },
    onError: (error: any) => {
      toast({
        title: 'Error en la búsqueda',
        description: error.response?.data?.detail?.msg || 'No se pudo realizar la búsqueda',
        variant: 'destructive',
      });
    },
  });
}

// Hook para escanear imagen (OCR + barcode)
export function useScanBook() {
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiClient.post<ScanResult>('/scan/book', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },
    onError: (error: any) => {
      toast({
        title: 'Error al escanear',
        description: error.response?.data?.detail?.msg || 'No se pudo procesar la imagen',
        variant: 'destructive',
      });
    },
  });
}

// Hook para búsqueda automática mientras el usuario escribe
export function useAutoSearch(query: string, enabled: boolean = true) {
  return useQuery({
    queryKey: ['bookSearch', query],
    queryFn: async () => {
      if (!query || query.length < 3) return [];
      
      const response = await apiClient.get<BookSearchResult[]>('/search/books', {
        params: { q: query, limit: 5 },
      });
      return response.data;
    },
    enabled: enabled && query.length >= 3,
    staleTime: 30000, // 30 segundos
  });
}
