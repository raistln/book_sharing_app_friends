'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/use-auth';
import { Header } from '@/components/layout/header';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Book, Users, Search, LogOut, Sparkles, Loader2 } from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, logout, isLoadingUser } = useAuth();

  useEffect(() => {
    // Solo redirigir si hemos terminado de cargar Y no estamos autenticados
    if (!isLoadingUser && !isAuthenticated && !user) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoadingUser, router, user]);

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-storybook-parchment via-storybook-cream to-storybook-gold-light">
      {/* Header */}
      <Header subtitle={`Welcome, ${user.username}!`} />

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12">
        {/* Welcome Section */}
        <div className="mb-12 text-center animate-fade-in-up">
          <div className="inline-block mb-4">
            <Sparkles className="h-12 w-12 text-storybook-gold animate-float mx-auto" />
          </div>
          <h2 className="font-display text-4xl font-bold text-storybook-leather mb-4">
            Welcome to Your Library
          </h2>
          <p className="text-xl text-storybook-ink-light max-w-2xl mx-auto">
            Your magical reading journey starts here. Explore, share, and discover amazing books.
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <Card className="hover:shadow-book-hover transition-all duration-300 cursor-pointer">
            <CardHeader>
              <div className="bg-storybook-gold/20 rounded-full w-12 h-12 flex items-center justify-center mb-4">
                <Book className="h-6 w-6 text-storybook-leather" />
              </div>
              <CardTitle>My Books</CardTitle>
              <CardDescription>
                Manage your personal book collection
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button className="w-full" onClick={() => router.push('/books')}>
                View Books
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-book-hover transition-all duration-300 cursor-pointer">
            <CardHeader>
              <div className="bg-storybook-gold/20 rounded-full w-12 h-12 flex items-center justify-center mb-4">
                <Users className="h-6 w-6 text-storybook-leather" />
              </div>
              <CardTitle>My Groups</CardTitle>
              <CardDescription>
                Connect and share with reading communities
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button className="w-full" onClick={() => router.push('/groups')}>
                View Groups
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-book-hover transition-all duration-300 cursor-pointer">
            <CardHeader>
              <div className="bg-storybook-gold/20 rounded-full w-12 h-12 flex items-center justify-center mb-4">
                <Search className="h-6 w-6 text-storybook-leather" />
              </div>
              <CardTitle>Discover</CardTitle>
              <CardDescription>
                Find your next great read
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button className="w-full" onClick={() => router.push('/search')}>
                Search Books
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Stats Section */}
        <Card className="bg-gradient-to-r from-storybook-leather to-storybook-leather-dark text-storybook-cream">
          <CardHeader>
            <CardTitle className="text-storybook-gold">Your Reading Stats</CardTitle>
            <CardDescription className="text-storybook-gold-light">
              Track your reading journey
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-6 text-center">
              <div>
                <p className="text-3xl font-display font-bold text-storybook-gold mb-2">0</p>
                <p className="text-sm text-storybook-cream">Books Owned</p>
              </div>
              <div>
                <p className="text-3xl font-display font-bold text-storybook-gold mb-2">0</p>
                <p className="text-sm text-storybook-cream">Books Borrowed</p>
              </div>
              <div>
                <p className="text-3xl font-display font-bold text-storybook-gold mb-2">0</p>
                <p className="text-sm text-storybook-cream">Books Shared</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>

      {/* Footer */}
      <footer className="bg-storybook-leather text-storybook-cream mt-20">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <p className="font-script text-xl mb-2">
              "A reader lives a thousand lives before he dies"
            </p>
            <p className="text-storybook-gold-light text-sm">
              - George R.R. Martin
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
