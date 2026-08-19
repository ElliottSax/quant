/**
 * QuantEngines home.
 *
 * The previous homepage was built on hooks that have no backend behind them
 * (useStockPredictions, useDiscoveries, useCriticalAnomalies all resolve to []).
 * From those empty stubs it drew an ECharts gauge captioned "ML Prediction
 * Sentiment — Bullish 50% / Bearish 50%", where the 50 came from the `total > 0
 * ? ... : 50` fallback rather than from any prediction; a regime pie chart that
 * spun on a loading state forever; and a status line asserting "Discovery:
 * CONNECTED / API: CONNECTED" regardless of whether anything was.
 *
 * A gauge, a chart or a status light derived from nothing must not render. The
 * homepage now links only to sections that have a real source behind them, and
 * carries no live-looking readout it cannot substantiate. It also no longer
 * links to /discoveries, which is an in-development page excluded from the
 * index — navigation and index signals have to agree.
 */

import Link from 'next/link'
import { EmailCaptureHero } from '@/components/EmailCaptureHero'

export default function Home() {
  return (
    <div className="space-y-6">

      {/* Hero Header */}
      <div className="terminal-panel overflow-hidden">
        <div className="terminal-panel-header">
          <span>QUANTENGINES TERMINAL</span>
        </div>

        <div className="p-6 bg-gradient-to-br from-[hsl(220,60%,4%)] via-[hsl(220,55%,6%)] to-[hsl(220,60%,4%)]">
          <h1 className="text-3xl md:text-4xl font-bold mb-3">
            <span className="text-[hsl(45,96%,58%)]">Quant</span>{' '}
            <span className="text-white">Research Terminal</span>
          </h1>
          <p className="text-[hsl(215,20%,60%)] text-sm md:text-base mb-4 max-w-2xl">
            Congressional trade filings, strategy backtesting and technical charts, built on
            data we can point at. Where a tool is still being rebuilt, this site says so
            rather than fill the space with numbers it cannot source.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link
              href="/congress-stock-trades"
              className="px-5 py-3 rounded-lg bg-[hsl(210,100%,56%)] text-white hover:bg-[hsl(210,100%,64%)] transition-colors text-sm font-semibold"
            >
              Congressional trade filings
            </Link>
            <Link
              href="/backtesting"
              className="px-5 py-3 rounded-lg bg-[hsl(215,50%,12%)] text-[hsl(210,20%,80%)] hover:text-white hover:bg-[hsl(215,50%,16%)] transition-colors text-sm font-semibold"
            >
              Backtest a strategy
            </Link>
          </div>
        </div>
      </div>

      {/* Congressional Trading Section */}
      <Link href="/politicians" className="block">
        <div className="terminal-panel border-[hsl(210,100%,56%)]/30 hover:border-[hsl(210,100%,56%)]/50 transition-colors cursor-pointer">
          <div className="terminal-panel-header bg-gradient-to-r from-[hsl(210,100%,20%)] to-transparent">
            <div className="flex items-center gap-2">
              <span className="text-lg">🏛️</span>
              <span className="text-[hsl(210,100%,70%)]">CONGRESSIONAL TRADING</span>
            </div>
            <span className="text-[10px] text-[hsl(142,71%,55%)]">BROWSE →</span>
          </div>
          <div className="p-4 bg-[hsl(220,60%,4%)]">
            <p className="text-sm text-[hsl(215,20%,70%)] mb-3">
              Members of Congress, their filed STOCK Act transactions, and the reporting lag on
              each disclosure. Filings as filed — value ranges are shown as ranges.
            </p>
            <div className="flex flex-wrap gap-4 text-xs text-[hsl(215,20%,55%)]">
              <span>🏛️ Filed disclosures</span>
              <span>📅 Reporting lag</span>
              <span>🔍 Per-member history</span>
            </div>
          </div>
        </div>
      </Link>

      {/* Backtesting Quick Start */}
      <Link href="/backtesting" className="block">
        <div className="terminal-panel border-[hsl(142,71%,55%)]/30 hover:border-[hsl(142,71%,55%)]/50 transition-colors cursor-pointer">
          <div className="terminal-panel-header bg-gradient-to-r from-[hsl(142,71%,20%)] to-transparent">
            <div className="flex items-center gap-2">
              <span className="text-lg">⚡</span>
              <span className="text-[hsl(142,71%,65%)]">STRATEGY BACKTESTING</span>
            </div>
            <span className="text-[10px] text-[hsl(45,96%,58%)]">10 STRATEGIES →</span>
          </div>
          <div className="p-4 bg-[hsl(220,60%,4%)]">
            <p className="text-sm text-[hsl(215,20%,70%)] mb-3">
              Test trading strategies against historical market data. MA Crossover, RSI, MACD,
              Bollinger Bands and more. Build a custom strategy or start from a template.
            </p>
            <div className="flex flex-wrap gap-4 text-xs text-[hsl(215,20%,55%)]">
              <span>📋 Strategy Library</span>
              <span>🔧 Strategy Builder</span>
              <span>💼 Portfolio Optimization</span>
              <span>📊 Results History</span>
            </div>
          </div>
        </div>
      </Link>

      {/* Quick Access */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <ToolCard title="Politicians" description="Congressional traders" href="/politicians" icon="🏛️" color="blue" />
        <ToolCard title="Trade Filings" description="Filed STOCK Act trades" href="/congress-stock-trades" icon="📄" color="blue" />
        <ToolCard title="Charts" description="Technical analysis" href="/charts" icon="📊" color="green" />
        <ToolCard title="Backtesting" description="Test strategies" href="/backtesting" icon="⚡" color="green" />
        <ToolCard title="Strategies" description="Strategy library" href="/strategies" icon="📋" color="yellow" />
        <ToolCard title="Network" description="Correlation analysis" href="/network" icon="🕸️" color="purple" />
      </div>

      {/* Email Capture */}
      <div className="py-4">
        <EmailCaptureHero />
      </div>
    </div>
  )
}

function ToolCard({ title, description, href, icon, color }: {
  title: string; description: string; href: string; icon: string; color: string
}) {
  const colors: Record<string, string> = {
    blue: 'hover:border-blue-500/50 hover:bg-blue-500/5',
    green: 'hover:border-green-500/50 hover:bg-green-500/5',
    yellow: 'hover:border-yellow-500/50 hover:bg-yellow-500/5',
    purple: 'hover:border-purple-500/50 hover:bg-purple-500/5',
  }

  return (
    <Link href={href} className={`terminal-panel p-4 transition-all cursor-pointer ${colors[color]} group`}>
      <div className="flex items-start gap-3">
        <span className="text-2xl">{icon}</span>
        <div>
          <h3 className="font-semibold text-white group-hover:text-[hsl(45,96%,58%)] transition-colors">{title}</h3>
          <p className="text-xs text-[hsl(215,20%,55%)]">{description}</p>
        </div>
      </div>
    </Link>
  )
}
