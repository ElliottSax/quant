/**
 * Dashboard Page
 * BigCharts-style overview with terminal panels and dense data visualization
 */

'use client'

import { useMemo } from 'react'
import Link from 'next/link'
import dynamic from 'next/dynamic'
import { usePoliticians, useNetworkAnalysis } from '@/lib/hooks'

const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

// BigCharts-style color palette
const COLORS = {
  gold: 'hsl(45, 96%, 58%)',
  green: 'hsl(142, 71%, 55%)',
  red: 'hsl(0, 72%, 55%)',
  blue: 'hsl(210, 100%, 56%)',
  cyan: 'hsl(180, 100%, 45%)',
  purple: 'hsl(270, 70%, 60%)',
  gray: 'hsl(215, 20%, 55%)',
  bg: 'hsl(220, 60%, 4%)',
  panel: 'hsl(220, 55%, 6%)',
  border: 'hsl(215, 40%, 18%)',
}

export default function DashboardPage() {
  // Fetch real data from API
  const { data: politicians, isLoading: politiciansLoading, error: politiciansError } = usePoliticians()
  const { data: network, isLoading: networkLoading, error: networkError } = useNetworkAnalysis()

  const isLoading = politiciansLoading || networkLoading
  const hasError = politiciansError || networkError

  // Generate mock historical data for charts
  const tradingActivityData = useMemo(() => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return months.map((month, i) => ({
      month,
      buys: Math.floor(150 + Math.sin(i * 0.5) * 50 + Math.random() * 30),
      sells: Math.floor(120 + Math.cos(i * 0.5) * 40 + Math.random() * 25),
    }))
  }, [])

  const sectorData = useMemo(() => [
    { name: 'Technology', value: 35, color: COLORS.blue },
    { name: 'Healthcare', value: 22, color: COLORS.green },
    { name: 'Finance', value: 18, color: COLORS.gold },
    { name: 'Energy', value: 12, color: COLORS.cyan },
    { name: 'Defense', value: 8, color: COLORS.red },
    { name: 'Other', value: 5, color: COLORS.gray },
  ], [])

  const partyData = useMemo(() => {
    if (!politicians) return []
    const dems = politicians.filter(p => p.party === 'Democratic').length
    const reps = politicians.filter(p => p.party === 'Republican').length
    const other = politicians.length - dems - reps
    return [
      { name: 'Democratic', value: dems, color: COLORS.blue },
      { name: 'Republican', value: reps, color: COLORS.red },
      { name: 'Independent', value: other, color: COLORS.gray },
    ].filter(d => d.value > 0)
  }, [politicians])

  // Trading activity line chart - Terminal style
  const activityChartOptions = useMemo(() => ({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'hsl(220, 55%, 8%)',
      borderColor: 'hsl(215, 40%, 20%)',
      textStyle: { color: '#fff', fontFamily: 'JetBrains Mono, monospace', fontSize: 11 },
    },
    legend: {
      data: ['BUYS', 'SELLS'],
      textStyle: { color: COLORS.gray, fontFamily: 'JetBrains Mono, monospace', fontSize: 10 },
      top: 5,
      itemWidth: 12,
      itemHeight: 2,
    },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '18%', containLabel: true },
    xAxis: {
      type: 'category',
      data: tradingActivityData.map(d => d.month),
      axisLine: { lineStyle: { color: 'hsl(215, 40%, 20%)' } },
      axisLabel: { color: COLORS.gray, fontFamily: 'JetBrains Mono, monospace', fontSize: 10 },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisLabel: { color: COLORS.gray, fontFamily: 'JetBrains Mono, monospace', fontSize: 10 },
      splitLine: { lineStyle: { color: 'hsl(215, 40%, 12%)', type: 'dashed' } },
    },
    series: [
      {
        name: 'BUYS',
        type: 'line',
        data: tradingActivityData.map(d => d.buys),
        smooth: false,
        lineStyle: { width: 2, color: COLORS.green },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'hsla(142, 71%, 55%, 0.25)' },
              { offset: 1, color: 'hsla(142, 71%, 55%, 0)' },
            ],
          },
        },
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { color: COLORS.green },
      },
      {
        name: 'SELLS',
        type: 'line',
        data: tradingActivityData.map(d => d.sells),
        smooth: false,
        lineStyle: { width: 2, color: COLORS.red },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'hsla(0, 72%, 55%, 0.25)' },
              { offset: 1, color: 'hsla(0, 72%, 55%, 0)' },
            ],
          },
        },
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { color: COLORS.red },
      },
    ],
  }), [tradingActivityData])

  // Sector allocation pie chart
  const sectorChartOptions = useMemo(() => ({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'hsl(220, 55%, 8%)',
      borderColor: 'hsl(215, 40%, 20%)',
      textStyle: { color: '#fff', fontFamily: 'JetBrains Mono, monospace', fontSize: 11 },
      formatter: '{b}: {c}%'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '65%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 3,
        borderColor: COLORS.bg,
        borderWidth: 2,
      },
      label: {
        show: true,
        position: 'outside',
        color: COLORS.gray,
        fontSize: 10,
        fontFamily: 'JetBrains Mono, monospace',
        formatter: '{b}\n{c}%',
      },
      labelLine: { lineStyle: { color: 'hsl(215, 40%, 25%)' } },
      emphasis: {
        label: { show: true, fontSize: 11, fontWeight: 'bold' },
        itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' },
      },
      data: sectorData.map(s => ({
        value: s.value,
        name: s.name,
        itemStyle: { color: s.color },
      })),
    }],
  }), [sectorData])

  // Party distribution donut
  const partyChartOptions = useMemo(() => ({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'hsl(220, 55%, 8%)',
      borderColor: 'hsl(215, 40%, 20%)',
      textStyle: { color: '#fff', fontFamily: 'JetBrains Mono, monospace', fontSize: 11 },
    },
    series: [{
      type: 'pie',
      radius: ['50%', '75%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 4,
        borderColor: COLORS.bg,
        borderWidth: 3,
      },
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 12, fontWeight: 'bold', color: '#fff', fontFamily: 'JetBrains Mono, monospace' },
      },
      labelLine: { show: false },
      data: partyData.map(p => ({
        value: p.value,
        name: p.name,
        itemStyle: { color: p.color },
      })),
    }],
  }), [partyData])

  // Network metrics gauge
  const networkGaugeOptions = useMemo(() => {
    const density = network?.density || 0
    return {
      backgroundColor: 'transparent',
      series: [{
        type: 'gauge',
        startAngle: 200,
        endAngle: -20,
        min: 0,
        max: 1,
        splitNumber: 5,
        radius: '85%',
        center: ['50%', '55%'],
        axisLine: {
          lineStyle: {
            width: 12,
            color: [
              [0.3, COLORS.red],
              [0.6, COLORS.gold],
              [1, COLORS.green]
            ]
          }
        },
        pointer: {
          icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
          length: '50%',
          width: 8,
          offsetCenter: [0, '-10%'],
          itemStyle: { color: COLORS.blue }
        },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        title: {
          offsetCenter: [0, '30%'],
          fontSize: 11,
          color: COLORS.gray,
          fontFamily: 'JetBrains Mono, monospace',
        },
        detail: {
          fontSize: 24,
          offsetCenter: [0, '5%'],
          valueAnimation: true,
          formatter: (value: number) => value.toFixed(3),
          color: COLORS.gold,
          fontWeight: 'bold',
          fontFamily: 'JetBrains Mono, monospace',
        },
        data: [{ value: density, name: 'DENSITY' }]
      }]
    }
  }, [network])

  // Weekly volume bar chart
  const volumeChartOptions = useMemo(() => {
    const days = ['MON', 'TUE', 'WED', 'THU', 'FRI']
    const volumes = days.map(() => Math.floor(Math.random() * 50 + 30))
    return {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'hsl(220, 55%, 8%)',
        borderColor: 'hsl(215, 40%, 20%)',
        textStyle: { color: '#fff', fontFamily: 'JetBrains Mono, monospace', fontSize: 11 },
      },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        data: days,
        axisLine: { lineStyle: { color: 'hsl(215, 40%, 20%)' } },
        axisLabel: { color: COLORS.gray, fontFamily: 'JetBrains Mono, monospace', fontSize: 10 },
        axisTick: { show: false },
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false },
        axisLabel: { color: COLORS.gray, fontFamily: 'JetBrains Mono, monospace', fontSize: 10 },
        splitLine: { lineStyle: { color: 'hsl(215, 40%, 12%)', type: 'dashed' } },
      },
      series: [{
        type: 'bar',
        data: volumes.map((v) => ({
          value: v,
          itemStyle: {
            color: {
              type: 'linear',
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: COLORS.gold },
                { offset: 1, color: 'hsl(38, 92%, 45%)' }
              ]
            },
            borderRadius: [2, 2, 0, 0],
          }
        })),
        barWidth: '45%',
      }]
    }
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="relative">
            <div className="inline-block h-12 w-12 animate-spin rounded-full border-2 border-[hsl(215,40%,20%)] border-t-[hsl(45,96%,58%)]" />
          </div>
          <p className="mt-4 text-sm font-mono text-[hsl(215,20%,55%)]">LOADING DATA...</p>
        </div>
      </div>
    )
  }

  if (hasError) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center terminal-panel p-8">
          <div className="text-4xl mb-4">!</div>
          <h2 className="text-lg font-bold text-[hsl(0,72%,55%)] mb-2">Connection Error</h2>
          <p className="text-sm text-[hsl(215,20%,55%)] font-mono mb-4">
            {politiciansError?.message || networkError?.message || 'Failed to load data from API'}
          </p>
          <p className="text-xs text-[hsl(215,20%,45%)] font-mono">
            Ensure the backend is running at localhost:8000
          </p>
        </div>
      </div>
    )
  }

  const totalPoliticians = politicians?.length || 0
  const totalTrades = politicians?.reduce((sum, p) => sum + (p.trade_count || 0), 0) || 0
  const activePoliticians = politicians?.filter(p => {
    if (!p.last_trade) return false
    const lastTradeDate = new Date(p.last_trade)
    const daysSinceLastTrade = (Date.now() - lastTradeDate.getTime()) / (1000 * 60 * 60 * 24)
    return daysSinceLastTrade <= 7
  }).length || 0

  const topTraders = [...(politicians || [])]
    .sort((a, b) => (b.trade_count || 0) - (a.trade_count || 0))
    .slice(0, 8)

  return (
    <div className="space-y-4">
      {/* Page header */}
      <div className="flex items-center justify-between mb-2">
        <div>
          <h1 className="text-xl font-bold text-[hsl(45,96%,58%)] uppercase tracking-wider">
            Market Dashboard
          </h1>
          <p className="text-xs text-[hsl(215,20%,55%)] font-mono">
            Congressional Trading Activity Overview
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono text-[hsl(215,20%,50%)]">
            Last Updated: {new Date().toLocaleTimeString()}
          </span>
          <span className="flex items-center gap-1.5 px-2 py-1 rounded bg-[hsl(142,71%,45%)]/10 border border-[hsl(142,71%,45%)]/30">
            <span className="w-1.5 h-1.5 rounded-full bg-[hsl(142,71%,55%)] animate-pulse"></span>
            <span className="text-[10px] font-bold text-[hsl(142,71%,55%)]">LIVE</span>
          </span>
        </div>
      </div>

      {/* Key metrics - Terminal style */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricPanel
          label="POLITICIANS"
          value={totalPoliticians.toString()}
          subtext="Active Traders"
          change="+5.2%"
          positive
        />
        <MetricPanel
          label="TOTAL TRADES"
          value={totalTrades.toLocaleString()}
          subtext="All Time"
          change="+12.3%"
          positive
        />
        <MetricPanel
          label="ACTIVE 7D"
          value={activePoliticians.toString()}
          subtext="Recent Activity"
          change={`${((activePoliticians / totalPoliticians) * 100).toFixed(1)}%`}
          positive
        />
        <MetricPanel
          label="NET DENSITY"
          value={(network?.density || 0).toFixed(3)}
          subtext="Correlation"
          change={(network?.clustering_coefficient || 0).toFixed(2)}
          positive={network?.density ? network.density > 0.3 : false}
        />
      </div>

      {/* Main Chart Panel */}
      <div className="terminal-panel">
        <div className="terminal-panel-header">
          <span>Trading Activity - 12 Month View</span>
          <div className="flex items-center gap-4 text-[10px]">
            <span className="flex items-center gap-1">
              <span className="w-2 h-0.5 bg-[hsl(142,71%,55%)]"></span>
              <span className="text-[hsl(142,71%,55%)]">BUYS</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-0.5 bg-[hsl(0,72%,55%)]"></span>
              <span className="text-[hsl(0,72%,55%)]">SELLS</span>
            </span>
          </div>
        </div>
        <div className="p-3 bg-[hsl(220,60%,4%)]">
          <div className="h-[260px]">
            <ReactECharts option={activityChartOptions} style={{ height: '100%', width: '100%' }} />
          </div>
        </div>
      </div>

      {/* Three column panel grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
        {/* Sector Allocation */}
        <div className="terminal-panel">
          <div className="terminal-panel-header">
            <span>Sector Allocation</span>
          </div>
          <div className="p-3 bg-[hsl(220,60%,4%)]">
            <div className="h-[220px]">
              <ReactECharts option={sectorChartOptions} style={{ height: '100%', width: '100%' }} />
            </div>
          </div>
        </div>

        {/* Party Distribution */}
        <div className="terminal-panel">
          <div className="terminal-panel-header">
            <span>Party Distribution</span>
          </div>
          <div className="p-3 bg-[hsl(220,60%,4%)]">
            <div className="h-[160px]">
              <ReactECharts option={partyChartOptions} style={{ height: '100%', width: '100%' }} />
            </div>
            <div className="flex justify-center gap-4 mt-3 pt-3 border-t border-[hsl(215,40%,14%)]">
              {partyData.map(p => (
                <div key={p.name} className="flex items-center gap-1.5 text-[10px] font-mono">
                  <span className="w-2 h-2 rounded-sm" style={{ backgroundColor: p.color }}></span>
                  <span className="text-[hsl(210,20%,70%)]">{p.name.substring(0, 3).toUpperCase()}</span>
                  <span className="text-white font-bold">{p.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Weekly Volume */}
        <div className="terminal-panel">
          <div className="terminal-panel-header">
            <span>Weekly Volume</span>
          </div>
          <div className="p-3 bg-[hsl(220,60%,4%)]">
            <div className="h-[220px]">
              <ReactECharts option={volumeChartOptions} style={{ height: '100%', width: '100%' }} />
            </div>
          </div>
        </div>
      </div>

      {/* Two column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        {/* Network Analysis */}
        <div className="terminal-panel">
          <div className="terminal-panel-header">
            <span>Network Analysis</span>
            <Link href="/network" className="text-[10px] text-[hsl(210,100%,56%)] hover:text-[hsl(45,96%,58%)] transition-colors">
              VIEW GRAPH →
            </Link>
          </div>
          <div className="p-3 bg-[hsl(220,60%,4%)]">
            {network ? (
              <div className="grid grid-cols-2 gap-3">
                <div className="h-[150px]">
                  <ReactECharts option={networkGaugeOptions} style={{ height: '100%', width: '100%' }} />
                </div>
                <div className="space-y-2">
                  <DataRow label="POLITICIANS" value={network.num_politicians.toString()} />
                  <DataRow label="CLUSTERING" value={network.clustering_coefficient.toFixed(3)} />
                  <DataRow label="AVG PATH" value={network.average_path_length.toFixed(2)} />
                  <DataRow label="DENSITY" value={network.density.toFixed(3)} highlight />
                </div>
              </div>
            ) : (
              <p className="text-sm text-[hsl(215,20%,50%)] font-mono">NO DATA</p>
            )}
          </div>
        </div>

        {/* Top Traders */}
        <div className="terminal-panel">
          <div className="terminal-panel-header">
            <span>Top Traders</span>
            <Link href="/politicians" className="text-[10px] text-[hsl(210,100%,56%)] hover:text-[hsl(45,96%,58%)] transition-colors">
              VIEW ALL →
            </Link>
          </div>
          <div className="bg-[hsl(220,60%,4%)]">
            <table className="w-full text-xs font-mono">
              <thead>
                <tr className="bg-[hsl(215,50%,10%)]">
                  <th className="px-3 py-2 text-left text-[10px] text-[hsl(45,96%,58%)] font-semibold">#</th>
                  <th className="px-3 py-2 text-left text-[10px] text-[hsl(45,96%,58%)] font-semibold">NAME</th>
                  <th className="px-3 py-2 text-left text-[10px] text-[hsl(45,96%,58%)] font-semibold">PARTY</th>
                  <th className="px-3 py-2 text-right text-[10px] text-[hsl(45,96%,58%)] font-semibold">TRADES</th>
                </tr>
              </thead>
              <tbody>
                {topTraders.map((pol, idx) => (
                  <tr
                    key={pol.id}
                    className={`border-b border-[hsl(215,40%,12%)] hover:bg-[hsl(215,50%,12%)] transition-colors cursor-pointer ${
                      idx % 2 === 0 ? 'bg-[hsl(220,55%,5%)]' : ''
                    }`}
                    onClick={() => window.location.href = `/politicians/${pol.id}`}
                  >
                    <td className="px-3 py-2">
                      <span className={`${idx < 3 ? 'text-[hsl(45,96%,58%)] font-bold' : 'text-[hsl(215,20%,50%)]'}`}>
                        {idx + 1}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-white">{pol.name}</td>
                    <td className="px-3 py-2">
                      <span className={pol.party === 'Democratic' ? 'text-[hsl(210,100%,56%)]' : 'text-[hsl(0,72%,55%)]'}>
                        {pol.party?.charAt(0)}
                      </span>
                      <span className="text-[hsl(215,20%,50%)] ml-1">{pol.state}</span>
                    </td>
                    <td className="px-3 py-2 text-right text-[hsl(45,96%,58%)] font-semibold">
                      {pol.trade_count?.toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Central Politicians Panel */}
      {network && network.central_politicians.length > 0 && (
        <div className="terminal-panel">
          <div className="terminal-panel-header">
            <span>Most Central Politicians - Network Influence Score</span>
          </div>
          <div className="p-3 bg-[hsl(220,60%,4%)]">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
              {network.central_politicians.slice(0, 6).map((central, idx) => (
                <Link
                  key={central.politician_id}
                  href={`/politicians/${central.politician_id}`}
                  className="p-3 rounded bg-[hsl(215,50%,10%)] border border-[hsl(215,40%,16%)] hover:border-[hsl(45,96%,58%)]/50 transition-colors group"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`w-5 h-5 rounded text-[10px] font-bold flex items-center justify-center ${
                      idx === 0 ? 'bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)]' :
                      idx === 1 ? 'bg-[hsl(0,0%,75%)] text-[hsl(220,60%,8%)]' :
                      idx === 2 ? 'bg-[hsl(30,80%,50%)] text-white' :
                      'bg-[hsl(215,50%,18%)] text-[hsl(210,20%,70%)]'
                    }`}>
                      {idx + 1}
                    </span>
                    <span className="text-[10px] text-[hsl(215,20%,55%)] uppercase">Rank</span>
                  </div>
                  <p className="text-xs text-white font-medium truncate group-hover:text-[hsl(45,96%,58%)] transition-colors">
                    {central.name}
                  </p>
                  <div className="mt-2 flex items-center justify-between">
                    <span className="text-[10px] text-[hsl(215,20%,50%)]">SCORE</span>
                    <span className="text-xs font-mono font-bold text-[hsl(45,96%,58%)]">
                      {central.centrality_score.toFixed(3)}
                    </span>
                  </div>
                  <div className="mt-1 w-full h-1 bg-[hsl(215,40%,14%)] rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-[hsl(45,96%,58%)] to-[hsl(38,92%,50%)] rounded-full"
                      style={{
                        width: `${(central.centrality_score / Math.max(...network.central_politicians.map(c => c.centrality_score))) * 100}%`,
                      }}
                    />
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <QuickActionCard
          href="/compare"
          title="Compare Politicians"
          description="Side-by-side trading analysis"
          color="blue"
        />
        <QuickActionCard
          href="/network"
          title="Network Visualization"
          description="Interactive correlation graph"
          color="gold"
        />
        <QuickActionCard
          href="/scanner"
          title="Quant Scanner"
          description="Pattern & anomaly detection"
          color="green"
        />
      </div>
    </div>
  )
}

interface MetricPanelProps {
  label: string
  value: string
  subtext: string
  change: string
  positive?: boolean
}

function MetricPanel({ label, value, subtext, change, positive }: MetricPanelProps) {
  return (
    <div className="terminal-panel p-3">
      <div className="flex items-start justify-between mb-1">
        <span className="text-[10px] font-semibold text-[hsl(45,96%,58%)] uppercase tracking-wider">{label}</span>
        <span className={`text-[10px] font-mono font-semibold ${positive ? 'text-[hsl(142,71%,55%)]' : 'text-[hsl(0,72%,55%)]'}`}>
          {positive ? '+' : ''}{change}
        </span>
      </div>
      <p className="text-2xl font-bold font-mono text-white mb-0.5">{value}</p>
      <p className="text-[10px] text-[hsl(215,20%,50%)]">{subtext}</p>
    </div>
  )
}

interface DataRowProps {
  label: string
  value: string
  highlight?: boolean
}

function DataRow({ label, value, highlight }: DataRowProps) {
  return (
    <div className="flex items-center justify-between py-1.5 px-2 rounded bg-[hsl(215,50%,10%)] border border-[hsl(215,40%,14%)]">
      <span className="text-[10px] text-[hsl(215,20%,55%)] uppercase">{label}</span>
      <span className={`text-xs font-mono font-bold ${highlight ? 'text-[hsl(45,96%,58%)]' : 'text-white'}`}>{value}</span>
    </div>
  )
}

interface QuickActionCardProps {
  href: string
  title: string
  description: string
  color: 'blue' | 'gold' | 'green'
}

function QuickActionCard({ href, title, description, color }: QuickActionCardProps) {
  const colorClasses = {
    blue: 'border-[hsl(210,100%,56%)]/30 hover:border-[hsl(210,100%,56%)] hover:bg-[hsl(210,100%,56%)]/5',
    gold: 'border-[hsl(45,96%,58%)]/30 hover:border-[hsl(45,96%,58%)] hover:bg-[hsl(45,96%,58%)]/5',
    green: 'border-[hsl(142,71%,55%)]/30 hover:border-[hsl(142,71%,55%)] hover:bg-[hsl(142,71%,55%)]/5',
  }
  const iconColors = {
    blue: 'text-[hsl(210,100%,56%)]',
    gold: 'text-[hsl(45,96%,58%)]',
    green: 'text-[hsl(142,71%,55%)]',
  }

  return (
    <Link
      href={href}
      className={`block p-4 rounded bg-[hsl(220,55%,6%)] border ${colorClasses[color]} transition-all duration-200 group`}
    >
      <div className="flex items-center gap-3">
        <div className={`w-8 h-8 rounded bg-current/10 flex items-center justify-center ${iconColors[color]}`}>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-white group-hover:text-[hsl(45,96%,58%)] transition-colors">{title}</h3>
          <p className="text-[10px] text-[hsl(215,20%,55%)]">{description}</p>
        </div>
      </div>
    </Link>
  )
}
