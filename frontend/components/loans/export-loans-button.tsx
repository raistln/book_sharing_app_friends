'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Download, FileText, FileSpreadsheet, FileJson } from 'lucide-react';
import { exportLoansToCSV, exportLoansToJSON, exportLoansToPDF } from '@/lib/utils/export';
import type { Loan } from '@/lib/types/loan';
import { toast } from '@/components/ui/use-toast';

interface ExportLoansButtonProps {
  loans: Loan[];
  variant?: 'default' | 'outline' | 'ghost';
  size?: 'default' | 'sm' | 'lg' | 'icon';
}

export function ExportLoansButton({ loans, variant = 'outline', size = 'default' }: ExportLoansButtonProps) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async (format: 'csv' | 'json' | 'pdf') => {
    if (loans.length === 0) {
      toast({
        title: 'No hay datos para exportar',
        description: 'No tienes préstamos para exportar',
        variant: 'destructive',
      });
      return;
    }

    setIsExporting(true);

    try {
      const timestamp = new Date().toISOString().split('T')[0];
      const filename = `prestamos_${timestamp}`;

      switch (format) {
        case 'csv':
          exportLoansToCSV(loans, `${filename}.csv`);
          toast({
            title: 'Exportado a CSV',
            description: `Se han exportado ${loans.length} préstamos`,
          });
          break;
        case 'json':
          exportLoansToJSON(loans, `${filename}.json`);
          toast({
            title: 'Exportado a JSON',
            description: `Se han exportado ${loans.length} préstamos`,
          });
          break;
        case 'pdf':
          exportLoansToPDF(loans);
          toast({
            title: 'Generando PDF',
            description: 'Se abrirá una ventana para imprimir/guardar el PDF',
          });
          break;
      }
    } catch (error) {
      toast({
        title: 'Error al exportar',
        description: 'No se pudo exportar el historial',
        variant: 'destructive',
      });
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant={variant} size={size} disabled={isExporting || loans.length === 0}>
          <Download className="h-4 w-4 mr-2" />
          Exportar
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel>Formato de exportación</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={() => handleExport('pdf')}>
          <FileText className="h-4 w-4 mr-2" />
          PDF (Imprimir)
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleExport('csv')}>
          <FileSpreadsheet className="h-4 w-4 mr-2" />
          CSV (Excel)
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleExport('json')}>
          <FileJson className="h-4 w-4 mr-2" />
          JSON (Datos)
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
