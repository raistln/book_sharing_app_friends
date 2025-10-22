'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ArrowLeft, Check, Loader2, BookOpen } from 'lucide-react';
import { type BookSearchResult } from '@/lib/hooks/use-book-search';
import { useCreateBook } from '@/lib/hooks/use-books';
import Image from 'next/image';

interface BookConfirmationProps {
  book: BookSearchResult;
  onBack: () => void;
}

export function BookConfirmation({ book, onBack }: BookConfirmationProps) {
  const createBook = useCreateBook();
  
  const [formData, setFormData] = useState({
    title: book.title || '',
    author: book.authors?.[0] || '',
    description: book.description || '',
    isbn: book.isbn || '',
    cover_url: book.cover_url || '',
    publisher: book.publisher || '',
    published_date: book.published_date || '',
    page_count: book.page_count?.toString() || '',
    language: book.language || '',
    genre: '',
    condition: 'good' as 'new' | 'like_new' | 'good' | 'fair' | 'poor',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Preparar datos para enviar
    const dataToSend: any = {
      title: formData.title,
      condition: formData.condition,
    };

    // Añadir campos opcionales solo si tienen valor
    if (formData.author) dataToSend.author = formData.author;
    if (formData.description) dataToSend.description = formData.description;
    if (formData.isbn) dataToSend.isbn = formData.isbn;
    if (formData.cover_url) dataToSend.cover_url = formData.cover_url;
    if (formData.publisher) dataToSend.publisher = formData.publisher;
    if (formData.published_date) dataToSend.published_date = formData.published_date;
    if (formData.page_count) dataToSend.page_count = formData.page_count;
    if (formData.language) dataToSend.language = formData.language;
    if (formData.genre) dataToSend.genre = formData.genre;

    createBook.mutate(dataToSend);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Check className="h-6 w-6 text-green-600" />
              Confirmar datos del libro
            </CardTitle>
            <CardDescription>
              Revisa y edita la información antes de añadir el libro a tu biblioteca
            </CardDescription>
          </div>
          <Button onClick={onBack} variant="ghost" size="sm" disabled={createBook.isPending}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Volver
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Vista previa de la portada */}
          <div className="flex justify-center">
            {formData.cover_url ? (
              <div className="relative w-32 h-48 bg-gray-100 rounded-lg overflow-hidden shadow-md">
                <Image
                  src={formData.cover_url}
                  alt={formData.title}
                  fill
                  className="object-cover"
                  unoptimized
                />
              </div>
            ) : (
              <div className="w-32 h-48 bg-gray-100 rounded-lg flex items-center justify-center shadow-md">
                <BookOpen className="h-12 w-12 text-gray-400" />
              </div>
            )}
          </div>

          {/* Campos del formulario */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Título */}
            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="title">Título *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
                disabled={createBook.isPending}
              />
            </div>

            {/* Autor */}
            <div className="space-y-2">
              <Label htmlFor="author">Autor</Label>
              <Input
                id="author"
                value={formData.author}
                onChange={(e) => setFormData({ ...formData, author: e.target.value })}
                disabled={createBook.isPending}
              />
            </div>

            {/* ISBN */}
            <div className="space-y-2">
              <Label htmlFor="isbn">ISBN</Label>
              <Input
                id="isbn"
                value={formData.isbn}
                onChange={(e) => setFormData({ ...formData, isbn: e.target.value })}
                disabled={createBook.isPending}
              />
            </div>

            {/* Editorial */}
            <div className="space-y-2">
              <Label htmlFor="publisher">Editorial</Label>
              <Input
                id="publisher"
                value={formData.publisher}
                onChange={(e) => setFormData({ ...formData, publisher: e.target.value })}
                disabled={createBook.isPending}
              />
            </div>

            {/* Fecha de publicación */}
            <div className="space-y-2">
              <Label htmlFor="published_date">Fecha de publicación</Label>
              <Input
                id="published_date"
                value={formData.published_date}
                onChange={(e) => setFormData({ ...formData, published_date: e.target.value })}
                disabled={createBook.isPending}
              />
            </div>

            {/* Páginas */}
            <div className="space-y-2">
              <Label htmlFor="page_count">Número de páginas</Label>
              <Input
                id="page_count"
                type="text"
                value={formData.page_count}
                onChange={(e) => setFormData({ ...formData, page_count: e.target.value })}
                disabled={createBook.isPending}
              />
            </div>

            {/* Idioma */}
            <div className="space-y-2">
              <Label htmlFor="language">Idioma</Label>
              <Input
                id="language"
                value={formData.language}
                onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                placeholder="es, en, fr..."
                disabled={createBook.isPending}
              />
            </div>

            {/* Condición */}
            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="condition">Estado del libro</Label>
              <Select
                value={formData.condition}
                onValueChange={(value: any) => setFormData({ ...formData, condition: value })}
                disabled={createBook.isPending}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="new">Nuevo</SelectItem>
                  <SelectItem value="like_new">Como nuevo</SelectItem>
                  <SelectItem value="good">Buen estado</SelectItem>
                  <SelectItem value="fair">Estado aceptable</SelectItem>
                  <SelectItem value="poor">Mal estado</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Descripción */}
            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="description">Descripción</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={4}
                disabled={createBook.isPending}
              />
            </div>
          </div>

          {/* Botones de acción */}
          <div className="flex gap-4 pt-4">
            <Button
              type="submit"
              className="flex-1"
              disabled={createBook.isPending || !formData.title}
            >
              {createBook.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Añadiendo libro...
                </>
              ) : (
                <>
                  <Check className="mr-2 h-4 w-4" />
                  Confirmar y añadir
                </>
              )}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={onBack}
              disabled={createBook.isPending}
            >
              Cancelar
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
