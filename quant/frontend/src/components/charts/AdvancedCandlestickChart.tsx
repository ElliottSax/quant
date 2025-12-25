"use client";

import { useEffect, useRef, useState, useCallback } from 'react';
import { createChart, CandlestickData, HistogramData, Time } from 'lightweight-charts';
import type { IChartApi } from 'lightweight-charts';

interface OHLCData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface AdvancedCandlestickChartProps {
  data: OHLCData[];
  symbol: string;
  height?: number;
  showVolume?: boolean;
  showSMA?: boolean;
  showRSI?: boolean;
  showBollingerBands?: boolean;
  onCrosshairMove?: (price: number | null, time: string | null) => void;
}

// Calculate SMA
function calculateSMA(data: OHLCData[], period: number): { time: Time; value: number }[] {
  const result: { time: Time; value: number }[] = [];
  for (let i = period - 1; i < data.length; i++) {
    let sum = 0;
    for (let j = 0; j < period; j++) {
      sum += data[i - j].close;
    }
    result.push({
      time: data[i].timestamp as Time,
      value: sum / period,
    });
  }
  return result;
}

// Calculate RSI
function calculateRSI(data: OHLCData[], period: number = 14): { time: Time; value: number }[] {
  const result: { time: Time; value: number }[] = [];
  const gains: number[] = [];
  const losses: number[] = [];

  for (let i = 1; i < data.length; i++) {
    const change = data[i].close - data[i - 1].close;
    gains.push(change > 0 ? change : 0);
    losses.push(change < 0 ? Math.abs(change) : 0);
  }

  for (let i = period; i < gains.length; i++) {
    const avgGain = gains.slice(i - period, i).reduce((a, b) => a + b, 0) / period;
    const avgLoss = losses.slice(i - period, i).reduce((a, b) => a + b, 0) / period;
    const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
    const rsi = 100 - (100 / (1 + rs));
    result.push({
      time: data[i + 1].timestamp as Time,
      value: rsi,
    });
  }
  return result;
}

// Calculate Bollinger Bands
function calculateBollingerBands(data: OHLCData[], period: number = 20, multiplier: number = 2): {
  upper: { time: Time; value: number }[];
  middle: { time: Time; value: number }[];
  lower: { time: Time; value: number }[];
} {
  const upper: { time: Time; value: number }[] = [];
  const middle: { time: Time; value: number }[] = [];
  const lower: { time: Time; value: number }[] = [];

  for (let i = period - 1; i < data.length; i++) {
    const slice = data.slice(i - period + 1, i + 1);
    const sma = slice.reduce((sum, d) => sum + d.close, 0) / period;
    const variance = slice.reduce((sum, d) => sum + Math.pow(d.close - sma, 2), 0) / period;
    const stdDev = Math.sqrt(variance);

    middle.push({ time: data[i].timestamp as Time, value: sma });
    upper.push({ time: data[i].timestamp as Time, value: sma + multiplier * stdDev });
    lower.push({ time: data[i].timestamp as Time, value: sma - multiplier * stdDev });
  }

  return { upper, middle, lower };
}

export function AdvancedCandlestickChart({
  data,
  symbol,
  height = 500,
  showVolume = true,
  showSMA = true,
  showRSI = false,
  showBollingerBands = false,
  onCrosshairMove,
}: AdvancedCandlestickChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const rsiContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const rsiChartRef = useRef<IChartApi | null>(null);
  const [currentPrice, setCurrentPrice] = useState<number | null>(null);
  const [priceChange, setPriceChange] = useState<{ value: number; percent: number } | null>(null);
  const [timeRange, setTimeRange] = useState<'1D' | '1W' | '1M' | '3M' | '1Y' | 'ALL'>('ALL');

  const initChart = useCallback(() => {
    if (!chartContainerRef.current || data.length === 0) return;

    // Cleanup existing charts
    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
    }
    if (rsiChartRef.current) {
      rsiChartRef.current.remove();
      rsiChartRef.current = null;
    }

    // Professional dark theme
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: showRSI ? height - 120 : height,
      layout: {
        background: { color: 'transparent' },
        textColor: '#9ca3af',
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
      },
      grid: {
        vertLines: { color: 'rgba(42, 46, 57, 0.5)' },
        horzLines: { color: 'rgba(42, 46, 57, 0.5)' },
      },
      crosshair: {
        mode: 1,
        vertLine: {
          color: 'rgba(99, 102, 241, 0.5)',
          width: 1,
          style: 2,
          labelBackgroundColor: '#6366f1',
        },
        horzLine: {
          color: 'rgba(99, 102, 241, 0.5)',
          width: 1,
          style: 2,
          labelBackgroundColor: '#6366f1',
        },
      },
      timeScale: {
        borderColor: 'rgba(42, 46, 57, 0.8)',
        timeVisible: true,
        secondsVisible: false,
      },
      rightPriceScale: {
        borderColor: 'rgba(42, 46, 57, 0.8)',
        scaleMargins: {
          top: 0.1,
          bottom: showVolume ? 0.25 : 0.1,
        },
      },
      handleScale: {
        axisPressedMouseMove: true,
      },
      handleScroll: {
        vertTouchDrag: true,
      },
    });

    chartRef.current = chart;

    // Use type assertion for v5 API compatibility
    const chartAny = chart as any;

    // Candlestick series
    const candlestickSeries = chartAny.addCandlestickSeries({
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderUpColor: '#22c55e',
      borderDownColor: '#ef4444',
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    });

    const candleData: CandlestickData[] = data.map((d) => ({
      time: d.timestamp as Time,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));

    candlestickSeries.setData(candleData);

    // Volume series
    if (showVolume) {
      const volumeSeries = chartAny.addHistogramSeries({
        priceFormat: { type: 'volume' },
        priceScaleId: '',
      });

      volumeSeries.priceScale().applyOptions({
        scaleMargins: {
          top: 0.85,
          bottom: 0,
        },
      });

      const volumeData: HistogramData[] = data.map((d, i) => ({
        time: d.timestamp as Time,
        value: d.volume,
        color: i > 0 && d.close >= data[i - 1].close
          ? 'rgba(34, 197, 94, 0.4)'
          : 'rgba(239, 68, 68, 0.4)',
      }));

      volumeSeries.setData(volumeData);
    }

    // SMA lines
    if (showSMA && data.length >= 50) {
      const sma20 = calculateSMA(data, 20);
      const sma50 = calculateSMA(data, 50);

      const sma20Series = chartAny.addLineSeries({
        color: '#f59e0b',
        lineWidth: 1,
        title: 'SMA 20',
      });
      sma20Series.setData(sma20);

      const sma50Series = chartAny.addLineSeries({
        color: '#8b5cf6',
        lineWidth: 1,
        title: 'SMA 50',
      });
      sma50Series.setData(sma50);
    }

    // Bollinger Bands
    if (showBollingerBands && data.length >= 20) {
      const bb = calculateBollingerBands(data);

      const bbUpperSeries = chartAny.addLineSeries({
        color: 'rgba(59, 130, 246, 0.5)',
        lineWidth: 1,
        title: 'BB Upper',
      });
      bbUpperSeries.setData(bb.upper);

      const bbLowerSeries = chartAny.addLineSeries({
        color: 'rgba(59, 130, 246, 0.5)',
        lineWidth: 1,
        title: 'BB Lower',
      });
      bbLowerSeries.setData(bb.lower);
    }

    // RSI Chart
    if (showRSI && rsiContainerRef.current && data.length >= 15) {
      const rsiChart = createChart(rsiContainerRef.current, {
        width: rsiContainerRef.current.clientWidth,
        height: 100,
        layout: {
          background: { color: 'transparent' },
          textColor: '#9ca3af',
          fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
        },
        grid: {
          vertLines: { color: 'rgba(42, 46, 57, 0.5)' },
          horzLines: { color: 'rgba(42, 46, 57, 0.5)' },
        },
        timeScale: {
          borderColor: 'rgba(42, 46, 57, 0.8)',
          visible: false,
        },
        rightPriceScale: {
          borderColor: 'rgba(42, 46, 57, 0.8)',
        },
      });

      rsiChartRef.current = rsiChart;
      const rsiChartAny = rsiChart as any;

      const rsiSeries = rsiChartAny.addLineSeries({
        color: '#6366f1',
        lineWidth: 2,
        title: 'RSI',
      });

      rsiSeries.setData(calculateRSI(data));

      // RSI levels
      const rsiUpperLevel = rsiChartAny.addLineSeries({
        color: 'rgba(239, 68, 68, 0.5)',
        lineWidth: 1,
        lineStyle: 2,
      });
      const rsiLowerLevel = rsiChartAny.addLineSeries({
        color: 'rgba(34, 197, 94, 0.5)',
        lineWidth: 1,
        lineStyle: 2,
      });

      const rsiData = calculateRSI(data);
      if (rsiData.length > 0) {
        rsiUpperLevel.setData(rsiData.map(d => ({ time: d.time, value: 70 })));
        rsiLowerLevel.setData(rsiData.map(d => ({ time: d.time, value: 30 })));
      }

      // Sync time scales
      chart.timeScale().subscribeVisibleLogicalRangeChange((range) => {
        if (range) {
          rsiChart.timeScale().setVisibleLogicalRange(range);
        }
      });
    }

    // Crosshair sync
    chart.subscribeCrosshairMove((param) => {
      if (param.point && param.time) {
        const priceData = param.seriesData.get(candlestickSeries) as CandlestickData | undefined;
        if (priceData) {
          setCurrentPrice(priceData.close);
          onCrosshairMove?.(priceData.close, param.time as string);
        }
      }
    });

    // Set current price and change
    if (data.length > 0) {
      const lastPrice = data[data.length - 1].close;
      const firstPrice = data[0].close;
      setCurrentPrice(lastPrice);
      setPriceChange({
        value: lastPrice - firstPrice,
        percent: ((lastPrice - firstPrice) / firstPrice) * 100,
      });
    }

    chart.timeScale().fitContent();

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
        if (rsiChartRef.current && rsiContainerRef.current) {
          rsiChartRef.current.applyOptions({ width: rsiContainerRef.current.clientWidth });
        }
      }
    };

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [data, height, showVolume, showSMA, showRSI, showBollingerBands, onCrosshairMove]);

  useEffect(() => {
    const cleanup = initChart();
    return () => {
      cleanup?.();
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
      if (rsiChartRef.current) {
        rsiChartRef.current.remove();
        rsiChartRef.current = null;
      }
    };
  }, [initChart]);

  const formatPrice = (price: number) => {
    return price.toLocaleString('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  };

  return (
    <div className="relative bg-slate-900/50 backdrop-blur-xl rounded-2xl border border-slate-700/50 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700/50">
        <div className="flex items-center gap-4">
          <div>
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              {symbol}
              <span className="px-2 py-0.5 text-xs font-medium bg-indigo-500/20 text-indigo-400 rounded-full">
                LIVE
              </span>
            </h3>
            {currentPrice && (
              <div className="flex items-center gap-2 mt-1">
                <span className="text-2xl font-semibold text-white">
                  {formatPrice(currentPrice)}
                </span>
                {priceChange && (
                  <span className={`text-sm font-medium px-2 py-0.5 rounded ${
                    priceChange.value >= 0
                      ? 'text-green-400 bg-green-500/10'
                      : 'text-red-400 bg-red-500/10'
                  }`}>
                    {priceChange.value >= 0 ? '+' : ''}{formatPrice(priceChange.value)}
                    ({priceChange.percent >= 0 ? '+' : ''}{priceChange.percent.toFixed(2)}%)
                  </span>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Time range selector */}
        <div className="flex items-center gap-1 bg-slate-800/50 rounded-lg p-1">
          {(['1D', '1W', '1M', '3M', '1Y', 'ALL'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                timeRange === range
                  ? 'bg-indigo-500 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Chart Legend */}
      <div className="flex items-center gap-4 px-4 py-2 border-b border-slate-700/50 text-xs">
        {showSMA && (
          <>
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-0.5 bg-amber-500 rounded-full" />
              <span className="text-slate-400">SMA 20</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-0.5 bg-purple-500 rounded-full" />
              <span className="text-slate-400">SMA 50</span>
            </div>
          </>
        )}
        {showBollingerBands && (
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-0.5 bg-blue-500/50 rounded-full" />
            <span className="text-slate-400">Bollinger Bands</span>
          </div>
        )}
        {showVolume && (
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 bg-gradient-to-t from-green-500/40 to-transparent rounded" />
            <span className="text-slate-400">Volume</span>
          </div>
        )}
      </div>

      {/* Main Chart */}
      <div ref={chartContainerRef} className="w-full" />

      {/* RSI Chart */}
      {showRSI && (
        <div className="border-t border-slate-700/50">
          <div className="px-4 py-1 flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">RSI (14)</span>
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <span className="text-red-400">Overbought: 70</span>
              <span className="text-green-400">Oversold: 30</span>
            </div>
          </div>
          <div ref={rsiContainerRef} className="w-full" />
        </div>
      )}

      {/* Footer Stats */}
      <div className="grid grid-cols-4 gap-4 p-4 border-t border-slate-700/50 bg-slate-800/30">
        {data.length > 0 && (
          <>
            <div>
              <p className="text-xs text-slate-500 mb-0.5">Open</p>
              <p className="text-sm font-semibold text-white">
                {formatPrice(data[data.length - 1].open)}
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-500 mb-0.5">High</p>
              <p className="text-sm font-semibold text-green-400">
                {formatPrice(data[data.length - 1].high)}
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-500 mb-0.5">Low</p>
              <p className="text-sm font-semibold text-red-400">
                {formatPrice(data[data.length - 1].low)}
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-500 mb-0.5">Volume</p>
              <p className="text-sm font-semibold text-white">
                {data[data.length - 1].volume.toLocaleString()}
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
