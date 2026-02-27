'use client'

import { useMemo } from 'react'
import dynamic from 'next/dynamic'

const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

interface RollingMetricsChartProps {
  rollingMetrics: Array<{ day: number; sharpe: number; volatility: number }>
}

export function RollingMetricsChart({ rollingMetrics }: RollingMetricsChartProps) {
  const option = useMemo(() => ({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(30, 41, 59, 0.95)',
      borderColor: '#334155',
      textStyle: { color: '#e2e8f0' },
    },
    legend: {
      data: ['Rolling Sharpe', 'Volatility %'],
      textStyle: { color: '#94a3b8' },
      top: 10,
    },
    grid: { left: '3%', right: '4%', bottom: '10%', top: '15%', containLabel: true },
    xAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#475569' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { show: false },
    },
    yAxis: [
      {
        type: 'value', name: 'Sharpe',
        axisLine: { lineStyle: { color: '#3b82f6' } },
        axisLabel: { color: '#3b82f6' },
        splitLine: { lineStyle: { color: '#334155', type: 'dashed' } },
      },
      {
        type: 'value', name: 'Volatility %',
        axisLine: { lineStyle: { color: '#f59e0b' } },
        axisLabel: { color: '#f59e0b' },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: 'Rolling Sharpe', type: 'line',
        data: rollingMetrics.map(d => [d.day, d.sharpe]),
        smooth: true, lineStyle: { color: '#3b82f6', width: 2 }, symbol: 'none',
      },
      {
        name: 'Volatility %', type: 'line', yAxisIndex: 1,
        data: rollingMetrics.map(d => [d.day, d.volatility]),
        smooth: true, lineStyle: { color: '#f59e0b', width: 2 }, symbol: 'none',
      },
    ],
  }), [rollingMetrics])

  return (
    <div className="glass-strong rounded-xl p-6">
      <h2 className="text-2xl font-bold mb-4">Rolling Risk Metrics (20-day window)</h2>
      <div className="h-[350px]">
        <ReactECharts option={option} style={{ height: '100%', width: '100%' }} opts={{ renderer: 'canvas' }} />
      </div>
    </div>
  )
}
