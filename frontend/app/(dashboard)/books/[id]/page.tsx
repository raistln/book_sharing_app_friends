'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { useAuth } from '@/lib/hooks/use-auth';
import { useBook, useDeleteBook, useUploadCover } from '@/lib/hooks/use-books';
import { booksApi } from '@/lib/api/books';
import { RequestLoanButton } from '@/components/loans/request-loan-button';
import { BookReviewsSection } from '@/components/reviews/book-reviews-section';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Book, ArrowLeft, Edit, Trash2, Loader2, Upload, Calendar, User, Tag, Globe, Package } from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

export default function BookDetailPage() {
  const router = useRouter();
  const params = useParams();
  const bookId = params.id as string;
  
  const { user, isAuthenticated, isLoadingUser } = useAuth();
  const { book, isLoading } = useBook(bookId);
  const deleteBook = useDeleteBook();
  const uploadCover = useUploadCover();
  
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    if (!isAuthenticated && !isLoadingUser) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoadingUser, router]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUploadCover = () => {
    if (selectedFile && bookId) {
      uploadCover.mutate({ bookId, file: selectedFile });
      setSelectedFile(null);
    }
  };

  const handleDelete = () => {
    if (bookId) {
      deleteBook.mutate(bookId);
    }
  };

  if (isLoadingUser || isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-storybook-parchment via-storybook-cream to-storybook-gold-light flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-storybook-leather mx-auto mb-4" />
          <p className="text-storybook-ink-light">Cargando los detalles del libro...</p>
        </div>
      </div>
    );
  }

  if (!book) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-storybook-parchment via-storybook-cream to-storybook-gold-light flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="text-center py-12">
            <Book className="h-16 w-16 text-storybook-leather opacity-30 mx-auto mb-4" />
            <h3 className="font-display text-2xl font-bold text-storybook-leather mb-2">
              Libro no encontrado
            </h3>
            <p className="text-storybook-ink-light mb-6">
              El libro que buscas no existe o ha sido eliminado.
            </p>
            <Link href="/books">
              <Button>Volver a mis libros</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  const isOwner = user?.id === book.owner_id;

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'available': return 'available';
      case 'borrowed': return 'borrowed';
      case 'reserved': return 'reserved';
      default: return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'available':
        return 'Disponible';
      case 'borrowed':
        return 'Prestado';
      case 'reserved':
        return 'Reservado';
      default:
        return status;
    }
  };

  return (
    <main className="container mx-auto px-4 py-12 max-w-6xl">
        <Link href="/books">
          <Button variant="ghost" className="mb-6">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Volver a mis libros
          </Button>
        </Link>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Book Cover */}
          <div className="md:col-span-1">
            <Card>
              <CardContent className="p-0">
                <div className="relative h-96 bg-storybook-parchment overflow-hidden rounded-t-lg">
                  <Image
                    src={book.cover_url || '/placeholder-book.jpg'}
                    alt={book.title}
                    fill
                    className="object-cover"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.src = '/placeholder-book.jpg';
                    }}
                  />
                </div>
                
                {/* Subir portada (solo propietario) */}
                {isOwner && (
                  <div className="p-4 space-y-3">
                    <Label htmlFor="cover-upload" className="text-sm font-semibold">
                      Actualizar portada
                    </Label>
                    <Input
                      id="cover-upload"
                      type="file"
                      accept="image/*"
                      onChange={handleFileChange}
                      disabled={uploadCover.isPending}
                    />
                    {selectedFile && (
                      <Button
                        onClick={handleUploadCover}
                        disabled={uploadCover.isPending}
                        size="sm"
                        className="w-full"
                      >
                        {uploadCover.isPending ? (
                          <>
                            <Loader2 className="mr-2 h-3 w-3 animate-spin" />
                            Subiendo...
                          </>
                        ) : (
                          <>
                            <Upload className="mr-2 h-3 w-3" />
                            Subir portada
                          </>
                        )}
                      </Button>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Book Details */}
          <div className="md:col-span-2 space-y-6">
            {/* Título y acciones */}
            <Card>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-3xl mb-2">{book.title}</CardTitle>
                    <CardDescription className="text-lg">por {book.author}</CardDescription>
                  </div>
                  <Badge variant={getStatusBadgeVariant(book.status)} className="ml-4">
                    {getStatusLabel(book.status)}
                  </Badge>
                </div>
              </CardHeader>
              
              <CardContent>
                {isOwner ? (
                  <div className="flex gap-3">
                    <Link href={`/books/${book.id}/edit`} className="flex-1">
                      <Button variant="outline" className="w-full">
                        <Edit className="mr-2 h-4 w-4" />
                        Editar libro
                      </Button>
                    </Link>
                    <Button
                      variant="destructive"
                      onClick={() => setShowDeleteConfirm(true)}
                      disabled={deleteBook.isPending}
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      Eliminar
                    </Button>
                  </div>
                ) : (
                  <RequestLoanButton
                    bookId={book.id}
                    bookTitle={book.title}
                    ownerId={book.owner_id}
                    ownerName={book.owner?.username || 'Desconocido'}
                    isAvailable={book.status === 'available'}
                    className="w-full"
                  />
                )}
              </CardContent>
            </Card>

            {/* Descripción */}
            {book.description && (
              <Card>
                <CardHeader>
                  <CardTitle>Descripción</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-storybook-ink-light leading-relaxed">
                    {book.description}
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Información del libro */}
            <Card>
              <CardHeader>
                <CardTitle>Información del libro</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  {book.genre && (
                    <div className="flex items-center gap-3">
                      <Tag className="h-5 w-5 text-storybook-leather" />
                      <div>
                        <p className="text-sm text-storybook-ink-light">Género</p>
                        <p className="font-semibold">{book.genre}</p>
                      </div>
                    </div>
                  )}
                  
                  {book.condition && (
                    <div className="flex items-center gap-3">
                      <Package className="h-5 w-5 text-storybook-leather" />
                      <div>
                        <p className="text-sm text-storybook-ink-light">Estado</p>
                        <p className="font-semibold capitalize">{book.condition}</p>
                      </div>
                    </div>
                  )}

                  {book.language && (
                    <div className="flex items-center gap-3">
                      <Globe className="h-5 w-5 text-storybook-leather" />
                      <div>
                        <p className="text-sm text-storybook-ink-light">Idioma</p>
                        <p className="font-semibold">{book.language}</p>
                      </div>
                    </div>
                  )}

                  {book.isbn && (
                    <div className="flex items-center gap-3 col-span-2">
                      <Tag className="h-5 w-5 text-storybook-leather" />
                      <div>
                        <p className="text-sm text-storybook-ink-light">ISBN</p>
                        <p className="font-semibold font-mono">{book.isbn}</p>
                      </div>
                    </div>
                  )}

                  <div className="flex items-center gap-3">
                    <Calendar className="h-5 w-5 text-storybook-leather" />
                    <div>
                      <p className="text-sm text-storybook-ink-light">Añadido</p>
                      <p className="font-semibold">
                        {format(new Date(book.created_at), "d 'de' MMMM 'de' yyyy", { locale: es })}
                      </p>
                    </div>
                  </div>

                  {book.owner && (
                    <div className="flex items-center gap-3">
                      <User className="h-5 w-5 text-storybook-leather" />
                      <div>
                        <p className="text-sm text-storybook-ink-light">Propietario</p>
                        <p className="font-semibold">{book.owner.username}</p>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Reviews Section */}
        <div className="mt-12">
          <BookReviewsSection bookId={bookId} />
        </div>

        {/* Cuadro de confirmación de borrado */}
        {showDeleteConfirm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <Card className="max-w-md">
              <CardHeader>
                <CardTitle>¿Eliminar libro?</CardTitle>
                <CardDescription>
                  ¿Seguro que quieres eliminar «{book.title}»? Esta acción no se puede deshacer.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-3">
                  <Button
                    variant="destructive"
                    onClick={handleDelete}
                    disabled={deleteBook.isPending}
                    className="flex-1"
                  >
                    {deleteBook.isPending ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Eliminando...
                      </>
                    ) : (
                      'Sí, eliminar'
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowDeleteConfirm(false)}
                    disabled={deleteBook.isPending}
                    className="flex-1"
                  >
                    Cancelar
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
    </main>
  );
}
