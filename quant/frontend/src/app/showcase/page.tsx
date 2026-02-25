"use client";

import { useState, useMemo } from 'react';
import { AdvancedCandlestickChart } from '@/components/charts/AdvancedCandlestickChart';
import { NetworkGraph } from '@/components/charts/NetworkGraph';
import { AdvancedHeatmap } from '@/components/charts/AdvancedHeatmap';
import { AdvancedTimeSeriesChart } from '@/components/charts/AdvancedTimeSeriesChart';
import { GaugeChart } from '@/components/charts/GaugeChart';
import { RadarChart } from '@/components/charts/RadarChart';
import { DraggableDashboard, StatCard } from '@/components/dashboard/DraggableDashboard';

// Generate mock OHLC data
function generateOHLCData(days: number = 90) {
  const data = [];
  let price = 150;

  for (let i = 0; i < days; i++) {
    const date = new Date();
    date.setDate(date.getDate() - (days - i));

    const volatility = 0.02 + Math.random() * 0.03;
    const change = (Math.random() - 0.48) * price * volatility;

    const open = price;
    const close = price + change;
    const high = Math.max(open, close) * (1 + Math.random() * 0.01);
    const low = Math.min(open, close) * (1 - Math.random() * 0.01);
    const volume = Math.floor(1000000 + Math.random() * 5000000);

    data.push({
      timestamp: date.toISOString().split('T')[0],
      open,
      high,
      low,
      close,
      volume,
    });

    price = close;
  }

  return data;
}

// Generate mock network data
function generateNetworkData() {
  const parties = ['Democratic', 'Republican', 'Independent'];
  const names = [
    'Nancy Pelosi', 'Mitch McConnell', 'Chuck Schumer', 'Kevin McCarthy',
    'Alexandria Ocasio-Cortez', 'Ted Cruz', 'Elizabeth Warren', 'Marco Rubio',
    'Bernie Sanders', 'Mitt Romney', 'Josh Hawley', 'Cory Booker',
  ];

  const nodes = names.map((name, i) => ({
    id: `pol-${i}`,
    name,
    party: parties[i % 3] as 'Democratic' | 'Republican' | 'Independent',
    centrality: 0.3 + Math.random() * 0.7,
    tradeCount: Math.floor(50 + Math.random() * 200),
  }));

  const links = [];
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      if (Math.random() > 0.6) {
        links.push({
          source: nodes[i].id,
          target: nodes[j].id,
          correlation: (Math.random() - 0.3) * 1.5,
          significance: Math.random() > 0.3,
        });
      }
    }
  }

  return { nodes, links };
}

// Generate mock heatmap data
function generateHeatmapData() {
  const politicians = [
    'Pelosi', 'McConnell', 'Schumer', 'McCarthy', 'AOC',
    'Cruz', 'Warren', 'Rubio', 'Sanders', 'Romney',
  ];

  const data = [];
  for (let i = 0; i < politicians.length; i++) {
    for (let j = 0; j < politicians.length; j++) {
      data.push({
        xLabel: politicians[i],
        yLabel: politicians[j],
        value: i === j ? 1 : (Math.random() - 0.5) * 1.6,
      });
    }
  }

  return data;
}

// Generate mock time series data
function generateTimeSeriesData(days: number = 60) {
  const data = [];
  let value = 100;

  for (let i = 0; i < days; i++) {
    const date = new Date();
    date.setDate(date.getDate() - (days - i));
    value += (Math.random() - 0.48) * 10;
    data.push({
      timestamp: date.toISOString().split('T')[0],
      value: Math.max(0, value),
    });
  }

  return data;
}

export default function ShowcasePage() {
  const [activeTab, setActiveTab] = useState<'charts' | 'dashboard'>('charts');

  const ohlcData = useMemo(() => generateOHLCData(120), []);
  const networkData = useMemo(() => generateNetworkData(), []);
  const heatmapData = useMemo(() => generateHeatmapData(), []);
  const timeSeriesData = useMemo(() => generateTimeSeriesData(90), []);

  const radarData = [
    { name: 'Volume', value: 85 },
    { name: 'Timing', value: 72 },
    { name: 'Returns', value: 68 },
    { name: 'Risk', value: 45 },
    { name: 'Consistency', value: 90 },
    { name: 'Diversification', value: 55 },
  ];

  // Dashboard widgets
  const dashboardWidgets = [
    {
      id: 'stat-1',
      type: 'stat' as const,
      title: 'Total Trades',
      component: (
        <StatCard
          title="Total Trades"
          value={12847}
          change={12.5}
          trend="up"
          sparkline={[10, 15, 12, 18, 22, 19, 25, 28, 24, 30]}
        />
      ),
    },
    {
      id: 'stat-2',
      type: 'stat' as const,
      title: 'Active Politicians',
      component: (
        <StatCard
          title="Active Politicians"
          value={534}
          change={-2.1}
          trend="down"
          sparkline={[50, 48, 52, 47, 45, 48, 44, 42, 46, 43]}
        />
      ),
    },
    {
      id: 'stat-3',
      type: 'stat' as const,
      title: 'Anomalies Detected',
      component: (
        <StatCard
          title="Anomalies Detected"
          value={23}
          change={45}
          trend="up"
          sparkline={[2, 3, 5, 4, 8, 7, 12, 15, 18, 23]}
        />
      ),
    },
    {
      id: 'gauge-1',
      type: 'gauge' as const,
      title: 'Risk Score',
      minH: 3,
      component: <GaugeChart value={67} title="Risk Score" subtitle="Current Market Exposure" size="md" />,
    },
    {
      id: 'timeseries-1',
      type: 'chart' as const,
      title: 'Trading Activity',
      minW: 6,
      minH: 4,
      component: (
        <AdvancedTimeSeriesChart
          data={timeSeriesData}
          title="Trading Activity Over Time"
          seriesName="Trade Count"
          color="#6366f1"
          height={300}
        />
      ),
    },
    {
      id: 'radar-1',
      type: 'chart' as const,
      title: 'Performance Metrics',
      component: <RadarChart data={radarData} title="Performance Analysis" height={300} />,
    },
  ];

  return (
    <div className="min-h-screen bg-slate-950 bg-grid-pattern">
      {/* Header */}
      <header className="sticky top-0 z-50 glass-strong border-b border-slate-700/50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold gradient-text">Quant Analytics</h1>
              <p className="text-sm text-slate-400">Advanced Visualization Showcase</p>
            </div>

            {/* Tab switcher */}
            <div className="flex items-center gap-2 p-1 bg-slate-800/50 rounded-xl">
              {(['charts', 'dashboard'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-2 text-sm font-medium rounded-lg capitalize transition-all ${
                    activeTab === tab
                      ? 'bg-indigo-500 text-white'
                      : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {activeTab === 'charts' ? (
          <div className="space-y-8">
            {/* Candlestick Chart */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">
                TradingView-Style Candlestick Chart
              </h2>
              <AdvancedCandlestickChart
                data={ohlcData}
                symbol="AAPL"
                height={500}
                showVolume={true}
                showSMA={true}
                showRSI={true}
                showBollingerBands={true}
              />
            </section>

            {/* Network Graph */}
            <section>
              <h2 className="text-xl font-semibold text-white mb-4">
                Interactive Network Graph
              </h2>
              <NetworkGraph
                nodes={networkData.nodes}
                links={networkData.links}
                height={500}
              />
            </section>

            {/* Two Column Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Heatmap */}
              <section>
                <h2 className="text-xl font-semibold text-white mb-4">
                  Correlation Heatmap
                </h2>
                <AdvancedHeatmap
                  data={heatmapData}
                  title="Politician Trading Correlations"
                  height={400}
                />
              </section>

              {/* Time Series */}
              <section>
                <h2 className="text-xl font-semibold text-white mb-4">
                  Time Series Analysis
                </h2>
                <AdvancedTimeSeriesChart
                  data={timeSeriesData}
                  title="Trading Volume Trend"
                  seriesName="Volume"
                  color="#22c55e"
                  height={400}
                  showDataZoom={true}
                />
              </section>
            </div>

            {/* Gauge and Radar */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              <section>
                <h2 className="text-lg font-semibold text-white mb-4">
                  Risk Gauge
                </h2>
                <GaugeChart
                  value={73}
                  title="Anomaly Risk"
                  subtitle="Real-time risk assessment"
                  size="lg"
                />
              </section>

              <section>
                <h2 className="text-lg font-semibold text-white mb-4">
                  Performance Radar
                </h2>
                <RadarChart
                  data={radarData}
                  title="Trading Performance"
                  height={280}
                />
              </section>

              <section>
                <h2 className="text-lg font-semibold text-white mb-4">
                  Comparison Radar
                </h2>
                <RadarChart
                  data={radarData}
                  comparisonData={radarData.map((d) => ({
                    ...d,
                    value: d.value * (0.7 + Math.random() * 0.5),
                  }))}
                  primaryLabel="Current"
                  comparisonLabel="Average"
                  title="vs. Market Average"
                  height={280}
                />
              </section>
            </div>
          </div>
        ) : (
          /* Dashboard View */
          <section>
            <h2 className="text-xl font-semibold text-white mb-6">
              Interactive Dashboard
            </h2>
            <DraggableDashboard
              widgets={dashboardWidgets}
              columns={12}
              rowHeight={80}
              editable={true}
            />
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-8 mt-16">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p className="text-slate-500 text-sm">
            Built with TradingView Lightweight Charts, Apache ECharts, React Force Graph, and React Grid Layout
          </p>
          <div className="flex justify-center gap-4 mt-4 text-xs text-slate-600">
            <a href="https://github.com/tradingview/lightweight-charts" target="_blank" rel="noopener noreferrer" className="hover:text-indigo-400 transition-colors">
              Lightweight Charts
            </a>
            <a href="https://github.com/hustcc/echarts-for-react" target="_blank" rel="noopener noreferrer" className="hover:text-indigo-400 transition-colors">
              ECharts for React
            </a>
            <a href="https://github.com/vasturiano/react-force-graph" target="_blank" rel="noopener noreferrer" className="hover:text-indigo-400 transition-colors">
              React Force Graph
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
