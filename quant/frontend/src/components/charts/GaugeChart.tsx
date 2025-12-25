"use client";

import { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';

interface GaugeChartProps {
  value: number;
  min?: number;
  max?: number;
  title?: string;
  subtitle?: string;
  thresholds?: {
    low: number;
    medium: number;
    high: number;
  };
  colors?: {
    low: string;
    medium: string;
    high: string;
    critical: string;
  };
  size?: 'sm' | 'md' | 'lg';
  showTicks?: boolean;
}

export function GaugeChart({
  value,
  min = 0,
  max = 100,
  title,
  subtitle,
  thresholds = { low: 30, medium: 60, high: 80 },
  colors = {
    low: '#22c55e',
    medium: '#f59e0b',
    high: '#f97316',
    critical: '#ef4444',
  },
  size = 'md',
  showTicks = true,
}: GaugeChartProps) {
  const dimensions = {
    sm: { height: 180, radius: '70%', titleSize: 12, valueSize: 20 },
    md: { height: 250, radius: '75%', titleSize: 14, valueSize: 28 },
    lg: { height: 320, radius: '80%', titleSize: 16, valueSize: 36 },
  }[size];

  // Determine color based on value
  const getColor = (val: number) => {
    const normalizedVal = ((val - min) / (max - min)) * 100;
    if (normalizedVal < thresholds.low) return colors.low;
    if (normalizedVal < thresholds.medium) return colors.medium;
    if (normalizedVal < thresholds.high) return colors.high;
    return colors.critical;
  };

  const currentColor = getColor(value);

  const option: EChartsOption = useMemo(() => ({
    backgroundColor: 'transparent',
    series: [
      {
        type: 'gauge',
        startAngle: 200,
        endAngle: -20,
        min,
        max,
        splitNumber: 5,
        radius: dimensions.radius,
        center: ['50%', '60%'],
        itemStyle: {
          color: currentColor,
          shadowColor: `${currentColor}66`,
          shadowBlur: 20,
          shadowOffsetX: 0,
          shadowOffsetY: 0,
        },
        progress: {
          show: true,
          roundCap: true,
          width: 12,
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 1,
              y2: 0,
              colorStops: [
                { offset: 0, color: `${currentColor}99` },
                { offset: 1, color: currentColor },
              ],
            },
          },
        },
        pointer: {
          show: true,
          length: '60%',
          width: 6,
          itemStyle: {
            color: currentColor,
          },
        },
        axisLine: {
          roundCap: true,
          lineStyle: {
            width: 12,
            color: [[1, 'rgba(51, 65, 85, 0.3)']],
          },
        },
        axisTick: {
          show: showTicks,
          distance: -20,
          length: 6,
          lineStyle: {
            color: 'rgba(148, 163, 184, 0.5)',
            width: 1,
          },
        },
        splitLine: {
          show: showTicks,
          distance: -24,
          length: 10,
          lineStyle: {
            color: 'rgba(148, 163, 184, 0.5)',
            width: 2,
          },
        },
        axisLabel: {
          show: showTicks,
          distance: 30,
          color: '#94a3b8',
          fontSize: 10,
          fontFamily: 'Inter, sans-serif',
        },
        title: {
          show: !!title,
          offsetCenter: [0, '70%'],
          color: '#94a3b8',
          fontSize: dimensions.titleSize,
          fontWeight: 500,
          fontFamily: 'Inter, sans-serif',
        },
        detail: {
          valueAnimation: true,
          offsetCenter: [0, '35%'],
          fontSize: dimensions.valueSize,
          fontWeight: 700,
          fontFamily: 'Inter, sans-serif',
          color: '#fff',
          formatter: (val: number) => val.toFixed(1),
        },
        data: [{ value, name: title || '' }],
      },
      // Background arc for visual effect
      {
        type: 'gauge',
        startAngle: 200,
        endAngle: -20,
        min,
        max,
        radius: dimensions.radius,
        center: ['50%', '60%'],
        itemStyle: {
          color: 'transparent',
        },
        progress: {
          show: false,
        },
        pointer: {
          show: false,
        },
        axisLine: {
          roundCap: true,
          lineStyle: {
            width: 20,
            color: [[1, 'rgba(30, 41, 59, 0.5)']],
          },
        },
        axisTick: {
          show: false,
        },
        splitLine: {
          show: false,
        },
        axisLabel: {
          show: false,
        },
      },
    ],
    animation: true,
    animationDuration: 1000,
    animationEasing: 'elasticOut',
  }), [value, min, max, title, currentColor, dimensions, showTicks]);

  return (
    <div className="relative bg-slate-900/50 backdrop-blur-xl rounded-2xl border border-slate-700/50 overflow-hidden p-4">
      {subtitle && (
        <p className="text-xs text-slate-500 text-center mb-2">{subtitle}</p>
      )}
      <ReactECharts
        option={option}
        style={{ height: dimensions.height }}
        opts={{ renderer: 'canvas' }}
        notMerge={true}
      />
      {/* Status indicator */}
      <div className="flex justify-center mt-2">
        <div
          className="px-3 py-1 rounded-full text-xs font-medium"
          style={{
            backgroundColor: `${currentColor}20`,
            color: currentColor,
          }}
        >
          {value < thresholds.low * (max - min) / 100 + min
            ? 'Low Risk'
            : value < thresholds.medium * (max - min) / 100 + min
            ? 'Moderate'
            : value < thresholds.high * (max - min) / 100 + min
            ? 'Elevated'
            : 'Critical'}
        </div>
      </div>
    </div>
  );
}
