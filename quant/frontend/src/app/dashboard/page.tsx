/**
 * Dashboard Page
 * Overview of platform metrics, top traders, and recent activity with interactive visualizations
 */

'use client'

import { useMemo } from 'react'
import { usePoliticians, useNetworkAnalysis } from '@/lib/hooks'
import Link from 'next/link'
import dynamic from 'next/dynamic'

const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

export default function DashboardPage() {
  const { data: politicians, isLoading: politiciansLoading } = usePoliticians(30)
  const { data: network, isLoading: networkLoading } = useNetworkAnalysis({
    min_trades: 50,
    min_correlation: 0.5,
  })

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
    { name: 'Technology', value: 35, color: '#3b82f6' },
    { name: 'Healthcare', value: 22, color: '#22c55e' },
    { name: 'Finance', value: 18, color: '#a855f7' },
    { name: 'Energy', value: 12, color: '#f59e0b' },
    { name: 'Defense', value: 8, color: '#ef4444' },
    { name: 'Other', value: 5, color: '#6b7280' },
  ], [])

  const partyData = useMemo(() => {
    if (!politicians) return []
    const dems = politicians.filter(p => p.party === 'Democratic').length
    const reps = politicians.filter(p => p.party === 'Republican').length
    const other = politicians.length - dems - reps
    return [
      { name: 'Democratic', value: dems, color: '#3b82f6' },
      { name: 'Republican', value: reps, color: '#ef4444' },
      { name: 'Independent', value: other, color: '#6b7280' },
    ].filter(d => d.value > 0)
  }, [politicians])

  // Trading activity line chart
  const activityChartOptions = useMemo(() => ({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0,0,0,0.8)',
      borderColor: 'rgba(59,130,246,0.5)',
      textStyle: { color: '#fff' },
    },
    legend: {
      data: ['Buys', 'Sells'],
      textStyle: { color: '#94a3b8' },
      top: 0,
    },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: tradingActivityData.map(d => d.month),
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' },
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#1e293b' } },
    },
    series: [
      {
        name: 'Buys',
        type: 'line',
        data: tradingActivityData.map(d => d.buys),
        smooth: true,
        lineStyle: { width: 3, color: '#22c55e' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(34,197,94,0.3)' },
              { offset: 1, color: 'rgba(34,197,94,0)' },
            ],
          },
        },
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: { color: '#22c55e' },
      },
      {
        name: 'Sells',
        type: 'line',
        data: tradingActivityData.map(d => d.sells),
        smooth: true,
        lineStyle: { width: 3, color: '#ef4444' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(239,68,68,0.3)' },
              { offset: 1, color: 'rgba(239,68,68,0)' },
            ],
          },
        },
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: { color: '#ef4444' },
      },
    ],
  }), [tradingActivityData])

  // Sector allocation pie chart
  const sectorChartOptions = useMemo(() => ({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(0,0,0,0.8)',
      borderColor: 'rgba(59,130,246,0.5)',
      textStyle: { color: '#fff' },
      formatter: '{b}: {c}% ({d}%)'
    },
    series: [{
      type: 'pie',
      radius: ['45%', '70%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 6,
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
      labelLine: { lineStyle: { color: '#475569' } },
      emphasis: {
        label: { show: true, fontSize: 14, fontWeight: 'bold' },
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
      backgroundColor: 'rgba(0,0,0,0.8)',
      textStyle: { color: '#fff' },
    },
    series: [{
      type: 'pie',
      radius: ['55%', '80%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#0f172a',
        borderWidth: 3,
      },
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 16, fontWeight: 'bold', color: '#fff' },
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
        radius: '90%',
        center: ['50%', '60%'],
        axisLine: {
          lineStyle: {
            width: 15,
            color: [
              [0.3, '#ef4444'],
              [0.6, '#f59e0b'],
              [1, '#22c55e']
            ]
          }
        },
        pointer: {
          icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
          length: '55%',
          width: 10,
          offsetCenter: [0, '-10%'],
          itemStyle: { color: '#3b82f6' }
        },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        title: {
          offsetCenter: [0, '25%'],
          fontSize: 14,
          color: '#94a3b8',
        },
        detail: {
          fontSize: 28,
          offsetCenter: [0, '0%'],
          valueAnimation: true,
          formatter: (value: number) => value.toFixed(3),
          color: '#fff',
          fontWeight: 'bold',
        },
        data: [{ value: density, name: 'Network Density' }]
      }]
    }
  }, [network])

  // Weekly volume bar chart
  const volumeChartOptions = useMemo(() => {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    const volumes = days.map(() => Math.floor(Math.random() * 50 + 30))
    return {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(0,0,0,0.8)',
        textStyle: { color: '#fff' },
      },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        data: days,
        axisLine: { lineStyle: { color: '#334155' } },
        axisLabel: { color: '#94a3b8' },
      },
      yAxis: {
        type: 'value',
        axisLine: { lineStyle: { color: '#334155' } },
        axisLabel: { color: '#94a3b8' },
        splitLine: { lineStyle: { color: '#1e293b' } },
      },
      series: [{
        type: 'bar',
        data: volumes.map((v, i) => ({
          value: v,
          itemStyle: {
            color: {
              type: 'linear',
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: '#6366f1' },
                { offset: 1, color: '#3b82f6' }
              ]
            },
            borderRadius: [4, 4, 0, 0],
          }
        })),
        barWidth: '50%',
      }]
    }
  }, [])

  if (politiciansLoading || networkLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="relative">
            <div className="inline-block h-16 w-16 animate-spin rounded-full border-4 border-solid border-primary/20 border-t-primary" />
            <div className="absolute inset-0 h-16 w-16 rounded-full bg-primary/10 blur-xl animate-pulse" />
          </div>
          <p className="mt-6 text-lg font-medium text-muted-foreground animate-pulse">Loading dashboard...</p>
          <p className="mt-2 text-sm text-muted-foreground/60">Fetching latest data</p>
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
    <div className="space-y-8">
      {/* Page header */}
      <div className="animate-fade-in">
        <h1 className="text-4xl md:text-5xl font-bold mb-3 bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
          Dashboard
        </h1>
        <p className="text-lg text-muted-foreground">
          Overview of Congressional trading activity and network analytics
        </p>
      </div>

      {/* Key metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        <MetricCard
          title="Total Politicians"
          value={totalPoliticians.toLocaleString()}
          subtitle="With ≥30 trades"
          trend="+5.2%"
          gradient="from-blue-500 to-cyan-500"
          delay={0}
        />
        <MetricCard
          title="Total Trades"
          value={totalTrades.toLocaleString()}
          subtitle="All time"
          trend="+12.3%"
          gradient="from-purple-500 to-pink-500"
          delay={100}
        />
        <MetricCard
          title="Active Last 7 Days"
          value={activePoliticians.toLocaleString()}
          subtitle="Recent traders"
          trend={`${((activePoliticians / totalPoliticians) * 100).toFixed(1)}%`}
          gradient="from-green-500 to-emerald-500"
          delay={200}
        />
        <MetricCard
          title="Network Density"
          value={(network?.density || 0).toFixed(3)}
          subtitle="Correlation strength"
          trend={(network?.clustering_coefficient || 0).toFixed(2)}
          gradient="from-orange-500 to-red-500"
          delay={300}
        />
      </div>

      {/* Trading Activity Chart */}
      <div className="glass-strong rounded-xl p-6 border border-border/50 animate-fade-in" style={{ animationDelay: '400ms', animationFillMode: 'backwards' }}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold">Trading Activity</h2>
            <p className="text-sm text-muted-foreground">Monthly buy/sell volume over the past year</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-green-500"></span>
              <span className="text-sm text-muted-foreground">Buys</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-red-500"></span>
              <span className="text-sm text-muted-foreground">Sells</span>
            </div>
          </div>
        </div>
        <div className="h-[300px]">
          <ReactECharts option={activityChartOptions} style={{ height: '100%', width: '100%' }} />
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sector Allocation */}
        <div className="glass-strong rounded-xl p-6 border border-border/50 animate-fade-in" style={{ animationDelay: '500ms', animationFillMode: 'backwards' }}>
          <h3 className="text-lg font-semibold mb-4">Sector Allocation</h3>
          <div className="h-[250px]">
            <ReactECharts option={sectorChartOptions} style={{ height: '100%', width: '100%' }} />
          </div>
        </div>

        {/* Party Distribution */}
        <div className="glass-strong rounded-xl p-6 border border-border/50 animate-fade-in" style={{ animationDelay: '550ms', animationFillMode: 'backwards' }}>
          <h3 className="text-lg font-semibold mb-4">Party Distribution</h3>
          <div className="h-[200px]">
            <ReactECharts option={partyChartOptions} style={{ height: '100%', width: '100%' }} />
          </div>
          <div className="flex justify-center gap-6 mt-4">
            {partyData.map(p => (
              <div key={p.name} className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full" style={{ backgroundColor: p.color }}></span>
                <span className="text-sm">{p.name}: {p.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Weekly Volume */}
        <div className="glass-strong rounded-xl p-6 border border-border/50 animate-fade-in" style={{ animationDelay: '600ms', animationFillMode: 'backwards' }}>
          <h3 className="text-lg font-semibold mb-4">This Week's Volume</h3>
          <div className="h-[250px]">
            <ReactECharts option={volumeChartOptions} style={{ height: '100%', width: '100%' }} />
          </div>
        </div>
      </div>

      {/* Network overview and top traders */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Network metrics with gauge */}
        <div className="glass-strong rounded-xl p-6 border border-border/50 hover:shadow-xl hover:border-primary/30 transition-all duration-300 group animate-fade-in" style={{ animationDelay: '650ms', animationFillMode: 'backwards' }}>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Network Analysis</h2>
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center group-hover:scale-110 transition-transform">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
            </div>
          </div>
          {network ? (
            <div className="grid grid-cols-2 gap-4">
              <div className="h-[180px]">
                <ReactECharts option={networkGaugeOptions} style={{ height: '100%', width: '100%' }} />
              </div>
              <div className="space-y-4">
                <div className="bg-muted/30 rounded-lg p-3">
                  <p className="text-xs text-muted-foreground mb-1">Politicians in Network</p>
                  <p className="text-2xl font-bold">{network.num_politicians}</p>
                </div>
                <div className="bg-muted/30 rounded-lg p-3">
                  <p className="text-xs text-muted-foreground mb-1">Clustering Coefficient</p>
                  <p className="text-2xl font-bold">{network.clustering_coefficient.toFixed(3)}</p>
                </div>
                <div className="bg-muted/30 rounded-lg p-3">
                  <p className="text-xs text-muted-foreground mb-1">Avg Path Length</p>
                  <p className="text-2xl font-bold">{network.average_path_length.toFixed(2)}</p>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-muted-foreground">No network data available</p>
          )}
          <div className="mt-4 pt-4 border-t border-border">
            <Link
              href="/network"
              className="inline-flex items-center text-sm text-primary hover:underline"
            >
              View Network Visualization →
            </Link>
          </div>
        </div>

        {/* Top traders */}
        <div className="glass-strong rounded-xl p-6 border border-border/50 hover:shadow-xl hover:border-primary/30 transition-all duration-300 group animate-fade-in" style={{ animationDelay: '700ms', animationFillMode: 'backwards' }}>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold">Top Traders</h2>
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center group-hover:scale-110 transition-transform">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
          </div>
          <div className="space-y-2">
            {topTraders.map((pol, idx) => (
              <Link
                key={pol.id}
                href={`/politicians/${pol.id}`}
                className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/50 transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <div className={`flex items-center justify-center w-8 h-8 rounded-full font-semibold text-sm ${
                    idx < 3 ? 'bg-gradient-to-br from-yellow-500 to-orange-500 text-white' : 'bg-primary/10 text-primary'
                  }`}>
                    {idx + 1}
                  </div>
                  <div>
                    <p className="font-medium group-hover:text-primary transition-colors">
                      {pol.name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      <span className={pol.party === 'Democratic' ? 'text-blue-500' : 'text-red-500'}>{pol.party?.charAt(0)}</span> • {pol.state}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold">{pol.trade_count?.toLocaleString()}</p>
                  <p className="text-xs text-muted-foreground">trades</p>
                </div>
              </Link>
            ))}
          </div>
          <div className="mt-4 pt-4 border-t border-border">
            <Link
              href="/politicians"
              className="inline-flex items-center text-sm text-primary hover:underline"
            >
              View All Politicians →
            </Link>
          </div>
        </div>
      </div>

      {/* Central politicians */}
      {network && network.central_politicians.length > 0 && (
        <div className="glass-strong rounded-xl p-6 border border-border/50 animate-fade-in" style={{ animationDelay: '750ms', animationFillMode: 'backwards' }}>
          <h2 className="text-xl font-semibold mb-2">Most Central Politicians</h2>
          <p className="text-sm text-muted-foreground mb-6">
            Politicians with the highest network centrality scores (most interconnected)
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {network.central_politicians.slice(0, 6).map((central, idx) => (
              <Link
                key={central.politician_id}
                href={`/politicians/${central.politician_id}`}
                className="flex items-center gap-3 p-4 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors group border border-transparent hover:border-primary/20"
              >
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                  idx === 0 ? 'bg-gradient-to-br from-yellow-500 to-orange-500 text-white' :
                  idx === 1 ? 'bg-gradient-to-br from-gray-300 to-gray-400 text-gray-800' :
                  idx === 2 ? 'bg-gradient-to-br from-amber-600 to-amber-700 text-white' :
                  'bg-primary/10 text-primary'
                }`}>
                  {idx + 1}
                </div>
                <div className="flex-1">
                  <p className="font-medium group-hover:text-primary transition-colors">
                    {central.name}
                  </p>
                  <div className="mt-1">
                    <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                      <span>Centrality</span>
                      <span className="font-medium text-primary">{central.centrality_score.toFixed(3)}</span>
                    </div>
                    <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-primary to-blue-400 rounded-full transition-all"
                        style={{
                          width: `${(central.centrality_score / Math.max(...network.central_politicians.map(c => c.centrality_score))) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Quick actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
        <Link
          href="/compare"
          className="block p-6 glass-strong border border-border/50 rounded-xl hover:border-primary/50 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-500" />
          <div className="relative">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">
              Compare Politicians
            </h3>
            <p className="text-sm text-muted-foreground">
              Side-by-side comparison of trading performance and strategies
            </p>
            <div className="mt-4 text-primary text-sm font-medium flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              Explore <span>→</span>
            </div>
          </div>
        </Link>

        <Link
          href="/network"
          className="block p-6 glass-strong border border-border/50 rounded-xl hover:border-primary/50 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-500" />
          <div className="relative">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">
              Network Visualization
            </h3>
            <p className="text-sm text-muted-foreground">
              Interactive network graph showing politician trading correlations
            </p>
            <div className="mt-4 text-primary text-sm font-medium flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              Explore <span>→</span>
            </div>
          </div>
        </Link>

        <Link
          href="/scanner"
          className="block p-6 glass-strong border border-border/50 rounded-xl hover:border-primary/50 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-green-500/10 to-emerald-500/10 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-500" />
          <div className="relative">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">
              Quant Scanner
            </h3>
            <p className="text-sm text-muted-foreground">
              Pattern recognition, stat arb, and volume anomaly detection
            </p>
            <div className="mt-4 text-primary text-sm font-medium flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              Explore <span>→</span>
            </div>
          </div>
        </Link>
      </div>
    </div>
  )
}

interface MetricCardProps {
  title: string
  value: string
  subtitle: string
  trend?: string
  gradient?: string
  delay?: number
}

function MetricCard({ title, value, subtitle, trend, gradient, delay = 0 }: MetricCardProps) {
  return (
    <div
      className="relative group glass-strong border border-border/50 rounded-xl p-6 hover:shadow-2xl hover:-translate-y-1 hover:border-primary/50 transition-all duration-300 overflow-hidden animate-fade-in"
      style={{
        animationDelay: `${delay}ms`,
        animationFillMode: 'backwards',
      }}
    >
      {/* Gradient background on hover */}
      {gradient && (
        <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />
      )}

      {/* Content */}
      <div className="relative">
        <p className="text-sm font-medium text-muted-foreground mb-3">{title}</p>
        <p className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-br from-foreground to-foreground/70">
          {value}
        </p>
        <div className="flex items-center justify-between">
          <p className="text-xs text-muted-foreground">{subtitle}</p>
          {trend && (
            <span className="inline-flex items-center gap-1 text-xs font-semibold text-green-500 bg-green-500/10 px-2 py-1 rounded-full">
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              {trend}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
