'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/hooks/use-auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Book, Sparkles, Loader2 } from 'lucide-react';

export default function LoginPage() {
  const { login, isLoggingIn } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login(formData);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-storybook-parchment via-storybook-cream to-storybook-gold-light flex items-center justify-center p-4">
      {/* Decorative elements */}
      <div className="absolute top-10 left-10 animate-float">
        <Sparkles className="h-8 w-8 text-storybook-gold opacity-50" />
      </div>
      <div className="absolute bottom-10 right-10 animate-float" style={{ animationDelay: '1s' }}>
        <Book className="h-10 w-10 text-storybook-leather opacity-30" />
      </div>

      <div className="w-full max-w-md">
        {/* Logo/Header */}
        <div className="text-center mb-8 animate-fade-in-up">
          <div className="inline-block mb-4">
            <Book className="h-16 w-16 text-storybook-leather mx-auto" />
          </div>
          <h1 className="font-display text-4xl font-bold text-storybook-leather mb-2">
            Welcome Back
          </h1>
          <p className="text-storybook-ink-light font-serif">
            Continue your reading journey
          </p>
        </div>

        {/* Login Card */}
        <Card className="animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
          <CardHeader>
            <CardTitle>Sign In</CardTitle>
            <CardDescription>
              Enter your credentials to access your library
            </CardDescription>
          </CardHeader>
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">Username or Email</Label>
                <Input
                  id="username"
                  type="text"
                  placeholder="Enter your username"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  required
                  disabled={isLoggingIn}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
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
                    Signing in...
                  </>
                ) : (
                  <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Sign In
                  </>
                )}
              </Button>
              <div className="text-center text-sm text-storybook-ink-light">
                Don't have an account?{' '}
                <Link
                  href="/register"
                  className="text-storybook-leather hover:text-storybook-leather-dark font-semibold underline"
                >
                  Create one
                </Link>
              </div>
            </CardFooter>
          </form>
        </Card>

        {/* Back to home */}
        <div className="text-center mt-6">
          <Link
            href="/"
            className="text-sm text-storybook-ink-light hover:text-storybook-leather transition-colors"
          >
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}
