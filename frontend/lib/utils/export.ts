import type { Loan } from '@/lib/types/loan';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

// Exportar préstamos a CSV
export function exportLoansToCSV(loans: Loan[], filename: string = 'prestamos.csv'): void {
  // Encabezados
  const headers = [
    'ID',
    'Libro',
    'Autor',
    'Prestatario',
    'Prestador',
    'Estado',
    'Fecha Solicitud',
    'Fecha Aprobación',
    'Fecha Devolución',
    'Fecha Límite',
  ];

  // Convertir préstamos a filas CSV
  const rows = loans.map((loan) => [
    loan.id,
    loan.book?.title || '',
    loan.book?.author || '',
    loan.borrower?.username || '',
    loan.lender?.username || '',
    loan.status,
    format(new Date(loan.requested_at), 'dd/MM/yyyy HH:mm', { locale: es }),
    loan.approved_at ? format(new Date(loan.approved_at), 'dd/MM/yyyy HH:mm', { locale: es }) : '',
    loan.returned_at ? format(new Date(loan.returned_at), 'dd/MM/yyyy HH:mm', { locale: es }) : '',
    loan.due_date ? format(new Date(loan.due_date), 'dd/MM/yyyy', { locale: es }) : '',
  ]);

  // Crear contenido CSV
  const csvContent = [
    headers.join(','),
    ...rows.map((row) =>
      row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(',')
    ),
  ].join('\n');

  // Crear y descargar archivo
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Exportar préstamos a JSON
export function exportLoansToJSON(loans: Loan[], filename: string = 'prestamos.json'): void {
  const jsonContent = JSON.stringify(loans, null, 2);
  
  const blob = new Blob([jsonContent], { type: 'application/json' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Generar HTML para PDF (se puede usar con jsPDF o similar)
export function generateLoansPDFHTML(loans: Loan[]): string {
  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Historial de Préstamos</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          padding: 20px;
          color: #333;
        }
        h1 {
          color: #5D4E37;
          border-bottom: 2px solid #D4AF37;
          padding-bottom: 10px;
        }
        table {
          width: 100%;
          border-collapse: collapse;
          margin-top: 20px;
        }
        th, td {
          border: 1px solid #ddd;
          padding: 12px;
          text-align: left;
        }
        th {
          background-color: #5D4E37;
          color: white;
        }
        tr:nth-child(even) {
          background-color: #f9f9f9;
        }
        .status {
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: bold;
        }
        .status-PENDING { background-color: #fef3c7; color: #92400e; }
        .status-APPROVED { background-color: #d1fae5; color: #065f46; }
        .status-ACTIVE { background-color: #dbeafe; color: #1e40af; }
        .status-RETURNED { background-color: #f3f4f6; color: #374151; }
        .status-REJECTED { background-color: #fee2e2; color: #991b1b; }
        .footer {
          margin-top: 30px;
          text-align: center;
          color: #666;
          font-size: 12px;
        }
      </style>
    </head>
    <body>
      <h1>📚 Historial de Préstamos</h1>
      <p><strong>Fecha de generación:</strong> ${format(new Date(), 'PPP', { locale: es })}</p>
      <p><strong>Total de préstamos:</strong> ${loans.length}</p>
      
      <table>
        <thead>
          <tr>
            <th>Libro</th>
            <th>Autor</th>
            <th>Prestatario</th>
            <th>Prestador</th>
            <th>Estado</th>
            <th>Solicitado</th>
            <th>Devuelto</th>
          </tr>
        </thead>
        <tbody>
          ${loans
            .map(
              (loan) => `
            <tr>
              <td>${loan.book?.title || 'N/A'}</td>
              <td>${loan.book?.author || 'N/A'}</td>
              <td>${loan.borrower?.username || 'N/A'}</td>
              <td>${loan.lender?.username || 'N/A'}</td>
              <td><span class="status status-${loan.status}">${loan.status}</span></td>
              <td>${format(new Date(loan.requested_at), 'dd/MM/yyyy', { locale: es })}</td>
              <td>${loan.returned_at ? format(new Date(loan.returned_at), 'dd/MM/yyyy', { locale: es }) : '-'}</td>
            </tr>
          `
            )
            .join('')}
        </tbody>
      </table>
      
      <div class="footer">
        <p>Book Sharing App - Generado automáticamente</p>
      </div>
    </body>
    </html>
  `;
  
  return html;
}

// Exportar a PDF usando window.print
export function exportLoansToPDF(loans: Loan[]): void {
  const html = generateLoansPDFHTML(loans);
  
  // Crear ventana temporal
  const printWindow = window.open('', '_blank');
  if (!printWindow) {
    alert('Por favor, permite las ventanas emergentes para exportar a PDF');
    return;
  }
  
  printWindow.document.write(html);
  printWindow.document.close();
  
  // Esperar a que cargue y luego imprimir
  printWindow.onload = () => {
    printWindow.print();
  };
}

// Estadísticas para el reporte
export function generateLoanStats(loans: Loan[]) {
  return {
    total: loans.length,
    pending: loans.filter((l) => l.status === 'PENDING').length,
    approved: loans.filter((l) => l.status === 'APPROVED').length,
    active: loans.filter((l) => l.status === 'ACTIVE').length,
    returned: loans.filter((l) => l.status === 'RETURNED').length,
    rejected: loans.filter((l) => l.status === 'REJECTED').length,
    overdue: loans.filter(
      (l) =>
        (l.status === 'APPROVED' || l.status === 'ACTIVE') &&
        l.due_date &&
        new Date(l.due_date) < new Date()
    ).length,
  };
}
