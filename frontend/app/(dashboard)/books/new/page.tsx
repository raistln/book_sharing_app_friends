'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/hooks/use-auth';
import { Button } from '@/components/ui/button';
import { Book, ArrowLeft, Loader2 } from 'lucide-react';
import { AddBookForm } from '@/components/books/AddBookForm';

export default function NewBookPage() {
  const router = useRouter();
  const { isAuthenticated, isLoadingUser } = useAuth();

  useEffect(() => {
    if (!isAuthenticated && !isLoadingUser) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoadingUser, router]);

  if (isLoadingUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-storybook-parchment via-storybook-cream to-storybook-gold-light flex items-center justify-center">
        <Loader2 className="h-12 w-12 animate-spin text-storybook-leather" />
      </div>
    );
  }

  return (
    <main className="container mx-auto px-4 py-12 max-w-3xl">
        <Link href="/books">
          <Button variant="ghost" className="mb-6">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Volver a Mis Libros
          </Button>
        </Link>

        <AddBookForm />
    </main>
  );
}
