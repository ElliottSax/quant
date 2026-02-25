/**
 * Advanced Chart Components
 *
 * A collection of sophisticated, interactive chart components for
 * financial data visualization and analysis.
 *
 * Features:
 * - TradingView-style candlestick charts with technical indicators
 * - Interactive network graphs for relationship visualization
 * - ECharts-powered heatmaps, time series, and gauges
 * - Real-time data streaming support
 * - Drag-and-drop dashboard layouts
 *
 * GitHub Repos Used:
 * - https://github.com/tradingview/lightweight-charts (TradingView Lightweight Charts)
 * - https://github.com/hustcc/echarts-for-react (Apache ECharts for React)
 * - https://github.com/vasturiano/react-force-graph (Force-directed graphs)
 * - https://github.com/react-grid-layout/react-grid-layout (Draggable dashboard)
 */

// TradingView-style candlestick chart with technical indicators
export { AdvancedCandlestickChart } from './AdvancedCandlestickChart';

// Interactive network graph for politician connections
export { NetworkGraph } from './NetworkGraph';

// ECharts-powered correlation heatmap with zoom/pan
export { AdvancedHeatmap } from './AdvancedHeatmap';

// Advanced time series chart with forecasting
export { AdvancedTimeSeriesChart } from './AdvancedTimeSeriesChart';

// Professional gauge charts for metrics
export { GaugeChart } from './GaugeChart';

// Radar charts for multi-dimensional analysis
export { RadarChart } from './RadarChart';

// Legacy chart exports (for backwards compatibility)
export { PriceChart } from './PriceChart';
export { CorrelationHeatmap } from './CorrelationHeatmap';
export { TimeSeriesChart } from './TimeSeriesChart';
export { AnomalyScoreGauge } from './AnomalyScoreGauge';
export { PatternMatchChart } from './PatternMatchChart';
export { FourierSpectrumChart } from './FourierSpectrumChart';
export { RegimeTransitionChart } from './RegimeTransitionChart';
export { EquityCurveChart } from './EquityCurveChart';
export { EfficientFrontierChart } from './EfficientFrontierChart';
