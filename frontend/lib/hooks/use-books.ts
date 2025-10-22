import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { booksApi, type CreateBookData, type UpdateBookData, type BookFilters } from '@/lib/api/books';
import { toast } from '@/components/ui/use-toast';

export function useBooks(filters?: BookFilters) {
  const queryClient = useQueryClient();

  // Get all books
  const { data: booksData, isLoading, error } = useQuery({
    queryKey: ['books', filters],
    queryFn: () => booksApi.getBooks(filters),
  });

  return {
    books: booksData?.items || [],
    pagination: booksData ? {
      total: booksData.total,
      page: booksData.page,
      per_page: booksData.per_page,
      total_pages: booksData.total_pages,
    } : null,
    isLoading,
    error,
  };
}

export function useMyBooks(page: number = 1, per_page: number = 10) {
  const queryClient = useQueryClient();

  // Get my books
  const { data: booksData, isLoading, error } = useQuery({
    queryKey: ['myBooks', page, per_page],
    queryFn: () => booksApi.getMyBooks(page, per_page),
  });

  return {
    books: booksData?.items || [],
    pagination: booksData ? {
      total: booksData.total,
      page: booksData.page,
      per_page: booksData.per_page,
      total_pages: booksData.total_pages,
    } : null,
    isLoading,
    error,
  };
}

export function useBook(id: string) {
  const { data: book, isLoading, error } = useQuery({
    queryKey: ['book', id],
    queryFn: () => booksApi.getBook(id),
    enabled: !!id,
  });

  return { book, isLoading, error };
}

export function useCreateBook() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: booksApi.createBook,
    onSuccess: (newBook) => {
      queryClient.invalidateQueries({ queryKey: ['books'] });
      queryClient.invalidateQueries({ queryKey: ['myBooks'] });
      toast({
        title: '¡Libro añadido! 📚',
        description: `"${newBook.title}" se ha añadido a tu biblioteca`,
      });
      router.push('/books');
    },
    onError: (error: any) => {
      toast({
        title: 'Error al añadir libro',
        description: error.response?.data?.detail || 'No se pudo añadir el libro',
        variant: 'destructive',
      });
    },
  });
}

export function useUpdateBook() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateBookData }) =>
      booksApi.updateBook(id, data),
    onSuccess: (updatedBook) => {
      queryClient.invalidateQueries({ queryKey: ['books'] });
      queryClient.invalidateQueries({ queryKey: ['myBooks'] });
      queryClient.invalidateQueries({ queryKey: ['book', updatedBook.id] });
      toast({
        title: '¡Libro actualizado! ✨',
        description: `"${updatedBook.title}" se ha actualizado correctamente`,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al actualizar',
        description: error.response?.data?.detail || 'No se pudo actualizar el libro',
        variant: 'destructive',
      });
    },
  });
}

export function useDeleteBook() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: booksApi.deleteBook,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['books'] });
      queryClient.invalidateQueries({ queryKey: ['myBooks'] });
      toast({
        title: 'Libro eliminado',
        description: 'El libro se ha eliminado de tu biblioteca',
      });
      router.push('/books');
    },
    onError: (error: any) => {
      toast({
        title: 'Error al eliminar',
        description: error.response?.data?.detail || 'No se pudo eliminar el libro',
        variant: 'destructive',
      });
    },
  });
}

export function useUploadCover() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ bookId, file }: { bookId: string; file: File }) =>
      booksApi.uploadCover(bookId, file),
    onSuccess: (updatedBook) => {
      queryClient.invalidateQueries({ queryKey: ['books'] });
      queryClient.invalidateQueries({ queryKey: ['myBooks'] });
      queryClient.invalidateQueries({ queryKey: ['book', updatedBook.id] });
      toast({
        title: '¡Portada actualizada! 🎨',
        description: 'La imagen de portada se ha subido correctamente',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al subir imagen',
        description: error.response?.data?.detail || 'No se pudo subir la imagen',
        variant: 'destructive',
      });
    },
  });
}
