'use client'

import { useEffect, useState } from 'react'
import { use } from 'react'
import Link from 'next/link'
import dynamic from 'next/dynamic'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { formatCurrency, formatDate, formatPercent } from '@/lib/utils'

const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

interface Politician {
  id: string
  name: string
  chamber: string
  party: string
  state: string
  total_trades: number
  total_value: number
  win_rate: number
  avg_return: number
}

interface Trade {
  id: string
  ticker: string
  transaction_type: string
  amount_min: number
  amount_max: number
  transaction_date: string
  disclosure_date: string
}

export default function PoliticianProfilePage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params)
  const [politician, setPolitician] = useState<Politician | null>(null)
  const [trades, setTrades] = useState<Trade[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchData = async () => {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
      try {
        const [politicianRes, tradesRes] = await Promise.all([
          fetch(`${API_BASE}/politicians/${resolvedParams.id}`),
          fetch(`${API_BASE}/politicians/${resolvedParams.id}/trades`),
        ])

        if (!politicianRes.ok) {
          throw new Error('Politician not found')
        }

        const [politicianData, tradesData] = await Promise.all([
          politicianRes.json(),
          tradesRes.json(),
        ])

        setPolitician(politicianData)
        setTrades(tradesData.items || tradesData || [])
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred')
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [resolvedParams.id])

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-32 w-full" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
        </div>
        <Skeleton className="h-96 w-full" />
      </div>
    )
  }

  if (error || !politician) {
    return (
      <div className="text-center py-20">
        <h1 className="text-2xl font-bold text-white mb-4">Politician Not Found</h1>
        <p className="text-[hsl(215,20%,60%)] mb-6">{error}</p>
        <Link href="/politicians" className="text-[hsl(45,96%,58%)] hover:underline">
          View All Politicians
        </Link>
      </div>
    )
  }

  const tradesByType = trades.reduce((acc, trade) => {
    const type = trade.transaction_type
    acc[type] = (acc[type] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const chartData = {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: Object.entries(tradesByType).map(([name, value]) => ({
        name: name === 'purchase' ? 'Purchases' : 'Sales',
        value,
        itemStyle: {
          color: name === 'purchase' ? '#22c55e' : '#ef4444'
        }
      }))
    }]
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="border-[hsl(215,40%,18%)] bg-gradient-to-r from-[hsl(220,55%,7%)] to-[hsl(220,60%,5%)]">
        <CardContent className="py-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">{politician.name}</h1>
              <div className="flex gap-2">
                <Badge className={politician.party === 'Republican' ? 'bg-red-500' : 'bg-blue-500'}>
                  {politician.party}
                </Badge>
                <Badge variant="outline">{politician.chamber}</Badge>
                <Badge variant="outline">{politician.state}</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          label="Total Trades"
          value={politician.total_trades?.toString() || '0'}
          icon="📊"
        />
        <StatCard
          label="Total Value"
          value={formatCurrency(politician.total_value || 0)}
          icon="💰"
        />
        <StatCard
          label="Win Rate"
          value={formatPercent(politician.win_rate || 0)}
          icon="🎯"
          positive={politician.win_rate > 50}
        />
        <StatCard
          label="Avg Return"
          value={formatPercent(politician.avg_return || 0)}
          icon="📈"
          positive={politician.avg_return > 0}
        />
      </div>

      {/* Trading Activity */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
          <CardHeader>
            <CardTitle className="text-white">Trade Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ReactECharts option={chartData} style={{ height: '100%', width: '100%' }} />
            </div>
          </CardContent>
        </Card>

        <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
          <CardHeader>
            <CardTitle className="text-white">Top Holdings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {trades.slice(0, 5).map((trade) => (
                <div key={trade.id} className="flex items-center justify-between p-2 rounded bg-[hsl(220,60%,4%)]">
                  <Link href={`/charts?symbol=${trade.ticker}`} className="font-semibold text-white hover:text-[hsl(45,96%,58%)]">
                    {trade.ticker}
                  </Link>
                  <span className={`text-sm ${trade.transaction_type === 'purchase' ? 'text-green-500' : 'text-red-500'}`}>
                    {trade.transaction_type === 'purchase' ? '↑ BUY' : '↓ SELL'}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Trades */}
      <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
        <CardHeader>
          <CardTitle className="text-white">Recent Trades</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {trades.slice(0, 10).map((trade) => (
              <Link
                key={trade.id}
                href={`/trades/${trade.id}`}
                className="block p-4 rounded bg-[hsl(220,60%,4%)] hover:bg-[hsl(220,60%,6%)] transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl ${
                      trade.transaction_type === 'purchase' ? 'bg-green-500/20' : 'bg-red-500/20'
                    }`}>
                      {trade.transaction_type === 'purchase' ? '↑' : '↓'}
                    </div>
                    <div>
                      <p className="font-semibold text-white">{trade.ticker}</p>
                      <p className="text-xs text-[hsl(215,20%,55%)]">
                        {formatDate(trade.transaction_date)}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`font-semibold ${trade.transaction_type === 'purchase' ? 'text-green-500' : 'text-red-500'}`}>
                      {trade.transaction_type === 'purchase' ? 'PURCHASE' : 'SALE'}
                    </p>
                    <p className="text-sm text-[hsl(215,20%,60%)]">
                      {formatCurrency(trade.amount_min)} - {formatCurrency(trade.amount_max)}
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Back Link */}
      <Link href="/politicians" className="inline-block text-[hsl(45,96%,58%)] hover:underline">
        ← Back to All Politicians
      </Link>
    </div>
  )
}

function StatCard({ label, value, icon, positive }: { label: string; value: string; icon: string; positive?: boolean }) {
  return (
    <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
      <CardContent className="p-6">
        <div className="flex items-start justify-between mb-2">
          <span className="text-2xl">{icon}</span>
          {typeof positive === 'boolean' && (
            <span className={positive ? 'text-green-500' : 'text-red-500'}>
              {positive ? '↑' : '↓'}
            </span>
          )}
        </div>
        <p className="text-2xl font-bold text-white mb-1">{value}</p>
        <p className="text-xs text-[hsl(215,20%,55%)] uppercase tracking-wider">{label}</p>
      </CardContent>
    </Card>
  )
}
