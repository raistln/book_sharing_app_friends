'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/hooks/use-auth';
import { useMyGroups } from '@/lib/hooks/use-groups';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Book, Plus, LogOut, Loader2, Users, Crown, Calendar } from 'lucide-react';

export default function GroupsPage() {
  const router = useRouter();
  const { user, isAuthenticated, logout, isLoadingUser } = useAuth();
  const { groups, isLoading } = useMyGroups();

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
          <p className="text-storybook-ink-light font-serif">Cargando...</p>
        </div>
      </div>
    );
  }

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
                  <p className="text-sm text-storybook-gold-light">Mis Grupos</p>
                </div>
              </Link>
              <nav className="hidden md:flex gap-4">
                <Link href="/dashboard">
                  <Button variant="ghost" className="text-storybook-cream hover:bg-storybook-leather-dark">
                    Dashboard
                  </Button>
                </Link>
                <Link href="/books">
                  <Button variant="ghost" className="text-storybook-cream hover:bg-storybook-leather-dark">
                    My Books
                  </Button>
                </Link>
                <Link href="/groups">
                  <Button variant="ghost" className="text-storybook-gold hover:bg-storybook-leather-dark">
                    Groups
                  </Button>
                </Link>
                <Link href="/search">
                  <Button variant="ghost" className="text-storybook-cream hover:bg-storybook-leather-dark">
                    Discover
                  </Button>
                </Link>
              </nav>
            </div>
            <Button onClick={logout} variant="outline" className="border-storybook-gold text-storybook-leather hover:text-storybook-cream hover:bg-storybook-leather-dark">
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
              Mis Grupos
            </h2>
            <p className="text-storybook-ink-light">
              {groups.length} {groups.length === 1 ? 'grupo' : 'grupos'}
            </p>
          </div>
          <div className="flex gap-3">
            <Link href="/groups/join">
              <Button size="lg" variant="outline" className="shadow-lg">
                <Users className="mr-2 h-5 w-5" />
                Unirse con Código
              </Button>
            </Link>
            <Link href="/groups/new">
              <Button size="lg" className="shadow-lg">
                <Plus className="mr-2 h-5 w-5" />
                Crear Grupo
              </Button>
            </Link>
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center items-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-storybook-leather" />
          </div>
        )}

        {/* Empty State */}
        {!isLoading && groups.length === 0 && (
          <Card className="text-center py-12">
            <CardContent>
              <Users className="h-16 w-16 text-storybook-leather opacity-30 mx-auto mb-4" />
              <h3 className="font-display text-2xl font-bold text-storybook-leather mb-2">
                No tienes grupos aún
              </h3>
              <p className="text-storybook-ink-light mb-6">
                Crea tu primer grupo para compartir libros con amigos
              </p>
              <Link href="/groups/new">
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Crear Mi Primer Grupo
                </Button>
              </Link>
            </CardContent>
          </Card>
        )}

        {/* Groups Grid */}
        {!isLoading && groups.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {groups.map((group) => (
              <Link key={group.id} href={`/groups/${group.id}`}>
                <Card className="hover:shadow-book-hover transition-all duration-300 cursor-pointer h-full">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="line-clamp-1 mb-2">{group.name}</CardTitle>
                        <CardDescription className="line-clamp-2 min-h-[2.5rem]">
                          {group.description || 'Sin descripción'}
                        </CardDescription>
                      </div>
                      {group.is_admin && (
                        <Badge variant="default" className="ml-2">
                          <Crown className="h-3 w-3 mr-1" />
                          Admin
                        </Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between text-sm text-storybook-ink-light">
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1">
                          <Users className="h-4 w-4" />
                          <span>{group.member_count}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Crown className="h-4 w-4" />
                          <span>{group.admin_count}</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        <span>{new Date(group.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
