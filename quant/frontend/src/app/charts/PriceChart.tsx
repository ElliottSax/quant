'use client'

/**
 * Candlestick + volume renderer.
 *
 * It draws exactly the bars and overlay points it is handed. Overlay points may be null
 * where the indicator window is not yet filled; those are rendered as gaps, never joined
 * across or replaced with a substitute value.
 */

import { useMemo } from 'react'
import dynamic from 'next/dynamic'
import type { Bar } from './artefact'

const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

const UP = '#10b981'
const DOWN = '#ef4444'

export interface Overlay {
  name: string
  color: string
  values: (number | null)[]
  dashed?: boolean
}

interface PriceChartProps {
  symbol: string
  bars: Bar[]
  overlays: Overlay[]
  height?: number
}

function formatVolume(v: number): string {
  if (v >= 1e9) return `${(v / 1e9).toFixed(2)}B`
  if (v >= 1e6) return `${(v / 1e6).toFixed(2)}M`
  if (v >= 1e3) return `${(v / 1e3).toFixed(1)}K`
  return v.toFixed(0)
}

export function PriceChart({ symbol, bars, overlays, height = 620 }: PriceChartProps) {
  const option = useMemo(() => {
    const dates = bars.map((b) => b[0])
    // ECharts candlestick order is [open, close, low, high].
    const candles = bars.map((b) => [b[1], b[4], b[3], b[2]])
    const volumes = bars.map((b, i) => ({
      value: b[5],
      itemStyle: { color: b[4] >= b[1] ? `${UP}66` : `${DOWN}66` },
      name: dates[i],
    }))

    const overlaySeries = overlays.map((o) => ({
      name: o.name,
      type: 'line',
      data: o.values,
      xAxisIndex: 0,
      yAxisIndex: 0,
      symbol: 'none',
      smooth: false,
      connectNulls: false,
      lineStyle: { width: 1.2, color: o.color, type: o.dashed ? 'dashed' : 'solid' },
      itemStyle: { color: o.color },
      z: 3,
    }))

    return {
      backgroundColor: 'transparent',
      animation: false,
      legend: {
        show: overlays.length > 0,
        data: overlays.map((o) => o.name),
        textStyle: { color: '#94a3b8', fontSize: 11 },
        top: 4,
        itemWidth: 18,
        itemHeight: 8,
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross', link: [{ xAxisIndex: 'all' }] },
        backgroundColor: 'rgba(15, 23, 42, 0.96)',
        borderColor: '#334155',
        textStyle: { color: '#e2e8f0', fontSize: 12 },
        formatter: (params: any) => {
          const list = Array.isArray(params) ? params : [params]
          const idx = list[0]?.dataIndex
          if (typeof idx !== 'number' || !bars[idx]) return ''
          const [date, open, high, low, close, volume] = bars[idx]
          const prev = idx > 0 ? bars[idx - 1][4] : null
          const chg = prev === null ? null : close - prev
          const chgPct = prev === null || prev === 0 ? null : ((close - prev) / prev) * 100
          const chgColor = chg === null ? '#94a3b8' : chg >= 0 ? UP : DOWN

          const overlayRows = overlays
            .map((o) => {
              const v = o.values[idx]
              if (v === null || v === undefined) return ''
              return `<div style="display:flex;justify-content:space-between;gap:16px"><span style="color:${o.color}">${o.name}</span><span style="font-family:monospace">${v.toFixed(2)}</span></div>`
            })
            .join('')

          return `
            <div style="padding:4px 2px;min-width:190px">
              <div style="font-weight:600;margin-bottom:6px">${symbol} · ${date}</div>
              <div style="display:flex;justify-content:space-between;gap:16px"><span style="color:#94a3b8">Open</span><span style="font-family:monospace">${open.toFixed(2)}</span></div>
              <div style="display:flex;justify-content:space-between;gap:16px"><span style="color:#94a3b8">High</span><span style="font-family:monospace">${high.toFixed(2)}</span></div>
              <div style="display:flex;justify-content:space-between;gap:16px"><span style="color:#94a3b8">Low</span><span style="font-family:monospace">${low.toFixed(2)}</span></div>
              <div style="display:flex;justify-content:space-between;gap:16px"><span style="color:#94a3b8">Close</span><span style="font-family:monospace;font-weight:600">${close.toFixed(2)}</span></div>
              <div style="display:flex;justify-content:space-between;gap:16px"><span style="color:#94a3b8">Volume</span><span style="font-family:monospace">${formatVolume(volume)}</span></div>
              ${
                chg === null
                  ? '<div style="color:#64748b;font-size:11px;margin-top:4px">No prior bar in this dataset</div>'
                  : `<div style="display:flex;justify-content:space-between;gap:16px;margin-top:4px;border-top:1px solid #1e293b;padding-top:4px"><span style="color:#94a3b8">vs prev close</span><span style="font-family:monospace;color:${chgColor}">${chg >= 0 ? '+' : ''}${chg.toFixed(2)}${chgPct === null ? '' : ` (${chgPct >= 0 ? '+' : ''}${chgPct.toFixed(2)}%)`}</span></div>`
              }
              ${overlayRows ? `<div style="margin-top:4px;border-top:1px solid #1e293b;padding-top:4px">${overlayRows}</div>` : ''}
            </div>`
        },
      },
      axisPointer: { link: [{ xAxisIndex: 'all' }], label: { backgroundColor: '#1e293b' } },
      grid: [
        { left: 58, right: 24, top: 34, height: '58%' },
        { left: 58, right: 24, top: '72%', height: '13%' },
      ],
      xAxis: [
        {
          type: 'category',
          data: dates,
          gridIndex: 0,
          boundaryGap: true,
          axisLine: { lineStyle: { color: '#334155' } },
          axisLabel: { color: '#94a3b8', fontSize: 11 },
          splitLine: { show: false },
          axisTick: { show: false },
        },
        {
          type: 'category',
          data: dates,
          gridIndex: 1,
          boundaryGap: true,
          axisLine: { lineStyle: { color: '#334155' } },
          axisLabel: { show: false },
          axisTick: { show: false },
          splitLine: { show: false },
        },
      ],
      yAxis: [
        {
          scale: true,
          gridIndex: 0,
          position: 'left',
          axisLine: { show: false },
          axisLabel: { color: '#94a3b8', fontSize: 11, formatter: (v: number) => v.toFixed(0) },
          splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } },
        },
        {
          scale: true,
          gridIndex: 1,
          axisLine: { show: false },
          axisLabel: { color: '#94a3b8', fontSize: 10, formatter: (v: number) => formatVolume(v) },
          splitLine: { show: false },
          splitNumber: 2,
        },
      ],
      dataZoom: [
        { type: 'inside', xAxisIndex: [0, 1], start: 0, end: 100 },
        {
          type: 'slider',
          xAxisIndex: [0, 1],
          start: 0,
          end: 100,
          bottom: 8,
          height: 22,
          borderColor: '#334155',
          backgroundColor: 'rgba(30, 41, 59, 0.4)',
          fillerColor: 'rgba(234, 179, 8, 0.15)',
          handleStyle: { color: '#eab308' },
          textStyle: { color: '#94a3b8', fontSize: 10 },
        },
      ],
      series: [
        {
          name: `${symbol} OHLC`,
          type: 'candlestick',
          data: candles,
          xAxisIndex: 0,
          yAxisIndex: 0,
          itemStyle: {
            color: UP,
            color0: DOWN,
            borderColor: UP,
            borderColor0: DOWN,
          },
          z: 2,
        },
        {
          name: 'Volume',
          type: 'bar',
          data: volumes,
          xAxisIndex: 1,
          yAxisIndex: 1,
          large: true,
        },
        ...overlaySeries,
      ],
    }
  }, [bars, overlays, symbol])

  // The chart renders to a <canvas>, which exposes nothing to a screen reader. This
  // summary is the only accessible description of what the candlestick/volume chart
  // shows; the exact numbers it reports (last close, range, overlays) are also visible
  // on-screen in the stat tiles and provenance text below the chart on this page.
  const summary = useMemo(() => {
    if (!bars.length) return `${symbol}: no price data in this range.`
    const first = bars[0]
    const last = bars[bars.length - 1]
    const change = last[4] - first[4]
    const changePct = first[4] === 0 ? null : (change / first[4]) * 100
    const activeOverlays = overlays.length
      ? ` Overlays shown: ${overlays.map((o) => o.name).join(', ')}.`
      : ''
    return (
      `Candlestick and volume chart for ${symbol}, ${first[0]} to ${last[0]}, ${bars.length} daily bars. ` +
      `Close moved from ${first[4].toFixed(2)} to ${last[4].toFixed(2)} ` +
      `(${change >= 0 ? '+' : ''}${change.toFixed(2)}${changePct === null ? '' : `, ${changePct >= 0 ? '+' : ''}${changePct.toFixed(2)}%`}) ` +
      `over this window.${activeOverlays}`
    )
  }, [bars, overlays, symbol])

  return (
    <div role="img" aria-label={summary}>
      <ReactECharts
        option={option as any}
        style={{ height, width: '100%' }}
        notMerge
        opts={{ renderer: 'canvas' }}
        aria-hidden="true"
      />
    </div>
  )
}
