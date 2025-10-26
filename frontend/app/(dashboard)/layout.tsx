'use client';

import { useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/use-auth';
import { Header } from '@/components/layout/header';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, isLoadingUser } = useAuth();

  useEffect(() => {
    if (!isAuthenticated && !isLoadingUser) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoadingUser, router]);

  if (isLoadingUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-storybook-parchment via-storybook-cream to-storybook-gold-light flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-storybook-leather mx-auto mb-4" />
          <p className="text-storybook-ink-light font-serif">Cargando...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  const isLoansRoute = pathname?.startsWith('/loans');

  return (
    <div
      className={cn(
        'min-h-screen bg-gradient-to-br from-storybook-parchment via-storybook-cream to-storybook-gold-light',
        !isLoansRoute && 'storybook-silhouettes storybook-silhouettes-dashboard'
      )}
    >
      <Header />
      {children}
    </div>
  );
}
