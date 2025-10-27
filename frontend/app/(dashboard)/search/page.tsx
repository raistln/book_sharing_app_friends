'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { useAuth } from '@/lib/hooks/use-auth';
import { useSearch, useGenres, useLanguages, useConditions } from '@/lib/hooks/use-search';
import { useMyGroups } from '@/lib/hooks/use-groups';
import { booksApi } from '@/lib/api/books';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Book, Search, Filter, X, LogOut, Loader2, Eye, SlidersHorizontal } from 'lucide-react';

export default function SearchPage() {
  const router = useRouter();
  const { user, isAuthenticated, logout, isLoadingUser } = useAuth();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    q: '',
    page: 1,
    per_page: 12,
    genre: '',
    language: '',
    available_only: false,
    condition: '',
    sort_by: 'created_at',
    sort_order: 'desc' as 'asc' | 'desc',
    group_id: '',
  });

  const { books, pagination, isLoading } = useSearch(filters);
  const { genres } = useGenres();
  const { languages } = useLanguages();
  const { conditions } = useConditions();
  const { groups } = useMyGroups();

  useEffect(() => {
    if (!isAuthenticated && !isLoadingUser) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoadingUser, router]);

  const handleSearch = () => {
    setFilters({ ...filters, q: searchQuery, page: 1 });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const clearFilters = () => {
    setSearchQuery('');
    setFilters({
      q: '',
      page: 1,
      per_page: 12,
      genre: '',
      language: '',
      available_only: false,
      condition: '',
      sort_by: 'created_at',
      sort_order: 'desc',
      group_id: '',
    });
  };

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
    <main className="container mx-auto px-4 py-12">
        {/* Barra de búsqueda */}
        <Card className="mb-8">
          <CardContent className="pt-6">
            <div className="flex gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-storybook-ink-light" />
                  <Input
                    placeholder="Busca libros por título, autor o ISBN..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={handleKeyPress}
                    className="pl-10"
                  />
                </div>
              </div>
              <Button onClick={handleSearch} disabled={isLoading}>
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <Search className="mr-2 h-4 w-4" />
                    Buscar
                  </>
                )}
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowFilters(!showFilters)}
              >
                <SlidersHorizontal className="mr-2 h-4 w-4" />
                Filtros
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Panel de filtros */}
        {showFilters && (
          <Card className="mb-8 animate-fade-in-up">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Filter className="h-5 w-5" />
                  Filtros avanzados
                </CardTitle>
                <Button variant="ghost" size="sm" onClick={clearFilters}>
                  <X className="mr-2 h-4 w-4" />
                  Limpiar todo
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Group Filter */}
                <div className="space-y-2">
                  <Label>Grupo</Label>
                  <Select
                    value={filters.group_id || 'all'}
                    onValueChange={(value) => setFilters({ ...filters, group_id: value === 'all' ? '' : value, page: 1 })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Todos los grupos" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Todos los grupos</SelectItem>
                      {groups?.map((group) => (
                        <SelectItem key={group.id} value={group.id}>
                          {group.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Genre */}
                <div className="space-y-2">
                  <Label>Género</Label>
                  <Select
                    value={filters.genre || 'all'}
                    onValueChange={(value) => setFilters({ ...filters, genre: value === 'all' ? '' : value, page: 1 })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Todos los géneros" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Todos los géneros</SelectItem>
                      {genres.map((genre) => (
                        <SelectItem key={genre} value={genre}>
                          {genre}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Language */}
                <div className="space-y-2">
                  <Label>Idioma</Label>
                  <Select
                    value={filters.language || 'all'}
                    onValueChange={(value) => setFilters({ ...filters, language: value === 'all' ? '' : value, page: 1 })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Todos los idiomas" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Todos los idiomas</SelectItem>
                      {languages.map((lang) => (
                        <SelectItem key={lang.code} value={lang.name}>
                          {lang.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Condition */}
                <div className="space-y-2">
                  <Label>Estado</Label>
                  <Select
                    value={filters.condition || 'all'}
                    onValueChange={(value) => setFilters({ ...filters, condition: value === 'all' ? '' : value, page: 1 })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Cualquier estado" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Cualquier estado</SelectItem>
                      {conditions.map((cond) => (
                        <SelectItem key={cond.value} value={cond.value}>
                          {cond.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Sort By */}
                <div className="space-y-2">
                  <Label>Ordenar por</Label>
                  <Select
                    value={filters.sort_by}
                    onValueChange={(value) => setFilters({ ...filters, sort_by: value, page: 1 })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="created_at">Fecha de alta</SelectItem>
                      <SelectItem value="title">Título</SelectItem>
                      <SelectItem value="author">Autor</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Sort Order */}
                <div className="space-y-2">
                  <Label>Orden</Label>
                  <Select
                    value={filters.sort_order}
                    onValueChange={(value: 'asc' | 'desc') => setFilters({ ...filters, sort_order: value, page: 1 })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="desc">Descendente</SelectItem>
                      <SelectItem value="asc">Ascendente</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Available Only Toggle */}
              <div className="mt-4 flex items-center gap-2">
                <input
                  type="checkbox"
                  id="available_only"
                  checked={filters.available_only}
                  onChange={(e) => setFilters({ ...filters, available_only: e.target.checked, page: 1 })}
                  className="h-4 w-4 rounded border-storybook-leather text-storybook-gold focus:ring-storybook-gold"
                />
                <Label htmlFor="available_only" className="cursor-pointer">
                  Mostrar solo libros disponibles
                </Label>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results */}
        <div className="mb-6">
          <h2 className="font-display text-2xl font-bold text-storybook-leather">
            {pagination ? `${pagination.total} libros encontrados` : 'Resultados de la búsqueda'}
          </h2>
          {filters.q && (
            <p className="text-storybook-ink-light mt-1">
              Buscando: <span className="font-semibold">"{filters.q}"</span>
            </p>
          )}
        </div>

        {/* Books Grid */}
        {isLoading ? (
          <div className="text-center py-20">
            <Loader2 className="h-12 w-12 animate-spin text-storybook-leather mx-auto mb-4" />
            <p className="text-storybook-ink-light">Buscando libros...</p>
          </div>
        ) : books.length === 0 ? (
          <Card className="text-center py-20">
            <CardContent>
              <Search className="h-16 w-16 text-storybook-leather opacity-30 mx-auto mb-4" />
              <h3 className="font-display text-2xl font-bold text-storybook-leather mb-2">
                No se han encontrado libros
              </h3>
              <p className="text-storybook-ink-light mb-6">
                Prueba a ajustar tu búsqueda o los filtros
              </p>
              <Button onClick={clearFilters} variant="outline">
                Limpiar filtros
              </Button>
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
                      src={book.cover_url || '/placeholder-book.jpg'}
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
                        {getStatusLabel(book.status)}
                      </Badge>
                    </div>
                  </div>

                  {/* Book Info */}
                  <CardHeader>
                    <CardTitle className="line-clamp-2 min-h-[3.5rem]">{book.title}</CardTitle>
                    <CardDescription className="line-clamp-1">
                      por {book.author || 'Autor desconocido'}
                    </CardDescription>
                  </CardHeader>

                  <CardContent>
                    <div className="flex flex-wrap gap-2 mb-4">
                      {book.genre && (
                        <Badge variant="outline" className="text-xs">
                          {book.genre}
                        </Badge>
                      )}
                      {book.condition && (
                        <Badge variant="secondary" className="text-xs">
                          {book.condition}
                        </Badge>
                      )}
                    </div>

                    {book.owner && (
                      <p className="text-sm text-storybook-ink-light mb-4">
                        Propietario: <span className="font-semibold">{book.owner.username}</span>
                      </p>
                    )}

                    {/* Actions */}
                    <Link href={`/books/${book.id}`} className="block">
                      <Button variant="outline" className="w-full" size="sm">
                        <Eye className="mr-2 h-3 w-3" />
                        Ver detalles
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Pagination */}
            {pagination && pagination.total_pages > 1 && (
              <div className="flex justify-center gap-2 mt-8">
                <Button
                  variant="outline"
                  onClick={() => setFilters({ ...filters, page: filters.page - 1 })}
                  disabled={filters.page === 1}
                >
                  Anterior
                </Button>
                <div className="flex items-center gap-2">
                  {Array.from({ length: Math.min(pagination.total_pages, 5) }, (_, i) => {
                    const page = i + 1;
                    return (
                      <Button
                        key={page}
                        variant={page === filters.page ? 'default' : 'outline'}
                        onClick={() => setFilters({ ...filters, page })}
                        size="sm"
                      >
                        {page}
                      </Button>
                    );
                  })}
                  {pagination.total_pages > 5 && (
                    <span className="text-storybook-ink-light">...</span>
                  )}
                </div>
                <Button
                  variant="outline"
                  onClick={() => setFilters({ ...filters, page: filters.page + 1 })}
                  disabled={filters.page === pagination.total_pages}
                >
                  Siguiente
                </Button>
              </div>
            )}
          </>
        )}
    </main>
  );
}
