"use client";

import { useState, useEffect } from 'react';
import { AnimatedCard } from '@/components/ui/AnimatedCard';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { PriceChart } from '@/components/charts/PriceChart';

interface TradingSignal {
  symbol: string;
  signal_type: string;
  confidence: string;
  confidence_score: number;
  price: number;
  timestamp: string;
  risk_score: number;
  target_price?: number;
  stop_loss?: number;
  reasoning: string;
  indicators: Record<string, number>;
}

interface PriceData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export default function SignalsPage() {
  const [signals, setSignals] = useState<TradingSignal[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [watchlist] = useState(['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']);
  const [priceData, setPriceData] = useState<PriceData[]>([]);

  const generateSignal = async (symbol: string) => {
    setLoading(true);
    try {
      // Generate mock price data for demo
      const prices = Array.from({ length: 50 }, (_, i) => {
        const base = 150;
        const trend = i * 0.5;
        const noise = (Math.random() - 0.5) * 10;
        return base + trend + noise;
      });

      // Generate OHLCV data for chart
      const now = new Date();
      const chartData: PriceData[] = prices.map((price, i) => {
        const timestamp = new Date(now.getTime() - (50 - i) * 86400000); // Daily bars
        const volatility = price * 0.02;
        return {
          timestamp: timestamp.toISOString(),
          open: price + (Math.random() - 0.5) * volatility,
          high: price + Math.random() * volatility * 1.5,
          low: price - Math.random() * volatility * 1.5,
          close: price,
          volume: Math.floor(Math.random() * 10000000) + 1000000
        };
      });
      setPriceData(chartData);

      const response = await fetch('/api/v1/signals/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          symbol,
          price_data: prices,
          use_ai: true
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSignals(prev => [data.signal, ...prev].slice(0, 10));
      }
    } catch (error) {
      console.error('Error generating signal:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSignalColor = (signalType: string) => {
    const colors: Record<string, string> = {
      'strong_buy': 'text-green-600 dark:text-green-400',
      'buy': 'text-green-500 dark:text-green-300',
      'hold': 'text-gray-500 dark:text-gray-400',
      'sell': 'text-red-500 dark:text-red-300',
      'strong_sell': 'text-red-600 dark:text-red-400'
    };
    return colors[signalType] || 'text-gray-500';
  };

  const getSignalBadgeColor = (signalType: string) => {
    const colors: Record<string, string> = {
      'strong_buy': 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200',
      'buy': 'bg-green-50 dark:bg-green-800 text-green-700 dark:text-green-100',
      'hold': 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300',
      'sell': 'bg-red-50 dark:bg-red-800 text-red-700 dark:text-red-100',
      'strong_sell': 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
    };
    return colors[signalType] || 'bg-gray-100';
  };

  const formatSignalType = (type: string) => {
    return type.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Trading Signals
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            AI-powered trading signals with technical analysis
          </p>
        </div>

        {/* Watchlist */}
        <AnimatedCard className="mb-8">
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
              Watchlist
            </h2>
            <div className="flex gap-3 flex-wrap">
              {watchlist.map(symbol => (
                <button
                  key={symbol}
                  onClick={() => setSelectedSymbol(symbol)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    selectedSymbol === symbol
                      ? 'bg-blue-500 text-white shadow-lg scale-105'
                      : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-slate-700'
                  }`}
                >
                  {symbol}
                </button>
              ))}
            </div>
          </div>
        </AnimatedCard>

        {/* Generate Signal Button */}
        <div className="mb-8 flex justify-center">
          <button
            onClick={() => generateSignal(selectedSymbol)}
            disabled={loading}
            className="px-8 py-4 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg font-semibold text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <LoadingSpinner size="sm" />
                Generating Signal...
              </span>
            ) : (
              `Generate Signal for ${selectedSymbol}`
            )}
          </button>
        </div>

        {/* Price Chart */}
        {priceData.length > 0 && (
          <div className="mb-8">
            <PriceChart data={priceData} symbol={selectedSymbol} />
          </div>
        )}

        {/* Signals List */}
        <div className="space-y-4">
          {signals.length === 0 ? (
            <AnimatedCard variant="glass" className="p-12 text-center">
              <div className="text-gray-500 dark:text-gray-400">
                <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <p className="text-lg font-medium">No signals generated yet</p>
                <p className="text-sm mt-2">Click the button above to generate your first trading signal</p>
              </div>
            </AnimatedCard>
          ) : (
            signals.map((signal, idx) => (
              <AnimatedCard key={idx} variant="glass" className="p-6 hover:shadow-xl transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                        {signal.symbol}
                      </h3>
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getSignalBadgeColor(signal.signal_type)}`}>
                        {formatSignalType(signal.signal_type)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {new Date(signal.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-3xl font-bold text-gray-900 dark:text-white">
                      ${signal.price.toFixed(2)}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Current Price
                    </p>
                  </div>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="bg-white dark:bg-slate-800 rounded-lg p-3">
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Confidence</p>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">
                      {(signal.confidence_score * 100).toFixed(0)}%
                    </p>
                  </div>
                  <div className="bg-white dark:bg-slate-800 rounded-lg p-3">
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Risk Score</p>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">
                      {signal.risk_score.toFixed(0)}/100
                    </p>
                  </div>
                  {signal.target_price && (
                    <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                      <p className="text-xs text-green-600 dark:text-green-400 mb-1">Target</p>
                      <p className="text-lg font-semibold text-green-700 dark:text-green-300">
                        ${signal.target_price.toFixed(2)}
                      </p>
                    </div>
                  )}
                  {signal.stop_loss && (
                    <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
                      <p className="text-xs text-red-600 dark:text-red-400 mb-1">Stop Loss</p>
                      <p className="text-lg font-semibold text-red-700 dark:text-red-300">
                        ${signal.stop_loss.toFixed(2)}
                      </p>
                    </div>
                  )}
                </div>

                {/* Reasoning */}
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 mb-4">
                  <p className="text-sm text-blue-900 dark:text-blue-100">
                    <strong>Analysis:</strong> {signal.reasoning}
                  </p>
                </div>

                {/* Technical Indicators */}
                <details className="group">
                  <summary className="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400">
                    View Technical Indicators ({Object.keys(signal.indicators).length})
                  </summary>
                  <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-2">
                    {Object.entries(signal.indicators).map(([key, value]) => (
                      <div key={key} className="bg-gray-50 dark:bg-slate-800 rounded p-2">
                        <p className="text-xs text-gray-500 dark:text-gray-400">{key.toUpperCase()}</p>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {typeof value === 'number' ? value.toFixed(2) : value}
                        </p>
                      </div>
                    ))}
                  </div>
                </details>
              </AnimatedCard>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
