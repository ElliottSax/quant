'use client'

import { useEffect, useState } from 'react'
import { use } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { formatCurrency, formatDate } from '@/lib/utils'

interface Trade {
  id: string
  politician_name: string
  politician_id: string
  ticker: string
  transaction_type: string
  amount_min: number
  amount_max: number
  transaction_date: string
  disclosure_date: string
  asset_description: string
  politician_party: string
  politician_chamber: string
}

export default function TradeDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params)
  const [trade, setTrade] = useState<Trade | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchTrade = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/trades/${resolvedParams.id}`)
        if (!response.ok) {
          throw new Error('Trade not found')
        }
        const data = await response.json()
        setTrade(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred')
      } finally {
        setIsLoading(false)
      }
    }

    fetchTrade()
  }, [resolvedParams.id])

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-64" />
        <Skeleton className="h-96 w-full" />
      </div>
    )
  }

  if (error || !trade) {
    return (
      <div className="text-center py-20">
        <h1 className="text-2xl font-bold text-white mb-4">Trade Not Found</h1>
        <p className="text-[hsl(215,20%,60%)] mb-6">{error}</p>
        <Link href="/politicians" className="text-[hsl(45,96%,58%)] hover:underline">
          View All Trades
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Trade Details</h1>
          <p className="text-[hsl(215,20%,60%)]">
            Transaction ID: {trade.id}
          </p>
        </div>
        <Badge className={trade.transaction_type === 'purchase' ? 'bg-green-500' : 'bg-red-500'}>
          {trade.transaction_type.toUpperCase()}
        </Badge>
      </div>

      {/* Main Info */}
      <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
        <CardHeader>
          <CardTitle className="text-white">Transaction Information</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p className="text-sm text-[hsl(215,20%,55%)] mb-1">Politician</p>
            <Link href={`/politicians/${trade.politician_id}`} className="text-lg font-semibold text-[hsl(45,96%,58%)] hover:underline">
              {trade.politician_name}
            </Link>
            <div className="flex gap-2 mt-2">
              <Badge variant="outline">{trade.politician_party}</Badge>
              <Badge variant="outline">{trade.politician_chamber}</Badge>
            </div>
          </div>
          <div>
            <p className="text-sm text-[hsl(215,20%,55%)] mb-1">Stock Ticker</p>
            <Link href={`/charts?symbol=${trade.ticker}`} className="text-lg font-semibold text-white">
              {trade.ticker}
            </Link>
            <p className="text-sm text-[hsl(215,20%,60%)] mt-1">{trade.asset_description}</p>
          </div>
          <div>
            <p className="text-sm text-[hsl(215,20%,55%)] mb-1">Transaction Date</p>
            <p className="text-lg font-semibold text-white">{formatDate(trade.transaction_date)}</p>
          </div>
          <div>
            <p className="text-sm text-[hsl(215,20%,55%)] mb-1">Disclosure Date</p>
            <p className="text-lg font-semibold text-white">{formatDate(trade.disclosure_date)}</p>
          </div>
          <div>
            <p className="text-sm text-[hsl(215,20%,55%)] mb-1">Amount Range</p>
            <p className="text-lg font-semibold text-white">
              {formatCurrency(trade.amount_min)} - {formatCurrency(trade.amount_max)}
            </p>
          </div>
          <div>
            <p className="text-sm text-[hsl(215,20%,55%)] mb-1">Transaction Type</p>
            <p className={`text-lg font-semibold ${trade.transaction_type === 'purchase' ? 'text-green-500' : 'text-red-500'}`}>
              {trade.transaction_type === 'purchase' ? 'Purchase' : 'Sale'}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Related Trades */}
      <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
        <CardHeader>
          <CardTitle className="text-white">Related Trades</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-[hsl(215,20%,60%)]">
            Similar trades from {trade.politician_name} in {trade.ticker}
          </p>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex gap-4">
        <Link href="/politicians" className="text-[hsl(45,96%,58%)] hover:underline">
          ← Back to Politicians
        </Link>
        <Link href={`/politicians/${trade.politician_id}`} className="text-[hsl(45,96%,58%)] hover:underline">
          View Politician Profile →
        </Link>
      </div>
    </div>
  )
}
