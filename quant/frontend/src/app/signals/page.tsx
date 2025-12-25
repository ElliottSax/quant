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
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-fade-in">
        <h1 className="text-4xl md:text-5xl font-bold mb-3 bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
          Trading Signals
        </h1>
        <p className="text-lg text-muted-foreground">
          AI-powered trading signals with advanced technical analysis
        </p>
      </div>

      {/* Watchlist */}
      <div className="glass-strong rounded-xl p-6 border border-border/50 animate-fade-in" style={{ animationDelay: '100ms', animationFillMode: 'backwards' }}>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">Watchlist</h2>
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </div>
        </div>
        <div className="flex gap-3 flex-wrap">
          {watchlist.map(symbol => (
            <button
              key={symbol}
              onClick={() => setSelectedSymbol(symbol)}
              className={`px-5 py-2.5 rounded-lg font-semibold transition-all ${
                selectedSymbol === symbol
                  ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/25 scale-105'
                  : 'bg-card border border-border hover:border-primary/50 hover:bg-primary/5 hover:scale-105'
              }`}
            >
              {symbol}
            </button>
          ))}
        </div>
      </div>

      {/* Generate Signal Button */}
      <div className="flex justify-center animate-fade-in" style={{ animationDelay: '200ms', animationFillMode: 'backwards' }}>
        <button
          onClick={() => generateSignal(selectedSymbol)}
          disabled={loading}
          className="btn-primary text-lg px-12 py-4 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <div className="h-5 w-5 animate-spin rounded-full border-2 border-solid border-current border-r-transparent" />
              Generating Signal...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Generate Signal for {selectedSymbol}
            </span>
          )}
        </button>
      </div>

      {/* Price Chart */}
      {priceData.length > 0 && (
        <div className="animate-fade-in" style={{ animationDelay: '300ms', animationFillMode: 'backwards' }}>
          <PriceChart data={priceData} symbol={selectedSymbol} />
        </div>
      )}

      {/* Signals List */}
      <div className="space-y-6">
        {signals.length === 0 ? (
          <div className="glass rounded-xl p-16 text-center animate-fade-in" style={{ animationDelay: '400ms', animationFillMode: 'backwards' }}>
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary/10 mb-6">
              <svg className="w-10 h-10 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <p className="text-xl font-semibold mb-2">No signals generated yet</p>
            <p className="text-muted-foreground">Click the button above to generate your first trading signal</p>
          </div>
        ) : (
          signals.map((signal, idx) => (
            <div
              key={idx}
              className="glass-strong rounded-xl p-6 border border-border/50 hover:shadow-2xl hover:border-primary/30 transition-all duration-300 animate-fade-in"
              style={{ animationDelay: `${400 + idx * 100}ms`, animationFillMode: 'backwards' }}
            >
              <div className="flex items-start justify-between mb-6">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-3xl font-bold">
                      {signal.symbol}
                    </h3>
                    <span className={`px-4 py-1.5 rounded-full text-sm font-bold border ${
                      signal.signal_type.includes('buy')
                        ? 'bg-green-500/10 text-green-500 border-green-500/20'
                        : signal.signal_type === 'hold'
                        ? 'bg-gray-500/10 text-gray-500 border-gray-500/20'
                        : 'bg-red-500/10 text-red-500 border-red-500/20'
                    }`}>
                      {formatSignalType(signal.signal_type)}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {new Date(signal.timestamp).toLocaleString()}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-4xl font-bold text-gradient-blue">
                    ${signal.price.toFixed(2)}
                  </p>
                  <p className="text-sm text-muted-foreground mt-1">
                    Current Price
                  </p>
                </div>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-card border border-border rounded-xl p-4 hover:border-primary/30 transition-colors">
                  <p className="text-xs font-semibold text-muted-foreground mb-2">Confidence</p>
                  <p className="text-2xl font-bold">
                    {(signal.confidence_score * 100).toFixed(0)}%
                  </p>
                </div>
                <div className="bg-card border border-border rounded-xl p-4 hover:border-primary/30 transition-colors">
                  <p className="text-xs font-semibold text-muted-foreground mb-2">Risk Score</p>
                  <p className="text-2xl font-bold">
                    {signal.risk_score.toFixed(0)}/100
                  </p>
                </div>
                {signal.target_price && (
                  <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-4">
                    <p className="text-xs font-semibold text-green-500 mb-2">Target</p>
                    <p className="text-2xl font-bold text-green-500">
                      ${signal.target_price.toFixed(2)}
                    </p>
                  </div>
                )}
                {signal.stop_loss && (
                  <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4">
                    <p className="text-xs font-semibold text-red-500 mb-2">Stop Loss</p>
                    <p className="text-2xl font-bold text-red-500">
                      ${signal.stop_loss.toFixed(2)}
                    </p>
                  </div>
                )}
              </div>

              {/* Reasoning */}
              <div className="bg-primary/5 border border-primary/10 rounded-xl p-4 mb-4">
                <p className="text-sm font-medium">
                  <span className="text-primary font-bold">Analysis:</span> {signal.reasoning}
                </p>
              </div>

              {/* Technical Indicators */}
              <details className="group">
                <summary className="cursor-pointer text-sm font-semibold text-muted-foreground hover:text-primary transition-colors flex items-center gap-2">
                  <svg className="w-4 h-4 group-open:rotate-90 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  View Technical Indicators ({Object.keys(signal.indicators).length})
                </summary>
                <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
                  {Object.entries(signal.indicators).map(([key, value]) => (
                    <div key={key} className="bg-muted/30 rounded-lg p-3 border border-border/50">
                      <p className="text-xs font-semibold text-muted-foreground mb-1">{key.toUpperCase()}</p>
                      <p className="text-sm font-bold">
                        {typeof value === 'number' ? value.toFixed(2) : value}
                      </p>
                    </div>
                  ))}
                </div>
              </details>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
