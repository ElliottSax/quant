'use client'

import { useMemo } from 'react'
import dynamic from 'next/dynamic'

const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

interface DrawdownChartProps {
  equityData: Array<{ day: number; drawdown: number }>
}

export function DrawdownChart({ equityData }: DrawdownChartProps) {
  const option = useMemo(() => ({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(30, 41, 59, 0.95)',
      borderColor: '#334155',
      textStyle: { color: '#e2e8f0' },
      formatter: (params: any) => {
        const data = params[0]?.data
        return `Day ${data[0]}: <span style="color: #ef4444; font-weight: bold;">${data[1].toFixed(2)}%</span>`
      },
    },
    grid: { left: '3%', right: '4%', bottom: '10%', top: '10%', containLabel: true },
    xAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#475569' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value', max: 0,
      axisLine: { lineStyle: { color: '#475569' } },
      axisLabel: { color: '#94a3b8', formatter: (value: number) => `${value}%` },
      splitLine: { lineStyle: { color: '#334155', type: 'dashed' } },
    },
    series: [{
      type: 'line',
      data: equityData.map(d => [d.day, d.drawdown]),
      smooth: true, lineStyle: { color: '#ef4444', width: 1 },
      areaStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(239, 68, 68, 0.5)' },
            { offset: 1, color: 'rgba(239, 68, 68, 0.1)' },
          ],
        },
      },
      symbol: 'none',
    }],
  }), [equityData])

  return (
    <div className="glass-strong rounded-xl p-6">
      <h2 className="text-2xl font-bold mb-4">Drawdown Analysis</h2>
      <div className="h-[300px]">
        <ReactECharts option={option} style={{ height: '100%', width: '100%' }} opts={{ renderer: 'canvas' }} />
      </div>
    </div>
  )
}
