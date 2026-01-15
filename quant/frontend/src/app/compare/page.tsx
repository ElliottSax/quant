/**
 * Compare Politicians Page
 * Side-by-side comparison of politician trading records with interactive visualizations
 */

'use client'

import { useState, useMemo } from 'react'
import dynamic from 'next/dynamic'

const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

interface PoliticianData {
  name: string
  party: string
  state: string
  totalTrades: number
  totalValue: string
  avgReturn: number
  winRate: number
  topSectors: { name: string; value: number }[]
  monthlyReturns: number[]
  cumulativeReturns: number[]
  recentTrades: { date: string; symbol: string; type: string; value: string; return: number }[]
  riskMetrics: { volatility: number; sharpe: number; maxDrawdown: number; beta: number }
}

const POLITICIANS = [
  'Nancy Pelosi',
  'Paul Pelosi Jr',
  'Dan Crenshaw',
  'Brian Higgins',
  'Josh Gottheimer',
  'Debbie Wasserman Schultz',
]

export default function ComparePage() {
  const [selected1, setSelected1] = useState('')
  const [selected2, setSelected2] = useState('')

  // Generate realistic mock data
  const generateData = (name: string, seed: number): PoliticianData => {
    const parties = ['Democratic', 'Republican']
    const states = ['CA', 'TX', 'FL', 'NY', 'PA', 'OH']

    // Seeded random for consistent data
    const random = (min: number, max: number) => {
      const x = Math.sin(seed++) * 10000
      return min + (x - Math.floor(x)) * (max - min)
    }

    const monthlyReturns = Array.from({ length: 12 }, () => random(-8, 15))
    let cumulative = 100
    const cumulativeReturns = monthlyReturns.map(r => {
      cumulative *= (1 + r / 100)
      return cumulative
    })

    return {
      name,
      party: parties[Math.floor(random(0, 2))],
      state: states[Math.floor(random(0, 6))],
      totalTrades: Math.floor(random(100, 300)),
      totalValue: `$${(random(15, 50)).toFixed(1)}M`,
      avgReturn: random(12, 28),
      winRate: random(55, 75),
      topSectors: [
        { name: 'Technology', value: random(25, 40) },
        { name: 'Finance', value: random(15, 25) },
        { name: 'Healthcare', value: random(10, 20) },
        { name: 'Energy', value: random(8, 15) },
        { name: 'Defense', value: random(5, 12) },
        { name: 'Other', value: random(5, 15) },
      ],
      monthlyReturns,
      cumulativeReturns,
      recentTrades: [
        { date: '2024-01-15', symbol: 'NVDA', type: 'BUY', value: `$${random(1, 3).toFixed(1)}M`, return: random(10, 40) },
        { date: '2024-01-10', symbol: 'MSFT', type: 'BUY', value: `$${random(0.8, 2).toFixed(1)}M`, return: random(5, 20) },
        { date: '2024-01-05', symbol: 'AAPL', type: 'SELL', value: `$${random(1.5, 4).toFixed(1)}M`, return: random(15, 50) },
        { date: '2023-12-28', symbol: 'GOOGL', type: 'BUY', value: `$${random(0.5, 1.5).toFixed(1)}M`, return: random(-5, 15) },
        { date: '2023-12-20', symbol: 'AMZN', type: 'SELL', value: `$${random(1, 2.5).toFixed(1)}M`, return: random(8, 25) },
      ],
      riskMetrics: {
        volatility: random(12, 25),
        sharpe: random(0.8, 2.2),
        maxDrawdown: random(8, 20),
        beta: random(0.8, 1.4),
      },
    }
  }

  const mockData1 = useMemo(() => selected1 ? generateData(selected1, POLITICIANS.indexOf(selected1) * 100) : null, [selected1])
  const mockData2 = useMemo(() => selected2 ? generateData(selected2, POLITICIANS.indexOf(selected2) * 100 + 50) : null, [selected2])

  const showComparison = selected1 && selected2 && mockData1 && mockData2

  // Performance comparison chart options
  const performanceChartOptions = useMemo(() => {
    if (!mockData1 || !mockData2) return {}

    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    return {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(0,0,0,0.8)',
        borderColor: 'rgba(59,130,246,0.5)',
        textStyle: { color: '#fff' },
        formatter: (params: any) => {
          let html = `<div style="font-weight:bold;margin-bottom:8px">${params[0].axisValue}</div>`
          params.forEach((p: any) => {
            html += `<div style="display:flex;align-items:center;gap:8px;margin:4px 0">
              <span style="width:10px;height:10px;border-radius:50%;background:${p.color}"></span>
              <span>${p.seriesName}: <strong>$${p.value.toFixed(2)}</strong></span>
            </div>`
          })
          return html
        }
      },
      legend: {
        data: [mockData1.name, mockData2.name],
        textStyle: { color: '#94a3b8' },
        top: 0,
      },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
      xAxis: {
        type: 'category',
        data: months,
        axisLine: { lineStyle: { color: '#334155' } },
        axisLabel: { color: '#94a3b8' },
      },
      yAxis: {
        type: 'value',
        name: 'Portfolio Value ($)',
        nameTextStyle: { color: '#94a3b8' },
        axisLine: { lineStyle: { color: '#334155' } },
        axisLabel: { color: '#94a3b8', formatter: '${value}' },
        splitLine: { lineStyle: { color: '#1e293b' } },
      },
      series: [
        {
          name: mockData1.name,
          type: 'line',
          data: mockData1.cumulativeReturns,
          smooth: true,
          lineStyle: { width: 3, color: '#3b82f6' },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(59,130,246,0.3)' },
                { offset: 1, color: 'rgba(59,130,246,0)' },
              ],
            },
          },
          symbol: 'circle',
          symbolSize: 8,
          itemStyle: { color: '#3b82f6' },
        },
        {
          name: mockData2.name,
          type: 'line',
          data: mockData2.cumulativeReturns,
          smooth: true,
          lineStyle: { width: 3, color: '#a855f7' },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(168,85,247,0.3)' },
                { offset: 1, color: 'rgba(168,85,247,0)' },
              ],
            },
          },
          symbol: 'circle',
          symbolSize: 8,
          itemStyle: { color: '#a855f7' },
        },
      ],
    }
  }, [mockData1, mockData2])

  // Monthly returns bar chart
  const monthlyReturnsOptions = useMemo(() => {
    if (!mockData1 || !mockData2) return {}

    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    return {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(0,0,0,0.8)',
        borderColor: 'rgba(59,130,246,0.5)',
        textStyle: { color: '#fff' },
        formatter: (params: any) => {
          let html = `<div style="font-weight:bold;margin-bottom:8px">${params[0].axisValue}</div>`
          params.forEach((p: any) => {
            const color = p.value >= 0 ? '#22c55e' : '#ef4444'
            html += `<div style="display:flex;align-items:center;gap:8px;margin:4px 0">
              <span style="width:10px;height:10px;border-radius:50%;background:${p.color}"></span>
              <span>${p.seriesName}: <strong style="color:${color}">${p.value >= 0 ? '+' : ''}${p.value.toFixed(1)}%</strong></span>
            </div>`
          })
          return html
        }
      },
      legend: {
        data: [mockData1.name, mockData2.name],
        textStyle: { color: '#94a3b8' },
        top: 0,
      },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
      xAxis: {
        type: 'category',
        data: months,
        axisLine: { lineStyle: { color: '#334155' } },
        axisLabel: { color: '#94a3b8' },
      },
      yAxis: {
        type: 'value',
        name: 'Monthly Return (%)',
        nameTextStyle: { color: '#94a3b8' },
        axisLine: { lineStyle: { color: '#334155' } },
        axisLabel: { color: '#94a3b8', formatter: '{value}%' },
        splitLine: { lineStyle: { color: '#1e293b' } },
      },
      series: [
        {
          name: mockData1.name,
          type: 'bar',
          data: mockData1.monthlyReturns.map(v => parseFloat(v.toFixed(1))),
          itemStyle: {
            color: (params: any) => params.value >= 0 ? '#3b82f6' : '#3b82f6aa',
            borderRadius: [4, 4, 0, 0],
          },
          barGap: '10%',
        },
        {
          name: mockData2.name,
          type: 'bar',
          data: mockData2.monthlyReturns.map(v => parseFloat(v.toFixed(1))),
          itemStyle: {
            color: (params: any) => params.value >= 0 ? '#a855f7' : '#a855f7aa',
            borderRadius: [4, 4, 0, 0],
          },
        },
      ],
    }
  }, [mockData1, mockData2])

  // Sector allocation pie charts
  const getSectorPieOptions = (data: PoliticianData, color: string) => ({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(0,0,0,0.8)',
      borderColor: color,
      textStyle: { color: '#fff' },
      formatter: '{b}: {c}% ({d}%)'
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#0f172a',
          borderWidth: 2,
        },
        label: {
          show: true,
          position: 'outside',
          color: '#94a3b8',
          fontSize: 11,
          formatter: '{b}\n{c}%',
        },
        labelLine: {
          lineStyle: { color: '#475569' },
        },
        emphasis: {
          label: { show: true, fontSize: 14, fontWeight: 'bold' },
          itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.5)' },
        },
        data: data.topSectors.map((s, i) => ({
          value: parseFloat(s.value.toFixed(1)),
          name: s.name,
          itemStyle: {
            color: color === '#3b82f6'
              ? ['#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe', '#eff6ff'][i]
              : ['#a855f7', '#c084fc', '#d8b4fe', '#e9d5ff', '#f3e8ff', '#faf5ff'][i]
          },
        })),
      },
    ],
  })

  // Radar chart for risk metrics comparison
  const riskRadarOptions = useMemo(() => {
    if (!mockData1 || !mockData2) return {}

    return {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(0,0,0,0.8)',
        borderColor: 'rgba(59,130,246,0.5)',
        textStyle: { color: '#fff' },
      },
      legend: {
        data: [mockData1.name, mockData2.name],
        textStyle: { color: '#94a3b8' },
        bottom: 0,
      },
      radar: {
        indicator: [
          { name: 'Win Rate', max: 100 },
          { name: 'Sharpe Ratio', max: 3 },
          { name: 'Low Volatility', max: 30 },
          { name: 'Low Drawdown', max: 25 },
          { name: 'Beta', max: 2 },
        ],
        shape: 'polygon',
        splitNumber: 4,
        axisName: { color: '#94a3b8', fontSize: 11 },
        splitLine: { lineStyle: { color: '#1e293b' } },
        splitArea: { show: true, areaStyle: { color: ['rgba(30,41,59,0.3)', 'rgba(15,23,42,0.3)'] } },
        axisLine: { lineStyle: { color: '#334155' } },
      },
      series: [
        {
          type: 'radar',
          data: [
            {
              value: [
                mockData1.winRate,
                mockData1.riskMetrics.sharpe,
                30 - mockData1.riskMetrics.volatility, // Invert for "low is good"
                25 - mockData1.riskMetrics.maxDrawdown, // Invert for "low is good"
                mockData1.riskMetrics.beta,
              ],
              name: mockData1.name,
              lineStyle: { color: '#3b82f6', width: 2 },
              areaStyle: { color: 'rgba(59,130,246,0.3)' },
              itemStyle: { color: '#3b82f6' },
              symbol: 'circle',
              symbolSize: 6,
            },
            {
              value: [
                mockData2.winRate,
                mockData2.riskMetrics.sharpe,
                30 - mockData2.riskMetrics.volatility,
                25 - mockData2.riskMetrics.maxDrawdown,
                mockData2.riskMetrics.beta,
              ],
              name: mockData2.name,
              lineStyle: { color: '#a855f7', width: 2 },
              areaStyle: { color: 'rgba(168,85,247,0.3)' },
              itemStyle: { color: '#a855f7' },
              symbol: 'circle',
              symbolSize: 6,
            },
          ],
        },
      ],
    }
  }, [mockData1, mockData2])

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-fade-in">
        <h1 className="text-4xl md:text-5xl font-bold mb-3 bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
          Compare Politicians
        </h1>
        <p className="text-lg text-muted-foreground">
          Compare trading performance, strategies, and returns side-by-side
        </p>
      </div>

      {/* Selection */}
      <div className="glass-strong rounded-xl p-6 border border-border/50">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-semibold mb-2">Select First Politician</label>
            <select
              value={selected1}
              onChange={(e) => setSelected1(e.target.value)}
              className="input-field"
            >
              <option value="">Choose a politician...</option>
              {POLITICIANS.filter(p => p !== selected2).map(pol => (
                <option key={pol} value={pol}>{pol}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-semibold mb-2">Select Second Politician</label>
            <select
              value={selected2}
              onChange={(e) => setSelected2(e.target.value)}
              className="input-field"
            >
              <option value="">Choose a politician...</option>
              {POLITICIANS.filter(p => p !== selected1).map(pol => (
                <option key={pol} value={pol}>{pol}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Comparison Results */}
      {showComparison ? (
        <div className="space-y-6 animate-fade-in">
          {/* Key Metrics Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <PoliticianCard data={mockData1} color="blue" />
            <PoliticianCard data={mockData2} color="purple" />
          </div>

          {/* Performance Chart */}
          <div className="glass-strong rounded-xl p-6 border border-border/50">
            <h3 className="text-xl font-bold mb-4">Performance Comparison (12 Months)</h3>
            <div className="h-[350px]">
              <ReactECharts option={performanceChartOptions} style={{ height: '100%', width: '100%' }} />
            </div>
          </div>

          {/* Monthly Returns */}
          <div className="glass-strong rounded-xl p-6 border border-border/50">
            <h3 className="text-xl font-bold mb-4">Monthly Returns Comparison</h3>
            <div className="h-[300px]">
              <ReactECharts option={monthlyReturnsOptions} style={{ height: '100%', width: '100%' }} />
            </div>
          </div>

          {/* Sector Allocation Side by Side */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass-strong rounded-xl p-6 border border-border/50">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-blue-500"></span>
                {mockData1.name} - Sector Allocation
              </h3>
              <div className="h-[280px]">
                <ReactECharts option={getSectorPieOptions(mockData1, '#3b82f6')} style={{ height: '100%', width: '100%' }} />
              </div>
            </div>
            <div className="glass-strong rounded-xl p-6 border border-border/50">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-purple-500"></span>
                {mockData2.name} - Sector Allocation
              </h3>
              <div className="h-[280px]">
                <ReactECharts option={getSectorPieOptions(mockData2, '#a855f7')} style={{ height: '100%', width: '100%' }} />
              </div>
            </div>
          </div>

          {/* Risk Metrics Radar */}
          <div className="glass-strong rounded-xl p-6 border border-border/50">
            <h3 className="text-xl font-bold mb-4">Risk Profile Comparison</h3>
            <div className="h-[350px]">
              <ReactECharts option={riskRadarOptions} style={{ height: '100%', width: '100%' }} />
            </div>
          </div>

          {/* Head-to-Head Stats */}
          <div className="glass-strong rounded-xl p-6 border border-border/50">
            <h3 className="text-xl font-bold mb-6">Head-to-Head Statistics</h3>
            <div className="space-y-4">
              <ComparisonBar
                label="Total Trades"
                value1={mockData1.totalTrades}
                value2={mockData2.totalTrades}
                name1={mockData1.name}
                name2={mockData2.name}
              />
              <ComparisonBar
                label="Average Return"
                value1={mockData1.avgReturn}
                value2={mockData2.avgReturn}
                name1={mockData1.name}
                name2={mockData2.name}
                suffix="%"
              />
              <ComparisonBar
                label="Win Rate"
                value1={mockData1.winRate}
                value2={mockData2.winRate}
                name1={mockData1.name}
                name2={mockData2.name}
                suffix="%"
              />
              <ComparisonBar
                label="Sharpe Ratio"
                value1={mockData1.riskMetrics.sharpe}
                value2={mockData2.riskMetrics.sharpe}
                name1={mockData1.name}
                name2={mockData2.name}
              />
              <ComparisonBar
                label="Max Drawdown"
                value1={mockData1.riskMetrics.maxDrawdown}
                value2={mockData2.riskMetrics.maxDrawdown}
                name1={mockData1.name}
                name2={mockData2.name}
                suffix="%"
                inverse
              />
            </div>
          </div>

          {/* Recent Trades Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <RecentTradesCard data={mockData1} color="blue" />
            <RecentTradesCard data={mockData2} color="purple" />
          </div>
        </div>
      ) : (
        <div className="glass rounded-xl p-16 text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary/10 mb-6">
            <svg className="w-10 h-10 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <p className="text-xl font-semibold mb-2">Select Two Politicians to Compare</p>
          <p className="text-muted-foreground">Choose politicians from the dropdowns above to see detailed comparisons</p>
        </div>
      )}
    </div>
  )
}

function PoliticianCard({ data, color }: { data: PoliticianData; color: 'blue' | 'purple' }) {
  const colorClasses = {
    blue: {
      badge: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
      highlight: 'text-blue-500',
      bg: 'bg-blue-500/5',
    },
    purple: {
      badge: 'bg-purple-500/10 text-purple-500 border-purple-500/20',
      highlight: 'text-purple-500',
      bg: 'bg-purple-500/5',
    },
  }[color]

  return (
    <div className={`glass-strong rounded-xl p-6 border border-border/50 ${colorClasses.bg}`}>
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <span className={`w-4 h-4 rounded-full ${color === 'blue' ? 'bg-blue-500' : 'bg-purple-500'}`}></span>
          <h3 className="text-2xl font-bold">{data.name}</h3>
        </div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
            data.party === 'Democratic'
              ? 'bg-blue-500/10 text-blue-500'
              : 'bg-red-500/10 text-red-500'
          }`}>
            {data.party}
          </span>
          <span>{data.state}</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <MetricBox label="Total Trades" value={data.totalTrades.toLocaleString()} />
        <MetricBox label="Total Value" value={data.totalValue} />
        <MetricBox label="Avg Return" value={`${data.avgReturn.toFixed(1)}%`} highlight="green" />
        <MetricBox label="Win Rate" value={`${data.winRate.toFixed(1)}%`} highlight={color} />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <MetricBox label="Volatility" value={`${data.riskMetrics.volatility.toFixed(1)}%`} />
        <MetricBox label="Sharpe Ratio" value={data.riskMetrics.sharpe.toFixed(2)} />
        <MetricBox label="Max Drawdown" value={`${data.riskMetrics.maxDrawdown.toFixed(1)}%`} highlight="red" />
        <MetricBox label="Beta" value={data.riskMetrics.beta.toFixed(2)} />
      </div>
    </div>
  )
}

function RecentTradesCard({ data, color }: { data: PoliticianData; color: 'blue' | 'purple' }) {
  return (
    <div className="glass-strong rounded-xl p-6 border border-border/50">
      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
        <span className={`w-3 h-3 rounded-full ${color === 'blue' ? 'bg-blue-500' : 'bg-purple-500'}`}></span>
        {data.name} - Recent Trades
      </h3>
      <div className="space-y-3">
        {data.recentTrades.map((trade, i) => (
          <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors">
            <div className="flex items-center gap-3">
              <span className="font-bold text-lg">{trade.symbol}</span>
              <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                trade.type === 'BUY'
                  ? 'bg-green-500/10 text-green-500'
                  : 'bg-red-500/10 text-red-500'
              }`}>
                {trade.type}
              </span>
              <span className="text-sm text-muted-foreground">{trade.value}</span>
            </div>
            <div className="text-right">
              <span className={`font-bold ${trade.return >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                {trade.return >= 0 ? '+' : ''}{trade.return.toFixed(1)}%
              </span>
              <p className="text-xs text-muted-foreground">{trade.date}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function MetricBox({ label, value, highlight }: { label: string; value: string | number; highlight?: string }) {
  const colorClass =
    highlight === 'green' ? 'text-green-500' :
    highlight === 'blue' ? 'text-blue-500' :
    highlight === 'purple' ? 'text-purple-500' :
    highlight === 'red' ? 'text-red-500' :
    ''

  return (
    <div className="bg-muted/30 rounded-lg p-3 hover:bg-muted/50 transition-colors">
      <p className="text-xs text-muted-foreground mb-1">{label}</p>
      <p className={`font-bold text-lg ${colorClass}`}>
        {value}
      </p>
    </div>
  )
}

function ComparisonBar({
  label,
  value1,
  value2,
  name1,
  name2,
  suffix = '',
  inverse = false,
}: {
  label: string
  value1: number
  value2: number
  name1: string
  name2: string
  suffix?: string
  inverse?: boolean
}) {
  const total = value1 + value2
  const percent1 = (value1 / total) * 100
  const percent2 = (value2 / total) * 100

  // For inverse metrics (like drawdown), lower is better
  const winner1 = inverse ? value1 < value2 : value1 > value2
  const winner2 = inverse ? value2 < value1 : value2 > value1

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <p className="font-semibold">{label}</p>
        <div className="flex items-center gap-4 text-sm">
          <span className={`font-bold ${winner1 ? 'text-green-500' : 'text-blue-500'}`}>
            {typeof value1 === 'number' ? value1.toFixed(1) : value1}{suffix}
          </span>
          <span className="text-muted-foreground">vs</span>
          <span className={`font-bold ${winner2 ? 'text-green-500' : 'text-purple-500'}`}>
            {typeof value2 === 'number' ? value2.toFixed(1) : value2}{suffix}
          </span>
        </div>
      </div>
      <div className="flex h-4 rounded-full overflow-hidden">
        <div
          className={`${winner1 ? 'bg-green-500' : 'bg-blue-500'} flex items-center justify-center text-[10px] font-bold text-white transition-all`}
          style={{ width: `${percent1}%` }}
        >
          {percent1 > 20 && `${percent1.toFixed(0)}%`}
        </div>
        <div
          className={`${winner2 ? 'bg-green-500' : 'bg-purple-500'} flex items-center justify-center text-[10px] font-bold text-white transition-all`}
          style={{ width: `${percent2}%` }}
        >
          {percent2 > 20 && `${percent2.toFixed(0)}%`}
        </div>
      </div>
    </div>
  )
}
