"use client";

import { useState } from 'react';
import { AnimatedCard } from '@/components/ui/AnimatedCard';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { EquityCurveChart } from '@/components/charts/EquityCurveChart';

interface BacktestResult {
  total_return: number;
  annual_return: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown: number;
  win_rate: number;
  profit_factor: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  final_capital: number;
}

interface EquityPoint {
  timestamp: string;
  equity: number;
}

export default function BacktestingPage() {
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [equityCurve, setEquityCurve] = useState<EquityPoint[]>([]);
  const [formData, setFormData] = useState({
    symbol: 'AAPL',
    strategy: 'simple_ma_crossover',
    start_date: '2023-01-01',
    end_date: '2024-01-01',
    initial_capital: 100000
  });

  const strategies = [
    { value: 'simple_ma_crossover', label: 'Moving Average Crossover', description: 'Buy when fast MA crosses above slow MA' },
    { value: 'rsi_mean_reversion', label: 'RSI Mean Reversion', description: 'Trade on RSI oversold/overbought levels' },
    { value: 'bollinger_breakout', label: 'Bollinger Bands Breakout', description: 'Trade on Bollinger Band breakouts' }
  ];

  const runBacktest = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/backtesting/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          ...formData,
          start_date: new Date(formData.start_date).toISOString(),
          end_date: new Date(formData.end_date).toISOString(),
          strategy_params: {}
        })
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);

        // Generate mock equity curve data
        const startDate = new Date(formData.start_date);
        const endDate = new Date(formData.end_date);
        const days = Math.floor((endDate.getTime() - startDate.getTime()) / 86400000);
        const equityData: EquityPoint[] = [];

        let currentEquity = formData.initial_capital;
        const dailyReturn = data.total_return / 100 / days;

        for (let i = 0; i <= days; i += Math.floor(days / 50) || 1) {
          const date = new Date(startDate.getTime() + i * 86400000);
          const volatility = (Math.random() - 0.5) * 0.02;
          currentEquity = currentEquity * (1 + dailyReturn + volatility);

          equityData.push({
            timestamp: date.toISOString(),
            equity: currentEquity
          });
        }

        // Ensure final equity matches the result
        equityData[equityData.length - 1].equity = data.final_capital;
        setEquityCurve(equityData);
      }
    } catch (error) {
      console.error('Error running backtest:', error);
    } finally {
      setLoading(false);
    }
  };

  const getMetricColor = (value: number, threshold: number, inverse: boolean = false) => {
    const isGood = inverse ? value < threshold : value > threshold;
    return isGood ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50 to-pink-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Backtesting Engine
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Test trading strategies on historical data
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Configuration Panel */}
          <div className="lg:col-span-1">
            <AnimatedCard variant="glass" className="p-6 sticky top-8">
              <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
                Configuration
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Symbol
                  </label>
                  <input
                    type="text"
                    value={formData.symbol}
                    onChange={(e) => setFormData({ ...formData, symbol: e.target.value.toUpperCase() })}
                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500"
                    placeholder="AAPL"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Strategy
                  </label>
                  <select
                    value={formData.strategy}
                    onChange={(e) => setFormData({ ...formData, strategy: e.target.value })}
                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500"
                  >
                    {strategies.map(s => (
                      <option key={s.value} value={s.value}>{s.label}</option>
                    ))}
                  </select>
                  <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    {strategies.find(s => s.value === formData.strategy)?.description}
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    End Date
                  </label>
                  <input
                    type="date"
                    value={formData.end_date}
                    onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Initial Capital ($)
                  </label>
                  <input
                    type="number"
                    value={formData.initial_capital}
                    onChange={(e) => setFormData({ ...formData, initial_capital: Number(e.target.value) })}
                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500"
                    min="1000"
                    step="1000"
                  />
                </div>

                <button
                  onClick={runBacktest}
                  disabled={loading}
                  className="w-full px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-lg font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <LoadingSpinner size="sm" />
                      Running...
                    </span>
                  ) : (
                    'Run Backtest'
                  )}
                </button>
              </div>
            </AnimatedCard>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-2">
            {!result ? (
              <AnimatedCard variant="glass" className="p-12 text-center">
                <div className="text-gray-500 dark:text-gray-400">
                  <svg className="w-20 h-20 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <p className="text-lg font-medium">No backtest results yet</p>
                  <p className="text-sm mt-2">Configure your strategy and click "Run Backtest"</p>
                </div>
              </AnimatedCard>
            ) : (
              <div className="space-y-6">
                {/* Performance Overview */}
                <AnimatedCard variant="gradient" className="p-6">
                  <h2 className="text-2xl font-bold text-white mb-6">Performance Overview</h2>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                      <p className="text-white/70 text-sm mb-1">Total Return</p>
                      <p className={`text-3xl font-bold ${getMetricColor(result.total_return, 0)}`}>
                        {result.total_return > 0 ? '+' : ''}{result.total_return.toFixed(2)}%
                      </p>
                    </div>
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                      <p className="text-white/70 text-sm mb-1">Annual Return</p>
                      <p className={`text-3xl font-bold ${getMetricColor(result.annual_return, 0)}`}>
                        {result.annual_return > 0 ? '+' : ''}{result.annual_return.toFixed(2)}%
                      </p>
                    </div>
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                      <p className="text-white/70 text-sm mb-1">Final Capital</p>
                      <p className="text-2xl font-bold text-white">
                        ${result.final_capital.toLocaleString()}
                      </p>
                    </div>
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                      <p className="text-white/70 text-sm mb-1">Profit</p>
                      <p className={`text-2xl font-bold ${getMetricColor(result.final_capital - formData.initial_capital, 0)}`}>
                        ${(result.final_capital - formData.initial_capital).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </AnimatedCard>

                {/* Equity Curve Chart */}
                {equityCurve.length > 0 && (
                  <EquityCurveChart
                    data={equityCurve}
                    initialCapital={formData.initial_capital}
                  />
                )}

                {/* Risk Metrics */}
                <AnimatedCard className="p-6">
                  <h3 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Risk Metrics</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-gray-50 dark:bg-slate-800 rounded-lg p-4">
                      <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Sharpe Ratio</p>
                      <p className={`text-2xl font-bold ${getMetricColor(result.sharpe_ratio, 1)}`}>
                        {result.sharpe_ratio.toFixed(2)}
                      </p>
                    </div>
                    <div className="bg-gray-50 dark:bg-slate-800 rounded-lg p-4">
                      <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Sortino Ratio</p>
                      <p className={`text-2xl font-bold ${getMetricColor(result.sortino_ratio, 1)}`}>
                        {result.sortino_ratio.toFixed(2)}
                      </p>
                    </div>
                    <div className="bg-gray-50 dark:bg-slate-800 rounded-lg p-4">
                      <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Max Drawdown</p>
                      <p className={`text-2xl font-bold ${getMetricColor(result.max_drawdown, -20, true)}`}>
                        -{result.max_drawdown.toFixed(2)}%
                      </p>
                    </div>
                    <div className="bg-gray-50 dark:bg-slate-800 rounded-lg p-4">
                      <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Profit Factor</p>
                      <p className={`text-2xl font-bold ${getMetricColor(result.profit_factor, 1)}`}>
                        {result.profit_factor.toFixed(2)}
                      </p>
                    </div>
                  </div>
                </AnimatedCard>

                {/* Trade Statistics */}
                <AnimatedCard className="p-6">
                  <h3 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Trade Statistics</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-gray-50 dark:bg-slate-800 rounded-lg p-4">
                      <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Total Trades</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">{result.total_trades}</p>
                    </div>
                    <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                      <p className="text-sm text-green-600 dark:text-green-400 mb-1">Winning Trades</p>
                      <p className="text-2xl font-bold text-green-700 dark:text-green-300">{result.winning_trades}</p>
                    </div>
                    <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                      <p className="text-sm text-red-600 dark:text-red-400 mb-1">Losing Trades</p>
                      <p className="text-2xl font-bold text-red-700 dark:text-red-300">{result.losing_trades}</p>
                    </div>
                    <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                      <p className="text-sm text-blue-600 dark:text-blue-400 mb-1">Win Rate</p>
                      <p className={`text-2xl font-bold ${getMetricColor(result.win_rate, 50)}`}>
                        {result.win_rate.toFixed(1)}%
                      </p>
                    </div>
                  </div>
                </AnimatedCard>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
