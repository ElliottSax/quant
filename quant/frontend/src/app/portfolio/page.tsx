/**
 * Portfolio Analyzer Page
 * Advanced portfolio optimization and risk analysis tools
 * Enhanced with ECharts visualizations
 */

'use client'

import { useState, useMemo } from 'react'
import dynamic from 'next/dynamic'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  ZAxis,
} from 'recharts'

// Dynamically import ECharts component
const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#14b8a6']

// Generate correlation matrix
const generateCorrelationMatrix = () => {
  const assets = ['SPY', 'QQQ', 'IWM', 'EFA', 'EEM', 'AGG', 'GLD', 'VNQ']
  const matrix: number[][] = []

  for (let i = 0; i < assets.length; i++) {
    const row: number[] = []
    for (let j = 0; j < assets.length; j++) {
      if (i === j) {
        row.push(1)
      } else if (j > i) {
        // Generate correlation
        let corr = Math.random() * 0.6 + 0.2
        // Some pairs have low/negative correlation
        if ((assets[i] === 'AGG' || assets[i] === 'GLD') && (assets[j] !== 'AGG' && assets[j] !== 'GLD')) {
          corr = Math.random() * 0.4 - 0.2
        }
        row.push(parseFloat(corr.toFixed(2)))
      } else {
        row.push(matrix[j][i])
      }
    }
    matrix.push(row)
  }

  return { assets, matrix }
}

// Generate efficient frontier data
const generateEfficientFrontier = () => {
  const points = []
  const numPoints = 50

  for (let i = 0; i < numPoints; i++) {
    const risk = 5 + (i / numPoints) * 25
    // Efficient frontier is a curve
    const maxReturn = 4 + Math.sqrt(risk - 5) * 4 - (Math.random() - 0.5) * 0.5
    const minReturn = maxReturn - 3 - Math.random() * 2

    // Add points along the frontier
    points.push({
      risk: parseFloat(risk.toFixed(2)),
      return: parseFloat(maxReturn.toFixed(2)),
      type: 'efficient',
    })

    // Add some sub-optimal portfolios
    if (i % 3 === 0) {
      points.push({
        risk: parseFloat((risk + Math.random() * 3).toFixed(2)),
        return: parseFloat((minReturn + Math.random() * 2).toFixed(2)),
        type: 'suboptimal',
      })
    }
  }

  // Add special portfolios
  points.push({ risk: 8.5, return: 6.2, type: 'current', name: 'Your Portfolio' })
  points.push({ risk: 15.8, return: 10.5, type: 'market', name: 'S&P 500' })
  points.push({ risk: 6.2, return: 7.8, type: 'optimal', name: 'Optimal' })
  points.push({ risk: 4.5, return: 4.2, type: 'minvar', name: 'Min Variance' })

  return points
}

// Generate Monte Carlo simulation data
const generateMonteCarloData = (numSimulations: number = 100) => {
  const data = []
  const days = 252

  for (let day = 0; day <= days; day++) {
    const dayData: any = { day }

    for (let sim = 0; sim < numSimulations; sim++) {
      const drift = 0.0003
      const volatility = 0.015
      const shock = (Math.random() - 0.5) * 2 * volatility

      if (day === 0) {
        dayData[`sim${sim}`] = 100000
      } else {
        const prevValue = data[day - 1][`sim${sim}`]
        dayData[`sim${sim}`] = prevValue * (1 + drift + shock)
      }
    }

    data.push(dayData)
  }

  return data
}

// Generate portfolio allocation data
const generateAllocationData = () => [
  { name: 'US Large Cap', ticker: 'SPY', value: 30, color: COLORS[0] },
  { name: 'US Tech', ticker: 'QQQ', value: 15, color: COLORS[1] },
  { name: 'US Small Cap', ticker: 'IWM', value: 10, color: COLORS[2] },
  { name: 'International', ticker: 'EFA', value: 15, color: COLORS[3] },
  { name: 'Emerging Markets', ticker: 'EEM', value: 5, color: COLORS[4] },
  { name: 'Bonds', ticker: 'AGG', value: 15, color: COLORS[5] },
  { name: 'Gold', ticker: 'GLD', value: 5, color: COLORS[6] },
  { name: 'Real Estate', ticker: 'VNQ', value: 5, color: COLORS[7] },
]

// Generate sector exposure data
const generateSectorData = () => [
  { sector: 'Technology', exposure: 28, benchmark: 25 },
  { sector: 'Healthcare', exposure: 18, benchmark: 15 },
  { sector: 'Financials', exposure: 15, benchmark: 18 },
  { sector: 'Consumer', exposure: 12, benchmark: 14 },
  { sector: 'Industrials', exposure: 10, benchmark: 11 },
  { sector: 'Energy', exposure: 8, benchmark: 9 },
  { sector: 'Utilities', exposure: 5, benchmark: 4 },
  { sector: 'Materials', exposure: 4, benchmark: 4 },
]

// Generate risk metrics over time
const generateRiskMetrics = () => {
  const data = []
  for (let i = 0; i < 24; i++) {
    data.push({
      month: `M${i + 1}`,
      var95: -(Math.random() * 3 + 2),
      cvar95: -(Math.random() * 5 + 3),
      beta: Math.random() * 0.4 + 0.8,
    })
  }
  return data
}

// Generate performance attribution
const generatePerformanceAttribution = () => {
  const assets = ['SPY', 'QQQ', 'IWM', 'EFA', 'EEM', 'AGG', 'GLD', 'VNQ']
  return assets.map(asset => ({
    asset,
    allocation: Math.random() * 20 + 5,
    return: (Math.random() - 0.3) * 30,
    contribution: (Math.random() - 0.2) * 8,
  }))
}

export default function PortfolioPage() {
  const [portfolioValue, setPortfolioValue] = useState(100000)
  const [riskTolerance, setRiskTolerance] = useState<'conservative' | 'moderate' | 'aggressive'>('moderate')
  const [simulationRuns, setSimulationRuns] = useState(50)
  const [activeTab, setActiveTab] = useState<'overview' | 'optimization' | 'risk'>('overview')

  const monteCarloData = useMemo(() => generateMonteCarloData(simulationRuns), [simulationRuns])
  const allocationData = useMemo(() => generateAllocationData(), [])
  const sectorData = useMemo(() => generateSectorData(), [])
  const riskMetricsData = useMemo(() => generateRiskMetrics(), [])
  const correlationData = useMemo(() => generateCorrelationMatrix(), [])
  const efficientFrontierData = useMemo(() => generateEfficientFrontier(), [])
  const performanceAttribution = useMemo(() => generatePerformanceAttribution(), [])

  // Calculate statistics from Monte Carlo
  const mcStats = useMemo(() => {
    const finalValues = monteCarloData[monteCarloData.length - 1]
    const simulations = Object.keys(finalValues)
      .filter(k => k.startsWith('sim'))
      .map(k => finalValues[k])
      .sort((a, b) => a - b)

    return {
      avg: simulations.reduce((a, b) => a + b, 0) / simulations.length,
      max: Math.max(...simulations),
      min: Math.min(...simulations),
      p5: simulations[Math.floor(simulations.length * 0.05)],
      p25: simulations[Math.floor(simulations.length * 0.25)],
      p50: simulations[Math.floor(simulations.length * 0.50)],
      p75: simulations[Math.floor(simulations.length * 0.75)],
      p95: simulations[Math.floor(simulations.length * 0.95)],
    }
  }, [monteCarloData])

  // ECharts correlation heatmap option
  const correlationHeatmapOption = useMemo(() => {
    const { assets, matrix } = correlationData
    const heatmapData: [number, number, number][] = []

    for (let i = 0; i < assets.length; i++) {
      for (let j = 0; j < assets.length; j++) {
        heatmapData.push([j, i, matrix[i][j]])
      }
    }

    return {
      backgroundColor: 'transparent',
      tooltip: {
        position: 'top',
        backgroundColor: 'rgba(30, 41, 59, 0.95)',
        borderColor: '#334155',
        textStyle: { color: '#e2e8f0' },
        formatter: (params: any) => {
          const [x, y, value] = params.data
          return `${assets[y]} ↔ ${assets[x]}<br/>Correlation: <b>${value.toFixed(2)}</b>`
        },
      },
      grid: {
        left: '15%',
        right: '10%',
        bottom: '15%',
        top: '10%',
      },
      xAxis: {
        type: 'category',
        data: assets,
        axisLabel: { color: '#94a3b8', rotate: 45 },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { show: false },
      },
      yAxis: {
        type: 'category',
        data: assets,
        axisLabel: { color: '#94a3b8' },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { show: false },
      },
      visualMap: {
        min: -0.5,
        max: 1,
        calculable: true,
        orient: 'vertical',
        right: '2%',
        top: 'center',
        textStyle: { color: '#94a3b8' },
        inRange: {
          color: ['#ef4444', '#fbbf24', '#22c55e', '#3b82f6'],
        },
      },
      series: [
        {
          type: 'heatmap',
          data: heatmapData,
          label: {
            show: true,
            formatter: (params: any) => params.data[2].toFixed(2),
            color: '#fff',
            fontSize: 10,
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)',
            },
          },
        },
      ],
    }
  }, [correlationData])

  // ECharts efficient frontier option
  const efficientFrontierOption = useMemo(() => {
    const efficientPoints = efficientFrontierData.filter(p => p.type === 'efficient')
    const suboptimalPoints = efficientFrontierData.filter(p => p.type === 'suboptimal')
    const specialPoints = efficientFrontierData.filter(p => !['efficient', 'suboptimal'].includes(p.type))

    return {
      backgroundColor: 'transparent',
      tooltip: {
        backgroundColor: 'rgba(30, 41, 59, 0.95)',
        borderColor: '#334155',
        textStyle: { color: '#e2e8f0' },
        formatter: (params: any) => {
          const data = params.data
          const name = data.name || params.seriesName
          return `
            <div style="padding: 8px;">
              <div style="font-weight: bold; margin-bottom: 4px;">${name}</div>
              <div>Expected Return: <b>${data[1] || data.return}%</b></div>
              <div>Risk (Std Dev): <b>${data[0] || data.risk}%</b></div>
              <div>Sharpe: <b>${((data[1] || data.return) / (data[0] || data.risk)).toFixed(2)}</b></div>
            </div>
          `
        },
      },
      legend: {
        data: ['Efficient Frontier', 'Suboptimal', 'Your Portfolio', 'S&P 500', 'Optimal', 'Min Variance'],
        textStyle: { color: '#94a3b8' },
        top: 10,
      },
      grid: {
        left: '10%',
        right: '5%',
        bottom: '10%',
        top: '15%',
      },
      xAxis: {
        type: 'value',
        name: 'Risk (Standard Deviation %)',
        nameLocation: 'middle',
        nameGap: 30,
        min: 0,
        max: 35,
        axisLine: { lineStyle: { color: '#475569' } },
        axisLabel: { color: '#94a3b8', formatter: '{value}%' },
        splitLine: { lineStyle: { color: '#334155', type: 'dashed' } },
      },
      yAxis: {
        type: 'value',
        name: 'Expected Return %',
        nameLocation: 'middle',
        nameGap: 40,
        min: 0,
        max: 20,
        axisLine: { lineStyle: { color: '#475569' } },
        axisLabel: { color: '#94a3b8', formatter: '{value}%' },
        splitLine: { lineStyle: { color: '#334155', type: 'dashed' } },
      },
      series: [
        {
          name: 'Efficient Frontier',
          type: 'line',
          data: efficientPoints.map(p => [p.risk, p.return]),
          smooth: true,
          lineStyle: { color: '#3b82f6', width: 3 },
          symbol: 'none',
          areaStyle: {
            color: {
              type: 'linear',
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
                { offset: 1, color: 'rgba(59, 130, 246, 0.05)' },
              ],
            },
          },
        },
        {
          name: 'Suboptimal',
          type: 'scatter',
          data: suboptimalPoints.map(p => [p.risk, p.return]),
          symbolSize: 8,
          itemStyle: { color: '#6b7280', opacity: 0.5 },
        },
        {
          name: 'Your Portfolio',
          type: 'scatter',
          data: specialPoints.filter(p => p.type === 'current').map(p => ({ value: [p.risk, p.return], name: p.name })),
          symbolSize: 20,
          symbol: 'diamond',
          itemStyle: { color: '#10b981' },
          label: { show: true, formatter: '{b}', position: 'right', color: '#10b981' },
        },
        {
          name: 'S&P 500',
          type: 'scatter',
          data: specialPoints.filter(p => p.type === 'market').map(p => ({ value: [p.risk, p.return], name: p.name })),
          symbolSize: 15,
          symbol: 'triangle',
          itemStyle: { color: '#f59e0b' },
          label: { show: true, formatter: '{b}', position: 'right', color: '#f59e0b' },
        },
        {
          name: 'Optimal',
          type: 'scatter',
          data: specialPoints.filter(p => p.type === 'optimal').map(p => ({ value: [p.risk, p.return], name: p.name })),
          symbolSize: 18,
          symbol: 'pin',
          itemStyle: { color: '#8b5cf6' },
          label: { show: true, formatter: '{b}', position: 'top', color: '#8b5cf6' },
        },
        {
          name: 'Min Variance',
          type: 'scatter',
          data: specialPoints.filter(p => p.type === 'minvar').map(p => ({ value: [p.risk, p.return], name: p.name })),
          symbolSize: 15,
          symbol: 'circle',
          itemStyle: { color: '#06b6d4' },
          label: { show: true, formatter: '{b}', position: 'left', color: '#06b6d4' },
        },
      ],
    }
  }, [efficientFrontierData])

  // Monte Carlo confidence bands option
  const monteCarloOption = useMemo(() => {
    // Calculate percentile bands
    const bands = monteCarloData.map((dayData, idx) => {
      const values = Object.keys(dayData)
        .filter(k => k.startsWith('sim'))
        .map(k => dayData[k])
        .sort((a, b) => a - b)

      return {
        day: dayData.day,
        p5: values[Math.floor(values.length * 0.05)],
        p25: values[Math.floor(values.length * 0.25)],
        p50: values[Math.floor(values.length * 0.50)],
        p75: values[Math.floor(values.length * 0.75)],
        p95: values[Math.floor(values.length * 0.95)],
      }
    })

    return {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(30, 41, 59, 0.95)',
        borderColor: '#334155',
        textStyle: { color: '#e2e8f0' },
        formatter: (params: any) => {
          const data = params[0]?.data
          if (!data) return ''
          const dayIdx = data[0]
          const band = bands[dayIdx]
          return `
            <div style="padding: 8px;">
              <div style="font-weight: bold; margin-bottom: 4px;">Day ${dayIdx}</div>
              <div>95th Percentile: <span style="color: #10b981;">$${band?.p95?.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span></div>
              <div>75th Percentile: <span style="color: #3b82f6;">$${band?.p75?.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span></div>
              <div>Median: <span style="color: #f59e0b;">$${band?.p50?.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span></div>
              <div>25th Percentile: <span style="color: #8b5cf6;">$${band?.p25?.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span></div>
              <div>5th Percentile: <span style="color: #ef4444;">$${band?.p5?.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span></div>
            </div>
          `
        },
      },
      legend: {
        data: ['95th Percentile', '75th Percentile', 'Median', '25th Percentile', '5th Percentile'],
        textStyle: { color: '#94a3b8' },
        top: 10,
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        top: '15%',
        containLabel: true,
      },
      xAxis: {
        type: 'value',
        name: 'Trading Days',
        nameLocation: 'middle',
        nameGap: 30,
        axisLine: { lineStyle: { color: '#475569' } },
        axisLabel: { color: '#94a3b8' },
        splitLine: { lineStyle: { color: '#334155', type: 'dashed' } },
      },
      yAxis: {
        type: 'value',
        name: 'Portfolio Value',
        nameLocation: 'middle',
        nameGap: 60,
        axisLine: { lineStyle: { color: '#475569' } },
        axisLabel: {
          color: '#94a3b8',
          formatter: (value: number) => `$${(value / 1000).toFixed(0)}k`,
        },
        splitLine: { lineStyle: { color: '#334155', type: 'dashed' } },
      },
      dataZoom: [
        { type: 'inside', start: 0, end: 100 },
        {
          type: 'slider',
          start: 0,
          end: 100,
          height: 20,
          bottom: 5,
          borderColor: '#475569',
          backgroundColor: 'rgba(71, 85, 105, 0.3)',
          fillerColor: 'rgba(59, 130, 246, 0.3)',
          handleStyle: { color: '#3b82f6' },
          textStyle: { color: '#94a3b8' },
        },
      ],
      series: [
        {
          name: '95th Percentile',
          type: 'line',
          data: bands.map(b => [b.day, b.p95]),
          smooth: true,
          lineStyle: { color: '#10b981', width: 2 },
          symbol: 'none',
        },
        {
          name: '75th Percentile',
          type: 'line',
          data: bands.map(b => [b.day, b.p75]),
          smooth: true,
          lineStyle: { color: '#3b82f6', width: 1, type: 'dashed' },
          symbol: 'none',
        },
        {
          name: 'Median',
          type: 'line',
          data: bands.map(b => [b.day, b.p50]),
          smooth: true,
          lineStyle: { color: '#f59e0b', width: 2 },
          symbol: 'none',
        },
        {
          name: '25th Percentile',
          type: 'line',
          data: bands.map(b => [b.day, b.p25]),
          smooth: true,
          lineStyle: { color: '#8b5cf6', width: 1, type: 'dashed' },
          symbol: 'none',
        },
        {
          name: '5th Percentile',
          type: 'line',
          data: bands.map(b => [b.day, b.p5]),
          smooth: true,
          lineStyle: { color: '#ef4444', width: 2 },
          symbol: 'none',
        },
      ],
    }
  }, [monteCarloData])

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold mb-2 gradient-text">Portfolio Analyzer</h1>
        <p className="text-muted-foreground text-lg">
          Advanced portfolio optimization, risk analysis, and Monte Carlo simulations
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-border pb-2">
        {(['overview', 'optimization', 'risk'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              activeTab === tab
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
            }`}
          >
            {tab === 'overview' && '📊 Overview'}
            {tab === 'optimization' && '🎯 Optimization'}
            {tab === 'risk' && '⚠️ Risk Analysis'}
          </button>
        ))}
      </div>

      {/* Portfolio Input */}
      <div className="glass-strong rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Portfolio Configuration</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="text-sm font-semibold text-muted-foreground mb-2 block">
              PORTFOLIO VALUE
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                $
              </span>
              <input
                type="number"
                value={portfolioValue}
                onChange={(e) => setPortfolioValue(Number(e.target.value))}
                className="input-field pl-7"
                min={1000}
                step={1000}
              />
            </div>
          </div>

          <div>
            <label className="text-sm font-semibold text-muted-foreground mb-2 block">
              RISK TOLERANCE
            </label>
            <select
              value={riskTolerance}
              onChange={(e) => setRiskTolerance(e.target.value as any)}
              className="input-field"
            >
              <option value="conservative">Conservative</option>
              <option value="moderate">Moderate</option>
              <option value="aggressive">Aggressive</option>
            </select>
          </div>

          <div>
            <label className="text-sm font-semibold text-muted-foreground mb-2 block">
              SIMULATION RUNS
            </label>
            <select
              value={simulationRuns}
              onChange={(e) => setSimulationRuns(Number(e.target.value))}
              className="input-field"
            >
              <option value={25}>25 Simulations</option>
              <option value={50}>50 Simulations</option>
              <option value={100}>100 Simulations</option>
            </select>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-strong rounded-xl p-6">
          <p className="text-sm text-muted-foreground mb-1">Total Return</p>
          <p className="text-3xl font-bold text-gradient-green">+24.7%</p>
          <p className="text-xs text-green-400 mt-1">vs SPY: +18.2%</p>
        </div>
        <div className="glass-strong rounded-xl p-6">
          <p className="text-sm text-muted-foreground mb-1">Sharpe Ratio</p>
          <p className="text-3xl font-bold text-gradient-blue">1.84</p>
          <p className="text-xs text-blue-400 mt-1">Excellent risk-adj return</p>
        </div>
        <div className="glass-strong rounded-xl p-6">
          <p className="text-sm text-muted-foreground mb-1">Max Drawdown</p>
          <p className="text-3xl font-bold text-gradient-red">-12.3%</p>
          <p className="text-xs text-red-400 mt-1">vs SPY: -15.8%</p>
        </div>
        <div className="glass-strong rounded-xl p-6">
          <p className="text-sm text-muted-foreground mb-1">Beta</p>
          <p className="text-3xl font-bold text-gradient-purple">0.92</p>
          <p className="text-xs text-purple-400 mt-1">Lower market sensitivity</p>
        </div>
      </div>

      {activeTab === 'overview' && (
        <>
          {/* Asset Allocation */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="glass-strong rounded-xl p-6">
              <h2 className="text-2xl font-bold mb-4">Asset Allocation</h2>
              <div className="flex items-center justify-center mb-6">
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie
                      data={allocationData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {allocationData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1e293b',
                        border: '1px solid #334155',
                        borderRadius: '8px',
                      }}
                      formatter={(value: any, name: any, props: any) => [
                        `${value}%`,
                        `${props.payload.name} (${props.payload.ticker})`,
                      ]}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="grid grid-cols-2 gap-2">
                {allocationData.map((item) => (
                  <div key={item.name} className="flex items-center justify-between p-2 rounded-lg hover:bg-muted/30">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded" style={{ backgroundColor: item.color }} />
                      <span className="text-sm">{item.ticker}</span>
                    </div>
                    <span className="text-sm font-bold">{item.value}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Sector Exposure */}
            <div className="glass-strong rounded-xl p-6">
              <h2 className="text-2xl font-bold mb-4">Sector Exposure vs Benchmark</h2>
              <ResponsiveContainer width="100%" height={380}>
                <BarChart data={sectorData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis type="number" stroke="#94a3b8" tick={{ fontSize: 12 }} />
                  <YAxis
                    type="category"
                    dataKey="sector"
                    stroke="#94a3b8"
                    tick={{ fontSize: 12 }}
                    width={80}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1e293b',
                      border: '1px solid #334155',
                      borderRadius: '8px',
                    }}
                  />
                  <Legend />
                  <Bar dataKey="exposure" fill="#3b82f6" name="Your Portfolio" />
                  <Bar dataKey="benchmark" fill="#6b7280" name="S&P 500" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Correlation Heatmap */}
          <div className="glass-strong rounded-xl p-6">
            <h2 className="text-2xl font-bold mb-4">Asset Correlation Matrix</h2>
            <p className="text-sm text-muted-foreground mb-4">
              Low correlations between assets improve diversification and reduce portfolio risk
            </p>
            <div className="h-[400px]">
              <ReactECharts
                option={correlationHeatmapOption}
                style={{ height: '100%', width: '100%' }}
                opts={{ renderer: 'canvas' }}
              />
            </div>
          </div>
        </>
      )}

      {activeTab === 'optimization' && (
        <>
          {/* Efficient Frontier */}
          <div className="glass-strong rounded-xl p-6">
            <h2 className="text-2xl font-bold mb-2">Efficient Frontier</h2>
            <p className="text-sm text-muted-foreground mb-4">
              Optimal portfolios that maximize return for a given level of risk
            </p>
            <div className="h-[450px]">
              <ReactECharts
                option={efficientFrontierOption}
                style={{ height: '100%', width: '100%' }}
                opts={{ renderer: 'canvas' }}
              />
            </div>
            <div className="grid grid-cols-4 gap-4 mt-6">
              <div className="glass rounded-lg p-4 border-l-4 border-l-green-500">
                <p className="text-xs text-muted-foreground mb-1">Your Portfolio</p>
                <p className="text-lg font-bold text-green-400">8.5% risk / 6.2% return</p>
              </div>
              <div className="glass rounded-lg p-4 border-l-4 border-l-purple-500">
                <p className="text-xs text-muted-foreground mb-1">Optimal Portfolio</p>
                <p className="text-lg font-bold text-purple-400">6.2% risk / 7.8% return</p>
              </div>
              <div className="glass rounded-lg p-4 border-l-4 border-l-cyan-500">
                <p className="text-xs text-muted-foreground mb-1">Min Variance</p>
                <p className="text-lg font-bold text-cyan-400">4.5% risk / 4.2% return</p>
              </div>
              <div className="glass rounded-lg p-4 border-l-4 border-l-amber-500">
                <p className="text-xs text-muted-foreground mb-1">S&P 500</p>
                <p className="text-lg font-bold text-amber-400">15.8% risk / 10.5% return</p>
              </div>
            </div>
          </div>

          {/* Optimization Recommendations */}
          <div className="glass-strong rounded-xl p-6">
            <h2 className="text-2xl font-bold mb-4">Optimization Recommendations</h2>
            <div className="space-y-4">
              <div className="border border-purple-500/30 bg-purple-500/10 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-xl">🎯</span>
                  </div>
                  <div>
                    <h3 className="font-bold text-purple-400 mb-1">Move to Optimal Portfolio</h3>
                    <p className="text-sm text-muted-foreground mb-2">
                      By rebalancing to the optimal allocation, you can improve your expected return by 1.6% while reducing risk by 2.3%.
                    </p>
                    <div className="flex gap-4 text-sm">
                      <span className="text-green-400">+1.6% return</span>
                      <span className="text-blue-400">-2.3% risk</span>
                      <span className="text-purple-400">+0.35 Sharpe</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="border border-yellow-500/30 bg-yellow-500/10 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-lg bg-yellow-500/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-xl">⚠️</span>
                  </div>
                  <div>
                    <h3 className="font-bold text-yellow-400 mb-1">Technology Overweight</h3>
                    <p className="text-sm text-muted-foreground mb-2">
                      Technology exposure is 3% above benchmark. Consider rebalancing to reduce sector concentration risk.
                    </p>
                    <button className="text-xs text-yellow-400 font-semibold hover:underline">
                      View rebalancing recommendations →
                    </button>
                  </div>
                </div>
              </div>

              <div className="border border-blue-500/30 bg-blue-500/10 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-xl">💡</span>
                  </div>
                  <div>
                    <h3 className="font-bold text-blue-400 mb-1">Add International Bonds</h3>
                    <p className="text-sm text-muted-foreground mb-2">
                      Increasing international bond exposure to 5% could improve diversification and reduce volatility by 0.8%.
                    </p>
                    <button className="text-xs text-blue-400 font-semibold hover:underline">
                      See detailed analysis →
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {activeTab === 'risk' && (
        <>
          {/* Monte Carlo Simulation */}
          <div className="glass-strong rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-2xl font-bold mb-1">Monte Carlo Simulation</h2>
                <p className="text-sm text-muted-foreground">
                  {simulationRuns} simulations over 1 year (252 trading days) with confidence bands
                </p>
              </div>
              <button
                onClick={() => setSimulationRuns(prev => prev)}
                className="btn-secondary !py-2 !px-4 text-sm"
              >
                🔄 Regenerate
              </button>
            </div>

            <div className="h-[400px]">
              <ReactECharts
                option={monteCarloOption}
                style={{ height: '100%', width: '100%' }}
                opts={{ renderer: 'canvas' }}
              />
            </div>

            <div className="grid grid-cols-5 gap-4 mt-6">
              <div className="glass rounded-lg p-4">
                <p className="text-xs text-muted-foreground mb-1">Mean Outcome</p>
                <p className="text-lg font-bold text-blue-400">
                  ${mcStats.avg.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </p>
              </div>
              <div className="glass rounded-lg p-4">
                <p className="text-xs text-muted-foreground mb-1">95th Percentile</p>
                <p className="text-lg font-bold text-green-400">
                  ${mcStats.p95.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </p>
              </div>
              <div className="glass rounded-lg p-4">
                <p className="text-xs text-muted-foreground mb-1">Median</p>
                <p className="text-lg font-bold text-amber-400">
                  ${mcStats.p50.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </p>
              </div>
              <div className="glass rounded-lg p-4">
                <p className="text-xs text-muted-foreground mb-1">5th Percentile</p>
                <p className="text-lg font-bold text-red-400">
                  ${mcStats.p5.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </p>
              </div>
              <div className="glass rounded-lg p-4">
                <p className="text-xs text-muted-foreground mb-1">Worst Case</p>
                <p className="text-lg font-bold text-red-500">
                  ${mcStats.min.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </p>
              </div>
            </div>
          </div>

          {/* Risk Metrics Over Time */}
          <div className="glass-strong rounded-xl p-6">
            <h2 className="text-2xl font-bold mb-4">Risk Metrics (24 Months)</h2>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={riskMetricsData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="month" stroke="#94a3b8" tick={{ fontSize: 12 }} />
                <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
                <YAxis yAxisId="right" orientation="right" stroke="#3b82f6" tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="var95"
                  stroke="#ef4444"
                  strokeWidth={2}
                  name="VaR 95%"
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="cvar95"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  name="CVaR 95%"
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="beta"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  name="Beta"
                  yAxisId="right"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>

            <div className="grid grid-cols-4 gap-4 mt-6">
              <div className="glass rounded-lg p-4">
                <p className="text-xs text-muted-foreground mb-1">Current VaR (95%)</p>
                <p className="text-lg font-bold text-red-400">-2.8%</p>
                <p className="text-xs text-muted-foreground mt-1">1-day, $2,800 at risk</p>
              </div>
              <div className="glass rounded-lg p-4">
                <p className="text-xs text-muted-foreground mb-1">Current CVaR (95%)</p>
                <p className="text-lg font-bold text-orange-400">-4.2%</p>
                <p className="text-xs text-muted-foreground mt-1">Expected tail loss</p>
              </div>
              <div className="glass rounded-lg p-4">
                <p className="text-xs text-muted-foreground mb-1">Portfolio Beta</p>
                <p className="text-lg font-bold text-blue-400">0.92</p>
                <p className="text-xs text-muted-foreground mt-1">vs S&P 500</p>
              </div>
              <div className="glass rounded-lg p-4">
                <p className="text-xs text-muted-foreground mb-1">Diversification</p>
                <p className="text-lg font-bold text-green-400">87%</p>
                <p className="text-xs text-muted-foreground mt-1">Well diversified</p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
