"use client";

import { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';

interface RadarDataPoint {
  name: string;
  value: number;
  max?: number;
}

interface RadarChartProps {
  data: RadarDataPoint[];
  title?: string;
  comparisonData?: RadarDataPoint[];
  comparisonLabel?: string;
  primaryLabel?: string;
  height?: number;
  colors?: [string, string];
}

export function RadarChart({
  data,
  title,
  comparisonData,
  comparisonLabel = 'Comparison',
  primaryLabel = 'Current',
  height = 350,
  colors = ['#6366f1', '#22c55e'],
}: RadarChartProps) {
  const option: EChartsOption = useMemo(() => ({
    backgroundColor: 'transparent',
    tooltip: {
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
    },
    legend: {
      show: !!comparisonData,
      bottom: 10,
      textStyle: {
        color: '#94a3b8',
        fontSize: 11,
        fontFamily: 'Inter, sans-serif',
      },
      itemWidth: 16,
      itemHeight: 8,
    },
    radar: {
      indicator: data.map((d) => ({
        name: d.name,
        max: d.max || 100,
      })),
      center: ['50%', '50%'],
      radius: '65%',
      axisName: {
        color: '#94a3b8',
        fontSize: 11,
        fontFamily: 'Inter, sans-serif',
      },
      splitNumber: 4,
      splitArea: {
        areaStyle: {
          color: [
            'rgba(30, 41, 59, 0.1)',
            'rgba(30, 41, 59, 0.2)',
            'rgba(30, 41, 59, 0.3)',
            'rgba(30, 41, 59, 0.4)',
          ],
        },
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(51, 65, 85, 0.5)',
        },
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(51, 65, 85, 0.5)',
        },
      },
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: data.map((d) => d.value),
            name: primaryLabel,
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: {
              color: colors[0],
              width: 2,
            },
            itemStyle: {
              color: colors[0],
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: `${colors[0]}40` },
                  { offset: 1, color: `${colors[0]}10` },
                ],
              },
            },
          },
          ...(comparisonData
            ? [
                {
                  value: comparisonData.map((d) => d.value),
                  name: comparisonLabel,
                  symbol: 'circle',
                  symbolSize: 6,
                  lineStyle: {
                    color: colors[1],
                    width: 2,
                  },
                  itemStyle: {
                    color: colors[1],
                  },
                  areaStyle: {
                    color: {
                      type: 'linear' as const,
                      x: 0,
                      y: 0,
                      x2: 0,
                      y2: 1,
                      colorStops: [
                        { offset: 0, color: `${colors[1]}40` },
                        { offset: 1, color: `${colors[1]}10` },
                      ],
                    },
                  },
                },
              ]
            : []),
        ],
      },
    ],
    animation: true,
    animationDuration: 800,
    animationEasing: 'cubicOut',
  }), [data, comparisonData, primaryLabel, comparisonLabel, colors]);

  // Calculate summary stats
  const stats = useMemo(() => {
    const values = data.map((d) => d.value);
    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    const max = Math.max(...values);
    const min = Math.min(...values);
    const maxDim = data.find((d) => d.value === max)?.name || '';
    const minDim = data.find((d) => d.value === min)?.name || '';

    return { avg, max, min, maxDim, minDim };
  }, [data]);

  return (
    <div className="relative bg-slate-900/50 backdrop-blur-xl rounded-2xl border border-slate-700/50 overflow-hidden">
      {/* Header */}
      {title && (
        <div className="p-4 border-b border-slate-700/50">
          <h3 className="text-lg font-bold text-white">{title}</h3>
        </div>
      )}

      {/* Chart */}
      <div className="p-2">
        <ReactECharts
          option={option}
          style={{ height }}
          opts={{ renderer: 'canvas' }}
          notMerge={true}
        />
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4 px-4 py-3 border-t border-slate-700/50 bg-slate-800/30">
        <div className="text-center">
          <p className="text-xs text-slate-500 mb-0.5">Average</p>
          <p className="text-sm font-semibold text-white">{stats.avg.toFixed(1)}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-slate-500 mb-0.5">Strongest</p>
          <p className="text-sm font-semibold text-green-400">{stats.maxDim}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-slate-500 mb-0.5">Weakest</p>
          <p className="text-sm font-semibold text-red-400">{stats.minDim}</p>
        </div>
      </div>
    </div>
  );
}
