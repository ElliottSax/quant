"use client";

import { useEffect, useRef, useMemo, useState, useCallback } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';

interface HeatmapData {
  xLabel: string;
  yLabel: string;
  value: number;
  metadata?: Record<string, any>;
}

interface AdvancedHeatmapProps {
  data: HeatmapData[];
  title?: string;
  height?: number;
  colorRange?: [string, string, string]; // [negative, neutral, positive]
  showValues?: boolean;
  onCellClick?: (data: HeatmapData) => void;
  onCellHover?: (data: HeatmapData | null) => void;
}

export function AdvancedHeatmap({
  data,
  title = 'Correlation Matrix',
  height = 500,
  colorRange = ['#ef4444', '#1e293b', '#22c55e'],
  showValues = true,
  onCellClick,
  onCellHover,
}: AdvancedHeatmapProps) {
  const chartRef = useRef<ReactECharts>(null);
  const [selectedCell, setSelectedCell] = useState<{ x: string; y: string } | null>(null);
  const [sortBy, setSortBy] = useState<'default' | 'value' | 'alphabetical'>('default');

  // Extract unique labels
  const { xLabels, yLabels, matrixData, minValue, maxValue } = useMemo(() => {
    const xSet = new Set<string>();
    const ySet = new Set<string>();
    data.forEach((d) => {
      xSet.add(d.xLabel);
      ySet.add(d.yLabel);
    });

    let xLabels = Array.from(xSet);
    let yLabels = Array.from(ySet);

    // Sort labels based on selection
    if (sortBy === 'alphabetical') {
      xLabels.sort();
      yLabels.sort();
    } else if (sortBy === 'value') {
      // Sort by average correlation
      const avgCorr = (label: string) => {
        const values = data.filter(d => d.xLabel === label || d.yLabel === label);
        return values.reduce((sum, d) => sum + Math.abs(d.value), 0) / values.length;
      };
      xLabels.sort((a, b) => avgCorr(b) - avgCorr(a));
      yLabels.sort((a, b) => avgCorr(b) - avgCorr(a));
    }

    const matrixData: [number, number, number][] = [];
    let minVal = Infinity;
    let maxVal = -Infinity;

    data.forEach((d) => {
      const xIdx = xLabels.indexOf(d.xLabel);
      const yIdx = yLabels.indexOf(d.yLabel);
      if (xIdx !== -1 && yIdx !== -1) {
        matrixData.push([xIdx, yIdx, d.value]);
        minVal = Math.min(minVal, d.value);
        maxVal = Math.max(maxVal, d.value);
      }
    });

    return {
      xLabels,
      yLabels,
      matrixData,
      minValue: minVal,
      maxValue: maxVal,
    };
  }, [data, sortBy]);

  // ECharts configuration - use any to avoid strict type issues with dynamic label colors
  const option = useMemo((): any => ({
    backgroundColor: 'transparent',
    title: {
      show: false,
    },
    tooltip: {
      show: true,
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(51, 65, 85, 0.5)',
      borderWidth: 1,
      padding: [12, 16],
      textStyle: {
        color: '#f1f5f9',
        fontSize: 12,
        fontFamily: 'Inter, sans-serif',
      },
      formatter: (params: any) => {
        const xLabel = xLabels[params.data[0]];
        const yLabel = yLabels[params.data[1]];
        const value = params.data[2];
        const absValue = Math.abs(value);
        const strength = absValue > 0.7 ? 'Strong' : absValue > 0.4 ? 'Moderate' : 'Weak';
        const direction = value > 0 ? 'Positive' : value < 0 ? 'Negative' : 'Neutral';

        return `
          <div style="font-weight: 600; margin-bottom: 8px; font-size: 13px;">
            ${xLabel} ↔ ${yLabel}
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
            <div>
              <div style="color: #94a3b8; font-size: 11px;">Correlation</div>
              <div style="font-weight: 600; color: ${value > 0 ? '#22c55e' : value < 0 ? '#ef4444' : '#94a3b8'};">
                ${value.toFixed(4)}
              </div>
            </div>
            <div>
              <div style="color: #94a3b8; font-size: 11px;">Strength</div>
              <div style="font-weight: 600;">${strength} ${direction}</div>
            </div>
          </div>
        `;
      },
    },
    grid: {
      left: 120,
      right: 80,
      top: 60,
      bottom: 100,
      containLabel: false,
    },
    xAxis: {
      type: 'category',
      data: xLabels,
      position: 'top',
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: '#94a3b8',
        fontSize: 11,
        fontFamily: 'Inter, sans-serif',
        rotate: 45,
        interval: 0,
        formatter: (value: string) => {
          // Show last name only if too long
          if (value.length > 12) {
            return value.split(' ').slice(-1)[0];
          }
          return value;
        },
      },
      splitArea: { show: false },
    },
    yAxis: {
      type: 'category',
      data: yLabels,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: '#94a3b8',
        fontSize: 11,
        fontFamily: 'Inter, sans-serif',
        formatter: (value: string) => {
          if (value.length > 15) {
            return value.split(' ').slice(-1)[0];
          }
          return value;
        },
      },
      splitArea: { show: false },
    },
    visualMap: {
      type: 'continuous',
      min: -1,
      max: 1,
      calculable: true,
      orient: 'vertical',
      right: 10,
      top: 'center',
      itemHeight: 200,
      itemWidth: 12,
      text: ['+1', '-1'],
      textStyle: {
        color: '#94a3b8',
        fontSize: 11,
        fontFamily: 'Inter, sans-serif',
      },
      inRange: {
        color: colorRange,
      },
      handleStyle: {
        color: '#6366f1',
        borderColor: '#6366f1',
      },
      indicatorStyle: {
        color: '#6366f1',
      },
    },
    series: [
      {
        name: 'Correlation',
        type: 'heatmap',
        data: matrixData,
        emphasis: {
          itemStyle: {
            shadowBlur: 20,
            shadowColor: 'rgba(99, 102, 241, 0.5)',
            borderColor: '#6366f1',
            borderWidth: 2,
          },
        },
        itemStyle: {
          borderColor: 'rgba(30, 41, 59, 0.8)',
          borderWidth: 1,
          borderRadius: 2,
        },
        label: {
          show: showValues && xLabels.length <= 15,
          formatter: (params: any) => {
            const value = params.data[2];
            return Math.abs(value) > 0.01 ? value.toFixed(2) : '';
          },
          fontSize: 9,
          fontWeight: 600,
          fontFamily: 'Inter, sans-serif',
          color: (params: any) => {
            const value = params.data?.[2] || 0;
            return Math.abs(value) > 0.5 ? '#fff' : '#94a3b8';
          },
        },
      },
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: 0,
        filterMode: 'none',
        zoomOnMouseWheel: 'ctrl',
        moveOnMouseMove: true,
      },
      {
        type: 'inside',
        yAxisIndex: 0,
        filterMode: 'none',
        zoomOnMouseWheel: 'ctrl',
        moveOnMouseMove: true,
      },
    ],
    animation: true,
    animationDuration: 500,
    animationEasing: 'cubicOut',
  }), [xLabels, yLabels, matrixData, colorRange, showValues]);

  // Event handlers
  const onEvents = useMemo(() => ({
    click: (params: any) => {
      if (params.componentType === 'series') {
        const cellData = {
          xLabel: xLabels[params.data[0]],
          yLabel: yLabels[params.data[1]],
          value: params.data[2],
        };
        setSelectedCell({ x: cellData.xLabel, y: cellData.yLabel });
        onCellClick?.(cellData);
      }
    },
    mouseover: (params: any) => {
      if (params.componentType === 'series') {
        const cellData = {
          xLabel: xLabels[params.data[0]],
          yLabel: yLabels[params.data[1]],
          value: params.data[2],
        };
        onCellHover?.(cellData);
      }
    },
    mouseout: () => {
      onCellHover?.(null);
    },
  }), [xLabels, yLabels, onCellClick, onCellHover]);

  // Calculate statistics
  const stats = useMemo(() => {
    const values = data.map(d => d.value).filter(v => v !== 1); // Exclude self-correlation
    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    const positiveCount = values.filter(v => v > 0.3).length;
    const negativeCount = values.filter(v => v < -0.3).length;
    const strongCorrelations = values.filter(v => Math.abs(v) > 0.7).length;

    return {
      average: avg,
      positive: positiveCount,
      negative: negativeCount,
      strong: strongCorrelations,
      total: values.length,
    };
  }, [data]);

  return (
    <div className="relative bg-slate-900/50 backdrop-blur-xl rounded-2xl border border-slate-700/50 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700/50">
        <div>
          <h3 className="text-lg font-bold text-white">{title}</h3>
          <p className="text-sm text-slate-400">
            {xLabels.length} × {yLabels.length} matrix · {data.length} pairs
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-4">
          {/* Sort selector */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500">Sort:</span>
            <div className="flex gap-1">
              {(['default', 'value', 'alphabetical'] as const).map((sort) => (
                <button
                  key={sort}
                  onClick={() => setSortBy(sort)}
                  className={`px-2 py-1 text-xs rounded capitalize transition-all ${
                    sortBy === sort
                      ? 'bg-indigo-500 text-white'
                      : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700'
                  }`}
                >
                  {sort}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Stats bar */}
      <div className="grid grid-cols-5 gap-4 px-4 py-3 border-b border-slate-700/50 bg-slate-800/30">
        <div className="text-center">
          <p className="text-xs text-slate-500">Avg Correlation</p>
          <p className={`text-sm font-semibold ${stats.average > 0 ? 'text-green-400' : 'text-red-400'}`}>
            {stats.average.toFixed(3)}
          </p>
        </div>
        <div className="text-center">
          <p className="text-xs text-slate-500">Positive ({">"} 0.3)</p>
          <p className="text-sm font-semibold text-green-400">{stats.positive}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-slate-500">Negative ({"<"} -0.3)</p>
          <p className="text-sm font-semibold text-red-400">{stats.negative}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-slate-500">Strong (|r| {">"} 0.7)</p>
          <p className="text-sm font-semibold text-indigo-400">{stats.strong}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-slate-500">Total Pairs</p>
          <p className="text-sm font-semibold text-white">{stats.total}</p>
        </div>
      </div>

      {/* Chart */}
      <div className="p-2">
        <ReactECharts
          ref={chartRef}
          option={option}
          style={{ height: height }}
          opts={{ renderer: 'canvas' }}
          onEvents={onEvents}
          notMerge={true}
        />
      </div>

      {/* Footer */}
      <div className="px-4 py-2 border-t border-slate-700/50 bg-slate-800/30 text-xs text-slate-500 flex items-center justify-between">
        <span>Ctrl + Scroll to zoom · Drag to pan</span>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded bg-red-500" />
            <span>Negative</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded bg-slate-700" />
            <span>Neutral</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded bg-green-500" />
            <span>Positive</span>
          </div>
        </div>
      </div>
    </div>
  );
}
