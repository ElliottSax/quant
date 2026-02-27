'use client'

import { useMemo } from 'react'
import dynamic from 'next/dynamic'

const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

interface EquityDataPoint {
  day: number
  equity: number
  benchmark: number
  drawdown: number
}

interface EquityCurveChartProps {
  equityData: EquityDataPoint[]
  initialCapital: number
  finalEquity: number
}

export function EquityCurveChart({ equityData, initialCapital, finalEquity }: EquityCurveChartProps) {
  const option = useMemo(() => ({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(30, 41, 59, 0.95)',
      borderColor: '#334155',
      textStyle: { color: '#e2e8f0' },
      formatter: (params: any) => {
        const data = params[0]?.data
        if (!data) return ''
        const point = equityData[data[0] - 1]
        return `
          <div style="padding: 8px;">
            <div style="font-weight: bold; margin-bottom: 4px;">Day ${data[0]}</div>
            <div>Strategy: <span style="color: #10b981; font-weight: bold;">$${data[1].toLocaleString()}</span></div>
            <div>Benchmark: <span style="color: #6b7280;">$${point?.benchmark.toLocaleString()}</span></div>
            <div>Drawdown: <span style="color: #ef4444;">${point?.drawdown.toFixed(2)}%</span></div>
          </div>
        `
      },
    },
    legend: {
      data: ['Strategy Equity', 'Benchmark (10% Annual)'],
      textStyle: { color: '#94a3b8' },
      top: 10,
    },
    grid: { left: '3%', right: '4%', bottom: '15%', top: '15%', containLabel: true },
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
      axisLabel: { color: '#94a3b8', formatter: (value: number) => `$${(value / 1000).toFixed(0)}k` },
      splitLine: { lineStyle: { color: '#334155', type: 'dashed' } },
    },
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
      {
        type: 'slider', start: 0, end: 100, height: 20, bottom: 5,
        borderColor: '#475569', backgroundColor: 'rgba(71, 85, 105, 0.3)',
        fillerColor: 'rgba(59, 130, 246, 0.3)', handleStyle: { color: '#3b82f6' },
        textStyle: { color: '#94a3b8' },
      },
    ],
    series: [
      {
        name: 'Strategy Equity', type: 'line',
        data: equityData.map(d => [d.day, d.equity]),
        smooth: true, lineStyle: { color: '#10b981', width: 2 },
        areaStyle: {
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(16, 185, 129, 0.4)' },
              { offset: 1, color: 'rgba(16, 185, 129, 0.05)' },
            ],
          },
        },
        symbol: 'none',
      },
      {
        name: 'Benchmark (10% Annual)', type: 'line',
        data: equityData.map(d => [d.day, d.benchmark]),
        smooth: true, lineStyle: { color: '#6b7280', width: 2, type: 'dashed' },
        symbol: 'none',
      },
    ],
  }), [equityData])

  return (
    <div className="glass-strong rounded-xl p-6">
      <h2 className="text-2xl font-bold mb-4">Equity Curve</h2>
      <div className="h-[450px]">
        <ReactECharts option={option} style={{ height: '100%', width: '100%' }} opts={{ renderer: 'canvas' }} />
      </div>
      <div className="grid grid-cols-3 gap-4 mt-6">
        <div className="glass rounded-lg p-4">
          <p className="text-xs text-muted-foreground mb-1">Initial Capital</p>
          <p className="text-xl font-bold">${initialCapital.toLocaleString()}</p>
        </div>
        <div className="glass rounded-lg p-4">
          <p className="text-xs text-muted-foreground mb-1">Final Equity</p>
          <p className="text-xl font-bold text-green-400">${finalEquity.toLocaleString(undefined, { maximumFractionDigits: 0 })}</p>
        </div>
        <div className="glass rounded-lg p-4">
          <p className="text-xs text-muted-foreground mb-1">Profit</p>
          <p className="text-xl font-bold text-cyan-400">
            ${(finalEquity - initialCapital).toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </p>
        </div>
      </div>
    </div>
  )
}
