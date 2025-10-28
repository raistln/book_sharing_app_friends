'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useMyProfile, useMyStats } from '@/lib/hooks/use-profile';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Book,
  Loader2,
  Edit,
  Mail,
  MapPin,
  Calendar,
  Users,
  BookOpen,
  Star,
  ArrowLeft,
  User,
} from 'lucide-react';

export default function ProfilePage() {
  const { profile, isLoading: loadingProfile } = useMyProfile();
  const { stats, isLoading: loadingStats } = useMyStats();

  if (loadingProfile) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-storybook-leather mx-auto mb-4" />
          <p className="text-storybook-ink-light font-serif">Cargando perfil...</p>
        </div>
      </div>
    );
  }

  return (
    <main className="container mx-auto px-4 py-12">
        {/* Back Button */}
        <Link href="/dashboard">
          <Button variant="ghost" className="mb-6">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Volver al Dashboard
          </Button>
        </Link>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Profile Card */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between mb-4">
                  <CardTitle>Perfil</CardTitle>
                  <Link href="/profile/edit">
                    <Button size="sm" variant="outline">
                      <Edit className="h-4 w-4 mr-2" />
                      Editar
                    </Button>
                  </Link>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col items-center text-center">
                  {/* Avatar */}
                  <div className="w-32 h-32 bg-storybook-gold-light rounded-full flex items-center justify-center mb-4">
                    {profile?.avatar_url ? (
                      <Image
                        src={profile.avatar_url}
                        alt={profile.username ?? 'Avatar del usuario'}
                        width={128}
                        height={128}
                        className="w-full h-full rounded-full object-cover"
                      />
                    ) : (
                      <User className="h-16 w-16 text-storybook-leather" />
                    )}
                  </div>

                  {/* User Info */}
                  <h2 className="font-display text-2xl font-bold text-storybook-leather mb-1">
                    {profile?.full_name || profile?.username}
                  </h2>
                  <p className="text-storybook-ink-light mb-4">@{profile?.username}</p>

                  {profile?.is_active && (
                    <Badge variant="default" className="mb-4">
                      Activo
                    </Badge>
                  )}

                  {/* Bio */}
                  {profile?.bio && (
                    <p className="text-sm text-storybook-ink-light mb-4 text-center">
                      {profile.bio}
                    </p>
                  )}

                  {/* Contact Info */}
                  <div className="w-full space-y-3 mt-4">
                    <div className="flex items-center gap-2 text-sm text-storybook-ink-light">
                      <Mail className="h-4 w-4" />
                      <span className="truncate">{profile?.email}</span>
                    </div>
                    {profile?.location && (
                      <div className="flex items-center gap-2 text-sm text-storybook-ink-light">
                        <MapPin className="h-4 w-4" />
                        <span>{profile.location}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2 text-sm text-storybook-ink-light">
                      <Calendar className="h-4 w-4" />
                      <span>
                        Miembro desde {new Date(profile?.created_at || '').toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Stats and Activity */}
          <div className="lg:col-span-2 space-y-6">
            {/* Stats Grid */}
            <Card>
              <CardHeader>
                <CardTitle>Estadísticas</CardTitle>
                <CardDescription>Tu actividad en la plataforma</CardDescription>
              </CardHeader>
              <CardContent>
                {loadingStats ? (
                  <div className="flex justify-center py-8">
                    <Loader2 className="h-8 w-8 animate-spin text-storybook-leather" />
                  </div>
                ) : (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-storybook-parchment rounded-lg text-center">
                      <Book className="h-8 w-8 text-storybook-leather mx-auto mb-2" />
                      <p className="text-2xl font-bold text-storybook-leather">
                        {stats?.books_owned || 0}
                      </p>
                      <p className="text-sm text-storybook-ink-light">Libros Propios</p>
                    </div>
                    <div className="p-4 bg-storybook-parchment rounded-lg text-center">
                      <BookOpen className="h-8 w-8 text-storybook-leather mx-auto mb-2" />
                      <p className="text-2xl font-bold text-storybook-leather">
                        {stats?.books_borrowed || 0}
                      </p>
                      <p className="text-sm text-storybook-ink-light">Libros Prestados</p>
                    </div>
                    <div className="p-4 bg-storybook-parchment rounded-lg text-center">
                      <Users className="h-8 w-8 text-storybook-leather mx-auto mb-2" />
                      <p className="text-2xl font-bold text-storybook-leather">
                        {stats?.groups_count || 0}
                      </p>
                      <p className="text-sm text-storybook-ink-light">Grupos</p>
                    </div>
                    <div className="p-4 bg-storybook-parchment rounded-lg text-center">
                      <Star className="h-8 w-8 text-storybook-leather mx-auto mb-2" />
                      <p className="text-2xl font-bold text-storybook-leather">
                        {stats?.reviews_count || 0}
                      </p>
                      <p className="text-sm text-storybook-ink-light">Reseñas</p>
                    </div>
                    <div className="p-4 bg-storybook-parchment rounded-lg text-center">
                      <BookOpen className="h-8 w-8 text-storybook-leather mx-auto mb-2" />
                      <p className="text-2xl font-bold text-storybook-leather">
                        {stats?.active_loans || 0}
                      </p>
                      <p className="text-sm text-storybook-ink-light">Préstamos Activos</p>
                    </div>
                    {stats?.average_rating !== undefined && (
                      <div className="p-4 bg-storybook-parchment rounded-lg text-center">
                        <Star className="h-8 w-8 text-storybook-gold mx-auto mb-2" />
                        <p className="text-2xl font-bold text-storybook-leather">
                          {stats.average_rating.toFixed(1)}
                        </p>
                        <p className="text-sm text-storybook-ink-light">Rating Promedio</p>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Acciones Rápidas</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Link href="/books">
                    <Button variant="outline" className="w-full justify-start">
                      <Book className="mr-2 h-4 w-4" />
                      Ver Mis Libros
                    </Button>
                  </Link>
                  <Link href="/groups">
                    <Button variant="outline" className="w-full justify-start">
                      <Users className="mr-2 h-4 w-4" />
                      Ver Mis Grupos
                    </Button>
                  </Link>
                  <Link href="/profile/edit">
                    <Button variant="outline" className="w-full justify-start">
                      <Edit className="mr-2 h-4 w-4" />
                      Editar Perfil
                    </Button>
                  </Link>
                  <Link href="/search">
                    <Button variant="outline" className="w-full justify-start">
                      <BookOpen className="mr-2 h-4 w-4" />
                      Descubrir Libros
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
    </main>
  );
}
