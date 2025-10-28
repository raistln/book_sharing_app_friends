'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/hooks/use-auth';
import { useBook, useUpdateBook } from '@/lib/hooks/use-books';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Book, ArrowLeft, Loader2, Save } from 'lucide-react';

const GENRE_OPTIONS = [
  { value: 'fiction', label: 'Fiction' },
  { value: 'science_fiction', label: 'Science Fiction' },
  { value: 'fantasy', label: 'Fantasy' },
  { value: 'mystery', label: 'Mystery' },
  { value: 'thriller', label: 'Thriller' },
  { value: 'horror', label: 'Horror' },
  { value: 'romance', label: 'Romance' },
  { value: 'historical_fiction', label: 'Historical Fiction' },
  { value: 'literary_fiction', label: 'Literary Fiction' },
  { value: 'adventure', label: 'Adventure' },
  { value: 'western', label: 'Western' },
  { value: 'dystopian', label: 'Dystopian' },
  { value: 'magical_realism', label: 'Magical Realism' },
  { value: 'non_fiction', label: 'Non Fiction' },
  { value: 'biography', label: 'Biography' },
  { value: 'autobiography', label: 'Autobiography' },
  { value: 'history', label: 'History' },
  { value: 'philosophy', label: 'Philosophy' },
  { value: 'psychology', label: 'Psychology' },
  { value: 'science', label: 'Science' },
  { value: 'technology', label: 'Technology' },
  { value: 'business', label: 'Business' },
  { value: 'self_help', label: 'Self Help' },
  { value: 'travel', label: 'Travel' },
  { value: 'cooking', label: 'Cooking' },
  { value: 'health', label: 'Health' },
  { value: 'religion', label: 'Religion' },
  { value: 'politics', label: 'Politics' },
  { value: 'economics', label: 'Economics' },
  { value: 'education', label: 'Education' },
  { value: 'children', label: 'Children' },
  { value: 'young_adult', label: 'Young Adult' },
  { value: 'reference', label: 'Reference' },
  { value: 'academic', label: 'Academic' },
  { value: 'other', label: 'Other' },
];

export default function EditBookPage() {
  const router = useRouter();
  const params = useParams();
  const bookId = params.id as string;
  
  const { user, isAuthenticated, isLoadingUser } = useAuth();
  const { book, isLoading: isLoadingBook } = useBook(bookId);
  const updateBook = useUpdateBook();

  const [formData, setFormData] = useState({
    title: '',
    author: '',
    description: '',
    isbn: '',
    genre: '',
    language: '',
    status: 'available' as 'available' | 'borrowed' | 'reserved',
  });

  // Load book data when available
  useEffect(() => {
    if (book) {
      setFormData({
        title: book.title || '',
        author: book.author || '',
        description: book.description || '',
        isbn: book.isbn || '',
        genre: book.genre || '',
        language: book.language || '',
        status: book.status || 'available',
      });
    }
  }, [book]);

  useEffect(() => {
    if (!isAuthenticated && !isLoadingUser) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoadingUser, router]);

  // Check if user is the owner
  useEffect(() => {
    if (book && user && book.owner_id !== user.id) {
      router.push(`/books/${bookId}`);
    }
  }, [book, user, bookId, router]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Remove empty optional fields
    const dataToSend: any = {
      title: formData.title,
      author: formData.author,
      status: formData.status,
    };

    if (formData.description) dataToSend.description = formData.description;
    if (formData.isbn) dataToSend.isbn = formData.isbn;
    if (formData.genre) dataToSend.genre = formData.genre;
    if (formData.language) dataToSend.language = formData.language;

    updateBook.mutate({ id: bookId, data: dataToSend });
  };

  if (isLoadingUser || isLoadingBook) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-storybook-parchment via-storybook-cream to-storybook-gold-light flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-storybook-leather mx-auto mb-4" />
          <p className="text-storybook-ink-light">Loading book...</p>
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
              Book not found
            </h3>
            <Link href="/books">
              <Button>Back to My Books</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <main className="container mx-auto px-4 py-12 max-w-2xl">
        <Link href={`/books/${bookId}`}>
          <Button variant="ghost" className="mb-6">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Book Details
          </Button>
        </Link>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Save className="h-6 w-6 text-storybook-gold" />
              Edit Book Details
            </CardTitle>
            <CardDescription>
              Update the information for &quot;{book.title}&quot;. Fields marked with * are required.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Title */}
              <div className="space-y-2">
                <Label htmlFor="title">Title *</Label>
                <Input
                  id="title"
                  placeholder="Enter book title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                  disabled={updateBook.isPending}
                />
              </div>

              {/* Author */}
              <div className="space-y-2">
                <Label htmlFor="author">Author *</Label>
                <Input
                  id="author"
                  placeholder="Enter author name"
                  value={formData.author}
                  onChange={(e) => setFormData({ ...formData, author: e.target.value })}
                  required
                  disabled={updateBook.isPending}
                />
              </div>

              {/* Description */}
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Brief description of the book..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={4}
                  disabled={updateBook.isPending}
                />
              </div>

              {/* ISBN */}
              <div className="space-y-2">
                <Label htmlFor="isbn">ISBN</Label>
                <Input
                  id="isbn"
                  placeholder="978-3-16-148410-0"
                  value={formData.isbn}
                  onChange={(e) => setFormData({ ...formData, isbn: e.target.value })}
                  disabled={updateBook.isPending}
                />
              </div>

              {/* Genre */}
              <div className="space-y-2">
                <Label htmlFor="genre">Genre</Label>
                <Select
                  value={formData.genre}
                  onValueChange={(value) => setFormData({ ...formData, genre: value })}
                  disabled={updateBook.isPending}
                >
                  <SelectTrigger id="genre">
                    <SelectValue placeholder="Select genre" />
                  </SelectTrigger>
                  <SelectContent>
                    {GENRE_OPTIONS.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Language */}
              <div className="space-y-2">
                <Label htmlFor="language">Language</Label>
                <Input
                  id="language"
                  placeholder="e.g., English, Spanish, French"
                  value={formData.language}
                  onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                  disabled={updateBook.isPending}
                />
              </div>

              {/* Status */}
              <div className="space-y-2">
                <Label htmlFor="status">Status *</Label>
                <Select
                  value={formData.status}
                  onValueChange={(value: any) =>
                    setFormData({ ...formData, status: value })
                  }
                  disabled={updateBook.isPending}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="available">Available</SelectItem>
                    <SelectItem value="borrowed">Borrowed</SelectItem>
                    <SelectItem value="reserved">Reserved</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Submit Buttons */}
              <div className="flex gap-4 pt-4">
                <Button
                  type="submit"
                  className="flex-1"
                  disabled={updateBook.isPending}
                >
                  {updateBook.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Saving Changes...
                    </>
                  ) : (
                    <>
                      <Save className="mr-2 h-4 w-4" />
                      Save Changes
                    </>
                  )}
                </Button>
                <Link href={`/books/${bookId}`}>
                  <Button
                    type="button"
                    variant="outline"
                    disabled={updateBook.isPending}
                  >
                    Cancel
                  </Button>
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>
    </main>
  );
}
