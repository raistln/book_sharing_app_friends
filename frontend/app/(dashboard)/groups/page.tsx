'use client';

import Link from 'next/link';
import { useMyGroups } from '@/lib/hooks/use-groups';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Plus, Loader2, Users, Crown, Calendar } from 'lucide-react';

export default function GroupsPage() {
  const { groups, isLoading } = useMyGroups();

  return (
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
  );
}
