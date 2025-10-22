'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/hooks/use-auth';
import { Button } from '@/components/ui/button';
import { Book, LogOut, User } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { NotificationBell } from '@/components/notifications/notification-bell';

interface HeaderProps {
  title?: string;
  subtitle?: string;
}

export function Header({ title = 'Book Sharing App', subtitle }: HeaderProps) {
  const { user, logout } = useAuth();
  const pathname = usePathname();

  const isActive = (path: string) => pathname === path;

  return (
    <header className="bg-storybook-leather text-storybook-cream shadow-book sticky top-0 z-10">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link href="/dashboard" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
              <Book className="h-8 w-8 text-storybook-gold" />
              <div>
                <h1 className="font-display text-2xl font-bold">{title}</h1>
                {subtitle && <p className="text-sm text-storybook-gold-light">{subtitle}</p>}
              </div>
            </Link>
            <nav className="hidden md:flex gap-4">
              <Link href="/dashboard">
                <Button
                  variant="ghost"
                  className={
                    isActive('/dashboard')
                      ? 'text-storybook-gold hover:bg-storybook-leather-dark'
                      : 'text-storybook-cream hover:bg-storybook-leather-dark'
                  }
                >
                  Dashboard
                </Button>
              </Link>
              <Link href="/books">
                <Button
                  variant="ghost"
                  className={
                    isActive('/books') || pathname?.startsWith('/books/')
                      ? 'text-storybook-gold hover:bg-storybook-leather-dark'
                      : 'text-storybook-cream hover:bg-storybook-leather-dark'
                  }
                >
                  My Books
                </Button>
              </Link>
              <Link href="/groups">
                <Button
                  variant="ghost"
                  className={
                    isActive('/groups') || pathname?.startsWith('/groups/')
                      ? 'text-storybook-gold hover:bg-storybook-leather-dark'
                      : 'text-storybook-cream hover:bg-storybook-leather-dark'
                  }
                >
                  Groups
                </Button>
              </Link>
              <Link href="/search">
                <Button
                  variant="ghost"
                  className={
                    isActive('/search')
                      ? 'text-storybook-gold hover:bg-storybook-leather-dark'
                      : 'text-storybook-cream hover:bg-storybook-leather-dark'
                  }
                >
                  Discover
                </Button>
              </Link>
              <Link href="/loans">
                <Button
                  variant="ghost"
                  className={
                    isActive('/loans') || pathname?.startsWith('/loans/')
                      ? 'text-storybook-gold hover:bg-storybook-leather-dark'
                      : 'text-storybook-cream hover:bg-storybook-leather-dark'
                  }
                >
                  Loans
                </Button>
              </Link>
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <NotificationBell />
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="rounded-full bg-storybook-gold-light hover:bg-storybook-gold"
                >
                  <User className="h-5 w-5 text-storybook-leather" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium">{user?.username}</p>
                    <p className="text-xs text-muted-foreground">{user?.email}</p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link href="/profile" className="cursor-pointer">
                    <User className="mr-2 h-4 w-4" />
                    Mi Perfil
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={logout} className="cursor-pointer text-red-600">
                  <LogOut className="mr-2 h-4 w-4" />
                  Cerrar Sesión
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </header>
  );
}
