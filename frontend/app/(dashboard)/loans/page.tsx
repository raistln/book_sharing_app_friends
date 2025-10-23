'use client';

import { useAuth } from '@/lib/hooks/use-auth';
import { useLoanStats, useUserLoans } from '@/lib/hooks/use-loans';
import { LoanList } from '@/components/loans/loan-list';
import { ExportLoansButton } from '@/components/loans/export-loans-button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BookOpen, Package, CheckCircle, Clock } from 'lucide-react';

export default function LoansPage() {
  const { user } = useAuth();
  const { stats, isLoading } = useLoanStats(user?.id);
  const { loans } = useUserLoans(user?.id);

  return (
    <main className="container mx-auto py-8 px-4 max-w-6xl">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-storybook-ink mb-2">Mis Préstamos</h1>
          <p className="text-storybook-ink-light">
            Gestiona tus préstamos activos y revisa el historial
          </p>
        </div>
        <ExportLoansButton loans={loans} />
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pendientes</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.pending}</div>
            <p className="text-xs text-storybook-ink-light">
              Esperando aprobación
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Activos</CardTitle>
            <Package className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.active}</div>
            <p className="text-xs text-storybook-ink-light">
              Préstamos en curso
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Lista de préstamos con tabs */}
      <LoanList userId={user?.id} showTabs={true} />
    </main>
  );
}
