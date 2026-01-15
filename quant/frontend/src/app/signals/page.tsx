"use client";

import { useState, useMemo, useEffect, useCallback } from 'react';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import { PriceChart } from '@/components/charts/PriceChart';

const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

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
  history?: number[];
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
  const [watchlist] = useState(['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META']);
  const [priceData, setPriceData] = useState<PriceData[]>([]);
  const [activeTab, setActiveTab] = useState<'signals' | 'analysis'>('signals');
  const [initialized, setInitialized] = useState(false);

  const generateSignal = useCallback(async (symbol: string, addToList = true) => {
    setLoading(true);
    try {
      // Generate mock price data for demo
      const base = 100 + Math.random() * 200;
      const prices = Array.from({ length: 50 }, (_, i) => {
        const trend = i * (Math.random() - 0.3) * 0.5;
        const noise = (Math.random() - 0.5) * 10;
        return base + trend + noise;
      });

      // Generate OHLCV data for chart
      const now = new Date();
      const chartData: PriceData[] = prices.map((price, i) => {
        const timestamp = new Date(now.getTime() - (50 - i) * 86400000);
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

      // Generate mock signal
      const signalTypes = ['strong_buy', 'buy', 'hold', 'sell', 'strong_sell'];
      const signalType = signalTypes[Math.floor(Math.random() * signalTypes.length)];
      const confidence = 0.6 + Math.random() * 0.35;
      const currentPrice = prices[prices.length - 1];

      const mockSignal: TradingSignal = {
        symbol,
        signal_type: signalType,
        confidence: signalType.includes('strong') ? 'high' : signalType === 'hold' ? 'medium' : 'moderate',
        confidence_score: confidence,
        price: currentPrice,
        timestamp: new Date().toISOString(),
        risk_score: Math.random() * 100,
        target_price: signalType.includes('buy') ? currentPrice * (1 + 0.05 + Math.random() * 0.15) : undefined,
        stop_loss: signalType.includes('buy') ? currentPrice * (1 - 0.03 - Math.random() * 0.05) : undefined,
        reasoning: getSignalReasoning(signalType, symbol),
        indicators: {
          RSI: 30 + Math.random() * 40,
          MACD: (Math.random() - 0.5) * 5,
          'MACD Signal': (Math.random() - 0.5) * 4,
          'Bollinger %B': Math.random(),
          'SMA 20': currentPrice * (0.95 + Math.random() * 0.1),
          'SMA 50': currentPrice * (0.9 + Math.random() * 0.2),
          'EMA 12': currentPrice * (0.97 + Math.random() * 0.06),
          'Volume Ratio': 0.5 + Math.random() * 1.5,
          'ATR': currentPrice * 0.02 * (1 + Math.random()),
          'Stochastic %K': Math.random() * 100,
        },
        history: Array.from({ length: 20 }, () => Math.random() * 100),
      };

      if (addToList) {
        setSignals(prev => [mockSignal, ...prev].slice(0, 10));
      }
      return mockSignal;
    } catch (error) {
      console.error('Error generating signal:', error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-load signals on page mount
  useEffect(() => {
    if (!initialized) {
      setInitialized(true);
      // Generate initial signals for all watchlist stocks
      const generateInitialSignals = async () => {
        setLoading(true);
        const initialSignals: TradingSignal[] = [];

        for (const symbol of watchlist) {
          const signal = await generateSignal(symbol, false);
          if (signal) {
            initialSignals.push(signal);
          }
        }

        setSignals(initialSignals);
        setLoading(false);

        // Also generate price data for the selected symbol
        generateSignal(selectedSymbol, false);
      };

      generateInitialSignals();
    }
  }, [initialized, watchlist, generateSignal, selectedSymbol]);

  const getSignalReasoning = (signalType: string, symbol: string) => {
    const reasons: Record<string, string[]> = {
      strong_buy: [
        `${symbol} shows strong bullish momentum with RSI recovering from oversold. MACD crossover confirmed with increasing volume.`,
        `Technical breakout above key resistance with strong institutional buying. Multiple moving averages turning bullish.`,
        `Golden cross formation detected with strong volume confirmation. Sentiment indicators highly bullish.`,
      ],
      buy: [
        `${symbol} testing support with bullish divergence on RSI. Risk/reward ratio favorable for entry.`,
        `Price consolidation near support with decreasing selling pressure. Watch for volume confirmation.`,
        `Bullish engulfing pattern on daily chart with positive sector momentum.`,
      ],
      hold: [
        `${symbol} trading in a range. Wait for clearer directional signal before taking action.`,
        `Mixed signals across timeframes. Maintain current position and monitor key levels.`,
        `Consolidation phase - neither bulls nor bears in control. Key support and resistance levels holding.`,
      ],
      sell: [
        `${symbol} showing weakness below moving averages. Consider reducing position size.`,
        `Bearish divergence forming on RSI with declining volume on rallies.`,
        `Breaking below support with negative momentum. Protect gains with trailing stops.`,
      ],
      strong_sell: [
        `${symbol} in confirmed downtrend. Death cross with high volume selling pressure.`,
        `Major breakdown below key support with bearish sentiment. Exit recommended.`,
        `Multiple technical indicators flashing sell. Significant downside risk identified.`,
      ],
    };
    const typeReasons = reasons[signalType] || reasons.hold;
    return typeReasons[Math.floor(Math.random() * typeReasons.length)];
  };

  const formatSignalType = (type: string) => {
    return type.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  };

  // Gauge chart for confidence
  const getGaugeOptions = (value: number, title: string, color: string) => ({
    backgroundColor: 'transparent',
    series: [
      {
        type: 'gauge',
        startAngle: 180,
        endAngle: 0,
        min: 0,
        max: 100,
        splitNumber: 5,
        radius: '100%',
        center: ['50%', '70%'],
        axisLine: {
          lineStyle: {
            width: 12,
            color: [
              [0.3, '#ef4444'],
              [0.7, '#eab308'],
              [1, '#22c55e']
            ]
          }
        },
        pointer: {
          icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
          length: '60%',
          width: 8,
          offsetCenter: [0, '-20%'],
          itemStyle: { color: color }
        },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        title: {
          offsetCenter: [0, '10%'],
          fontSize: 14,
          color: '#94a3b8',
        },
        detail: {
          fontSize: 28,
          offsetCenter: [0, '-10%'],
          valueAnimation: true,
          formatter: (value: number) => `${value.toFixed(0)}%`,
          color: color,
          fontWeight: 'bold',
        },
        data: [{ value: value, name: title }]
      }
    ]
  });

  // Indicator sparkline
  const getSparklineOptions = (data: number[], color: string) => ({
    backgroundColor: 'transparent',
    grid: { left: 0, right: 0, top: 0, bottom: 0 },
    xAxis: { type: 'category', show: false, data: data.map((_, i) => i) },
    yAxis: { type: 'value', show: false, min: Math.min(...data) * 0.95, max: Math.max(...data) * 1.05 },
    series: [{
      type: 'line',
      data: data,
      smooth: true,
      symbol: 'none',
      lineStyle: { width: 2, color },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: color + '40' },
            { offset: 1, color: color + '00' }
          ]
        }
      }
    }]
  });

  // Technical indicator distribution
  const getIndicatorRadarOptions = (indicators: Record<string, number>) => {
    const rsi = indicators.RSI || 50;
    const macd = Math.min(100, Math.max(0, 50 + (indicators.MACD || 0) * 10));
    const bollingerB = (indicators['Bollinger %B'] || 0.5) * 100;
    const stochK = indicators['Stochastic %K'] || 50;
    const volumeRatio = Math.min(100, (indicators['Volume Ratio'] || 1) * 50);

    return {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(0,0,0,0.8)',
        textStyle: { color: '#fff' },
      },
      radar: {
        indicator: [
          { name: 'RSI', max: 100 },
          { name: 'MACD', max: 100 },
          { name: 'Bollinger', max: 100 },
          { name: 'Stochastic', max: 100 },
          { name: 'Volume', max: 100 },
        ],
        shape: 'polygon',
        splitNumber: 4,
        axisName: { color: '#94a3b8', fontSize: 11 },
        splitLine: { lineStyle: { color: '#1e293b' } },
        splitArea: { show: true, areaStyle: { color: ['rgba(30,41,59,0.3)', 'rgba(15,23,42,0.3)'] } },
        axisLine: { lineStyle: { color: '#334155' } },
      },
      series: [{
        type: 'radar',
        data: [{
          value: [rsi, macd, bollingerB, stochK, volumeRatio],
          name: 'Indicators',
          lineStyle: { color: '#3b82f6', width: 2 },
          areaStyle: { color: 'rgba(59,130,246,0.3)' },
          itemStyle: { color: '#3b82f6' },
          symbol: 'circle',
          symbolSize: 6,
        }]
      }]
    };
  };

  // Signal history chart
  const signalHistoryOptions = useMemo(() => {
    if (signals.length === 0) return {};

    const signalCounts = { strong_buy: 0, buy: 0, hold: 0, sell: 0, strong_sell: 0 };
    signals.forEach(s => {
      if (s.signal_type in signalCounts) {
        signalCounts[s.signal_type as keyof typeof signalCounts]++;
      }
    });

    return {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(0,0,0,0.8)',
        textStyle: { color: '#fff' },
      },
      series: [{
        type: 'pie',
        radius: ['50%', '75%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#0f172a',
          borderWidth: 2,
        },
        label: { show: false },
        emphasis: {
          label: { show: true, fontSize: 14, fontWeight: 'bold', color: '#fff' },
          itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' }
        },
        labelLine: { show: false },
        data: [
          { value: signalCounts.strong_buy, name: 'Strong Buy', itemStyle: { color: '#22c55e' } },
          { value: signalCounts.buy, name: 'Buy', itemStyle: { color: '#4ade80' } },
          { value: signalCounts.hold, name: 'Hold', itemStyle: { color: '#94a3b8' } },
          { value: signalCounts.sell, name: 'Sell', itemStyle: { color: '#f87171' } },
          { value: signalCounts.strong_sell, name: 'Strong Sell', itemStyle: { color: '#ef4444' } },
        ].filter(d => d.value > 0)
      }]
    };
  }, [signals]);

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
              Analyzing {selectedSymbol}...
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

      {/* Tabs */}
      {signals.length > 0 && (
        <div className="flex gap-2 border-b border-border/50 animate-fade-in" style={{ animationDelay: '250ms', animationFillMode: 'backwards' }}>
          <button
            onClick={() => setActiveTab('signals')}
            className={`px-6 py-3 font-semibold transition-all ${
              activeTab === 'signals'
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Signal Cards
          </button>
          <button
            onClick={() => setActiveTab('analysis')}
            className={`px-6 py-3 font-semibold transition-all ${
              activeTab === 'analysis'
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Technical Analysis
          </button>
        </div>
      )}

      {/* Price Chart */}
      {priceData.length > 0 && (
        <div className="animate-fade-in" style={{ animationDelay: '300ms', animationFillMode: 'backwards' }}>
          <PriceChart data={priceData} symbol={selectedSymbol} />
        </div>
      )}

      {/* Signals Content */}
      {activeTab === 'signals' && (
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

                {/* Gauge Charts Row */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-card border border-border rounded-xl p-4">
                    <div className="h-[120px]">
                      <ReactECharts
                        option={getGaugeOptions(
                          signal.confidence_score * 100,
                          'Confidence',
                          signal.confidence_score > 0.7 ? '#22c55e' : signal.confidence_score > 0.5 ? '#eab308' : '#ef4444'
                        )}
                        style={{ height: '100%', width: '100%' }}
                      />
                    </div>
                  </div>
                  <div className="bg-card border border-border rounded-xl p-4">
                    <div className="h-[120px]">
                      <ReactECharts
                        option={getGaugeOptions(
                          100 - signal.risk_score,
                          'Safety',
                          signal.risk_score < 30 ? '#22c55e' : signal.risk_score < 60 ? '#eab308' : '#ef4444'
                        )}
                        style={{ height: '100%', width: '100%' }}
                      />
                    </div>
                  </div>
                  {signal.target_price && (
                    <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-4">
                      <p className="text-xs font-semibold text-green-500 mb-2">Target Price</p>
                      <p className="text-2xl font-bold text-green-500">
                        ${signal.target_price.toFixed(2)}
                      </p>
                      <p className="text-xs text-green-500/70 mt-1">
                        +{((signal.target_price / signal.price - 1) * 100).toFixed(1)}% upside
                      </p>
                    </div>
                  )}
                  {signal.stop_loss && (
                    <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4">
                      <p className="text-xs font-semibold text-red-500 mb-2">Stop Loss</p>
                      <p className="text-2xl font-bold text-red-500">
                        ${signal.stop_loss.toFixed(2)}
                      </p>
                      <p className="text-xs text-red-500/70 mt-1">
                        {((signal.stop_loss / signal.price - 1) * 100).toFixed(1)}% risk
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

                {/* Indicator Radar + Sparkline */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div className="bg-muted/30 rounded-xl p-4 border border-border/50">
                    <p className="text-sm font-semibold text-muted-foreground mb-2">Technical Profile</p>
                    <div className="h-[200px]">
                      <ReactECharts option={getIndicatorRadarOptions(signal.indicators)} style={{ height: '100%', width: '100%' }} />
                    </div>
                  </div>
                  {signal.history && (
                    <div className="bg-muted/30 rounded-xl p-4 border border-border/50">
                      <p className="text-sm font-semibold text-muted-foreground mb-2">Momentum Trend</p>
                      <div className="h-[200px]">
                        <ReactECharts
                          option={getSparklineOptions(
                            signal.history,
                            signal.signal_type.includes('buy') ? '#22c55e' : signal.signal_type === 'hold' ? '#94a3b8' : '#ef4444'
                          )}
                          style={{ height: '100%', width: '100%' }}
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Technical Indicators Grid */}
                <details className="group">
                  <summary className="cursor-pointer text-sm font-semibold text-muted-foreground hover:text-primary transition-colors flex items-center gap-2">
                    <svg className="w-4 h-4 group-open:rotate-90 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                    View All Technical Indicators ({Object.keys(signal.indicators).length})
                  </summary>
                  <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-3">
                    {Object.entries(signal.indicators).map(([key, value]) => {
                      let color = '#94a3b8';
                      if (key === 'RSI') {
                        color = value > 70 ? '#ef4444' : value < 30 ? '#22c55e' : '#94a3b8';
                      } else if (key === 'MACD') {
                        color = value > 0 ? '#22c55e' : '#ef4444';
                      } else if (key === 'Stochastic %K') {
                        color = value > 80 ? '#ef4444' : value < 20 ? '#22c55e' : '#94a3b8';
                      }

                      return (
                        <div key={key} className="bg-muted/30 rounded-lg p-3 border border-border/50 hover:border-primary/30 transition-colors">
                          <p className="text-xs font-semibold text-muted-foreground mb-1">{key}</p>
                          <p className="text-sm font-bold" style={{ color }}>
                            {typeof value === 'number' ? value.toFixed(2) : value}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                </details>
              </div>
            ))
          )}
        </div>
      )}

      {/* Technical Analysis Tab */}
      {activeTab === 'analysis' && signals.length > 0 && (
        <div className="space-y-6 animate-fade-in">
          {/* Signal Distribution */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass-strong rounded-xl p-6 border border-border/50">
              <h3 className="text-lg font-bold mb-4">Signal Distribution</h3>
              <div className="h-[250px]">
                <ReactECharts option={signalHistoryOptions} style={{ height: '100%', width: '100%' }} />
              </div>
            </div>

            <div className="glass-strong rounded-xl p-6 border border-border/50">
              <h3 className="text-lg font-bold mb-4">Recent Signal Summary</h3>
              <div className="space-y-4">
                {['strong_buy', 'buy', 'hold', 'sell', 'strong_sell'].map(type => {
                  const count = signals.filter(s => s.signal_type === type).length;
                  const percentage = signals.length > 0 ? (count / signals.length) * 100 : 0;
                  const color = type.includes('buy') ? 'bg-green-500' : type === 'hold' ? 'bg-gray-500' : 'bg-red-500';

                  return (
                    <div key={type} className="flex items-center gap-4">
                      <span className="w-24 text-sm font-medium capitalize">{type.replace('_', ' ')}</span>
                      <div className="flex-1 h-3 bg-muted rounded-full overflow-hidden">
                        <div
                          className={`h-full ${color} transition-all duration-500`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                      <span className="w-12 text-sm font-bold text-right">{count}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Average Indicators */}
          {signals.length > 0 && (
            <div className="glass-strong rounded-xl p-6 border border-border/50">
              <h3 className="text-lg font-bold mb-4">Average Technical Indicators</h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {(() => {
                  const avgIndicators: Record<string, number> = {};
                  const counts: Record<string, number> = {};

                  signals.forEach(s => {
                    Object.entries(s.indicators).forEach(([key, value]) => {
                      if (typeof value === 'number') {
                        avgIndicators[key] = (avgIndicators[key] || 0) + value;
                        counts[key] = (counts[key] || 0) + 1;
                      }
                    });
                  });

                  return Object.entries(avgIndicators).slice(0, 10).map(([key, total]) => {
                    const avg = total / (counts[key] || 1);
                    let color = '#94a3b8';
                    let status = 'Neutral';

                    if (key === 'RSI') {
                      if (avg > 70) { color = '#ef4444'; status = 'Overbought'; }
                      else if (avg < 30) { color = '#22c55e'; status = 'Oversold'; }
                    } else if (key === 'MACD') {
                      color = avg > 0 ? '#22c55e' : '#ef4444';
                      status = avg > 0 ? 'Bullish' : 'Bearish';
                    }

                    return (
                      <div key={key} className="bg-muted/30 rounded-xl p-4 border border-border/50">
                        <p className="text-xs font-semibold text-muted-foreground mb-1">{key}</p>
                        <p className="text-xl font-bold" style={{ color }}>{avg.toFixed(2)}</p>
                        <p className="text-xs mt-1" style={{ color }}>{status}</p>
                      </div>
                    );
                  });
                })()}
              </div>
            </div>
          )}

          {/* Signal Timeline */}
          <div className="glass-strong rounded-xl p-6 border border-border/50">
            <h3 className="text-lg font-bold mb-4">Signal Timeline</h3>
            <div className="space-y-3">
              {signals.map((signal, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-4 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors"
                >
                  <div className={`w-3 h-3 rounded-full ${
                    signal.signal_type.includes('buy') ? 'bg-green-500' :
                    signal.signal_type === 'hold' ? 'bg-gray-500' : 'bg-red-500'
                  }`} />
                  <span className="font-bold w-16">{signal.symbol}</span>
                  <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                    signal.signal_type.includes('buy') ? 'bg-green-500/10 text-green-500' :
                    signal.signal_type === 'hold' ? 'bg-gray-500/10 text-gray-500' : 'bg-red-500/10 text-red-500'
                  }`}>
                    {formatSignalType(signal.signal_type)}
                  </span>
                  <span className="text-sm text-muted-foreground flex-1">
                    ${signal.price.toFixed(2)}
                  </span>
                  <span className="text-sm font-medium">
                    {(signal.confidence_score * 100).toFixed(0)}% confidence
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {new Date(signal.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
