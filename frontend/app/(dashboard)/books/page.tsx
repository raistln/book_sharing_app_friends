'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { useAuth } from '@/lib/hooks/use-auth';
import { useMyBooks } from '@/lib/hooks/use-books';
import { booksApi } from '@/lib/api/books';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Book, Plus, LogOut, Loader2, Edit, Trash2, Eye } from 'lucide-react';

export default function BooksPage() {
  const router = useRouter();
  const { user, isAuthenticated, logout, isLoadingUser } = useAuth();
  const [page, setPage] = useState(1);
  const { books, pagination, isLoading } = useMyBooks(page, 12);

  useEffect(() => {
    if (!isAuthenticated && !isLoadingUser) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoadingUser, router]);

  if (isLoadingUser || !user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-storybook-parchment via-storybook-cream to-storybook-gold-light flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-storybook-leather mx-auto mb-4" />
          <p className="text-storybook-ink-light font-serif">Loading your library...</p>
        </div>
      </div>
    );
  }

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'available':
        return 'available';
      case 'borrowed':
        return 'borrowed';
      case 'reserved':
        return 'reserved';
      default:
        return 'default';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-storybook-parchment via-storybook-cream to-storybook-gold-light">
      {/* Header */}
      <header className="bg-storybook-leather text-storybook-cream shadow-book sticky top-0 z-10">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <Link href="/dashboard" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
                <Book className="h-8 w-8 text-storybook-gold" />
                <div>
                  <h1 className="font-display text-2xl font-bold">Book Sharing App</h1>
                  <p className="text-sm text-storybook-gold-light">{user.username}'s Library</p>
                </div>
              </Link>
              <nav className="hidden md:flex gap-4">
                <Link href="/dashboard">
                  <Button variant="ghost" className="text-storybook-cream hover:bg-storybook-leather-dark">
                    Dashboard
                  </Button>
                </Link>
                <Link href="/books">
                  <Button variant="ghost" className="text-storybook-gold hover:bg-storybook-leather-dark">
                    My Books
                  </Button>
                </Link>
                <Link href="/search">
                  <Button variant="ghost" className="text-storybook-cream hover:bg-storybook-leather-dark">
                    Discover
                  </Button>
                </Link>
              </nav>
            </div>
            <Button onClick={logout} variant="outline" className="border-storybook-gold text-storybook-cream hover:bg-storybook-leather-dark">
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12">
        {/* Header Section */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="font-display text-4xl font-bold text-storybook-leather mb-2">
              My Books
            </h2>
            <p className="text-storybook-ink-light">
              {pagination?.total || 0} {pagination?.total === 1 ? 'book' : 'books'} in your collection
            </p>
          </div>
          <Link href="/books/new">
            <Button className="shadow-book hover:shadow-book-hover">
              <Plus className="mr-2 h-4 w-4" />
              Add Book
            </Button>
          </Link>
        </div>

        {/* Books Grid */}
        {isLoading ? (
          <div className="text-center py-20">
            <Loader2 className="h-12 w-12 animate-spin text-storybook-leather mx-auto mb-4" />
            <p className="text-storybook-ink-light">Loading books...</p>
          </div>
        ) : books.length === 0 ? (
          <Card className="text-center py-20">
            <CardContent>
              <Book className="h-16 w-16 text-storybook-leather opacity-30 mx-auto mb-4" />
              <h3 className="font-display text-2xl font-bold text-storybook-leather mb-2">
                No books yet
              </h3>
              <p className="text-storybook-ink-light mb-6">
                Start building your library by adding your first book
              </p>
              <Link href="/books/new">
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Your First Book
                </Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {books.map((book) => (
                <Card key={book.id} className="hover:shadow-book-hover transition-all duration-300 overflow-hidden group">
                  {/* Book Cover */}
                  <div className="relative h-64 bg-storybook-parchment overflow-hidden">
                    <Image
                      src={booksApi.getCoverUrl(book.cover_image)}
                      alt={book.title}
                      fill
                      className="object-cover group-hover:scale-105 transition-transform duration-300"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.src = '/placeholder-book.jpg';
                      }}
                    />
                    <div className="absolute top-2 right-2">
                      <Badge variant={getStatusBadgeVariant(book.status)}>
                        {book.status}
                      </Badge>
                    </div>
                  </div>

                  {/* Book Info */}
                  <CardHeader>
                    <CardTitle className="line-clamp-1">{book.title}</CardTitle>
                    <CardDescription className="line-clamp-1">
                      by {book.author}
                    </CardDescription>
                  </CardHeader>

                  <CardContent>
                    <div className="flex flex-wrap gap-2 mb-4">
                      {book.genre && (
                        <Badge variant="outline" className="text-xs">
                          {book.genre}
                        </Badge>
                      )}
                      {book.book_type && (
                        <Badge variant="secondary" className="text-xs">
                          {book.book_type}
                        </Badge>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2">
                      <Link href={`/books/${book.id}`} className="flex-1">
                        <Button variant="outline" className="w-full" size="sm">
                          <Eye className="mr-2 h-3 w-3" />
                          View
                        </Button>
                      </Link>
                      <Link href={`/books/${book.id}/edit`}>
                        <Button variant="ghost" size="sm">
                          <Edit className="h-3 w-3" />
                        </Button>
                      </Link>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Pagination */}
            {pagination && pagination.total_pages > 1 && (
              <div className="flex justify-center gap-2 mt-8">
                <Button
                  variant="outline"
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                >
                  Previous
                </Button>
                <div className="flex items-center gap-2">
                  {Array.from({ length: pagination.total_pages }, (_, i) => i + 1).map((p) => (
                    <Button
                      key={p}
                      variant={p === page ? 'default' : 'outline'}
                      onClick={() => setPage(p)}
                      size="sm"
                    >
                      {p}
                    </Button>
                  ))}
                </div>
                <Button
                  variant="outline"
                  onClick={() => setPage(page + 1)}
                  disabled={page === pagination.total_pages}
                >
                  Next
                </Button>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
