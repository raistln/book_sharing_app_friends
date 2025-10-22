import { useQuery } from '@tanstack/react-query';
import { searchApi, type SearchParams } from '@/lib/api/search';
import { useState, useEffect } from 'react';

export function useSearch(params: SearchParams) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['search', params],
    queryFn: () => searchApi.searchBooks(params),
    enabled: true,
  });

  return {
    books: data?.items || [],
    pagination: data
      ? {
          total: data.total,
          page: data.page,
          per_page: data.per_page,
          total_pages: data.total_pages,
        }
      : null,
    isLoading,
    error,
  };
}

export function useSearchSuggestions(query: string) {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!query || query.length < 2) {
      setSuggestions([]);
      return;
    }

    const fetchSuggestions = async () => {
      setIsLoading(true);
      try {
        const results = await searchApi.getSuggestions(query);
        setSuggestions(results);
      } catch (error) {
        setSuggestions([]);
      } finally {
        setIsLoading(false);
      }
    };

    const debounceTimer = setTimeout(fetchSuggestions, 300);
    return () => clearTimeout(debounceTimer);
  }, [query]);

  return { suggestions, isLoading };
}

export function useGenres() {
  const { data: genres = [], isLoading } = useQuery({
    queryKey: ['genres'],
    queryFn: searchApi.getGenres,
    staleTime: Infinity, // Genres don't change often
  });

  return { genres, isLoading };
}

export function useLanguages() {
  const { data: languages = [], isLoading } = useQuery({
    queryKey: ['languages'],
    queryFn: searchApi.getLanguages,
    staleTime: Infinity,
  });

  return { languages, isLoading };
}

export function useConditions() {
  const { data: conditions = [], isLoading } = useQuery({
    queryKey: ['conditions'],
    queryFn: searchApi.getConditions,
    staleTime: Infinity,
  });

  return { conditions, isLoading };
}
