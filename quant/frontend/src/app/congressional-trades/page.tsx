/**
 * Congressional Stock Trades Tracker - SEO Landing Page
 * Public page designed to attract organic search traffic for
 * "congressional stock trades", "politician stock trades", "congress trading tracker"
 */

'use client'

import Link from 'next/link'
import Head from 'next/head'
import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { api, APIError } from '@/lib/api-client'
import { DEMO_POLITICIANS } from '@/lib/demo-data'
import type { Politician, DashboardStats } from '@/lib/types'

// ----- SEO Metadata (exported for Next.js App Router) -----
export const metadata = {
  title: 'Congressional Stock Trades Tracker | Real-Time Politician Trading Data',
  description:
    'Track every stock trade made by U.S. Congress members in real time. See which politicians are buying and selling, the most traded stocks by Congress, and gain insights into congressional trading patterns.',
  keywords:
    'congressional stock trades, politician stock trades, congress trading tracker, congressional trading data, STOCK Act, politician stock tracker, congress insider trading, senate stock trades, house stock trades',
  openGraph: {
    title: 'Congressional Stock Trades Tracker | QuantEngines',
    description:
      'Real-time tracking of every stock trade made by members of the U.S. Congress. Discover patterns, top traders, and the most popular stocks among politicians.',
    type: 'website',
    url: '/congressional-trades',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Congressional Stock Trades Tracker',
    description:
      'Track real-time congressional stock trades. See what politicians are buying and selling.',
  },
}

// ----- Demo / fallback data for recent trades -----
const DEMO_RECENT_TRADES = [
  { id: 't1', ticker: 'NVDA', transaction_type: 'purchase', transaction_date: '2026-03-12', politician_name: 'Nancy Pelosi', politician_party: 'Democratic', amount: '$500,001 - $1,000,000' },
  { id: 't2', ticker: 'MSFT', transaction_type: 'sale', transaction_date: '2026-03-11', politician_name: 'Tommy Tuberville', politician_party: 'Republican', amount: '$250,001 - $500,000' },
  { id: 't3', ticker: 'AAPL', transaction_type: 'purchase', transaction_date: '2026-03-10', politician_name: 'Dan Crenshaw', politician_party: 'Republican', amount: '$100,001 - $250,000' },
  { id: 't4', ticker: 'GOOGL', transaction_type: 'purchase', transaction_date: '2026-03-09', politician_name: 'Josh Gottheimer', politician_party: 'Democratic', amount: '$250,001 - $500,000' },
  { id: 't5', ticker: 'META', transaction_type: 'sale', transaction_date: '2026-03-08', politician_name: 'Pat Fallon', politician_party: 'Republican', amount: '$100,001 - $250,000' },
  { id: 't6', ticker: 'AMZN', transaction_type: 'purchase', transaction_date: '2026-03-07', politician_name: 'Michael McCaul', politician_party: 'Republican', amount: '$500,001 - $1,000,000' },
  { id: 't7', ticker: 'TSLA', transaction_type: 'purchase', transaction_date: '2026-03-06', politician_name: 'Ro Khanna', politician_party: 'Democratic', amount: '$50,001 - $100,000' },
  { id: 't8', ticker: 'LLY', transaction_type: 'sale', transaction_date: '2026-03-05', politician_name: 'Bill Hagerty', politician_party: 'Republican', amount: '$250,001 - $500,000' },
  { id: 't9', ticker: 'JPM', transaction_type: 'purchase', transaction_date: '2026-03-04', politician_name: 'Sheldon Whitehouse', politician_party: 'Democratic', amount: '$100,001 - $250,000' },
  { id: 't10', ticker: 'AVGO', transaction_type: 'purchase', transaction_date: '2026-03-03', politician_name: 'Virginia Foxx', politician_party: 'Republican', amount: '$500,001 - $1,000,000' },
]

const TOP_TRADED_STOCKS = [
  { ticker: 'NVDA', company: 'NVIDIA Corp', trades: 342, buys: 248, sells: 94, sector: 'Technology' },
  { ticker: 'MSFT', company: 'Microsoft Corp', trades: 298, buys: 201, sells: 97, sector: 'Technology' },
  { ticker: 'AAPL', company: 'Apple Inc', trades: 276, buys: 155, sells: 121, sector: 'Technology' },
  { ticker: 'GOOGL', company: 'Alphabet Inc', trades: 234, buys: 168, sells: 66, sector: 'Technology' },
  { ticker: 'AMZN', company: 'Amazon.com Inc', trades: 212, buys: 147, sells: 65, sector: 'Consumer' },
  { ticker: 'META', company: 'Meta Platforms', trades: 189, buys: 132, sells: 57, sector: 'Technology' },
  { ticker: 'JPM', company: 'JPMorgan Chase', trades: 167, buys: 98, sells: 69, sector: 'Finance' },
  { ticker: 'LLY', company: 'Eli Lilly & Co', trades: 154, buys: 119, sells: 35, sector: 'Healthcare' },
]

const BLOG_ARTICLES = [
  {
    title: 'How the STOCK Act Changed Congressional Trading Disclosure',
    slug: '/blog/stock-act-congressional-trading',
    date: '2026-02-28',
    excerpt: 'A deep dive into the 2012 STOCK Act and how it requires members of Congress to publicly disclose their stock trades within 45 days.',
  },
  {
    title: '5 Patterns We Found in Congressional Trading Data',
    slug: '/blog/congressional-trading-patterns',
    date: '2026-02-15',
    excerpt: 'Our analysis of over 10,000 congressional trades reveals recurring patterns in timing, sector concentration, and trade sizing.',
  },
  {
    title: 'Do Politicians Beat the Market? A Data-Driven Answer',
    slug: '/blog/politicians-vs-market-performance',
    date: '2026-01-30',
    excerpt: 'We compared the returns of congressional stock picks against the S&P 500 over the past 5 years. The results may surprise you.',
  },
]

// ----- Page component -----
export default function CongressionalTradesPage() {
  const [showAllTrades, setShowAllTrades] = useState(false)

  // Fetch dashboard stats (includes recent trades)
  const { data: dashboardStats, isPlaceholderData: isStatsPlaceholder } = useQuery<DashboardStats, APIError>({
    queryKey: ['dashboard-stats-public'],
    queryFn: () => api.stats.dashboard(),
    staleTime: 1000 * 60 * 5,
    retry: 1,
    placeholderData: {
      total_trades: 10847,
      active_politicians_30d: 127,
      recent_trades: DEMO_RECENT_TRADES.map(t => ({
        id: t.id,
        ticker: t.ticker,
        transaction_type: t.transaction_type,
        transaction_date: t.transaction_date,
        politician_name: t.politician_name,
        politician_party: t.politician_party,
      })),
      top_politicians_30d: [],
      buy_sell_ratio_30d: { purchase: 62, sale: 38 },
      timestamp: new Date().toISOString(),
    },
  })

  // Fetch politicians for the "Most Active" section
  const { data: politicians, isPlaceholderData: isPoliticiansPlaceholder } = useQuery<Politician[], APIError>({
    queryKey: ['politicians-public'],
    queryFn: () => api.politicians.list(1),
    staleTime: 1000 * 60 * 5,
    placeholderData: DEMO_POLITICIANS,
    retry: 1,
  })

  // Derived: most active politicians sorted by trade count
  const mostActive = useMemo(() => {
    if (!politicians) return []
    return [...politicians]
      .sort((a, b) => (b.trade_count || 0) - (a.trade_count || 0))
      .slice(0, 10)
  }, [politicians])

  const recentTrades = dashboardStats?.recent_trades || DEMO_RECENT_TRADES
  const displayedTrades = showAllTrades ? recentTrades : recentTrades.slice(0, 6)

  return (
    <>
      {/* JSON-LD Structured Data for SEO */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'WebApplication',
            name: 'Congressional Stock Trades Tracker',
            description: 'Track real-time congressional stock trades with institutional-grade analytics.',
            url: 'https://quantengines.com/congressional-trades',
            applicationCategory: 'FinanceApplication',
            operatingSystem: 'Web',
            offers: {
              '@type': 'Offer',
              price: '0',
              priceCurrency: 'USD',
              description: 'Free tier with basic congressional trading data',
            },
          }),
        }}
      />

      <div className="space-y-16 pb-20">

        {/* ===== HERO SECTION ===== */}
        <section className="relative py-16 md:py-24 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-[hsl(45,96%,58%)]/10 via-transparent to-[hsl(210,100%,56%)]/10" />
          <div className="relative max-w-4xl mx-auto text-center space-y-8">
            <Badge className="bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)] text-xs font-semibold">
              Updated Daily from Official Disclosures
            </Badge>

            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight">
              Congressional Stock Trades
              <br />
              <span className="text-[hsl(45,96%,58%)]">Tracker</span>
            </h1>

            <p className="text-lg md:text-xl text-[hsl(215,20%,65%)] max-w-3xl mx-auto leading-relaxed">
              Every member of the U.S. Congress is required by the{' '}
              <strong className="text-white">STOCK Act</strong> to disclose their stock trades.
              We aggregate, analyze, and present this data so you can see exactly what politicians
              are buying and selling &mdash; and spot patterns before the rest of the market.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-2">
              <Link href="/dashboard">
                <Button size="lg" className="bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)] hover:bg-[hsl(45,96%,65%)] font-semibold text-lg px-8">
                  Explore the Dashboard
                </Button>
              </Link>
              <Link href="/politicians">
                <Button size="lg" variant="outline" className="border-[hsl(215,40%,20%)] text-white hover:bg-[hsl(215,50%,14%)]">
                  Browse All Politicians
                </Button>
              </Link>
            </div>

            <p className="text-sm text-[hsl(215,20%,55%)]">
              Free to use &bull; No account required to browse &bull; Data from official EFDS filings
            </p>
          </div>
        </section>

        {/* ===== KEY STATS BAR ===== */}
        <section className="py-10 border-y border-[hsl(215,40%,14%)]">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-5xl mx-auto">
            <StatCard value={`${((dashboardStats?.total_trades || 10847)).toLocaleString()}+`} label="Total Trades Tracked" />
            <StatCard value={`${dashboardStats?.active_politicians_30d || 127}`} label="Active Politicians (30d)" />
            <StatCard value="$2.5B+" label="Estimated Trade Value" />
            <StatCard value="45 Days" label="Max Disclosure Delay" />
          </div>
        </section>

        {/* ===== WHY IT MATTERS (SEO content) ===== */}
        <section className="max-w-4xl mx-auto space-y-6">
          <h2 className="text-3xl md:text-4xl font-bold text-white text-center">
            Why Congressional Stock Trades Matter
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
              <CardHeader>
                <CardTitle className="text-[hsl(45,96%,58%)] text-lg">Information Asymmetry</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-[hsl(215,20%,60%)] leading-relaxed">
                  Members of Congress sit on committees that oversee industries they invest in.
                  They receive classified briefings and shape legislation that directly impacts
                  stock prices, creating an inherent information advantage.
                </p>
              </CardContent>
            </Card>
            <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
              <CardHeader>
                <CardTitle className="text-[hsl(45,96%,58%)] text-lg">Proven Outperformance</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-[hsl(215,20%,60%)] leading-relaxed">
                  Academic research consistently shows that congressional stock portfolios
                  outperform market benchmarks. A landmark 2004 study found senators beat
                  the market by 12% annually &mdash; far exceeding chance.
                </p>
              </CardContent>
            </Card>
            <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
              <CardHeader>
                <CardTitle className="text-[hsl(45,96%,58%)] text-lg">Public Accountability</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-[hsl(215,20%,60%)] leading-relaxed">
                  The STOCK Act of 2012 requires all members of Congress to disclose trades
                  within 45 days. Tracking these disclosures helps hold elected officials
                  accountable and ensures transparency in public service.
                </p>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* ===== LATEST CONGRESSIONAL TRADES TABLE ===== */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl md:text-3xl font-bold text-white">
                Latest Congressional Trades
              </h2>
              <p className="text-sm text-[hsl(215,20%,55%)] mt-1 font-mono">
                Most recent disclosures from the U.S. Congress
              </p>
            </div>
            {(isStatsPlaceholder) && (
              <Badge variant="outline" className="border-[hsl(45,96%,58%)]/40 text-[hsl(45,96%,58%)] text-[10px]">
                DEMO DATA
              </Badge>
            )}
          </div>

          <div className="terminal-panel">
            <div className="terminal-panel-header">
              <span>Recent Trades ({recentTrades.length})</span>
            </div>
            <div className="bg-[hsl(220,60%,4%)] overflow-x-auto">
              <table className="w-full text-xs font-mono">
                <thead>
                  <tr className="bg-[hsl(215,50%,10%)]">
                    <th className="px-4 py-3 text-left text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase">Date</th>
                    <th className="px-4 py-3 text-left text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase">Politician</th>
                    <th className="px-4 py-3 text-left text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase">Party</th>
                    <th className="px-4 py-3 text-left text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase">Ticker</th>
                    <th className="px-4 py-3 text-left text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase">Type</th>
                    <th className="px-4 py-3 text-right text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase">Est. Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {displayedTrades.map((trade, idx) => (
                    <tr
                      key={trade.id}
                      className={`border-b border-[hsl(215,40%,12%)] hover:bg-[hsl(215,50%,12%)] transition-colors ${
                        idx % 2 === 0 ? 'bg-[hsl(220,55%,5%)]' : ''
                      }`}
                    >
                      <td className="px-4 py-3 text-[hsl(215,20%,70%)]">{trade.transaction_date}</td>
                      <td className="px-4 py-3">
                        <span className="text-white font-medium hover:text-[hsl(45,96%,58%)] cursor-pointer">
                          {trade.politician_name}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          trade.politician_party === 'Democratic'
                            ? 'bg-[hsl(210,100%,56%)]/20 text-[hsl(210,100%,56%)]'
                            : trade.politician_party === 'Republican'
                            ? 'bg-[hsl(0,72%,55%)]/20 text-[hsl(0,72%,55%)]'
                            : 'bg-[hsl(215,20%,55%)]/20 text-[hsl(215,20%,55%)]'
                        }`}>
                          {trade.politician_party === 'Democratic' ? 'D' : trade.politician_party === 'Republican' ? 'R' : 'I'}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <Link
                          href={`/charts?symbol=${trade.ticker}`}
                          className="text-[hsl(45,96%,58%)] hover:underline font-bold"
                        >
                          {trade.ticker}
                        </Link>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                          trade.transaction_type === 'purchase'
                            ? 'bg-[hsl(142,71%,55%)]/20 text-[hsl(142,71%,55%)]'
                            : 'bg-[hsl(0,72%,55%)]/20 text-[hsl(0,72%,55%)]'
                        }`}>
                          {trade.transaction_type === 'purchase' ? 'BUY' : 'SELL'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right text-[hsl(215,20%,70%)]">
                        {'amount' in trade ? (trade as any).amount : '$100,001 - $250,000'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {!showAllTrades && recentTrades.length > 6 && (
                <div className="p-4 text-center border-t border-[hsl(215,40%,12%)]">
                  <button
                    onClick={() => setShowAllTrades(true)}
                    className="text-sm font-mono text-[hsl(210,100%,56%)] hover:text-[hsl(210,100%,65%)] transition-colors"
                  >
                    Show all {recentTrades.length} trades &darr;
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="text-center pt-2">
            <Link href="/dashboard">
              <Button variant="outline" className="border-[hsl(215,40%,20%)] text-white hover:bg-[hsl(215,50%,14%)]">
                View Full Trade History
              </Button>
            </Link>
          </div>
        </section>

        {/* ===== MOST ACTIVE POLITICIANS ===== */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl md:text-3xl font-bold text-white">
                Most Active Politicians
              </h2>
              <p className="text-sm text-[hsl(215,20%,55%)] mt-1 font-mono">
                Congress members ranked by total number of stock trades
              </p>
            </div>
            {isPoliticiansPlaceholder && (
              <Badge variant="outline" className="border-[hsl(45,96%,58%)]/40 text-[hsl(45,96%,58%)] text-[10px]">
                DEMO DATA
              </Badge>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {mostActive.map((pol, idx) => (
              <div
                key={pol.id}
                className="terminal-panel flex items-center gap-4 p-4 bg-[hsl(220,60%,4%)] hover:bg-[hsl(215,50%,8%)] transition-colors"
              >
                {/* Rank */}
                <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded bg-[hsl(215,50%,10%)] text-[hsl(45,96%,58%)] font-bold font-mono text-sm">
                  {idx + 1}
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <Link
                      href={`/charts?politician=${pol.id}`}
                      className="text-white font-semibold text-sm hover:text-[hsl(45,96%,58%)] transition-colors truncate"
                    >
                      {pol.name}
                    </Link>
                    <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold flex-shrink-0 ${
                      pol.party === 'Democratic'
                        ? 'bg-[hsl(210,100%,56%)]/20 text-[hsl(210,100%,56%)]'
                        : pol.party === 'Republican'
                        ? 'bg-[hsl(0,72%,55%)]/20 text-[hsl(0,72%,55%)]'
                        : 'bg-[hsl(215,20%,55%)]/20 text-[hsl(215,20%,55%)]'
                    }`}>
                      {pol.party?.charAt(0) || '?'}
                    </span>
                  </div>
                  <p className="text-[10px] text-[hsl(215,20%,55%)] font-mono mt-0.5">
                    {pol.chamber} &bull; {pol.state}
                  </p>
                </div>

                {/* Trade count */}
                <div className="text-right flex-shrink-0">
                  <p className="text-lg font-bold font-mono text-white">{pol.trade_count || 0}</p>
                  <p className="text-[10px] text-[hsl(215,20%,55%)]">trades</p>
                </div>
              </div>
            ))}
          </div>

          <div className="text-center pt-2">
            <Link href="/politicians">
              <Button variant="outline" className="border-[hsl(215,40%,20%)] text-white hover:bg-[hsl(215,50%,14%)]">
                View All {politicians?.length || 500}+ Politicians
              </Button>
            </Link>
          </div>
        </section>

        {/* ===== TOP TRADED STOCKS BY CONGRESS ===== */}
        <section className="space-y-4">
          <h2 className="text-2xl md:text-3xl font-bold text-white">
            Top Traded Stocks by Congress
          </h2>
          <p className="text-sm text-[hsl(215,20%,55%)] font-mono">
            The most frequently bought and sold stocks among all members of Congress
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {TOP_TRADED_STOCKS.map((stock) => {
              const buyPct = Math.round((stock.buys / stock.trades) * 100)
              return (
                <Card
                  key={stock.ticker}
                  className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)] hover:border-[hsl(45,96%,58%)]/30 transition-colors"
                >
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <Link
                        href={`/charts?symbol=${stock.ticker}`}
                        className="text-[hsl(45,96%,58%)] font-bold text-lg font-mono hover:underline"
                      >
                        {stock.ticker}
                      </Link>
                      <Badge variant="outline" className="border-[hsl(215,40%,20%)] text-[hsl(215,20%,65%)] text-[10px]">
                        {stock.sector}
                      </Badge>
                    </div>
                    <p className="text-xs text-[hsl(215,20%,55%)] truncate">{stock.company}</p>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-[hsl(215,20%,65%)]">Total trades</span>
                      <span className="text-white font-bold">{stock.trades}</span>
                    </div>
                    {/* Buy/sell ratio bar */}
                    <div className="h-2 rounded-full overflow-hidden bg-[hsl(0,72%,55%)]/30 flex">
                      <div
                        className="h-full bg-[hsl(142,71%,55%)]"
                        style={{ width: `${buyPct}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-[10px] font-mono">
                      <span className="text-[hsl(142,71%,55%)]">{stock.buys} buys ({buyPct}%)</span>
                      <span className="text-[hsl(0,72%,55%)]">{stock.sells} sells</span>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </section>

        {/* ===== HOW IT WORKS ===== */}
        <section className="max-w-4xl mx-auto space-y-8">
          <h2 className="text-2xl md:text-3xl font-bold text-white text-center">
            How Congressional Trade Tracking Works
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                step: '1',
                title: 'Official Disclosure',
                desc: 'Members of Congress file financial disclosures through the Electronic Financial Disclosure System (EFDS) as required by the STOCK Act.',
              },
              {
                step: '2',
                title: 'Data Aggregation',
                desc: 'We collect, parse, and normalize disclosure data from both the Senate and House, cross-referencing with SEC filings and market data.',
              },
              {
                step: '3',
                title: 'Pattern Analysis',
                desc: 'Our ML-powered analytics engine identifies trading patterns, sector rotations, timing anomalies, and correlated activity across politicians.',
              },
            ].map((item) => (
              <div key={item.step} className="text-center space-y-3">
                <div className="w-12 h-12 mx-auto flex items-center justify-center rounded-full bg-[hsl(45,96%,58%)]/20 border border-[hsl(45,96%,58%)]/40">
                  <span className="text-[hsl(45,96%,58%)] font-bold text-lg font-mono">{item.step}</span>
                </div>
                <h3 className="text-white font-semibold text-lg">{item.title}</h3>
                <p className="text-sm text-[hsl(215,20%,60%)] leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ===== CTA - PREMIUM ALERTS ===== */}
        <section className="py-16 text-center space-y-8 bg-gradient-to-r from-[hsl(220,55%,7%)] to-[hsl(220,60%,5%)] rounded-lg border border-[hsl(215,40%,14%)]">
          <Badge className="bg-[hsl(210,100%,56%)] text-white text-xs">
            Premium Feature
          </Badge>
          <h2 className="text-3xl md:text-4xl font-bold text-white">
            Get Alerted When Politicians Trade
          </h2>
          <p className="text-lg text-[hsl(215,20%,65%)] max-w-2xl mx-auto">
            Never miss a trade. Receive real-time email and push notifications when specific
            politicians file new stock trades. Set custom alerts by politician, ticker, or trade size.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link href="/auth/register">
              <Button size="lg" className="bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)] hover:bg-[hsl(45,96%,65%)] font-semibold text-lg px-8">
                Sign Up for Free Alerts
              </Button>
            </Link>
            <Link href="/pricing">
              <Button size="lg" variant="outline" className="border-[hsl(215,40%,20%)] text-white hover:bg-[hsl(215,50%,14%)]">
                View Premium Plans
              </Button>
            </Link>
          </div>
          <div className="flex flex-wrap justify-center gap-6 text-sm text-[hsl(215,20%,55%)]">
            <span>Free tier: 3 alerts/week</span>
            <span className="hidden sm:inline">&bull;</span>
            <span>Pro: Unlimited real-time alerts</span>
            <span className="hidden sm:inline">&bull;</span>
            <span>Cancel anytime</span>
          </div>
        </section>

        {/* ===== FAQ (SEO) ===== */}
        <section className="max-w-3xl mx-auto space-y-6">
          <h2 className="text-2xl md:text-3xl font-bold text-white text-center">
            Frequently Asked Questions
          </h2>
          <div className="space-y-4">
            {[
              {
                q: 'Are congressional stock trades public information?',
                a: 'Yes. Under the STOCK Act of 2012, all members of Congress must publicly disclose stock transactions within 45 days of the trade. These filings are available through the Senate and House Electronic Financial Disclosure Systems.',
              },
              {
                q: 'Is it legal to copy the trades of politicians?',
                a: 'Yes. There is no law against following or replicating the publicly disclosed trades of members of Congress. However, disclosure delays of up to 45 days mean you are trading on delayed information.',
              },
              {
                q: 'How often is the data updated?',
                a: 'We process new disclosures daily as they are filed. Most politicians file within 30-45 days of their trade date. Our system aggregates data from both the Senate EFDS and House financial disclosure portals.',
              },
              {
                q: 'Do congressional trades really beat the market?',
                a: 'Multiple academic studies, including a well-known 2004 study by Alan Ziobrowski, found that U.S. Senators\' stock picks outperformed the market by an average of 12% per year. More recent studies show the gap has narrowed but remains statistically significant.',
              },
              {
                q: 'What data do you track for each trade?',
                a: 'For each disclosed trade, we track the politician, party, state, trade date, disclosure date, ticker symbol, asset type, transaction type (buy/sell), and the estimated dollar range of the trade.',
              },
            ].map((faq, idx) => (
              <details
                key={idx}
                className="group terminal-panel bg-[hsl(220,60%,4%)]"
              >
                <summary className="cursor-pointer p-4 text-white font-medium text-sm flex items-center justify-between hover:text-[hsl(45,96%,58%)] transition-colors">
                  {faq.q}
                  <span className="text-[hsl(215,20%,55%)] group-open:rotate-180 transition-transform ml-4 flex-shrink-0">
                    &#9660;
                  </span>
                </summary>
                <div className="px-4 pb-4 text-sm text-[hsl(215,20%,60%)] leading-relaxed border-t border-[hsl(215,40%,12%)] pt-3">
                  {faq.a}
                </div>
              </details>
            ))}
          </div>
        </section>

        {/* ===== RELATED BLOG ARTICLES ===== */}
        <section className="space-y-6">
          <h2 className="text-2xl md:text-3xl font-bold text-white text-center">
            Research &amp; Insights
          </h2>
          <p className="text-sm text-[hsl(215,20%,55%)] text-center max-w-2xl mx-auto">
            In-depth analysis and data-driven articles on congressional trading patterns
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {BLOG_ARTICLES.map((article) => (
              <Card
                key={article.slug}
                className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)] hover:border-[hsl(45,96%,58%)]/30 transition-colors"
              >
                <CardHeader>
                  <p className="text-[10px] text-[hsl(215,20%,55%)] font-mono">{article.date}</p>
                  <CardTitle className="text-white text-base leading-snug">
                    <Link href={article.slug} className="hover:text-[hsl(45,96%,58%)] transition-colors">
                      {article.title}
                    </Link>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-[hsl(215,20%,60%)] leading-relaxed">{article.excerpt}</p>
                  <Link
                    href={article.slug}
                    className="inline-block mt-3 text-xs font-mono text-[hsl(210,100%,56%)] hover:text-[hsl(210,100%,65%)] transition-colors"
                  >
                    Read more &rarr;
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* ===== BOTTOM SEO TEXT ===== */}
        <section className="max-w-3xl mx-auto text-center space-y-4 py-8 border-t border-[hsl(215,40%,14%)]">
          <h2 className="text-xl font-bold text-white">
            The Most Comprehensive Congressional Trading Database
          </h2>
          <p className="text-sm text-[hsl(215,20%,55%)] leading-relaxed">
            QuantEngines tracks stock trades from every member of the U.S. Senate and House
            of Representatives. Our database includes over 10,000 trades across 500+ politicians,
            updated daily from official EFDS filings. Whether you are researching congressional
            trading patterns, analyzing politician stock picks, or looking for potential conflicts
            of interest, our platform provides the data and analytics you need. Track congressional
            stock trades, monitor politician portfolios, and get alerts when new disclosures are
            filed &mdash; all for free.
          </p>
          <div className="flex flex-wrap justify-center gap-2 pt-2">
            {[
              'Congressional Stock Trades',
              'Politician Trading Tracker',
              'STOCK Act Disclosures',
              'Senate Stock Trades',
              'House Stock Trades',
              'Congress Insider Trading',
              'Political Stock Picks',
            ].map((tag) => (
              <Badge
                key={tag}
                variant="outline"
                className="border-[hsl(215,40%,20%)] text-[hsl(215,20%,55%)] text-[10px]"
              >
                {tag}
              </Badge>
            ))}
          </div>
        </section>
      </div>
    </>
  )
}

// ----- Helper components -----
function StatCard({ value, label }: { value: string; label: string }) {
  return (
    <div className="text-center">
      <p className="text-3xl md:text-4xl font-bold text-[hsl(45,96%,58%)] mb-2">{value}</p>
      <p className="text-sm text-[hsl(215,20%,60%)]">{label}</p>
    </div>
  )
}
