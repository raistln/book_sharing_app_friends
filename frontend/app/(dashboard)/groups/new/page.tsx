'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useCreateGroup } from '@/lib/hooks/use-groups';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, Users, Loader2 } from 'lucide-react';

export default function NewGroupPage() {
  const router = useRouter();
  const createGroup = useCreateGroup();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.name.trim()) {
      createGroup.mutate({
        name: formData.name.trim(),
        description: formData.description.trim() || undefined,
      });
    }
  };

  return (
    <main className="container mx-auto px-4 py-12">
        {/* Back Button */}
        <Link href="/groups">
          <Button variant="ghost" className="mb-6">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Volver a Grupos
          </Button>
        </Link>

        {/* Main Card */}
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3 mb-2">
                <div className="p-3 bg-storybook-gold-light rounded-full">
                  <Users className="h-6 w-6 text-storybook-leather" />
                </div>
                <div>
                  <CardTitle className="text-2xl">Crear Nuevo Grupo</CardTitle>
                  <CardDescription>
                    Crea un grupo para compartir libros con tus amigos
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Name */}
                <div className="space-y-2">
                  <Label htmlFor="name">
                    Nombre del Grupo <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="name"
                    type="text"
                    placeholder="Ej: Club de Lectura de Fantasía"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                    maxLength={100}
                    disabled={createGroup.isPending}
                  />
                  <p className="text-sm text-storybook-ink-light">
                    Elige un nombre descriptivo para tu grupo
                  </p>
                </div>

                {/* Description */}
                <div className="space-y-2">
                  <Label htmlFor="description">Descripción (opcional)</Label>
                  <Textarea
                    id="description"
                    placeholder="Describe de qué trata tu grupo, qué tipo de libros comparten, etc."
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    rows={4}
                    maxLength={500}
                    disabled={createGroup.isPending}
                  />
                  <p className="text-sm text-storybook-ink-light">
                    {formData.description.length}/500 caracteres
                  </p>
                </div>

                {/* Info Box */}
                <div className="bg-storybook-gold-light/30 border border-storybook-gold rounded-lg p-4">
                  <h4 className="font-semibold text-storybook-leather mb-2">
                    ℹ️ Información sobre grupos
                  </h4>
                  <ul className="text-sm text-storybook-ink-light space-y-1">
                    <li>• Serás el administrador del grupo automáticamente</li>
                    <li>• Podrás invitar a otros usuarios a unirse</li>
                    <li>• Los administradores pueden gestionar miembros y configuración</li>
                    <li>• Los grupos facilitan compartir y prestar libros entre amigos</li>
                  </ul>
                </div>

                {/* Actions */}
                <div className="flex gap-3 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => router.back()}
                    disabled={createGroup.isPending}
                    className="flex-1"
                  >
                    Cancelar
                  </Button>
                  <Button
                    type="submit"
                    disabled={!formData.name.trim() || createGroup.isPending}
                    className="flex-1"
                  >
                    {createGroup.isPending ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Creando...
                      </>
                    ) : (
                      <>
                        <Users className="mr-2 h-4 w-4" />
                        Crear Grupo
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
    </main>
  );
}
