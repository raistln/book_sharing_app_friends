'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/use-auth';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Book, Users, Search, LogOut, Sparkles, Loader2, BookOpen } from 'lucide-react';

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
          <p className="text-storybook-ink-light font-serif">Cargando tu biblioteca...</p>
        </div>
      </div>
    );
  }

  return (
    <main className="container mx-auto px-4 py-12">
        {/* Sección de bienvenida */}
        <div className="mb-12 text-center animate-fade-in-up">
          <div className="inline-block mb-4">
            <Sparkles className="h-12 w-12 text-storybook-gold animate-float mx-auto" />
          </div>
          <h2 className="font-display text-4xl font-bold text-storybook-leather mb-4">
            Te damos la bienvenida a tu biblioteca
          </h2>
          <p className="text-xl text-storybook-ink-light max-w-2xl mx-auto">
            Tu viaje lector comienza aquí. Explora, comparte y descubre libros increíbles.
          </p>
        </div>

        {/* Acciones rápidas */}
        <div className="grid sm:grid-cols-2 gap-6 mb-12">
          <Card className="hover:shadow-book-hover transition-all duration-300 cursor-pointer">
            <CardHeader>
              <div className="bg-storybook-gold/20 rounded-full w-12 h-12 flex items-center justify-center mb-4">
                <Book className="h-6 w-6 text-storybook-leather" />
              </div>
              <CardTitle>Mis libros</CardTitle>
              <CardDescription>
                Gestiona tu colección personal de libros
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button className="w-full" onClick={() => router.push('/books')}>
                Ver libros
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-book-hover transition-all duration-300 cursor-pointer">
            <CardHeader>
              <div className="bg-storybook-gold/20 rounded-full w-12 h-12 flex items-center justify-center mb-4">
                <Users className="h-6 w-6 text-storybook-leather" />
              </div>
              <CardTitle>Mis grupos</CardTitle>
              <CardDescription>
                Conecta y comparte con comunidades lectoras
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button className="w-full" onClick={() => router.push('/groups')}>
                Ver grupos
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-book-hover transition-all duration-300 cursor-pointer">
            <CardHeader>
              <div className="bg-storybook-gold/20 rounded-full w-12 h-12 flex items-center justify-center mb-4">
                <Search className="h-6 w-6 text-storybook-leather" />
              </div>
              <CardTitle>Descubre</CardTitle>
              <CardDescription>
                Encuentra tu próxima gran lectura
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button className="w-full" onClick={() => router.push('/search')}>
                Buscar libros
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-book-hover transition-all duration-300 cursor-pointer">
            <CardHeader>
              <div className="bg-storybook-gold/20 rounded-full w-12 h-12 flex items-center justify-center mb-4">
                <BookOpen className="h-6 w-6 text-storybook-leather" />
              </div>
              <CardTitle>Mis préstamos</CardTitle>
              <CardDescription>
                Gestiona tus préstamos y solicitudes
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button className="w-full" onClick={() => router.push('/loans')}>
                Ver préstamos
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Sección de estadísticas */}
        <Card className="bg-gradient-to-r from-storybook-leather to-storybook-leather-dark text-storybook-cream">
          <CardHeader>
            <CardTitle className="text-storybook-gold">Tus estadísticas de lectura</CardTitle>
            <CardDescription className="text-storybook-gold-light">
              Sigue tu viaje lector
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-6 text-center">
              <div>
                <p className="text-3xl font-display font-bold text-storybook-gold mb-2">0</p>
                <p className="text-sm text-storybook-cream">Libros propios</p>
              </div>
              <div>
                <p className="text-3xl font-display font-bold text-storybook-gold mb-2">0</p>
                <p className="text-sm text-storybook-cream">Libros prestados</p>
              </div>
              <div>
                <p className="text-3xl font-display font-bold text-storybook-gold mb-2">0</p>
                <p className="text-sm text-storybook-cream">Libros compartidos</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Pie de página */}
        <footer className="bg-storybook-leather text-storybook-cream mt-20 -mx-4 px-4">
          <div className="container mx-auto px-4 py-8">
            <div className="text-center">
              <p className="font-script text-xl mb-2">
                «Un lector vive mil vidas antes de morir»
              </p>
              <p className="text-storybook-gold-light text-sm">
                - George R. R. Martin
              </p>
            </div>
          </div>
        </footer>
      </main>
  );
}
