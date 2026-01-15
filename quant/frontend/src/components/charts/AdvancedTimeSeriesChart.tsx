"use client";

import { useMemo, useRef, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';

interface TimeSeriesData {
  timestamp: string;
  value: number;
  category?: string;
}

interface AdvancedTimeSeriesChartProps {
  data: TimeSeriesData[];
  title?: string;
  height?: number;
  showForecast?: boolean;
  forecastData?: TimeSeriesData[];
  annotations?: Array<{
    timestamp: string;
    label: string;
    color?: string;
  }>;
  showAreaGradient?: boolean;
  showDataZoom?: boolean;
  yAxisLabel?: string;
  seriesName?: string;
  color?: string;
  onBrushSelect?: (range: { start: string; end: string }) => void;
}

export function AdvancedTimeSeriesChart({
  data,
  title = 'Time Series',
  height = 400,
  showForecast = false,
  forecastData = [],
  annotations = [],
  showAreaGradient = true,
  showDataZoom = true,
  yAxisLabel = 'Value',
  seriesName = 'Value',
  color = '#6366f1',
  onBrushSelect,
}: AdvancedTimeSeriesChartProps) {
  const chartRef = useRef<ReactECharts>(null);
  const [brushRange, setBrushRange] = useState<{ start: string; end: string } | null>(null);

  // Process data for ECharts
  const { timestamps, values, forecastTimestamps, forecastValues, minValue, maxValue } = useMemo(() => {
    const timestamps = data.map(d => d.timestamp);
    const values = data.map(d => d.value);
    const forecastTimestamps = forecastData.map(d => d.timestamp);
    const forecastValues = forecastData.map(d => d.value);

    const allValues = [...values, ...forecastValues];
    const minValue = Math.min(...allValues);
    const maxValue = Math.max(...allValues);

    return { timestamps, values, forecastTimestamps, forecastValues, minValue, maxValue };
  }, [data, forecastData]);

  // Generate mark lines for annotations
  const markLines = useMemo(() => {
    return annotations.map(ann => ({
      xAxis: ann.timestamp,
      label: {
        show: true,
        formatter: ann.label,
        position: 'end',
        color: ann.color || '#f59e0b',
        fontSize: 10,
        fontWeight: 600,
      },
      lineStyle: {
        color: ann.color || '#f59e0b',
        type: 'dashed' as const,
        width: 1,
      },
    }));
  }, [annotations]);

  // Use any to avoid strict type issues with markLine position types
  const option = useMemo((): any => ({
    backgroundColor: 'transparent',
    title: {
      show: false,
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(51, 65, 85, 0.5)',
      borderWidth: 1,
      padding: [12, 16],
      textStyle: {
        color: '#f1f5f9',
        fontSize: 12,
        fontFamily: 'Inter, sans-serif',
      },
      axisPointer: {
        type: 'cross',
        crossStyle: {
          color: 'rgba(99, 102, 241, 0.5)',
        },
        lineStyle: {
          color: 'rgba(99, 102, 241, 0.5)',
          type: 'dashed',
        },
      },
      formatter: (params: any) => {
        const point = Array.isArray(params) ? params[0] : params;
        const date = new Date(point.axisValue).toLocaleDateString('en-US', {
          weekday: 'short',
          year: 'numeric',
          month: 'short',
          day: 'numeric',
        });
        const value = point.data;
        const isForecast = point.seriesName?.includes('Forecast');

        return `
          <div style="font-weight: 600; margin-bottom: 8px;">${date}</div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 8px; height: 8px; border-radius: 50%; background: ${isForecast ? '#f59e0b' : color};"></div>
            <span style="color: #94a3b8;">${isForecast ? 'Forecast' : seriesName}:</span>
            <span style="font-weight: 600;">${typeof value === 'number' ? value.toLocaleString() : value}</span>
          </div>
        `;
      },
    },
    legend: {
      show: showForecast && forecastData.length > 0,
      top: 10,
      right: 20,
      textStyle: {
        color: '#94a3b8',
        fontSize: 11,
        fontFamily: 'Inter, sans-serif',
      },
      itemWidth: 16,
      itemHeight: 8,
      itemGap: 20,
    },
    grid: {
      left: 60,
      right: 40,
      top: showForecast ? 50 : 30,
      bottom: showDataZoom ? 80 : 40,
      containLabel: false,
    },
    xAxis: {
      type: 'category',
      data: [...timestamps, ...forecastTimestamps],
      axisLine: {
        lineStyle: {
          color: 'rgba(51, 65, 85, 0.5)',
        },
      },
      axisTick: {
        lineStyle: {
          color: 'rgba(51, 65, 85, 0.5)',
        },
      },
      axisLabel: {
        color: '#94a3b8',
        fontSize: 10,
        fontFamily: 'Inter, sans-serif',
        formatter: (value: string) => {
          const date = new Date(value);
          return `${date.getMonth() + 1}/${date.getDate()}`;
        },
      },
      splitLine: {
        show: false,
      },
    },
    yAxis: {
      type: 'value',
      name: yAxisLabel,
      nameTextStyle: {
        color: '#94a3b8',
        fontSize: 11,
        fontFamily: 'Inter, sans-serif',
        padding: [0, 0, 10, 0],
      },
      axisLine: {
        show: false,
      },
      axisTick: {
        show: false,
      },
      axisLabel: {
        color: '#94a3b8',
        fontSize: 10,
        fontFamily: 'Inter, sans-serif',
        formatter: (value: number) => {
          if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
          if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
          return value.toFixed(0);
        },
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(51, 65, 85, 0.3)',
          type: 'dashed',
        },
      },
      min: (value: { min: number }) => Math.floor(value.min * 0.95),
      max: (value: { max: number }) => Math.ceil(value.max * 1.05),
    },
    dataZoom: showDataZoom ? [
      {
        type: 'slider',
        show: true,
        xAxisIndex: 0,
        bottom: 20,
        height: 30,
        borderColor: 'rgba(51, 65, 85, 0.5)',
        backgroundColor: 'rgba(15, 23, 42, 0.5)',
        fillerColor: 'rgba(99, 102, 241, 0.2)',
        handleStyle: {
          color: '#6366f1',
          borderColor: '#6366f1',
        },
        textStyle: {
          color: '#94a3b8',
          fontSize: 10,
        },
        brushSelect: true,
      },
      {
        type: 'inside',
        xAxisIndex: 0,
        zoomOnMouseWheel: true,
        moveOnMouseMove: true,
      },
    ] : [],
    series: [
      {
        name: seriesName,
        type: 'line',
        data: values,
        smooth: true,
        symbol: 'none',
        lineStyle: {
          color: color,
          width: 2,
        },
        areaStyle: showAreaGradient ? {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: `${color}40` },
              { offset: 1, color: `${color}05` },
            ],
          },
        } : undefined,
        emphasis: {
          focus: 'series',
          lineStyle: {
            width: 3,
          },
        },
        markLine: markLines.length > 0 ? {
          silent: true,
          symbol: 'none',
          data: markLines,
        } : undefined,
      },
      ...(showForecast && forecastData.length > 0 ? [{
        name: 'Forecast',
        type: 'line' as const,
        data: [...new Array(timestamps.length).fill(null), ...forecastValues],
        smooth: true,
        symbol: 'none',
        lineStyle: {
          color: '#f59e0b',
          width: 2,
          type: 'dashed' as const,
        },
        areaStyle: showAreaGradient ? {
          color: {
            type: 'linear' as const,
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(245, 158, 11, 0.2)' },
              { offset: 1, color: 'rgba(245, 158, 11, 0.02)' },
            ],
          },
        } : undefined,
      }] : []),
    ],
    animation: true,
    animationDuration: 800,
    animationEasing: 'cubicOut',
  }), [timestamps, values, forecastTimestamps, forecastValues, forecastData.length, markLines, color, seriesName, yAxisLabel, showAreaGradient, showDataZoom, showForecast]);

  // Event handlers
  const onEvents = useMemo(() => ({
    datazoom: (params: any) => {
      if (params.batch) {
        const start = timestamps[Math.floor(params.batch[0].startValue)] || timestamps[0];
        const end = timestamps[Math.floor(params.batch[0].endValue)] || timestamps[timestamps.length - 1];
        setBrushRange({ start, end });
        onBrushSelect?.({ start, end });
      }
    },
  }), [timestamps, onBrushSelect]);

  // Calculate statistics
  const stats = useMemo(() => {
    if (values.length === 0) return null;

    const current = values[values.length - 1];
    const previous = values[0];
    const change = current - previous;
    const changePercent = (change / previous) * 100;
    const max = Math.max(...values);
    const min = Math.min(...values);
    const avg = values.reduce((a, b) => a + b, 0) / values.length;

    return {
      current,
      change,
      changePercent,
      max,
      min,
      avg,
    };
  }, [values]);

  return (
    <div className="relative bg-slate-900/50 backdrop-blur-xl rounded-2xl border border-slate-700/50 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700/50">
        <div>
          <h3 className="text-lg font-bold text-white">{title}</h3>
          {stats && (
            <div className="flex items-center gap-3 mt-1">
              <span className="text-2xl font-semibold text-white">
                {stats.current.toLocaleString()}
              </span>
              <span className={`text-sm font-medium px-2 py-0.5 rounded ${
                stats.change >= 0
                  ? 'text-green-400 bg-green-500/10'
                  : 'text-red-400 bg-red-500/10'
              }`}>
                {stats.change >= 0 ? '+' : ''}{stats.change.toLocaleString()}
                ({stats.changePercent >= 0 ? '+' : ''}{stats.changePercent.toFixed(2)}%)
              </span>
            </div>
          )}
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <div className="w-4 h-0.5 rounded" style={{ backgroundColor: color }} />
            <span className="text-slate-400">{seriesName}</span>
          </div>
          {showForecast && forecastData.length > 0 && (
            <div className="flex items-center gap-1.5">
              <div className="w-4 h-0.5 rounded border-dashed border-t-2 border-amber-500" />
              <span className="text-slate-400">Forecast</span>
            </div>
          )}
        </div>
      </div>

      {/* Stats bar */}
      {stats && (
        <div className="grid grid-cols-4 gap-4 px-4 py-3 border-b border-slate-700/50 bg-slate-800/30">
          <div className="text-center">
            <p className="text-xs text-slate-500">High</p>
            <p className="text-sm font-semibold text-green-400">{stats.max.toLocaleString()}</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-slate-500">Low</p>
            <p className="text-sm font-semibold text-red-400">{stats.min.toLocaleString()}</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-slate-500">Average</p>
            <p className="text-sm font-semibold text-white">{stats.avg.toLocaleString()}</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-slate-500">Data Points</p>
            <p className="text-sm font-semibold text-indigo-400">{values.length}</p>
          </div>
        </div>
      )}

      {/* Chart */}
      <div className="p-2">
        <ReactECharts
          ref={chartRef}
          option={option}
          style={{ height }}
          opts={{ renderer: 'canvas' }}
          onEvents={onEvents}
          notMerge={true}
        />
      </div>

      {/* Footer */}
      <div className="px-4 py-2 border-t border-slate-700/50 bg-slate-800/30 text-xs text-slate-500">
        {brushRange ? (
          <span>Selected range: {new Date(brushRange.start).toLocaleDateString()} - {new Date(brushRange.end).toLocaleDateString()}</span>
        ) : (
          <span>Scroll to zoom · Drag slider to select range · Hover for details</span>
        )}
      </div>
    </div>
  );
}
