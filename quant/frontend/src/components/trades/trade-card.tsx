/**
 * Trade Card Component
 * Displays individual trade with politician info
 */

'use client';

import { Trade } from '@/lib/api-client';
import { format } from 'date-fns';

interface TradeCardProps {
  trade: Trade;
}

export function TradeCard({ trade }: TradeCardProps) {
  const formatCurrency = (amount: number | null) => {
    if (amount === null) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), 'MMM d, yyyy');
    } catch {
      return dateString;
    }
  };

  const isBuy = trade.transaction_type === 'buy';

  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow">
      {/* Header: Ticker and Type */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-lg font-bold text-gray-900">{trade.ticker}</h3>
          <span
            className={`inline-block px-2 py-1 text-xs font-semibold rounded ${
              isBuy
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'
            }`}
          >
            {isBuy ? 'BUY' : 'SELL'}
          </span>
        </div>
        <div className="text-right">
          <div className="text-sm font-semibold text-gray-900">
            {trade.amount_min && trade.amount_max
              ? `${formatCurrency(trade.amount_min)} - ${formatCurrency(trade.amount_max)}`
              : trade.amount_min
              ? formatCurrency(trade.amount_min)
              : trade.amount_max
              ? formatCurrency(trade.amount_max)
              : 'Amount Unknown'}
          </div>
        </div>
      </div>

      {/* Politician Info */}
      <div className="mb-3 pb-3 border-b border-gray-100">
        <p className="font-medium text-gray-900">{trade.politician.name}</p>
        <p className="text-sm text-gray-600">
          {trade.politician.party && <span>{trade.politician.party} • </span>}
          <span className="capitalize">{trade.politician.chamber}</span>
          {trade.politician.state && <span> • {trade.politician.state}</span>}
        </p>
      </div>

      {/* Dates */}
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div>
          <p className="text-gray-600">Transaction Date</p>
          <p className="font-medium text-gray-900">
            {formatDate(trade.transaction_date)}
          </p>
        </div>
        <div>
          <p className="text-gray-600">Disclosed</p>
          <p className="font-medium text-gray-900">
            {formatDate(trade.disclosure_date)}
          </p>
        </div>
      </div>

      {/* Disclosure Delay */}
      {trade.disclosure_delay_days > 0 && (
        <div className="mt-2 text-xs text-gray-500">
          Disclosed {trade.disclosure_delay_days} days after transaction
        </div>
      )}
    </div>
  );
}
