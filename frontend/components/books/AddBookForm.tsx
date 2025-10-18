'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { BookOpen, Barcode, Camera, Search, Loader2 } from 'lucide-react';
import { useSearchBooks, useScanBook, type BookSearchResult } from '@/lib/hooks/use-book-search';
import { BookSearchResults } from '@/components/books/BookSearchResults';
import { BookConfirmation } from '@/components/books/BookConfirmation';

type SearchMethod = 'manual' | 'isbn' | 'image';

export function AddBookForm() {
  const [searchMethod, setSearchMethod] = useState<SearchMethod>('manual');
  const [searchQuery, setSearchQuery] = useState('');
  const [authorQuery, setAuthorQuery] = useState('');
  const [isbnQuery, setIsbnQuery] = useState('');
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [searchResults, setSearchResults] = useState<BookSearchResult[]>([]);
  const [selectedBook, setSelectedBook] = useState<BookSearchResult | null>(null);

  const searchBooks = useSearchBooks();
  const scanBook = useScanBook();

  // Búsqueda manual por título/autor
  const handleManualSearch = async () => {
    if (!searchQuery.trim()) return;
    
    const query = authorQuery 
      ? `${searchQuery} ${authorQuery}`
      : searchQuery;
    
    const results = await searchBooks.mutateAsync({ query, limit: 10 });
    setSearchResults(results || []);
  };

  // Búsqueda por ISBN
  const handleIsbnSearch = async () => {
    if (!isbnQuery.trim()) return;
    
    const results = await searchBooks.mutateAsync({ query: isbnQuery, limit: 5 });
    setSearchResults(results || []);
  };

  // Escaneo de imagen
  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedImage(file);
    
    try {
      const result = await scanBook.mutateAsync(file);
      
      if (result.success && result.search_results.length > 0) {
        setSearchResults(result.search_results);
      } else if (result.title) {
        // Si OCR encontró título pero no hay resultados, buscar manualmente
        const results = await searchBooks.mutateAsync({ 
          query: result.title, 
          limit: 10 
        });
        setSearchResults(results || []);
      }
    } catch (error) {
      console.error('Error scanning image:', error);
    }
  };

  const handleSelectBook = (book: BookSearchResult) => {
    setSelectedBook(book);
  };

  const handleBack = () => {
    setSelectedBook(null);
    setSearchResults([]);
    setSearchQuery('');
    setAuthorQuery('');
    setIsbnQuery('');
    setSelectedImage(null);
  };

  // Si hay un libro seleccionado, mostrar confirmación
  if (selectedBook) {
    return <BookConfirmation book={selectedBook} onBack={handleBack} />;
  }

  // Si hay resultados de búsqueda, mostrarlos
  if (searchResults.length > 0) {
    return (
      <BookSearchResults
        results={searchResults}
        onSelect={handleSelectBook}
        onBack={handleBack}
        isLoading={searchBooks.isPending || scanBook.isPending}
      />
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BookOpen className="h-6 w-6 text-storybook-gold" />
          Añadir Libro a tu Biblioteca
        </CardTitle>
        <CardDescription>
          Elige cómo quieres añadir tu libro: búsqueda manual, por ISBN o escaneando la portada
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={searchMethod} onValueChange={(v: string) => setSearchMethod(v as SearchMethod)}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="manual">
              <Search className="h-4 w-4 mr-2" />
              Título/Autor
            </TabsTrigger>
            <TabsTrigger value="isbn">
              <Barcode className="h-4 w-4 mr-2" />
              ISBN
            </TabsTrigger>
            <TabsTrigger value="image">
              <Camera className="h-4 w-4 mr-2" />
              Escanear
            </TabsTrigger>
          </TabsList>

          {/* Búsqueda por título/autor */}
          <TabsContent value="manual" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="title">Título del libro *</Label>
              <Input
                id="title"
                placeholder="Ej: El nombre del viento"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleManualSearch()}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="author">Autor (opcional)</Label>
              <Input
                id="author"
                placeholder="Ej: Patrick Rothfuss"
                value={authorQuery}
                onChange={(e) => setAuthorQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleManualSearch()}
              />
            </div>
            <Button
              onClick={handleManualSearch}
              disabled={!searchQuery.trim() || searchBooks.isPending}
              className="w-full"
            >
              {searchBooks.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Buscando...
                </>
              ) : (
                <>
                  <Search className="mr-2 h-4 w-4" />
                  Buscar Libro
                </>
              )}
            </Button>
          </TabsContent>

          {/* Búsqueda por ISBN */}
          <TabsContent value="isbn" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="isbn">ISBN</Label>
              <Input
                id="isbn"
                placeholder="978-3-16-148410-0"
                value={isbnQuery}
                onChange={(e) => setIsbnQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleIsbnSearch()}
              />
              <p className="text-sm text-muted-foreground">
                Introduce el código ISBN que aparece en la contraportada del libro
              </p>
            </div>
            <Button
              onClick={handleIsbnSearch}
              disabled={!isbnQuery.trim() || searchBooks.isPending}
              className="w-full"
            >
              {searchBooks.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Buscando...
                </>
              ) : (
                <>
                  <Barcode className="mr-2 h-4 w-4" />
                  Buscar por ISBN
                </>
              )}
            </Button>
          </TabsContent>

          {/* Escaneo de imagen */}
          <TabsContent value="image" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="image">Foto de la portada o código de barras</Label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-storybook-gold transition-colors">
                <input
                  id="image"
                  type="file"
                  accept="image/*"
                  capture="environment"
                  onChange={handleImageUpload}
                  className="hidden"
                  disabled={scanBook.isPending}
                />
                <label
                  htmlFor="image"
                  className="cursor-pointer flex flex-col items-center gap-2"
                >
                  {scanBook.isPending ? (
                    <>
                      <Loader2 className="h-12 w-12 text-storybook-gold animate-spin" />
                      <p className="text-sm text-muted-foreground">
                        Procesando imagen...
                      </p>
                    </>
                  ) : selectedImage ? (
                    <>
                      <Camera className="h-12 w-12 text-storybook-gold" />
                      <p className="text-sm font-medium">{selectedImage.name}</p>
                      <p className="text-xs text-muted-foreground">
                        Click para cambiar imagen
                      </p>
                    </>
                  ) : (
                    <>
                      <Camera className="h-12 w-12 text-gray-400" />
                      <p className="text-sm font-medium">
                        Toca para tomar foto o subir imagen
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Portada del libro o código de barras
                      </p>
                    </>
                  )}
                </label>
              </div>
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-800">
                <strong>💡 Consejo:</strong> Para mejores resultados, asegúrate de que la imagen esté bien iluminada y enfocada.
              </p>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
