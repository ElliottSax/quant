import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/** Merge Tailwind class names (shadcn/ui convention). */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export function formatCurrency(value: number | null | undefined, currency = 'USD'): string {
  const n = typeof value === 'number' && Number.isFinite(value) ? value : 0;
  return new Intl.NumberFormat('en-US', { style: 'currency', currency, maximumFractionDigits: 2 }).format(n);
}

export function formatPercent(value: number | null | undefined, digits = 2): string {
  const n = typeof value === 'number' && Number.isFinite(value) ? value : 0;
  return `${n >= 0 ? '' : ''}${n.toFixed(digits)}%`;
}

export function formatDate(value: string | number | Date | null | undefined): string {
  if (!value) return '';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}
