/**
 * Quant Scanner Page
 * Advanced pattern recognition with interactive ECharts visualizations
 */

'use client'

import { useState, useMemo, useCallback } from 'react'
import dynamic from 'next/dynamic'
import { GaugeChart } from '@/components/charts/GaugeChart'
import { RadarChart } from '@/components/charts/RadarChart'

// Dynamic import for ECharts
const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

// Generate mock scanner results
const generatePatternResults = () => [
  { symbol: 'AAPL', pattern: 'Head & Shoulders', confidence: 87, target: 178.50, stop: 165.20, rr: 2.4, volume: 'High', sector: 'Technology', priceHistory: [172, 175, 178, 174, 170, 165, 168, 172, 176, 173] },
  { symbol: 'GOOGL', pattern: 'Double Bottom', confidence: 92, target: 148.00, stop: 132.50, rr: 3.1, volume: 'High', sector: 'Technology', priceHistory: [145, 140, 135, 132, 130, 128, 130, 135, 138, 142] },
  { symbol: 'MSFT', pattern: 'Ascending Triangle', confidence: 78, target: 395.00, stop: 368.00, rr: 1.9, volume: 'Medium', sector: 'Technology', priceHistory: [375, 378, 380, 382, 379, 385, 388, 384, 390, 387] },
  { symbol: 'TSLA', pattern: 'Bull Flag', confidence: 85, target: 265.00, stop: 238.00, rr: 2.7, volume: 'Very High', sector: 'Automotive', priceHistory: [240, 245, 250, 255, 252, 248, 252, 258, 262, 256] },
  { symbol: 'NVDA', pattern: 'Cup & Handle', confidence: 81, target: 525.00, stop: 475.00, rr: 2.2, volume: 'High', sector: 'Technology', priceHistory: [480, 490, 505, 510, 498, 485, 495, 510, 520, 505] },
  { symbol: 'META', pattern: 'Inverse H&S', confidence: 89, target: 385.00, stop: 345.00, rr: 2.8, volume: 'High', sector: 'Technology', priceHistory: [350, 355, 345, 340, 345, 360, 370, 365, 375, 368] },
  { symbol: 'AMZN', pattern: 'Symmetrical Triangle', confidence: 74, target: 158.00, stop: 142.00, rr: 1.7, volume: 'Medium', sector: 'Consumer', priceHistory: [150, 148, 152, 149, 151, 147, 150, 152, 148, 151] },
  { symbol: 'NFLX', pattern: 'Falling Wedge', confidence: 83, target: 485.00, stop: 445.00, rr: 2.5, volume: 'High', sector: 'Entertainment', priceHistory: [460, 455, 450, 448, 455, 460, 468, 475, 470, 465] },
]

const generateStatArbResults = () => [
  { pair: 'GOOGL/MSFT', zscore: 2.8, correlation: 0.89, spread: 3.2, signal: 'Long GOOGL / Short MSFT', confidence: 84, spreadHistory: [1.2, 1.8, 2.1, 2.4, 2.0, 2.6, 2.9, 3.1, 2.8, 3.2] },
  { pair: 'XOM/CVX', zscore: -2.3, correlation: 0.94, spread: -2.1, signal: 'Short XOM / Long CVX', confidence: 91, spreadHistory: [-0.5, -0.8, -1.2, -1.5, -1.8, -1.6, -1.9, -2.2, -1.9, -2.1] },
  { pair: 'JPM/BAC', zscore: 2.1, correlation: 0.87, spread: 2.8, signal: 'Long JPM / Short BAC', confidence: 78, spreadHistory: [1.0, 1.4, 1.8, 2.0, 1.8, 2.2, 2.5, 2.6, 2.7, 2.8] },
  { pair: 'KO/PEP', zscore: -1.9, correlation: 0.92, spread: -1.7, signal: 'Short KO / Long PEP', confidence: 82, spreadHistory: [-0.3, -0.6, -0.9, -1.1, -1.3, -1.2, -1.5, -1.6, -1.8, -1.7] },
  { pair: 'DIS/NFLX', zscore: 2.6, correlation: 0.76, spread: 3.5, signal: 'Long DIS / Short NFLX', confidence: 73, spreadHistory: [1.5, 2.0, 2.4, 2.8, 2.5, 3.0, 3.2, 3.4, 3.3, 3.5] },
]

const generateMomentumResults = () => [
  { symbol: 'SMCI', momentum: 45.2, rsi: 72, volume_surge: 285, price_change: 12.8, grade: 'A+', history: [28, 32, 35, 38, 41, 40, 43, 44, 45] },
  { symbol: 'PLTR', momentum: 38.7, rsi: 68, volume_surge: 198, price_change: 9.5, grade: 'A', history: [25, 28, 30, 32, 35, 36, 37, 38, 39] },
  { symbol: 'AVGO', momentum: 32.1, rsi: 65, volume_surge: 156, price_change: 7.2, grade: 'A-', history: [20, 23, 25, 27, 28, 30, 31, 32, 32] },
  { symbol: 'ARM', momentum: 28.5, rsi: 61, volume_surge: 142, price_change: 6.8, grade: 'B+', history: [18, 20, 22, 24, 25, 26, 27, 28, 29] },
  { symbol: 'COIN', momentum: 25.3, rsi: 58, volume_surge: 124, price_change: 5.4, grade: 'B', history: [15, 17, 19, 21, 22, 23, 24, 25, 25] },
  { symbol: 'SQ', momentum: 22.1, rsi: 55, volume_surge: 108, price_change: 4.9, grade: 'B-', history: [12, 14, 16, 18, 19, 20, 21, 22, 22] },
]

const generateMeanReversionResults = () => [
  { symbol: 'INTC', deviation: -3.2, days_oversold: 8, rsi: 28, support: 42.50, current: 38.20, upside: 11.3, history: [-1.5, -1.8, -2.2, -2.5, -2.8, -3.0, -3.1, -3.2] },
  { symbol: 'BABA', deviation: -2.8, days_oversold: 6, rsi: 31, support: 78.00, current: 72.50, upside: 7.6, history: [-1.2, -1.5, -1.9, -2.2, -2.5, -2.8] },
  { symbol: 'PYPL', deviation: -2.5, days_oversold: 5, rsi: 33, support: 62.00, current: 58.80, upside: 5.4, history: [-1.0, -1.4, -1.8, -2.1, -2.5] },
  { symbol: 'SNAP', deviation: -2.3, days_oversold: 4, rsi: 35, support: 11.20, current: 10.60, upside: 5.7, history: [-1.1, -1.5, -1.9, -2.3] },
  { symbol: 'UBER', deviation: -2.1, days_oversold: 3, rsi: 37, support: 68.50, current: 65.80, upside: 4.1, history: [-1.0, -1.5, -2.1] },
]

const generateVolumeAnomalies = () => [
  { symbol: 'AMD', avg_volume: 45.2, current_volume: 156.8, surge: 247, price_change: 8.5, time: '10:45 AM', history: [100, 110, 125, 140, 145, 155, 157] },
  { symbol: 'SOFI', avg_volume: 28.5, current_volume: 89.2, surge: 213, price_change: 6.2, time: '11:20 AM', history: [100, 108, 120, 135, 160, 185, 213] },
  { symbol: 'F', avg_volume: 62.1, current_volume: 185.4, surge: 199, price_change: 4.8, time: '9:45 AM', history: [100, 115, 130, 145, 165, 180, 199] },
  { symbol: 'RIVN', avg_volume: 34.8, current_volume: 98.5, surge: 183, price_change: 7.1, time: '10:15 AM', history: [100, 112, 125, 140, 155, 170, 183] },
  { symbol: 'NIO', avg_volume: 41.2, current_volume: 112.7, surge: 174, price_change: 5.9, time: '11:05 AM', history: [100, 110, 122, 135, 150, 162, 174] },
]

type ScannerType = 'patterns' | 'statarb' | 'momentum' | 'meanreversion' | 'volume'

interface FilterState {
  minConfidence: number
  minRR: number
  sectors: string[]
  volumeFilter: string
}

export default function ScannerPage() {
  const [selectedScanner, setSelectedScanner] = useState<ScannerType>('patterns')
  const [filters, setFilters] = useState<FilterState>({
    minConfidence: 70,
    minRR: 1.5,
    sectors: [],
    volumeFilter: 'all',
  })
  const [hoveredItem, setHoveredItem] = useState<string | null>(null)
  const [showFilters, setShowFilters] = useState(false)

  const patternResults = useMemo(() => generatePatternResults(), [])
  const statArbResults = useMemo(() => generateStatArbResults(), [])
  const momentumResults = useMemo(() => generateMomentumResults(), [])
  const meanRevResults = useMemo(() => generateMeanReversionResults(), [])
  const volumeAnomalies = useMemo(() => generateVolumeAnomalies(), [])

  // Filter pattern results
  const filteredPatterns = useMemo(() => {
    return patternResults.filter(r => {
      if (r.confidence < filters.minConfidence) return false
      if (r.rr < filters.minRR) return false
      if (filters.sectors.length > 0 && !filters.sectors.includes(r.sector)) return false
      if (filters.volumeFilter !== 'all' && r.volume !== filters.volumeFilter) return false
      return true
    })
  }, [patternResults, filters])

  // Scatter chart data for pattern recognition
  const patternScatterOption = useMemo(() => ({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(99, 102, 241, 0.3)',
      borderWidth: 1,
      textStyle: { color: '#e2e8f0' },
      formatter: (params: any) => {
        const d = params.data
        return `<strong>${d.symbol}</strong><br/>
                Pattern: ${d.pattern}<br/>
                Confidence: ${d.confidence}%<br/>
                R:R Ratio: ${d.rr}:1<br/>
                Target: $${d.target}`
      }
    },
    grid: { left: 60, right: 30, top: 40, bottom: 50 },
    xAxis: {
      type: 'value',
      name: 'Risk:Reward Ratio',
      nameLocation: 'middle',
      nameGap: 30,
      nameTextStyle: { color: '#94a3b8' },
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8', formatter: '{value}:1' },
      splitLine: { lineStyle: { color: '#1e293b' } },
    },
    yAxis: {
      type: 'value',
      name: 'Confidence %',
      nameLocation: 'middle',
      nameGap: 40,
      nameTextStyle: { color: '#94a3b8' },
      min: 60,
      max: 100,
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#1e293b' } },
    },
    series: [{
      type: 'scatter',
      symbolSize: (data: any) => Math.max(20, data.volume === 'Very High' ? 45 : data.volume === 'High' ? 35 : 25),
      data: filteredPatterns.map(r => ({
        value: [r.rr, r.confidence],
        symbol: r.symbol,
        pattern: r.pattern,
        target: r.target.toFixed(2),
        rr: r.rr,
        confidence: r.confidence,
        volume: r.volume,
      })),
      itemStyle: {
        color: (params: any) => {
          const conf = params.data.confidence
          if (conf >= 85) return '#22c55e'
          if (conf >= 75) return '#f59e0b'
          return '#f97316'
        },
        shadowBlur: 10,
        shadowColor: 'rgba(99, 102, 241, 0.3)',
      },
      emphasis: {
        scale: 1.3,
        itemStyle: {
          shadowBlur: 20,
          shadowColor: 'rgba(99, 102, 241, 0.5)',
        }
      },
      label: {
        show: true,
        formatter: (params: any) => params.data.symbol,
        position: 'top',
        color: '#e2e8f0',
        fontSize: 11,
        fontWeight: 'bold',
      }
    }]
  }), [filteredPatterns])

  // Z-Score distribution chart for stat arb
  const statArbChartOption = useMemo(() => ({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(99, 102, 241, 0.3)',
      textStyle: { color: '#e2e8f0' },
    },
    grid: { left: 60, right: 30, top: 40, bottom: 60 },
    xAxis: {
      type: 'category',
      data: statArbResults.map(r => r.pair),
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8', rotate: 45 },
    },
    yAxis: {
      type: 'value',
      name: 'Z-Score (σ)',
      nameTextStyle: { color: '#94a3b8' },
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#1e293b' } },
    },
    series: [{
      type: 'bar',
      data: statArbResults.map(r => ({
        value: r.zscore,
        itemStyle: {
          color: r.zscore > 0
            ? { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#22c55e' }, { offset: 1, color: '#15803d' }] }
            : { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#ef4444' }, { offset: 1, color: '#b91c1c' }] },
          borderRadius: [4, 4, 0, 0],
        }
      })),
      barWidth: '60%',
      markLine: {
        silent: true,
        lineStyle: { color: '#6366f1', type: 'dashed' },
        data: [
          { yAxis: 2, label: { formatter: '+2σ', color: '#94a3b8' } },
          { yAxis: -2, label: { formatter: '-2σ', color: '#94a3b8' } },
        ]
      }
    }]
  }), [statArbResults])

  // Momentum bar race chart
  const momentumChartOption = useMemo(() => ({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(99, 102, 241, 0.3)',
      textStyle: { color: '#e2e8f0' },
    },
    grid: { left: 80, right: 40, top: 30, bottom: 30 },
    xAxis: {
      type: 'value',
      max: 50,
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#1e293b' } },
    },
    yAxis: {
      type: 'category',
      data: momentumResults.map(r => r.symbol).reverse(),
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#e2e8f0', fontWeight: 'bold' },
    },
    series: [{
      type: 'bar',
      data: momentumResults.map(r => ({
        value: r.momentum,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [
              { offset: 0, color: '#6366f1' },
              { offset: 1, color: r.grade.startsWith('A') ? '#22c55e' : '#3b82f6' }
            ]
          },
          borderRadius: [0, 4, 4, 0],
        }
      })).reverse(),
      barWidth: '65%',
      label: {
        show: true,
        position: 'right',
        formatter: (params: any) => {
          const result = momentumResults.find(r => r.symbol === momentumResults[momentumResults.length - 1 - params.dataIndex].symbol)
          return result ? result.grade : ''
        },
        color: '#e2e8f0',
        fontWeight: 'bold',
      }
    }]
  }), [momentumResults])

  // Mean reversion deviation chart
  const meanRevChartOption = useMemo(() => ({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(99, 102, 241, 0.3)',
      textStyle: { color: '#e2e8f0' },
      formatter: (params: any) => {
        const d = meanRevResults[params.dataIndex]
        return `<strong>${d.symbol}</strong><br/>
                Deviation: ${d.deviation}σ<br/>
                RSI: ${d.rsi}<br/>
                Upside: +${d.upside}%`
      }
    },
    grid: { left: 60, right: 40, top: 40, bottom: 50 },
    xAxis: {
      type: 'category',
      data: meanRevResults.map(r => r.symbol),
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#e2e8f0', fontWeight: 'bold' },
    },
    yAxis: {
      type: 'value',
      name: 'Standard Deviation',
      min: -4,
      max: 0,
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8', formatter: '{value}σ' },
      splitLine: { lineStyle: { color: '#1e293b' } },
    },
    series: [{
      type: 'bar',
      data: meanRevResults.map(r => ({
        value: r.deviation,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 1, x2: 0, y2: 0,
            colorStops: [
              { offset: 0, color: '#dc2626' },
              { offset: 0.5, color: '#f97316' },
              { offset: 1, color: '#f59e0b' }
            ]
          },
          borderRadius: [0, 0, 4, 4],
        }
      })),
      barWidth: '50%',
      markLine: {
        silent: true,
        lineStyle: { color: '#22c55e', type: 'dashed', width: 2 },
        data: [
          { yAxis: -2, label: { formatter: 'Oversold Zone', color: '#22c55e', position: 'end' } },
        ]
      }
    }]
  }), [meanRevResults])

  // Volume surge line chart
  const volumeChartOption = useMemo(() => ({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(99, 102, 241, 0.3)',
      textStyle: { color: '#e2e8f0' },
    },
    legend: {
      data: volumeAnomalies.map(r => r.symbol),
      textStyle: { color: '#94a3b8' },
      top: 0,
    },
    grid: { left: 60, right: 30, top: 50, bottom: 30 },
    xAxis: {
      type: 'category',
      data: ['T-6', 'T-5', 'T-4', 'T-3', 'T-2', 'T-1', 'Now'],
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' },
    },
    yAxis: {
      type: 'value',
      name: 'Volume Index',
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#1e293b' } },
    },
    series: volumeAnomalies.map((r, idx) => ({
      name: r.symbol,
      type: 'line',
      data: r.history,
      smooth: true,
      lineStyle: { width: 3 },
      itemStyle: {
        color: ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6'][idx],
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6'][idx] + '40' },
            { offset: 1, color: ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6'][idx] + '05' }
          ]
        }
      }
    }))
  }), [volumeAnomalies])

  const sectors = useMemo(() =>
    Array.from(new Set(patternResults.map(r => r.sector))),
    [patternResults]
  )

  const radarData = useMemo(() => [
    { name: 'Patterns', value: filteredPatterns.length * 10, max: 100 },
    { name: 'Stat Arb', value: statArbResults.filter(r => Math.abs(r.zscore) > 2).length * 20, max: 100 },
    { name: 'Momentum', value: momentumResults.filter(r => r.grade.startsWith('A')).length * 25, max: 100 },
    { name: 'Mean Rev', value: meanRevResults.filter(r => r.deviation < -2.5).length * 20, max: 100 },
    { name: 'Volume', value: volumeAnomalies.filter(r => r.surge > 200).length * 25, max: 100 },
  ], [filteredPatterns, statArbResults, momentumResults, meanRevResults, volumeAnomalies])

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-fade-in">
        <h1 className="text-4xl md:text-5xl font-bold mb-3 gradient-text">Quant Scanner</h1>
        <p className="text-lg text-slate-400 max-w-2xl">
          Real-time pattern recognition, statistical arbitrage, and anomaly detection
          powered by advanced quantitative algorithms.
        </p>
      </div>

      {/* Scanner Selection with Animated Cards */}
      <div className="glass-card p-6 animate-slide-up" style={{ animationDelay: '100ms' }}>
        <div className="flex flex-wrap gap-3">
          {[
            { id: 'patterns', label: 'Pattern Recognition', icon: '📐', count: filteredPatterns.length, color: 'indigo' },
            { id: 'statarb', label: 'Statistical Arbitrage', icon: '🔗', count: statArbResults.length, color: 'cyan' },
            { id: 'momentum', label: 'Momentum Signals', icon: '🚀', count: momentumResults.length, color: 'emerald' },
            { id: 'meanreversion', label: 'Mean Reversion', icon: '🔄', count: meanRevResults.length, color: 'amber' },
            { id: 'volume', label: 'Volume Anomalies', icon: '📊', count: volumeAnomalies.length, color: 'rose' },
          ].map((scanner) => (
            <button
              key={scanner.id}
              onClick={() => setSelectedScanner(scanner.id as ScannerType)}
              className={`group relative flex items-center gap-3 px-5 py-3.5 rounded-xl font-semibold transition-all duration-300 ${
                selectedScanner === scanner.id
                  ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg shadow-indigo-500/25 scale-105'
                  : 'bg-slate-800/50 text-slate-300 hover:bg-slate-700/50 border border-slate-700/50 hover:border-indigo-500/30'
              }`}
            >
              <span className="text-xl">{scanner.icon}</span>
              <span>{scanner.label}</span>
              <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                selectedScanner === scanner.id
                  ? 'bg-white/20'
                  : 'bg-indigo-500/20 text-indigo-400'
              }`}>
                {scanner.count}
              </span>
              {selectedScanner === scanner.id && (
                <div className="absolute -inset-px rounded-xl bg-gradient-to-r from-indigo-500 to-purple-500 opacity-20 blur-sm" />
              )}
            </button>
          ))}
        </div>

        {/* Advanced Filters Toggle */}
        {selectedScanner === 'patterns' && (
          <div className="mt-6 pt-6 border-t border-slate-700/50">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
            >
              <span>⚙️</span>
              <span>Advanced Filters</span>
              <svg
                className={`w-4 h-4 transition-transform ${showFilters ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {showFilters && (
              <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4 animate-fade-in">
                {/* Min Confidence Slider */}
                <div>
                  <label className="block text-xs text-slate-500 uppercase tracking-wider mb-2">
                    Min Confidence: {filters.minConfidence}%
                  </label>
                  <input
                    type="range"
                    min="50"
                    max="95"
                    value={filters.minConfidence}
                    onChange={(e) => setFilters(f => ({ ...f, minConfidence: parseInt(e.target.value) }))}
                    className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                  />
                </div>

                {/* Min R:R Slider */}
                <div>
                  <label className="block text-xs text-slate-500 uppercase tracking-wider mb-2">
                    Min R:R Ratio: {filters.minRR}:1
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="4"
                    step="0.5"
                    value={filters.minRR}
                    onChange={(e) => setFilters(f => ({ ...f, minRR: parseFloat(e.target.value) }))}
                    className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                  />
                </div>

                {/* Sector Filter */}
                <div>
                  <label className="block text-xs text-slate-500 uppercase tracking-wider mb-2">
                    Sectors
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {sectors.map(sector => (
                      <button
                        key={sector}
                        onClick={() => setFilters(f => ({
                          ...f,
                          sectors: f.sectors.includes(sector)
                            ? f.sectors.filter(s => s !== sector)
                            : [...f.sectors, sector]
                        }))}
                        className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                          filters.sectors.includes(sector)
                            ? 'bg-indigo-500 text-white'
                            : 'bg-slate-700/50 text-slate-400 hover:bg-slate-600/50'
                        }`}
                      >
                        {sector}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Volume Filter */}
                <div>
                  <label className="block text-xs text-slate-500 uppercase tracking-wider mb-2">
                    Volume
                  </label>
                  <select
                    value={filters.volumeFilter}
                    onChange={(e) => setFilters(f => ({ ...f, volumeFilter: e.target.value }))}
                    className="w-full px-3 py-2 rounded-lg bg-slate-800/50 border border-slate-700/50 text-slate-300 text-sm focus:outline-none focus:border-indigo-500/50"
                  >
                    <option value="all">All Volumes</option>
                    <option value="Very High">Very High</option>
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                  </select>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Chart Area - 2/3 width */}
        <div className="xl:col-span-2 space-y-6">
          {/* Pattern Recognition */}
          {selectedScanner === 'patterns' && (
            <div className="glass-card p-6 animate-fade-in">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <span className="text-2xl">📐</span>
                    Pattern Distribution
                  </h2>
                  <p className="text-sm text-slate-400 mt-1">
                    Bubble size represents volume intensity
                  </p>
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </span>
                  <span className="text-xs font-medium text-emerald-400">Live Scanning</span>
                </div>
              </div>
              <ReactECharts option={patternScatterOption} style={{ height: 400 }} />
            </div>
          )}

          {/* Statistical Arbitrage */}
          {selectedScanner === 'statarb' && (
            <div className="glass-card p-6 animate-fade-in">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <span className="text-2xl">🔗</span>
                    Z-Score Distribution
                  </h2>
                  <p className="text-sm text-slate-400 mt-1">
                    Pairs outside ±2σ indicate trading opportunities
                  </p>
                </div>
              </div>
              <ReactECharts option={statArbChartOption} style={{ height: 400 }} />
            </div>
          )}

          {/* Momentum */}
          {selectedScanner === 'momentum' && (
            <div className="glass-card p-6 animate-fade-in">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <span className="text-2xl">🚀</span>
                    Momentum Rankings
                  </h2>
                  <p className="text-sm text-slate-400 mt-1">
                    Composite score based on price action, RSI, and volume
                  </p>
                </div>
              </div>
              <ReactECharts option={momentumChartOption} style={{ height: 400 }} />
            </div>
          )}

          {/* Mean Reversion */}
          {selectedScanner === 'meanreversion' && (
            <div className="glass-card p-6 animate-fade-in">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <span className="text-2xl">🔄</span>
                    Deviation from Mean
                  </h2>
                  <p className="text-sm text-slate-400 mt-1">
                    Stocks trading below -2σ may be oversold
                  </p>
                </div>
              </div>
              <ReactECharts option={meanRevChartOption} style={{ height: 400 }} />
            </div>
          )}

          {/* Volume Anomalies */}
          {selectedScanner === 'volume' && (
            <div className="glass-card p-6 animate-fade-in">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <span className="text-2xl">📊</span>
                    Volume Surge Tracking
                  </h2>
                  <p className="text-sm text-slate-400 mt-1">
                    Intraday volume index relative to 20-day average
                  </p>
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-rose-500/10 border border-rose-500/20">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
                  </span>
                  <span className="text-xs font-medium text-rose-400">Updating</span>
                </div>
              </div>
              <ReactECharts option={volumeChartOption} style={{ height: 400 }} />
            </div>
          )}

          {/* Results Table */}
          <div className="glass-card overflow-hidden animate-slide-up" style={{ animationDelay: '200ms' }}>
            <div className="p-6 border-b border-slate-700/50">
              <h2 className="text-lg font-bold text-white">Detailed Results</h2>
            </div>
            <div className="overflow-x-auto">
              {selectedScanner === 'patterns' && (
                <table className="table-pro">
                  <thead>
                    <tr>
                      <th>Symbol</th>
                      <th>Pattern</th>
                      <th>Confidence</th>
                      <th>Target</th>
                      <th>Stop</th>
                      <th>R:R</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredPatterns.map((result) => (
                      <tr
                        key={result.symbol}
                        onMouseEnter={() => setHoveredItem(result.symbol)}
                        onMouseLeave={() => setHoveredItem(null)}
                        className={hoveredItem === result.symbol ? 'bg-indigo-500/10' : ''}
                      >
                        <td className="font-mono font-bold text-indigo-400">{result.symbol}</td>
                        <td>{result.pattern}</td>
                        <td>
                          <div className="flex items-center gap-2">
                            <div className="w-16 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                              <div
                                className={`h-full rounded-full ${
                                  result.confidence >= 85 ? 'bg-emerald-500' :
                                  result.confidence >= 75 ? 'bg-amber-500' : 'bg-orange-500'
                                }`}
                                style={{ width: `${result.confidence}%` }}
                              />
                            </div>
                            <span className="text-sm font-semibold">{result.confidence}%</span>
                          </div>
                        </td>
                        <td className="font-mono text-emerald-400">${result.target.toFixed(2)}</td>
                        <td className="font-mono text-red-400">${result.stop.toFixed(2)}</td>
                        <td>
                          <span className="px-2 py-1 rounded bg-cyan-500/20 text-cyan-400 text-xs font-bold">
                            {result.rr}:1
                          </span>
                        </td>
                        <td>
                          <button className="px-3 py-1.5 rounded-lg bg-indigo-500/20 text-indigo-400 text-xs font-semibold hover:bg-indigo-500/30 transition-colors">
                            View Chart
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}

              {selectedScanner === 'statarb' && (
                <table className="table-pro">
                  <thead>
                    <tr>
                      <th>Pair</th>
                      <th>Z-Score</th>
                      <th>Correlation</th>
                      <th>Signal</th>
                      <th>Confidence</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {statArbResults.map((result) => (
                      <tr key={result.pair}>
                        <td className="font-mono font-bold text-indigo-400">{result.pair}</td>
                        <td>
                          <span className={`font-bold ${result.zscore > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                            {result.zscore.toFixed(2)}σ
                          </span>
                        </td>
                        <td>{result.correlation.toFixed(2)}</td>
                        <td className="text-sm text-slate-300">{result.signal}</td>
                        <td>
                          <div className="flex items-center gap-2">
                            <div className="w-12 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-cyan-500 to-indigo-500 rounded-full"
                                style={{ width: `${result.confidence}%` }}
                              />
                            </div>
                            <span className="text-sm">{result.confidence}%</span>
                          </div>
                        </td>
                        <td>
                          <button className="px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 text-xs font-semibold hover:bg-emerald-500/30 transition-colors">
                            Execute
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}

              {selectedScanner === 'momentum' && (
                <table className="table-pro">
                  <thead>
                    <tr>
                      <th>Symbol</th>
                      <th>Grade</th>
                      <th>Momentum</th>
                      <th>RSI</th>
                      <th>Vol Surge</th>
                      <th>Price Δ</th>
                    </tr>
                  </thead>
                  <tbody>
                    {momentumResults.map((result) => (
                      <tr key={result.symbol}>
                        <td className="font-mono font-bold text-indigo-400">{result.symbol}</td>
                        <td>
                          <span className={`px-2 py-1 rounded font-bold text-xs ${
                            result.grade.startsWith('A') ? 'bg-emerald-500/20 text-emerald-400' :
                            result.grade.startsWith('B') ? 'bg-blue-500/20 text-blue-400' :
                            'bg-amber-500/20 text-amber-400'
                          }`}>
                            {result.grade}
                          </span>
                        </td>
                        <td className="font-semibold">{result.momentum.toFixed(1)}</td>
                        <td>{result.rsi}</td>
                        <td className="text-cyan-400">+{result.volume_surge}%</td>
                        <td className="text-emerald-400">+{result.price_change}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}

              {selectedScanner === 'meanreversion' && (
                <table className="table-pro">
                  <thead>
                    <tr>
                      <th>Symbol</th>
                      <th>Deviation</th>
                      <th>Days Oversold</th>
                      <th>RSI</th>
                      <th>Current</th>
                      <th>Support</th>
                      <th>Upside</th>
                    </tr>
                  </thead>
                  <tbody>
                    {meanRevResults.map((result) => (
                      <tr key={result.symbol}>
                        <td className="font-mono font-bold text-indigo-400">{result.symbol}</td>
                        <td>
                          <span className="px-2 py-1 rounded bg-red-500/20 text-red-400 text-xs font-bold">
                            {result.deviation.toFixed(1)}σ
                          </span>
                        </td>
                        <td>{result.days_oversold} days</td>
                        <td className="text-red-400">{result.rsi}</td>
                        <td className="font-mono">${result.current.toFixed(2)}</td>
                        <td className="font-mono text-emerald-400">${result.support.toFixed(2)}</td>
                        <td className="text-emerald-400 font-bold">+{result.upside.toFixed(1)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}

              {selectedScanner === 'volume' && (
                <table className="table-pro">
                  <thead>
                    <tr>
                      <th>Symbol</th>
                      <th>Time</th>
                      <th>Avg Vol</th>
                      <th>Current Vol</th>
                      <th>Surge</th>
                      <th>Price Δ</th>
                    </tr>
                  </thead>
                  <tbody>
                    {volumeAnomalies.map((result) => (
                      <tr key={result.symbol}>
                        <td className="font-mono font-bold text-indigo-400">{result.symbol}</td>
                        <td className="text-slate-400">{result.time}</td>
                        <td>{result.avg_volume}M</td>
                        <td className="text-amber-400 font-semibold">{result.current_volume}M</td>
                        <td>
                          <span className="px-2 py-1 rounded bg-rose-500/20 text-rose-400 text-xs font-bold">
                            +{result.surge}%
                          </span>
                        </td>
                        <td className="text-emerald-400">+{result.price_change}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar - 1/3 width */}
        <div className="space-y-6">
          {/* Scanner Health Radar */}
          <div className="animate-slide-up" style={{ animationDelay: '150ms' }}>
            <RadarChart
              data={radarData}
              title="Signal Strength Overview"
              height={300}
              colors={['#6366f1', '#22c55e']}
            />
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 gap-4 animate-fade-in" style={{ animationDelay: '200ms' }}>
            <div className="glass-card p-5">
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Total Signals</p>
              <p className="text-3xl font-bold gradient-text">
                {filteredPatterns.length + statArbResults.length + momentumResults.length + meanRevResults.length + volumeAnomalies.length}
              </p>
            </div>
            <div className="glass-card p-5">
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">High Conf</p>
              <p className="text-3xl font-bold text-emerald-400">
                {filteredPatterns.filter(r => r.confidence >= 85).length +
                 statArbResults.filter(r => r.confidence >= 85).length +
                 momentumResults.filter(r => r.grade.startsWith('A')).length}
              </p>
            </div>
            <div className="glass-card p-5">
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Avg R:R</p>
              <p className="text-3xl font-bold text-cyan-400">
                {(filteredPatterns.reduce((sum, r) => sum + r.rr, 0) / Math.max(1, filteredPatterns.length)).toFixed(1)}:1
              </p>
            </div>
            <div className="glass-card p-5">
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Alerts</p>
              <p className="text-3xl font-bold text-rose-400">
                {volumeAnomalies.filter(r => r.surge > 200).length}
              </p>
            </div>
          </div>

          {/* Market Sentiment Gauge */}
          <div className="animate-slide-up" style={{ animationDelay: '250ms' }}>
            <GaugeChart
              value={68}
              title="Market Sentiment"
              subtitle="Aggregated from all scanner signals"
              size="md"
              thresholds={{ low: 30, medium: 50, high: 70 }}
            />
          </div>

          {/* Pro Features CTA */}
          <div className="glass-card p-6 text-center relative overflow-hidden animate-fade-in" style={{ animationDelay: '300ms' }}>
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 via-purple-500/10 to-pink-500/10" />
            <div className="relative">
              <h3 className="text-lg font-bold mb-2 text-white">Unlock Pro Scanners</h3>
              <p className="text-sm text-slate-400 mb-4">
                Real-time alerts, custom filters, and AI-powered signal validation.
              </p>
              <button className="btn-primary w-full">
                Start Free Trial
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Resources Section */}
      <div className="glass-card p-8 text-center animate-fade-in" style={{ animationDelay: '350ms' }}>
        <h3 className="text-2xl font-bold mb-2 gradient-text">Build Your Own Quant Scanners</h3>
        <p className="text-slate-400 mb-6 max-w-lg mx-auto">
          Download our complete guide to quantitative pattern recognition with Python source code.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button className="btn-primary">
            📥 Download Guide + Code (Free)
          </button>
          <button className="btn-secondary">
            🎥 Watch Scanner Tutorial
          </button>
        </div>
      </div>
    </div>
  )
}
