'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/hooks/use-auth';
import { useCreateBook } from '@/lib/hooks/use-books';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Book, ArrowLeft, Loader2, Sparkles } from 'lucide-react';

export default function NewBookPage() {
  const router = useRouter();
  const { isAuthenticated, isLoadingUser } = useAuth();
  const createBook = useCreateBook();

  const [formData, setFormData] = useState({
    title: '',
    author: '',
    description: '',
    isbn: '',
    genre: '',
    book_type: 'physical' as 'physical' | 'digital',
    language: '',
    condition: '' as 'new' | 'like_new' | 'good' | 'fair' | 'poor' | '',
  });

  useEffect(() => {
    if (!isAuthenticated && !isLoadingUser) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoadingUser, router]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Remove empty optional fields
    const dataToSend: any = {
      title: formData.title,
      author: formData.author,
      book_type: formData.book_type,
    };

    if (formData.description) dataToSend.description = formData.description;
    if (formData.isbn) dataToSend.isbn = formData.isbn;
    if (formData.genre) dataToSend.genre = formData.genre;
    if (formData.language) dataToSend.language = formData.language;
    if (formData.condition) dataToSend.condition = formData.condition;

    createBook.mutate(dataToSend);
  };

  if (isLoadingUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-storybook-parchment via-storybook-cream to-storybook-gold-light flex items-center justify-center">
        <Loader2 className="h-12 w-12 animate-spin text-storybook-leather" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-storybook-parchment via-storybook-cream to-storybook-gold-light">
      {/* Header */}
      <header className="bg-storybook-leather text-storybook-cream shadow-book">
        <div className="container mx-auto px-4 py-6">
          <Link href="/books" className="flex items-center gap-3 hover:opacity-80 transition-opacity w-fit">
            <Book className="h-8 w-8 text-storybook-gold" />
            <h1 className="font-display text-2xl font-bold">Add New Book</h1>
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12 max-w-2xl">
        <Link href="/books">
          <Button variant="ghost" className="mb-6">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to My Books
          </Button>
        </Link>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-storybook-gold" />
              Add a Book to Your Library
            </CardTitle>
            <CardDescription>
              Fill in the details of your book. Fields marked with * are required.
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
                  disabled={createBook.isPending}
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
                  disabled={createBook.isPending}
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
                  disabled={createBook.isPending}
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
                  disabled={createBook.isPending}
                />
              </div>

              {/* Genre */}
              <div className="space-y-2">
                <Label htmlFor="genre">Genre</Label>
                <Input
                  id="genre"
                  placeholder="e.g., Fiction, Science Fiction, Mystery"
                  value={formData.genre}
                  onChange={(e) => setFormData({ ...formData, genre: e.target.value })}
                  disabled={createBook.isPending}
                />
              </div>

              {/* Book Type */}
              <div className="space-y-2">
                <Label htmlFor="book_type">Book Type *</Label>
                <Select
                  value={formData.book_type}
                  onValueChange={(value: 'physical' | 'digital') =>
                    setFormData({ ...formData, book_type: value })
                  }
                  disabled={createBook.isPending}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select book type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="physical">Physical</SelectItem>
                    <SelectItem value="digital">Digital</SelectItem>
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
                  disabled={createBook.isPending}
                />
              </div>

              {/* Condition (only for physical books) */}
              {formData.book_type === 'physical' && (
                <div className="space-y-2">
                  <Label htmlFor="condition">Condition</Label>
                  <Select
                    value={formData.condition}
                    onValueChange={(value: any) =>
                      setFormData({ ...formData, condition: value })
                    }
                    disabled={createBook.isPending}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select condition" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="new">New</SelectItem>
                      <SelectItem value="like_new">Like New</SelectItem>
                      <SelectItem value="good">Good</SelectItem>
                      <SelectItem value="fair">Fair</SelectItem>
                      <SelectItem value="poor">Poor</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}

              {/* Submit Buttons */}
              <div className="flex gap-4 pt-4">
                <Button
                  type="submit"
                  className="flex-1"
                  disabled={createBook.isPending}
                >
                  {createBook.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Adding Book...
                    </>
                  ) : (
                    <>
                      <Sparkles className="mr-2 h-4 w-4" />
                      Add Book
                    </>
                  )}
                </Button>
                <Link href="/books">
                  <Button
                    type="button"
                    variant="outline"
                    disabled={createBook.isPending}
                  >
                    Cancel
                  </Button>
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
