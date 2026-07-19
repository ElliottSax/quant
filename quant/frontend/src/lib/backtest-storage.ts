/**
 * Client-side persistence for saved backtest results (localStorage-backed).
 * Restored module (referenced by src/app/backtesting/*). All functions are
 * SSR-safe: on the server (no window) reads return empty and writes are no-ops.
 */

export interface BacktestResultRecord {
  id: string;
  name: string;
  symbol: string;
  strategyId?: string;
  totalReturn: number;
  equity?: number[];
  result?: unknown;
  createdAt: string;
  [key: string]: unknown;
}

const KEY = 'quant_backtest_results';

function readAll(): BacktestResultRecord[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = window.localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as BacktestResultRecord[]) : [];
  } catch {
    return [];
  }
}

function writeAll(records: BacktestResultRecord[]): void {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(KEY, JSON.stringify(records));
  } catch {
    /* quota / disabled storage — ignore */
  }
}

export function getBacktestResults(): BacktestResultRecord[] {
  return readAll().sort((a, b) => (b.createdAt || '').localeCompare(a.createdAt || ''));
}

export function getBacktestResult(id: string): BacktestResultRecord | null {
  return readAll().find((r) => r.id === id) || null;
}

export function saveBacktestResult(record: Partial<BacktestResultRecord>): string {
  const id = record.id || `bt_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  const full: BacktestResultRecord = {
    name: 'Untitled backtest',
    symbol: '',
    totalReturn: 0,
    createdAt: new Date().toISOString(),
    ...record,
    id,
  };
  const all = readAll().filter((r) => r.id !== id);
  all.push(full);
  writeAll(all);
  return id;
}

export function deleteBacktestResult(id: string): void {
  writeAll(readAll().filter((r) => r.id !== id));
}
