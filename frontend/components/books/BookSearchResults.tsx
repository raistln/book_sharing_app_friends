'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, BookOpen, Check } from 'lucide-react';
import { type BookSearchResult } from '@/lib/hooks/use-book-search';
import Image from 'next/image';

interface BookSearchResultsProps {
  results: BookSearchResult[];
  onSelect: (book: BookSearchResult) => void;
  onBack: () => void;
  isLoading?: boolean;
}

export function BookSearchResults({ results, onSelect, onBack, isLoading }: BookSearchResultsProps) {
  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-12">
          <div className="flex flex-col items-center gap-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-storybook-gold"></div>
            <p className="text-muted-foreground">Buscando libros...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (results.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>No se encontraron resultados</CardTitle>
          <CardDescription>
            No pudimos encontrar libros que coincidan con tu búsqueda
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={onBack} variant="outline">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Intentar de nuevo
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Resultados de búsqueda</CardTitle>
            <CardDescription>
              Encontramos {results.length} {results.length === 1 ? 'libro' : 'libros'}. Selecciona el que quieres añadir.
            </CardDescription>
          </div>
          <Button onClick={onBack} variant="ghost" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Volver
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {results.map((book, index) => (
            <div
              key={index}
              className="border rounded-lg p-4 hover:border-storybook-gold transition-colors cursor-pointer"
              onClick={() => onSelect(book)}
            >
              <div className="flex gap-4">
                {/* Portada */}
                <div className="flex-shrink-0">
                  {book.cover_url ? (
                    <div className="relative w-20 h-28 bg-gray-100 rounded overflow-hidden">
                      <Image
                        src={book.cover_url}
                        alt={book.title}
                        fill
                        className="object-cover"
                        unoptimized
                      />
                    </div>
                  ) : (
                    <div className="w-20 h-28 bg-gray-100 rounded flex items-center justify-center">
                      <BookOpen className="h-8 w-8 text-gray-400" />
                    </div>
                  )}
                </div>

                {/* Información */}
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-lg mb-1 truncate">
                    {book.title}
                  </h3>
                  
                  {book.authors && book.authors.length > 0 && (
                    <p className="text-sm text-muted-foreground mb-2">
                      por {book.authors.join(', ')}
                    </p>
                  )}

                  {book.description && (
                    <p className="text-sm text-muted-foreground line-clamp-2 mb-2">
                      {book.description}
                    </p>
                  )}

                  <div className="flex flex-wrap gap-2 mt-2">
                    {book.isbn && (
                      <Badge variant="secondary" className="text-xs">
                        ISBN: {book.isbn}
                      </Badge>
                    )}
                    {book.published_date && (
                      <Badge variant="secondary" className="text-xs">
                        {book.published_date}
                      </Badge>
                    )}
                    {book.language && (
                      <Badge variant="secondary" className="text-xs">
                        {book.language.toUpperCase()}
                      </Badge>
                    )}
                    {book.page_count && (
                      <Badge variant="secondary" className="text-xs">
                        {book.page_count} págs.
                      </Badge>
                    )}
                    <Badge variant="outline" className="text-xs">
                      {book.source === 'openlibrary' ? 'OpenLibrary' : 'Google Books'}
                    </Badge>
                  </div>
                </div>

                {/* Botón de selección */}
                <div className="flex-shrink-0 flex items-center">
                  <Button size="sm" className="gap-2">
                    <Check className="h-4 w-4" />
                    Seleccionar
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
