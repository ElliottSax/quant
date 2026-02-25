"use client";

import { useState, useCallback, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { motion, AnimatePresence } from 'framer-motion';

// Dynamically import react-grid-layout to avoid SSR issues
const GridLayout = dynamic(
  () => import('react-grid-layout').then((mod) => mod.default),
  { ssr: false }
) as any;

// Import layout CSS
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

interface Widget {
  id: string;
  type: 'chart' | 'stat' | 'table' | 'network' | 'heatmap' | 'gauge' | 'custom';
  title: string;
  component: React.ReactNode;
  minW?: number;
  minH?: number;
  maxW?: number;
  maxH?: number;
}

interface LayoutItem {
  i: string;
  x: number;
  y: number;
  w: number;
  h: number;
  minW?: number;
  minH?: number;
  maxW?: number;
  maxH?: number;
}

interface DraggableDashboardProps {
  widgets: Widget[];
  columns?: number;
  rowHeight?: number;
  onLayoutChange?: (layout: LayoutItem[]) => void;
  editable?: boolean;
}

const WIDGET_ICONS: Record<Widget['type'], string> = {
  chart: '📈',
  stat: '📊',
  table: '📋',
  network: '🕸️',
  heatmap: '🔥',
  gauge: '⏱️',
  custom: '🔧',
};

export function DraggableDashboard({
  widgets,
  columns = 12,
  rowHeight = 100,
  onLayoutChange,
  editable = true,
}: DraggableDashboardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [layout, setLayout] = useState<LayoutItem[]>(() =>
    widgets.map((widget, index) => ({
      i: widget.id,
      x: (index % 2) * 6,
      y: Math.floor(index / 2) * 4,
      w: 6,
      h: 4,
      minW: widget.minW || 3,
      minH: widget.minH || 2,
      maxW: widget.maxW || 12,
      maxH: widget.maxH || 8,
    }))
  );
  const [removedWidgets, setRemovedWidgets] = useState<string[]>([]);

  const handleLayoutChange = useCallback(
    (newLayout: readonly LayoutItem[] | LayoutItem[]) => {
      setLayout([...newLayout]);
      onLayoutChange?.([...newLayout]);
    },
    [onLayoutChange]
  );

  const handleRemoveWidget = useCallback((widgetId: string) => {
    setRemovedWidgets((prev) => [...prev, widgetId]);
    setLayout((prev) => prev.filter((item) => item.i !== widgetId));
  }, []);

  const handleRestoreWidget = useCallback((widgetId: string) => {
    setRemovedWidgets((prev) => prev.filter((id) => id !== widgetId));
    const widget = widgets.find((w) => w.id === widgetId);
    if (widget) {
      setLayout((prev) => [
        ...prev,
        {
          i: widget.id,
          x: 0,
          y: Infinity, // Push to bottom
          w: 6,
          h: 4,
          minW: widget.minW || 3,
          minH: widget.minH || 2,
        },
      ]);
    }
  }, [widgets]);

  const handleResetLayout = useCallback(() => {
    setRemovedWidgets([]);
    setLayout(
      widgets.map((widget, index) => ({
        i: widget.id,
        x: (index % 2) * 6,
        y: Math.floor(index / 2) * 4,
        w: 6,
        h: 4,
        minW: widget.minW || 3,
        minH: widget.minH || 2,
        maxW: widget.maxW || 12,
        maxH: widget.maxH || 8,
      }))
    );
  }, [widgets]);

  const visibleWidgets = useMemo(
    () => widgets.filter((w) => !removedWidgets.includes(w.id)),
    [widgets, removedWidgets]
  );

  const hiddenWidgets = useMemo(
    () => widgets.filter((w) => removedWidgets.includes(w.id)),
    [widgets, removedWidgets]
  );

  return (
    <div className="relative">
      {/* Dashboard Controls */}
      {editable && (
        <div className="flex items-center justify-between mb-6 p-4 glass-card">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-semibold text-white">Dashboard</h2>
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Live
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Hidden widgets dropdown */}
            {hiddenWidgets.length > 0 && (
              <div className="relative group">
                <button className="btn-secondary text-sm px-4 py-2">
                  + Add Widget ({hiddenWidgets.length})
                </button>
                <div className="absolute right-0 top-full mt-2 w-64 p-2 glass-card rounded-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                  {hiddenWidgets.map((widget) => (
                    <button
                      key={widget.id}
                      onClick={() => handleRestoreWidget(widget.id)}
                      className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left text-sm text-slate-300 hover:bg-slate-700/50 transition-colors"
                    >
                      <span>{WIDGET_ICONS[widget.type]}</span>
                      <span>{widget.title}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Edit mode toggle */}
            <button
              onClick={() => setIsEditing(!isEditing)}
              className={`px-4 py-2 text-sm rounded-lg transition-all ${
                isEditing
                  ? 'bg-indigo-500 text-white'
                  : 'bg-slate-800/80 text-slate-300 hover:bg-slate-700/80'
              }`}
            >
              {isEditing ? '✓ Done' : '✎ Edit Layout'}
            </button>

            {/* Reset layout */}
            {isEditing && (
              <button
                onClick={handleResetLayout}
                className="btn-ghost text-sm px-4 py-2"
              >
                ↺ Reset
              </button>
            )}
          </div>
        </div>
      )}

      {/* Grid Layout */}
      <div className={`relative ${isEditing ? 'ring-2 ring-indigo-500/20 ring-offset-4 ring-offset-slate-900 rounded-2xl' : ''}`}>
        {isEditing && (
          <div className="absolute inset-0 bg-grid-pattern rounded-2xl pointer-events-none z-0" />
        )}

        <GridLayout
          className="layout"
          layout={layout}
          cols={columns}
          rowHeight={rowHeight}
          width={1200}
          onLayoutChange={handleLayoutChange}
          isDraggable={isEditing}
          isResizable={isEditing}
          draggableHandle=".widget-drag-handle"
          margin={[16, 16]}
          containerPadding={[0, 0]}
          useCSSTransforms={true}
        >
          {visibleWidgets.map((widget) => (
            <div key={widget.id} className="relative group">
              <div className="h-full glass-card overflow-hidden">
                {/* Widget Header - visible in edit mode */}
                <AnimatePresence>
                  {isEditing && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="widget-drag-handle flex items-center justify-between px-4 py-2 bg-slate-800/50 border-b border-slate-700/50 cursor-move"
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{WIDGET_ICONS[widget.type]}</span>
                        <span className="text-sm font-medium text-slate-300">
                          {widget.title}
                        </span>
                      </div>
                      <button
                        onClick={() => handleRemoveWidget(widget.id)}
                        className="p-1 rounded hover:bg-red-500/20 text-slate-400 hover:text-red-400 transition-colors"
                      >
                        ✕
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Widget Content */}
                <div className={`${isEditing ? 'h-[calc(100%-44px)]' : 'h-full'} overflow-auto scrollbar-thin`}>
                  {widget.component}
                </div>

                {/* Resize indicator */}
                {isEditing && (
                  <div className="absolute bottom-1 right-1 w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity">
                    <svg
                      className="w-full h-full text-slate-500"
                      viewBox="0 0 24 24"
                      fill="currentColor"
                    >
                      <path d="M22 22H20V20H22V22ZM22 18H20V16H22V18ZM18 22H16V20H18V22ZM22 14H20V12H22V14ZM18 18H16V16H18V18ZM14 22H12V20H14V22Z" />
                    </svg>
                  </div>
                )}
              </div>
            </div>
          ))}
        </GridLayout>
      </div>

      {/* Empty state */}
      {visibleWidgets.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-xl font-semibold text-white mb-2">No widgets visible</h3>
          <p className="text-slate-400 mb-6">
            All widgets have been removed. Click the button below to restore them.
          </p>
          <button onClick={handleResetLayout} className="btn-primary">
            Restore All Widgets
          </button>
        </div>
      )}

      {/* Edit mode indicator */}
      <AnimatePresence>
        {isEditing && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50"
          >
            <div className="flex items-center gap-3 px-6 py-3 glass-strong rounded-full">
              <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
              <span className="text-sm font-medium text-white">
                Editing Layout
              </span>
              <span className="text-xs text-slate-400">
                Drag to move • Resize from corners
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// Widget wrapper component for consistent styling
export function DashboardWidget({
  title,
  subtitle,
  icon,
  actions,
  children,
  className = '',
}: {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  actions?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`h-full flex flex-col ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700/50">
        <div className="flex items-center gap-3">
          {icon && (
            <div className="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center text-indigo-400">
              {icon}
            </div>
          )}
          <div>
            <h3 className="text-sm font-semibold text-white">{title}</h3>
            {subtitle && (
              <p className="text-xs text-slate-500">{subtitle}</p>
            )}
          </div>
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4">{children}</div>
    </div>
  );
}

// Stat card for dashboard
export function StatCard({
  title,
  value,
  change,
  changeLabel,
  icon,
  trend,
  sparkline,
}: {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon?: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  sparkline?: number[];
}) {
  const trendColor = {
    up: 'text-emerald-400',
    down: 'text-red-400',
    neutral: 'text-slate-400',
  }[trend || 'neutral'];

  const trendBg = {
    up: 'bg-emerald-500/10',
    down: 'bg-red-500/10',
    neutral: 'bg-slate-500/10',
  }[trend || 'neutral'];

  return (
    <div className="relative p-5 h-full">
      {/* Background glow effect */}
      {trend === 'up' && (
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent rounded-2xl" />
      )}
      {trend === 'down' && (
        <div className="absolute inset-0 bg-gradient-to-br from-red-500/5 to-transparent rounded-2xl" />
      )}

      <div className="relative">
        <div className="flex items-start justify-between mb-3">
          <p className="text-sm text-slate-400">{title}</p>
          {icon && (
            <div className="w-8 h-8 rounded-lg bg-slate-800/80 flex items-center justify-center text-slate-400">
              {icon}
            </div>
          )}
        </div>

        <div className="flex items-end justify-between">
          <div>
            <p className="text-2xl font-bold text-white mb-1">
              {typeof value === 'number' ? value.toLocaleString() : value}
            </p>
            {change !== undefined && (
              <div className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${trendBg} ${trendColor}`}>
                {trend === 'up' && '↑'}
                {trend === 'down' && '↓'}
                {change > 0 ? '+' : ''}{change}%
                {changeLabel && <span className="text-slate-500 ml-1">{changeLabel}</span>}
              </div>
            )}
          </div>

          {/* Mini sparkline */}
          {sparkline && sparkline.length > 0 && (
            <div className="w-20 h-10">
              <svg viewBox="0 0 100 40" className="w-full h-full">
                <defs>
                  <linearGradient id={`sparkline-${title}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={trend === 'up' ? '#22c55e' : trend === 'down' ? '#ef4444' : '#6366f1'} stopOpacity="0.3" />
                    <stop offset="100%" stopColor={trend === 'up' ? '#22c55e' : trend === 'down' ? '#ef4444' : '#6366f1'} stopOpacity="0" />
                  </linearGradient>
                </defs>
                <path
                  d={`M0,${40 - (sparkline[0] / Math.max(...sparkline)) * 35} ${sparkline.map((v, i) => `L${(i / (sparkline.length - 1)) * 100},${40 - (v / Math.max(...sparkline)) * 35}`).join(' ')} L100,40 L0,40 Z`}
                  fill={`url(#sparkline-${title})`}
                />
                <path
                  d={`M0,${40 - (sparkline[0] / Math.max(...sparkline)) * 35} ${sparkline.map((v, i) => `L${(i / (sparkline.length - 1)) * 100},${40 - (v / Math.max(...sparkline)) * 35}`).join(' ')}`}
                  fill="none"
                  stroke={trend === 'up' ? '#22c55e' : trend === 'down' ? '#ef4444' : '#6366f1'}
                  strokeWidth="2"
                />
              </svg>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
