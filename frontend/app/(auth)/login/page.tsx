'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/hooks/use-auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Book, Sparkles, Loader2, AlertCircle } from 'lucide-react';
import type { LoginRequest } from '@/lib/types/api';

export default function LoginPage() {
  const { login, isLoggingIn, loginError } = useAuth();
  const [formData, setFormData] = useState<LoginRequest>({
    username: '',
    password: '',
  });

  const [error, setError] = useState<string>('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const loginData: LoginRequest = {
      username: formData.username,
      password: formData.password
    };

    login(loginData);
  };

  // Actualizar el estado de error cuando cambie el error del hook
  React.useEffect(() => {
    if (loginError) {
      setError(loginError.response?.data?.detail || loginError.response?.data?.message || 'Error de autenticación');
    }
  }, [loginError]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-storybook-parchment via-storybook-cream to-storybook-gold-light flex items-center justify-center p-4 storybook-silhouettes storybook-silhouettes-auth">
      {/* Elementos decorativos */}
      <div className="absolute top-10 left-10 animate-float">
        <Sparkles className="h-8 w-8 text-storybook-gold opacity-50" />
      </div>
      <div className="absolute bottom-10 right-10 animate-float" style={{ animationDelay: '1s' }}>
        <Book className="h-10 w-10 text-storybook-leather opacity-30" />
      </div>

      <div className="w-full max-w-md">
        {/* Logotipo / Cabecera */}
        <div className="text-center mb-8 animate-fade-in-up">
          <div className="inline-block mb-4">
            <Book className="h-16 w-16 text-storybook-leather mx-auto" />
          </div>
          <h1 className="font-display text-4xl font-bold text-storybook-leather mb-2">
            ¡Hola de nuevo!
          </h1>
          <p className="text-storybook-ink-light font-serif">
            Continúa tu aventura lectora
          </p>
        </div>

        {/* Tarjeta de acceso */}
        <Card className="animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
          <CardHeader>
            <CardTitle>Iniciar sesión</CardTitle>
            <CardDescription>
              Introduce tus credenciales para acceder a tu biblioteca
            </CardDescription>
          </CardHeader>
          {error && (
            <div className="px-6 pb-4">
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md text-red-800 text-sm">
                <AlertCircle className="h-4 w-4" />
                <span>{error}</span>
              </div>
            </div>
          )}
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">Usuario o correo electrónico</Label>
                <Input
                  id="username"
                  type="text"
                  placeholder="Escribe tu usuario o correo"
                  value={formData.username}
                  onChange={(e) => {
                    setFormData({ ...formData, username: e.target.value });
                    if (error) setError('');
                  }}
                  required
                  disabled={isLoggingIn}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Contraseña</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Escribe tu contraseña"
                  value={formData.password}
                  onChange={(e) => {
                    setFormData({ ...formData, password: e.target.value });
                    if (error) setError('');
                  }}
                  required
                  disabled={isLoggingIn}
                />
              </div>
            </CardContent>
            <CardFooter className="flex flex-col space-y-4">
              <Button
                type="submit"
                className="w-full"
                disabled={isLoggingIn}
              >
                {isLoggingIn ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Conectando...
                  </>
                ) : (
                  <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Acceder
                  </>
                )}
              </Button>
              <div className="text-center text-sm text-storybook-ink-light">
                ¿Aún no tienes cuenta?{' '}
                <Link
                  href="/register"
                  className="text-storybook-leather hover:text-storybook-leather-dark font-semibold underline"
                >
                  Crear una
                </Link>
              </div>
            </CardFooter>
          </form>
        </Card>

        {/* Volver al inicio */}
        <div className="text-center mt-6">
          <Link
            href="/"
            className="text-sm text-storybook-ink-light hover:text-storybook-leather transition-colors"
          >
            ← Volver al inicio
          </Link>
        </div>
      </div>
    </div>
  );
}
