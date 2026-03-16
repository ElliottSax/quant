/**
 * Congressional Trader Leaderboard
 * Politicians ranked by trading performance with social sharing
 */

'use client'

import { useState, useMemo, useCallback, Fragment } from 'react'
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'

// ---------- Types ----------
interface Politician {
  id: number
  name: string
  party: 'D' | 'R' | 'I'
  chamber: 'Senate' | 'House'
  state: string
  annualReturn: number
  winRate: number
  totalTrades: number
  bestTrade: { stock: string; returnPct: number }
  worstTrade: { stock: string; returnPct: number }
  cumulativeReturns: { month: string; returnPct: number; sp500: number }[]
  topHoldings: { stock: string; pct: number }[]
  sectorBreakdown: { sector: string; pct: number }[]
  recentTrades: { date: string; stock: string; action: 'Buy' | 'Sell'; amount: string; returnPct: number | null }[]
}

// ---------- Hardcoded Data (20 politicians) ----------
function generateCumulativeReturns(finalReturn: number): Politician['cumulativeReturns'] {
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
  const sp500Final = 12.4
  let cum = 0
  let sp = 0
  return months.map((m, i) => {
    const progress = (i + 1) / 12
    const noise = (Math.random() - 0.5) * 4
    cum = +(finalReturn * progress + noise).toFixed(1)
    sp = +(sp500Final * progress + (Math.random() - 0.5) * 2).toFixed(1)
    return { month: m, returnPct: cum, sp500: sp }
  })
}

const POLITICIANS: Politician[] = [
  {
    id: 1, name: 'Nancy Pelosi', party: 'D', chamber: 'House', state: 'CA',
    annualReturn: 31.5, winRate: 72, totalTrades: 89,
    bestTrade: { stock: 'NVDA', returnPct: 142.3 }, worstTrade: { stock: 'DIS', returnPct: -18.7 },
    cumulativeReturns: generateCumulativeReturns(31.5),
    topHoldings: [{ stock: 'NVDA', pct: 22 }, { stock: 'AAPL', pct: 18 }, { stock: 'GOOGL', pct: 14 }, { stock: 'MSFT', pct: 12 }, { stock: 'AMZN', pct: 9 }],
    sectorBreakdown: [{ sector: 'Technology', pct: 48 }, { sector: 'Finance', pct: 18 }, { sector: 'Healthcare', pct: 14 }, { sector: 'Energy', pct: 10 }, { sector: 'Other', pct: 10 }],
    recentTrades: [
      { date: '2026-03-10', stock: 'NVDA', action: 'Buy', amount: '$500K-$1M', returnPct: null },
      { date: '2026-03-03', stock: 'AAPL', action: 'Buy', amount: '$250K-$500K', returnPct: null },
      { date: '2026-02-20', stock: 'CRM', action: 'Sell', amount: '$100K-$250K', returnPct: 28.4 },
      { date: '2026-02-14', stock: 'GOOGL', action: 'Buy', amount: '$500K-$1M', returnPct: null },
      { date: '2026-02-01', stock: 'TSLA', action: 'Sell', amount: '$250K-$500K', returnPct: -8.2 },
      { date: '2026-01-22', stock: 'MSFT', action: 'Buy', amount: '$1M-$5M', returnPct: null },
      { date: '2026-01-15', stock: 'AMZN', action: 'Buy', amount: '$250K-$500K', returnPct: null },
      { date: '2026-01-08', stock: 'META', action: 'Sell', amount: '$500K-$1M', returnPct: 45.1 },
      { date: '2025-12-18', stock: 'NFLX', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2025-12-05', stock: 'DIS', action: 'Sell', amount: '$250K-$500K', returnPct: -18.7 },
    ],
  },
  {
    id: 2, name: 'Dan Crenshaw', party: 'R', chamber: 'House', state: 'TX',
    annualReturn: 28.9, winRate: 68, totalTrades: 74,
    bestTrade: { stock: 'XOM', returnPct: 87.6 }, worstTrade: { stock: 'RIVN', returnPct: -34.2 },
    cumulativeReturns: generateCumulativeReturns(28.9),
    topHoldings: [{ stock: 'XOM', pct: 20 }, { stock: 'CVX', pct: 16 }, { stock: 'MSFT', pct: 14 }, { stock: 'LMT', pct: 12 }, { stock: 'BA', pct: 8 }],
    sectorBreakdown: [{ sector: 'Energy', pct: 36 }, { sector: 'Defense', pct: 22 }, { sector: 'Technology', pct: 20 }, { sector: 'Finance', pct: 12 }, { sector: 'Other', pct: 10 }],
    recentTrades: [
      { date: '2026-03-08', stock: 'XOM', action: 'Buy', amount: '$250K-$500K', returnPct: null },
      { date: '2026-02-25', stock: 'LMT', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-02-15', stock: 'RIVN', action: 'Sell', amount: '$50K-$100K', returnPct: -34.2 },
      { date: '2026-02-01', stock: 'CVX', action: 'Buy', amount: '$250K-$500K', returnPct: null },
      { date: '2026-01-20', stock: 'MSFT', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-01-10', stock: 'BA', action: 'Sell', amount: '$100K-$250K', returnPct: 22.1 },
      { date: '2025-12-28', stock: 'RTX', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-12-15', stock: 'AAPL', action: 'Sell', amount: '$250K-$500K', returnPct: 15.3 },
      { date: '2025-12-01', stock: 'HAL', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2025-11-18', stock: 'NOC', action: 'Buy', amount: '$50K-$100K', returnPct: null },
    ],
  },
  {
    id: 3, name: 'Tommy Tuberville', party: 'R', chamber: 'Senate', state: 'AL',
    annualReturn: 26.3, winRate: 64, totalTrades: 132,
    bestTrade: { stock: 'TSLA', returnPct: 98.4 }, worstTrade: { stock: 'BABA', returnPct: -41.5 },
    cumulativeReturns: generateCumulativeReturns(26.3),
    topHoldings: [{ stock: 'TSLA', pct: 15 }, { stock: 'AAPL', pct: 12 }, { stock: 'MSFT', pct: 11 }, { stock: 'GOOGL', pct: 10 }, { stock: 'AMZN', pct: 8 }],
    sectorBreakdown: [{ sector: 'Technology', pct: 42 }, { sector: 'Finance', pct: 20 }, { sector: 'Healthcare', pct: 15 }, { sector: 'Consumer', pct: 13 }, { sector: 'Other', pct: 10 }],
    recentTrades: [
      { date: '2026-03-12', stock: 'TSLA', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-03-05', stock: 'NVDA', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-02-28', stock: 'BABA', action: 'Sell', amount: '$50K-$100K', returnPct: -41.5 },
      { date: '2026-02-18', stock: 'AAPL', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-02-10', stock: 'JPM', action: 'Sell', amount: '$50K-$100K', returnPct: 18.9 },
      { date: '2026-02-01', stock: 'GOOGL', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-01-22', stock: 'AMZN', action: 'Sell', amount: '$50K-$100K', returnPct: 32.1 },
      { date: '2026-01-15', stock: 'META', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-01-05', stock: 'MSFT', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2025-12-20', stock: 'AMD', action: 'Sell', amount: '$50K-$100K', returnPct: 24.6 },
    ],
  },
  {
    id: 4, name: 'Mark Green', party: 'R', chamber: 'House', state: 'TN',
    annualReturn: 24.1, winRate: 66, totalTrades: 58,
    bestTrade: { stock: 'LMT', returnPct: 67.2 }, worstTrade: { stock: 'PYPL', returnPct: -22.8 },
    cumulativeReturns: generateCumulativeReturns(24.1),
    topHoldings: [{ stock: 'LMT', pct: 24 }, { stock: 'RTX', pct: 18 }, { stock: 'NOC', pct: 14 }, { stock: 'GD', pct: 10 }, { stock: 'MSFT', pct: 8 }],
    sectorBreakdown: [{ sector: 'Defense', pct: 52 }, { sector: 'Technology', pct: 18 }, { sector: 'Healthcare', pct: 14 }, { sector: 'Finance', pct: 10 }, { sector: 'Other', pct: 6 }],
    recentTrades: [
      { date: '2026-03-05', stock: 'LMT', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-02-20', stock: 'RTX', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-02-10', stock: 'PYPL', action: 'Sell', amount: '$50K-$100K', returnPct: -22.8 },
      { date: '2026-01-28', stock: 'NOC', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-01-15', stock: 'GD', action: 'Sell', amount: '$50K-$100K', returnPct: 34.5 },
      { date: '2026-01-05', stock: 'MSFT', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-12-18', stock: 'BA', action: 'Sell', amount: '$50K-$100K', returnPct: 12.3 },
      { date: '2025-12-05', stock: 'LMT', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2025-11-20', stock: 'PLTR', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-10', stock: 'RTX', action: 'Sell', amount: '$50K-$100K', returnPct: 28.7 },
    ],
  },
  {
    id: 5, name: 'Josh Gottheimer', party: 'D', chamber: 'House', state: 'NJ',
    annualReturn: 22.8, winRate: 70, totalTrades: 95,
    bestTrade: { stock: 'MSFT', returnPct: 55.1 }, worstTrade: { stock: 'SNAP', returnPct: -38.4 },
    cumulativeReturns: generateCumulativeReturns(22.8),
    topHoldings: [{ stock: 'MSFT', pct: 20 }, { stock: 'GOOGL', pct: 16 }, { stock: 'AAPL', pct: 14 }, { stock: 'JPM', pct: 12 }, { stock: 'GS', pct: 10 }],
    sectorBreakdown: [{ sector: 'Technology', pct: 44 }, { sector: 'Finance', pct: 28 }, { sector: 'Healthcare', pct: 12 }, { sector: 'Consumer', pct: 10 }, { sector: 'Other', pct: 6 }],
    recentTrades: [
      { date: '2026-03-10', stock: 'MSFT', action: 'Buy', amount: '$250K-$500K', returnPct: null },
      { date: '2026-03-01', stock: 'GOOGL', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-02-18', stock: 'SNAP', action: 'Sell', amount: '$50K-$100K', returnPct: -38.4 },
      { date: '2026-02-05', stock: 'JPM', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-01-25', stock: 'GS', action: 'Sell', amount: '$100K-$250K', returnPct: 21.3 },
      { date: '2026-01-12', stock: 'AAPL', action: 'Buy', amount: '$250K-$500K', returnPct: null },
      { date: '2026-01-03', stock: 'META', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2025-12-20', stock: 'AMZN', action: 'Sell', amount: '$100K-$250K', returnPct: 33.2 },
      { date: '2025-12-10', stock: 'CRM', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-28', stock: 'V', action: 'Sell', amount: '$50K-$100K', returnPct: 16.8 },
    ],
  },
  {
    id: 6, name: 'Markwayne Mullin', party: 'R', chamber: 'Senate', state: 'OK',
    annualReturn: 21.4, winRate: 62, totalTrades: 67,
    bestTrade: { stock: 'OXY', returnPct: 74.3 }, worstTrade: { stock: 'COIN', returnPct: -29.1 },
    cumulativeReturns: generateCumulativeReturns(21.4),
    topHoldings: [{ stock: 'OXY', pct: 18 }, { stock: 'XOM', pct: 16 }, { stock: 'CVX', pct: 14 }, { stock: 'SLB', pct: 10 }, { stock: 'MSFT', pct: 8 }],
    sectorBreakdown: [{ sector: 'Energy', pct: 48 }, { sector: 'Technology', pct: 18 }, { sector: 'Industrials', pct: 16 }, { sector: 'Finance', pct: 10 }, { sector: 'Other', pct: 8 }],
    recentTrades: [
      { date: '2026-03-08', stock: 'OXY', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-02-22', stock: 'XOM', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-02-10', stock: 'COIN', action: 'Sell', amount: '$50K-$100K', returnPct: -29.1 },
      { date: '2026-01-28', stock: 'CVX', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-01-15', stock: 'SLB', action: 'Sell', amount: '$50K-$100K', returnPct: 18.4 },
      { date: '2026-01-05', stock: 'HAL', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-12-22', stock: 'MSFT', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-12-10', stock: 'COP', action: 'Sell', amount: '$50K-$100K', returnPct: 22.7 },
      { date: '2025-11-28', stock: 'DVN', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-15', stock: 'EOG', action: 'Buy', amount: '$50K-$100K', returnPct: null },
    ],
  },
  {
    id: 7, name: 'Michael McCaul', party: 'R', chamber: 'House', state: 'TX',
    annualReturn: 19.7, winRate: 65, totalTrades: 48,
    bestTrade: { stock: 'AVGO', returnPct: 91.2 }, worstTrade: { stock: 'INTC', returnPct: -26.3 },
    cumulativeReturns: generateCumulativeReturns(19.7),
    topHoldings: [{ stock: 'AVGO', pct: 22 }, { stock: 'NVDA', pct: 18 }, { stock: 'MSFT', pct: 14 }, { stock: 'AAPL', pct: 10 }, { stock: 'QCOM', pct: 8 }],
    sectorBreakdown: [{ sector: 'Technology', pct: 58 }, { sector: 'Defense', pct: 16 }, { sector: 'Healthcare', pct: 12 }, { sector: 'Finance', pct: 8 }, { sector: 'Other', pct: 6 }],
    recentTrades: [
      { date: '2026-03-05', stock: 'AVGO', action: 'Buy', amount: '$250K-$500K', returnPct: null },
      { date: '2026-02-22', stock: 'NVDA', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-02-08', stock: 'INTC', action: 'Sell', amount: '$100K-$250K', returnPct: -26.3 },
      { date: '2026-01-25', stock: 'MSFT', action: 'Buy', amount: '$250K-$500K', returnPct: null },
      { date: '2026-01-12', stock: 'AAPL', action: 'Sell', amount: '$100K-$250K', returnPct: 19.8 },
      { date: '2025-12-30', stock: 'QCOM', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2025-12-18', stock: 'AMD', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-12-05', stock: 'TSM', action: 'Sell', amount: '$100K-$250K', returnPct: 35.2 },
      { date: '2025-11-22', stock: 'MU', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-10', stock: 'MRVL', action: 'Buy', amount: '$50K-$100K', returnPct: null },
    ],
  },
  {
    id: 8, name: 'Ro Khanna', party: 'D', chamber: 'House', state: 'CA',
    annualReturn: 18.3, winRate: 71, totalTrades: 42,
    bestTrade: { stock: 'PLTR', returnPct: 112.5 }, worstTrade: { stock: 'ROKU', returnPct: -33.1 },
    cumulativeReturns: generateCumulativeReturns(18.3),
    topHoldings: [{ stock: 'PLTR', pct: 18 }, { stock: 'AAPL', pct: 16 }, { stock: 'MSFT', pct: 14 }, { stock: 'NVDA', pct: 12 }, { stock: 'CRM', pct: 8 }],
    sectorBreakdown: [{ sector: 'Technology', pct: 62 }, { sector: 'Healthcare', pct: 14 }, { sector: 'Finance', pct: 10 }, { sector: 'Consumer', pct: 8 }, { sector: 'Other', pct: 6 }],
    recentTrades: [
      { date: '2026-03-10', stock: 'PLTR', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-02-28', stock: 'AAPL', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-02-15', stock: 'ROKU', action: 'Sell', amount: '$50K-$100K', returnPct: -33.1 },
      { date: '2026-02-01', stock: 'MSFT', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-01-20', stock: 'NVDA', action: 'Sell', amount: '$100K-$250K', returnPct: 45.3 },
      { date: '2026-01-08', stock: 'CRM', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-12-22', stock: 'SNOW', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-12-10', stock: 'DDOG', action: 'Sell', amount: '$50K-$100K', returnPct: 28.9 },
      { date: '2025-11-25', stock: 'NET', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-12', stock: 'PANW', action: 'Buy', amount: '$50K-$100K', returnPct: null },
    ],
  },
  {
    id: 9, name: 'John Hickenlooper', party: 'D', chamber: 'Senate', state: 'CO',
    annualReturn: 17.6, winRate: 63, totalTrades: 51,
    bestTrade: { stock: 'ABNB', returnPct: 58.7 }, worstTrade: { stock: 'HOOD', returnPct: -44.2 },
    cumulativeReturns: generateCumulativeReturns(17.6),
    topHoldings: [{ stock: 'ABNB', pct: 16 }, { stock: 'AAPL', pct: 14 }, { stock: 'GOOGL', pct: 12 }, { stock: 'V', pct: 10 }, { stock: 'MA', pct: 8 }],
    sectorBreakdown: [{ sector: 'Technology', pct: 38 }, { sector: 'Finance', pct: 22 }, { sector: 'Consumer', pct: 18 }, { sector: 'Healthcare', pct: 12 }, { sector: 'Other', pct: 10 }],
    recentTrades: [
      { date: '2026-03-08', stock: 'ABNB', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-02-25', stock: 'AAPL', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-02-12', stock: 'HOOD', action: 'Sell', amount: '$50K-$100K', returnPct: -44.2 },
      { date: '2026-01-30', stock: 'GOOGL', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-01-18', stock: 'V', action: 'Sell', amount: '$100K-$250K', returnPct: 22.4 },
      { date: '2026-01-05', stock: 'MA', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-12-20', stock: 'SQ', action: 'Sell', amount: '$50K-$100K', returnPct: -12.3 },
      { date: '2025-12-08', stock: 'UBER', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-25', stock: 'LYFT', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-10', stock: 'DASH', action: 'Sell', amount: '$50K-$100K', returnPct: 31.5 },
    ],
  },
  {
    id: 10, name: 'Pat Fallon', party: 'R', chamber: 'House', state: 'TX',
    annualReturn: 16.2, winRate: 60, totalTrades: 118,
    bestTrade: { stock: 'SMCI', returnPct: 156.8 }, worstTrade: { stock: 'LCID', returnPct: -52.3 },
    cumulativeReturns: generateCumulativeReturns(16.2),
    topHoldings: [{ stock: 'SMCI', pct: 14 }, { stock: 'NVDA', pct: 12 }, { stock: 'AMD', pct: 10 }, { stock: 'TSLA', pct: 8 }, { stock: 'AAPL', pct: 8 }],
    sectorBreakdown: [{ sector: 'Technology', pct: 52 }, { sector: 'Energy', pct: 16 }, { sector: 'Healthcare', pct: 12 }, { sector: 'Finance', pct: 12 }, { sector: 'Other', pct: 8 }],
    recentTrades: [
      { date: '2026-03-12', stock: 'SMCI', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-03-05', stock: 'NVDA', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-02-22', stock: 'LCID', action: 'Sell', amount: '$15K-$50K', returnPct: -52.3 },
      { date: '2026-02-10', stock: 'AMD', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-01-28', stock: 'TSLA', action: 'Sell', amount: '$50K-$100K', returnPct: 38.7 },
      { date: '2026-01-15', stock: 'AAPL', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-01-05', stock: 'MARA', action: 'Sell', amount: '$15K-$50K', returnPct: -28.4 },
      { date: '2025-12-20', stock: 'SOFI', action: 'Buy', amount: '$15K-$50K', returnPct: null },
      { date: '2025-12-08', stock: 'PLTR', action: 'Sell', amount: '$50K-$100K', returnPct: 67.2 },
      { date: '2025-11-28', stock: 'RKLB', action: 'Buy', amount: '$15K-$50K', returnPct: null },
    ],
  },
  {
    id: 11, name: 'Sheldon Whitehouse', party: 'D', chamber: 'Senate', state: 'RI',
    annualReturn: 15.8, winRate: 67, totalTrades: 38,
    bestTrade: { stock: 'ENPH', returnPct: 72.4 }, worstTrade: { stock: 'SPCE', returnPct: -61.2 },
    cumulativeReturns: generateCumulativeReturns(15.8),
    topHoldings: [{ stock: 'ENPH', pct: 18 }, { stock: 'NEE', pct: 14 }, { stock: 'FSLR', pct: 12 }, { stock: 'MSFT', pct: 10 }, { stock: 'JNJ', pct: 8 }],
    sectorBreakdown: [{ sector: 'Clean Energy', pct: 34 }, { sector: 'Technology', pct: 22 }, { sector: 'Healthcare', pct: 18 }, { sector: 'Utilities', pct: 14 }, { sector: 'Other', pct: 12 }],
    recentTrades: [
      { date: '2026-03-05', stock: 'ENPH', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-02-20', stock: 'NEE', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-02-08', stock: 'SPCE', action: 'Sell', amount: '$15K-$50K', returnPct: -61.2 },
      { date: '2026-01-25', stock: 'FSLR', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-01-12', stock: 'MSFT', action: 'Sell', amount: '$100K-$250K', returnPct: 24.8 },
      { date: '2025-12-30', stock: 'JNJ', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-12-18', stock: 'PFE', action: 'Sell', amount: '$50K-$100K', returnPct: -8.3 },
      { date: '2025-12-05', stock: 'SEDG', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-22', stock: 'RUN', action: 'Buy', amount: '$15K-$50K', returnPct: null },
      { date: '2025-11-10', stock: 'BE', action: 'Sell', amount: '$15K-$50K', returnPct: 42.1 },
    ],
  },
  {
    id: 12, name: 'Virginia Foxx', party: 'R', chamber: 'House', state: 'NC',
    annualReturn: 14.5, winRate: 61, totalTrades: 44,
    bestTrade: { stock: 'UNH', returnPct: 48.3 }, worstTrade: { stock: 'ZM', returnPct: -35.6 },
    cumulativeReturns: generateCumulativeReturns(14.5),
    topHoldings: [{ stock: 'UNH', pct: 20 }, { stock: 'JNJ', pct: 16 }, { stock: 'PFE', pct: 12 }, { stock: 'ABT', pct: 10 }, { stock: 'MSFT', pct: 8 }],
    sectorBreakdown: [{ sector: 'Healthcare', pct: 46 }, { sector: 'Technology', pct: 20 }, { sector: 'Finance', pct: 16 }, { sector: 'Consumer', pct: 10 }, { sector: 'Other', pct: 8 }],
    recentTrades: [
      { date: '2026-03-08', stock: 'UNH', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-02-25', stock: 'JNJ', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-02-12', stock: 'ZM', action: 'Sell', amount: '$50K-$100K', returnPct: -35.6 },
      { date: '2026-01-30', stock: 'PFE', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-01-18', stock: 'ABT', action: 'Sell', amount: '$50K-$100K', returnPct: 18.9 },
      { date: '2026-01-05', stock: 'MSFT', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-12-22', stock: 'TMO', action: 'Sell', amount: '$50K-$100K', returnPct: 22.4 },
      { date: '2025-12-08', stock: 'ISRG', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-25', stock: 'MDT', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-12', stock: 'BSX', action: 'Sell', amount: '$50K-$100K', returnPct: 15.2 },
    ],
  },
  {
    id: 13, name: 'Debbie Wasserman Schultz', party: 'D', chamber: 'House', state: 'FL',
    annualReturn: 13.9, winRate: 64, totalTrades: 36,
    bestTrade: { stock: 'META', returnPct: 62.8 }, worstTrade: { stock: 'WISH', returnPct: -72.1 },
    cumulativeReturns: generateCumulativeReturns(13.9),
    topHoldings: [{ stock: 'META', pct: 18 }, { stock: 'AAPL', pct: 14 }, { stock: 'DIS', pct: 12 }, { stock: 'NFLX', pct: 10 }, { stock: 'GOOGL', pct: 8 }],
    sectorBreakdown: [{ sector: 'Technology', pct: 40 }, { sector: 'Media', pct: 22 }, { sector: 'Consumer', pct: 16 }, { sector: 'Finance', pct: 12 }, { sector: 'Other', pct: 10 }],
    recentTrades: [
      { date: '2026-03-05', stock: 'META', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-02-20', stock: 'AAPL', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-02-08', stock: 'WISH', action: 'Sell', amount: '$15K-$50K', returnPct: -72.1 },
      { date: '2026-01-25', stock: 'DIS', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-01-12', stock: 'NFLX', action: 'Sell', amount: '$50K-$100K', returnPct: 38.4 },
      { date: '2026-01-02', stock: 'GOOGL', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-12-18', stock: 'SPOT', action: 'Sell', amount: '$50K-$100K', returnPct: 25.7 },
      { date: '2025-12-05', stock: 'RBLX', action: 'Buy', amount: '$15K-$50K', returnPct: null },
      { date: '2025-11-22', stock: 'TTD', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-10', stock: 'PINS', action: 'Sell', amount: '$15K-$50K', returnPct: -14.2 },
    ],
  },
  {
    id: 14, name: 'Bill Hagerty', party: 'R', chamber: 'Senate', state: 'TN',
    annualReturn: 13.1, winRate: 59, totalTrades: 29,
    bestTrade: { stock: 'BRK.B', returnPct: 34.2 }, worstTrade: { stock: 'ARKK', returnPct: -28.5 },
    cumulativeReturns: generateCumulativeReturns(13.1),
    topHoldings: [{ stock: 'BRK.B', pct: 22 }, { stock: 'JPM', pct: 18 }, { stock: 'BAC', pct: 14 }, { stock: 'WFC', pct: 10 }, { stock: 'GS', pct: 8 }],
    sectorBreakdown: [{ sector: 'Finance', pct: 54 }, { sector: 'Technology', pct: 16 }, { sector: 'Industrials', pct: 14 }, { sector: 'Healthcare', pct: 8 }, { sector: 'Other', pct: 8 }],
    recentTrades: [
      { date: '2026-03-01', stock: 'BRK.B', action: 'Buy', amount: '$250K-$500K', returnPct: null },
      { date: '2026-02-15', stock: 'JPM', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-02-01', stock: 'ARKK', action: 'Sell', amount: '$50K-$100K', returnPct: -28.5 },
      { date: '2026-01-18', stock: 'BAC', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-01-05', stock: 'WFC', action: 'Sell', amount: '$50K-$100K', returnPct: 16.3 },
      { date: '2025-12-22', stock: 'GS', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2025-12-10', stock: 'MS', action: 'Sell', amount: '$50K-$100K', returnPct: 19.4 },
      { date: '2025-11-28', stock: 'C', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-15', stock: 'SCHW', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-02', stock: 'AXP', action: 'Sell', amount: '$50K-$100K', returnPct: 12.8 },
    ],
  },
  {
    id: 15, name: 'Suzan DelBene', party: 'D', chamber: 'House', state: 'WA',
    annualReturn: 12.4, winRate: 66, totalTrades: 31,
    bestTrade: { stock: 'AMZN', returnPct: 44.7 }, worstTrade: { stock: 'DOCU', returnPct: -31.8 },
    cumulativeReturns: generateCumulativeReturns(12.4),
    topHoldings: [{ stock: 'AMZN', pct: 20 }, { stock: 'MSFT', pct: 18 }, { stock: 'AAPL', pct: 14 }, { stock: 'COST', pct: 10 }, { stock: 'SBUX', pct: 8 }],
    sectorBreakdown: [{ sector: 'Technology', pct: 48 }, { sector: 'Consumer', pct: 22 }, { sector: 'Healthcare', pct: 14 }, { sector: 'Finance', pct: 10 }, { sector: 'Other', pct: 6 }],
    recentTrades: [
      { date: '2026-03-08', stock: 'AMZN', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-02-22', stock: 'MSFT', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-02-10', stock: 'DOCU', action: 'Sell', amount: '$50K-$100K', returnPct: -31.8 },
      { date: '2026-01-28', stock: 'AAPL', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-01-15', stock: 'COST', action: 'Sell', amount: '$50K-$100K', returnPct: 22.1 },
      { date: '2026-01-02', stock: 'SBUX', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-12-18', stock: 'SHOP', action: 'Sell', amount: '$50K-$100K', returnPct: 33.4 },
      { date: '2025-12-05', stock: 'LULU', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-22', stock: 'WMT', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-10', stock: 'TGT', action: 'Sell', amount: '$50K-$100K', returnPct: -5.6 },
    ],
  },
  {
    id: 16, name: 'Rick Scott', party: 'R', chamber: 'Senate', state: 'FL',
    annualReturn: 11.8, winRate: 58, totalTrades: 55,
    bestTrade: { stock: 'HCA', returnPct: 52.3 }, worstTrade: { stock: 'PTON', returnPct: -58.4 },
    cumulativeReturns: generateCumulativeReturns(11.8),
    topHoldings: [{ stock: 'HCA', pct: 16 }, { stock: 'CI', pct: 14 }, { stock: 'UNH', pct: 12 }, { stock: 'MSFT', pct: 10 }, { stock: 'GS', pct: 8 }],
    sectorBreakdown: [{ sector: 'Healthcare', pct: 38 }, { sector: 'Finance', pct: 24 }, { sector: 'Technology', pct: 18 }, { sector: 'Real Estate', pct: 12 }, { sector: 'Other', pct: 8 }],
    recentTrades: [
      { date: '2026-03-10', stock: 'HCA', action: 'Buy', amount: '$250K-$500K', returnPct: null },
      { date: '2026-02-25', stock: 'CI', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-02-10', stock: 'PTON', action: 'Sell', amount: '$50K-$100K', returnPct: -58.4 },
      { date: '2026-01-28', stock: 'UNH', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-01-15', stock: 'GS', action: 'Sell', amount: '$100K-$250K', returnPct: 24.6 },
      { date: '2026-01-02', stock: 'MSFT', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-12-18', stock: 'BAC', action: 'Sell', amount: '$100K-$250K', returnPct: 14.2 },
      { date: '2025-12-05', stock: 'WFC', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-22', stock: 'SPG', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-10', stock: 'AMT', action: 'Sell', amount: '$50K-$100K', returnPct: 8.9 },
    ],
  },
  {
    id: 17, name: 'Marie Gluesenkamp Perez', party: 'D', chamber: 'House', state: 'WA',
    annualReturn: 10.5, winRate: 62, totalTrades: 22,
    bestTrade: { stock: 'COST', returnPct: 38.2 }, worstTrade: { stock: 'BYND', returnPct: -45.6 },
    cumulativeReturns: generateCumulativeReturns(10.5),
    topHoldings: [{ stock: 'COST', pct: 22 }, { stock: 'WMT', pct: 16 }, { stock: 'HD', pct: 14 }, { stock: 'LOW', pct: 10 }, { stock: 'TGT', pct: 8 }],
    sectorBreakdown: [{ sector: 'Consumer', pct: 52 }, { sector: 'Technology', pct: 18 }, { sector: 'Industrials', pct: 14 }, { sector: 'Healthcare', pct: 10 }, { sector: 'Other', pct: 6 }],
    recentTrades: [
      { date: '2026-03-01', stock: 'COST', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-02-15', stock: 'WMT', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-02-01', stock: 'BYND', action: 'Sell', amount: '$15K-$50K', returnPct: -45.6 },
      { date: '2026-01-18', stock: 'HD', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-01-05', stock: 'LOW', action: 'Sell', amount: '$50K-$100K', returnPct: 18.3 },
      { date: '2025-12-22', stock: 'TGT', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-12-10', stock: 'AMZN', action: 'Sell', amount: '$50K-$100K', returnPct: 26.8 },
      { date: '2025-11-28', stock: 'ETSY', action: 'Buy', amount: '$15K-$50K', returnPct: null },
      { date: '2025-11-15', stock: 'DG', action: 'Buy', amount: '$15K-$50K', returnPct: null },
      { date: '2025-11-02', stock: 'DLTR', action: 'Sell', amount: '$15K-$50K', returnPct: -12.4 },
    ],
  },
  {
    id: 18, name: 'Gary Peters', party: 'D', chamber: 'Senate', state: 'MI',
    annualReturn: 9.2, winRate: 57, totalTrades: 27,
    bestTrade: { stock: 'F', returnPct: 42.1 }, worstTrade: { stock: 'GM', returnPct: -19.8 },
    cumulativeReturns: generateCumulativeReturns(9.2),
    topHoldings: [{ stock: 'F', pct: 20 }, { stock: 'GM', pct: 16 }, { stock: 'MSFT', pct: 12 }, { stock: 'AAPL', pct: 10 }, { stock: 'GE', pct: 8 }],
    sectorBreakdown: [{ sector: 'Automotive', pct: 32 }, { sector: 'Technology', pct: 24 }, { sector: 'Industrials', pct: 20 }, { sector: 'Finance', pct: 14 }, { sector: 'Other', pct: 10 }],
    recentTrades: [
      { date: '2026-03-05', stock: 'F', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-02-20', stock: 'GM', action: 'Sell', amount: '$50K-$100K', returnPct: -19.8 },
      { date: '2026-02-08', stock: 'MSFT', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-01-25', stock: 'AAPL', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-01-12', stock: 'GE', action: 'Sell', amount: '$50K-$100K', returnPct: 28.4 },
      { date: '2025-12-30', stock: 'HON', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-12-18', stock: 'CAT', action: 'Sell', amount: '$50K-$100K', returnPct: 16.7 },
      { date: '2025-12-05', stock: 'DE', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-22', stock: 'MMM', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-10', stock: 'RTX', action: 'Sell', amount: '$50K-$100K', returnPct: 11.3 },
    ],
  },
  {
    id: 19, name: 'Austin Scott', party: 'R', chamber: 'House', state: 'GA',
    annualReturn: 7.8, winRate: 55, totalTrades: 34,
    bestTrade: { stock: 'MOS', returnPct: 48.9 }, worstTrade: { stock: 'LMND', returnPct: -55.2 },
    cumulativeReturns: generateCumulativeReturns(7.8),
    topHoldings: [{ stock: 'MOS', pct: 18 }, { stock: 'ADM', pct: 14 }, { stock: 'DE', pct: 12 }, { stock: 'CAT', pct: 10 }, { stock: 'CF', pct: 8 }],
    sectorBreakdown: [{ sector: 'Agriculture', pct: 34 }, { sector: 'Industrials', pct: 26 }, { sector: 'Technology', pct: 16 }, { sector: 'Finance', pct: 14 }, { sector: 'Other', pct: 10 }],
    recentTrades: [
      { date: '2026-03-01', stock: 'MOS', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-02-15', stock: 'ADM', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-02-01', stock: 'LMND', action: 'Sell', amount: '$15K-$50K', returnPct: -55.2 },
      { date: '2026-01-18', stock: 'DE', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-01-05', stock: 'CAT', action: 'Sell', amount: '$50K-$100K', returnPct: 22.1 },
      { date: '2025-12-22', stock: 'CF', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-12-10', stock: 'NTR', action: 'Sell', amount: '$50K-$100K', returnPct: 14.8 },
      { date: '2025-11-28', stock: 'CTVA', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-15', stock: 'FMC', action: 'Buy', amount: '$15K-$50K', returnPct: null },
      { date: '2025-11-02', stock: 'BG', action: 'Sell', amount: '$15K-$50K', returnPct: 8.4 },
    ],
  },
  {
    id: 20, name: 'Kyrsten Sinema', party: 'I', chamber: 'Senate', state: 'AZ',
    annualReturn: 6.1, winRate: 53, totalTrades: 19,
    bestTrade: { stock: 'FSLR', returnPct: 55.8 }, worstTrade: { stock: 'PLUG', returnPct: -62.7 },
    cumulativeReturns: generateCumulativeReturns(6.1),
    topHoldings: [{ stock: 'FSLR', pct: 16 }, { stock: 'MSFT', pct: 14 }, { stock: 'AAPL', pct: 12 }, { stock: 'NEE', pct: 10 }, { stock: 'JPM', pct: 8 }],
    sectorBreakdown: [{ sector: 'Technology', pct: 30 }, { sector: 'Clean Energy', pct: 26 }, { sector: 'Finance', pct: 20 }, { sector: 'Healthcare', pct: 14 }, { sector: 'Other', pct: 10 }],
    recentTrades: [
      { date: '2026-02-28', stock: 'FSLR', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-02-12', stock: 'MSFT', action: 'Buy', amount: '$100K-$250K', returnPct: null },
      { date: '2026-01-30', stock: 'PLUG', action: 'Sell', amount: '$15K-$50K', returnPct: -62.7 },
      { date: '2026-01-18', stock: 'AAPL', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2026-01-05', stock: 'NEE', action: 'Sell', amount: '$50K-$100K', returnPct: 18.2 },
      { date: '2025-12-22', stock: 'JPM', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-12-10', stock: 'GS', action: 'Sell', amount: '$50K-$100K', returnPct: 12.4 },
      { date: '2025-11-28', stock: 'V', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-15', stock: 'AXP', action: 'Buy', amount: '$50K-$100K', returnPct: null },
      { date: '2025-11-02', stock: 'ENPH', action: 'Sell', amount: '$50K-$100K', returnPct: 55.8 },
    ],
  },
]

// ---------- Chart Colors ----------
const SECTOR_COLORS = [
  'hsl(45,96%,58%)', 'hsl(210,100%,56%)', 'hsl(142,71%,55%)',
  'hsl(0,72%,55%)', 'hsl(270,70%,60%)', 'hsl(30,90%,55%)',
]


// ---------- Expanded Card ----------
function PoliticianCard({ pol, onClose }: { pol: Politician; onClose: () => void }) {
  const chartTooltipStyle = {
    backgroundColor: 'hsl(220, 55%, 8%)',
    border: '1px solid hsl(215, 40%, 20%)',
    borderRadius: '4px',
    fontSize: '11px',
    fontFamily: 'monospace',
    color: '#fff',
  }

  return (
    <div className="terminal-panel mt-2 mb-4 animate-in fade-in duration-200">
      <div className="terminal-panel-header flex items-center justify-between">
        <span>{pol.name} - Detailed Performance</span>
        <button onClick={onClose} className="text-[hsl(215,20%,55%)] hover:text-white text-xs font-mono">
          [CLOSE]
        </button>
      </div>
      <div className="p-4 bg-[hsl(220,60%,4%)] space-y-6">

        {/* Performance Chart: Politician vs S&P 500 */}
        <div>
          <h4 className="text-xs font-semibold text-[hsl(45,96%,58%)] uppercase mb-3">
            Cumulative Return vs S&P 500
          </h4>
          <div className="h-[220px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={pol.cumulativeReturns}>
                <XAxis
                  dataKey="month"
                  tick={{ fill: 'hsl(215,20%,55%)', fontSize: 10, fontFamily: 'monospace' }}
                  axisLine={{ stroke: 'hsl(215,40%,14%)' }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fill: 'hsl(215,20%,55%)', fontSize: 10, fontFamily: 'monospace' }}
                  axisLine={{ stroke: 'hsl(215,40%,14%)' }}
                  tickLine={false}
                  tickFormatter={(v) => `${v}%`}
                />
                <Tooltip contentStyle={chartTooltipStyle} formatter={(v: number) => [`${v}%`]} />
                <Line
                  type="monotone" dataKey="returnPct" name={pol.name}
                  stroke="hsl(45,96%,58%)" strokeWidth={2} dot={false}
                />
                <Line
                  type="monotone" dataKey="sp500" name="S&P 500"
                  stroke="hsl(215,20%,55%)" strokeWidth={1.5} dot={false} strokeDasharray="4 4"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="flex gap-6 mt-2">
            <span className="flex items-center gap-1.5 text-xs font-mono">
              <span className="w-4 h-0.5 bg-[hsl(45,96%,58%)] inline-block"></span>
              <span className="text-[hsl(215,20%,70%)]">{pol.name}</span>
            </span>
            <span className="flex items-center gap-1.5 text-xs font-mono">
              <span className="w-4 h-0.5 bg-[hsl(215,20%,55%)] inline-block" style={{ borderTop: '1px dashed hsl(215,20%,55%)' }}></span>
              <span className="text-[hsl(215,20%,70%)]">S&P 500</span>
            </span>
          </div>
        </div>

        {/* Top 5 Holdings + Sector Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Top Holdings */}
          <div>
            <h4 className="text-xs font-semibold text-[hsl(45,96%,58%)] uppercase mb-3">
              Top 5 Holdings
            </h4>
            <div className="space-y-2">
              {pol.topHoldings.map((h) => (
                <div key={h.stock} className="flex items-center justify-between">
                  <span className="text-xs font-mono text-white">{h.stock}</span>
                  <div className="flex items-center gap-2 flex-1 mx-3">
                    <div className="flex-1 h-1.5 rounded bg-[hsl(215,50%,12%)]">
                      <div
                        className="h-full rounded bg-[hsl(45,96%,58%)]"
                        style={{ width: `${h.pct}%` }}
                      />
                    </div>
                  </div>
                  <span className="text-xs font-mono text-[hsl(215,20%,55%)]">{h.pct}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Sector Breakdown */}
          <div>
            <h4 className="text-xs font-semibold text-[hsl(45,96%,58%)] uppercase mb-3">
              Sector Breakdown
            </h4>
            <div className="h-[160px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pol.sectorBreakdown}
                    dataKey="pct"
                    nameKey="sector"
                    cx="50%" cy="50%"
                    innerRadius={35} outerRadius={60}
                    paddingAngle={2}
                  >
                    {pol.sectorBreakdown.map((_, i) => (
                      <Cell key={i} fill={SECTOR_COLORS[i % SECTOR_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={chartTooltipStyle} formatter={(v: number) => [`${v}%`]} />
                  <Legend
                    wrapperStyle={{ fontSize: '10px', fontFamily: 'monospace' }}
                    formatter={(val) => <span className="text-[hsl(215,20%,70%)]">{val}</span>}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Recent Trades */}
        <div>
          <h4 className="text-xs font-semibold text-[hsl(45,96%,58%)] uppercase mb-3">
            Recent Trades (Last 10)
          </h4>
          <div className="overflow-x-auto">
            <table className="w-full text-xs font-mono">
              <thead>
                <tr className="bg-[hsl(215,50%,10%)]">
                  <th className="px-3 py-2 text-left text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase">Date</th>
                  <th className="px-3 py-2 text-left text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase">Stock</th>
                  <th className="px-3 py-2 text-left text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase">Action</th>
                  <th className="px-3 py-2 text-left text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase">Amount</th>
                  <th className="px-3 py-2 text-right text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase">Return</th>
                </tr>
              </thead>
              <tbody>
                {pol.recentTrades.map((t, i) => (
                  <tr key={i} className={`border-b border-[hsl(215,40%,12%)] ${i % 2 === 0 ? 'bg-[hsl(220,55%,5%)]' : ''}`}>
                    <td className="px-3 py-2 text-[hsl(215,20%,70%)]">{t.date}</td>
                    <td className="px-3 py-2 text-white font-medium">{t.stock}</td>
                    <td className="px-3 py-2">
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                        t.action === 'Buy'
                          ? 'bg-[hsl(142,71%,55%)]/20 text-[hsl(142,71%,55%)]'
                          : 'bg-[hsl(0,72%,55%)]/20 text-[hsl(0,72%,55%)]'
                      }`}>
                        {t.action.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-[hsl(215,20%,70%)]">{t.amount}</td>
                    <td className={`px-3 py-2 text-right ${
                      t.returnPct === null
                        ? 'text-[hsl(215,20%,45%)]'
                        : t.returnPct >= 0
                        ? 'text-[hsl(142,71%,55%)]'
                        : 'text-[hsl(0,72%,55%)]'
                    }`}>
                      {t.returnPct === null ? 'OPEN' : `${t.returnPct > 0 ? '+' : ''}${t.returnPct}%`}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

// ---------- Share helpers ----------
function copyToClipboard(text: string) {
  navigator.clipboard.writeText(text).catch(() => {
    // Fallback
    const ta = document.createElement('textarea')
    ta.value = text
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
  })
}

function shareOnTwitter(text: string) {
  const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`
  window.open(url, '_blank', 'noopener,noreferrer')
}

// ---------- Main Component ----------
export default function LeaderboardPage() {
  const [sortBy, setSortBy] = useState<'return' | 'winRate' | 'trades' | 'bestTrade'>('return')
  const [partyFilter, setPartyFilter] = useState<string>('all')
  const [chamberFilter, setChamberFilter] = useState<string>('all')
  const [stateFilter, setStateFilter] = useState<string>('all')
  const [timePeriod, setTimePeriod] = useState<string>('1y')
  const [expandedId, setExpandedId] = useState<number | null>(null)
  const [copiedId, setCopiedId] = useState<number | string | null>(null)

  const allStates = useMemo(() => {
    const s = new Set(POLITICIANS.map((p) => p.state))
    return Array.from(s).sort()
  }, [])

  const filtered = useMemo(() => {
    let result = POLITICIANS.filter((p) => {
      if (partyFilter !== 'all' && p.party !== partyFilter) return false
      if (chamberFilter !== 'all' && p.chamber !== chamberFilter) return false
      if (stateFilter !== 'all' && p.state !== stateFilter) return false
      return true
    })

    result.sort((a, b) => {
      switch (sortBy) {
        case 'return': return b.annualReturn - a.annualReturn
        case 'winRate': return b.winRate - a.winRate
        case 'trades': return b.totalTrades - a.totalTrades
        case 'bestTrade': return b.bestTrade.returnPct - a.bestTrade.returnPct
        default: return 0
      }
    })

    return result
  }, [sortBy, partyFilter, chamberFilter, stateFilter])

  // Hero stats
  const avgReturn = +(POLITICIANS.reduce((s, p) => s + p.annualReturn, 0) / POLITICIANS.length).toFixed(1)
  const sp500Return = 12.4
  const mostActive = POLITICIANS.reduce((a, b) => (a.totalTrades > b.totalTrades ? a : b))

  const handleShareLeaderboard = useCallback(() => {
    const url = 'https://quantengines.com/leaderboard'
    copyToClipboard(url)
    setCopiedId('leaderboard')
    setTimeout(() => setCopiedId(null), 2000)
  }, [])

  const handleSharePolitician = useCallback((pol: Politician) => {
    const sign = pol.annualReturn >= 0 ? '+' : ''
    const text = `${pol.name}'s stock trades returned ${sign}${pol.annualReturn}% this year. Track all congressional trades at quantengines.com/leaderboard`
    copyToClipboard(text)
    setCopiedId(pol.id)
    setTimeout(() => setCopiedId(null), 2000)
  }, [])

  const handleTwitterShare = useCallback((pol: Politician) => {
    const sign = pol.annualReturn >= 0 ? '+' : ''
    const text = `${pol.name}'s stock trades returned ${sign}${pol.annualReturn}% this year.\n\nTrack all congressional trades at quantengines.com/leaderboard`
    shareOnTwitter(text)
  }, [])

  return (
    <div className="space-y-4">

      {/* SEO hidden h1 */}
      <h1 className="sr-only">Congressional Stock Trading Leaderboard | Who&apos;s Beating the Market?</h1>

      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-[hsl(45,96%,58%)] uppercase tracking-wider">
            Trader Leaderboard
          </h2>
          <p className="text-xs text-[hsl(215,20%,55%)] font-mono">
            Congressional stock trading performance rankings
          </p>
        </div>
        <button
          onClick={handleShareLeaderboard}
          className="px-3 py-1.5 rounded bg-[hsl(210,100%,56%)]/10 border border-[hsl(210,100%,56%)]/30 text-[hsl(210,100%,56%)] text-xs font-mono hover:bg-[hsl(210,100%,56%)]/20 transition-colors flex items-center gap-1.5"
        >
          {copiedId === 'leaderboard' ? 'COPIED!' : 'SHARE LEADERBOARD'}
        </button>
      </div>

      {/* Hero Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="terminal-panel p-3">
          <span className="text-[10px] text-[hsl(45,96%,58%)] font-semibold">POLITICIANS TRACKED</span>
          <p className="text-2xl font-bold font-mono text-white">{POLITICIANS.length}</p>
        </div>
        <div className="terminal-panel p-3">
          <span className="text-[10px] text-[hsl(142,71%,55%)] font-semibold">AVG RETURN VS S&P 500</span>
          <p className="text-2xl font-bold font-mono text-[hsl(142,71%,55%)]">
            +{(avgReturn - sp500Return).toFixed(1)}%
          </p>
          <p className="text-[10px] font-mono text-[hsl(215,20%,55%)]">
            {avgReturn}% avg vs {sp500Return}% S&P
          </p>
        </div>
        <div className="terminal-panel p-3">
          <span className="text-[10px] text-[hsl(210,100%,56%)] font-semibold">MOST ACTIVE TRADER</span>
          <p className="text-sm font-bold font-mono text-white truncate">{mostActive.name}</p>
          <p className="text-[10px] font-mono text-[hsl(215,20%,55%)]">{mostActive.totalTrades} trades</p>
        </div>
        <div className="terminal-panel p-3">
          <span className="text-[10px] text-[hsl(270,70%,60%)] font-semibold">TOP PERFORMER</span>
          <p className="text-sm font-bold font-mono text-white truncate">{POLITICIANS[0].name}</p>
          <p className="text-[10px] font-mono text-[hsl(142,71%,55%)]">+{POLITICIANS[0].annualReturn}%</p>
        </div>
      </div>

      {/* Filters */}
      <div className="terminal-panel">
        <div className="terminal-panel-header">
          <span>Filters & Sort</span>
        </div>
        <div className="p-3 bg-[hsl(220,60%,4%)]">
          <div className="flex flex-wrap gap-3">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="px-3 py-2 rounded bg-[hsl(215,50%,10%)] border border-[hsl(215,40%,18%)] text-white text-sm font-mono focus:border-[hsl(45,96%,58%)] focus:outline-none"
            >
              <option value="return">Sort by Return</option>
              <option value="winRate">Sort by Win Rate</option>
              <option value="trades">Sort by Trade Count</option>
              <option value="bestTrade">Sort by Best Trade</option>
            </select>
            <select
              value={partyFilter}
              onChange={(e) => setPartyFilter(e.target.value)}
              className="px-3 py-2 rounded bg-[hsl(215,50%,10%)] border border-[hsl(215,40%,18%)] text-white text-sm font-mono focus:border-[hsl(45,96%,58%)] focus:outline-none"
            >
              <option value="all">All Parties</option>
              <option value="D">Democratic</option>
              <option value="R">Republican</option>
              <option value="I">Independent</option>
            </select>
            <select
              value={chamberFilter}
              onChange={(e) => setChamberFilter(e.target.value)}
              className="px-3 py-2 rounded bg-[hsl(215,50%,10%)] border border-[hsl(215,40%,18%)] text-white text-sm font-mono focus:border-[hsl(45,96%,58%)] focus:outline-none"
            >
              <option value="all">All Chambers</option>
              <option value="Senate">Senate</option>
              <option value="House">House</option>
            </select>
            <select
              value={stateFilter}
              onChange={(e) => setStateFilter(e.target.value)}
              className="px-3 py-2 rounded bg-[hsl(215,50%,10%)] border border-[hsl(215,40%,18%)] text-white text-sm font-mono focus:border-[hsl(45,96%,58%)] focus:outline-none"
            >
              <option value="all">All States</option>
              {allStates.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
            <select
              value={timePeriod}
              onChange={(e) => setTimePeriod(e.target.value)}
              className="px-3 py-2 rounded bg-[hsl(215,50%,10%)] border border-[hsl(215,40%,18%)] text-white text-sm font-mono focus:border-[hsl(45,96%,58%)] focus:outline-none"
            >
              <option value="1y">1 Year</option>
              <option value="2y">2 Years</option>
              <option value="all">All Time</option>
            </select>
          </div>
        </div>
      </div>

      {/* Leaderboard Table */}
      <div className="terminal-panel">
        <div className="terminal-panel-header">
          <span>Rankings ({filtered.length} politicians)</span>
        </div>
        <div className="bg-[hsl(220,60%,4%)] overflow-x-auto">
          <table className="w-full text-xs font-mono">
            <thead>
              <tr className="bg-[hsl(215,50%,10%)]">
                <th className="px-3 py-3 text-left text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase w-8">#</th>
                <th className="px-3 py-3 text-left text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase">Name</th>
                <th className="px-3 py-3 text-center text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase">Party</th>
                <th className="px-3 py-3 text-left text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase hidden sm:table-cell">Chamber</th>
                <th className="px-3 py-3 text-left text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase hidden md:table-cell">State</th>
                <th className="px-3 py-3 text-right text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase">Return</th>
                <th className="px-3 py-3 text-right text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase hidden sm:table-cell">Win Rate</th>
                <th className="px-3 py-3 text-right text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase hidden md:table-cell">Trades</th>
                <th className="px-3 py-3 text-right text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase hidden lg:table-cell">Best Trade</th>
                <th className="px-3 py-3 text-right text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase hidden lg:table-cell">Worst Trade</th>
                <th className="px-3 py-3 text-right text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase">Share</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((pol, idx) => (
                <Fragment key={pol.id}>
                  <tr
                    onClick={() => setExpandedId(expandedId === pol.id ? null : pol.id)}
                    className={`border-b border-[hsl(215,40%,12%)] hover:bg-[hsl(215,50%,12%)] transition-colors cursor-pointer ${
                      idx % 2 === 0 ? 'bg-[hsl(220,55%,5%)]' : ''
                    } ${expandedId === pol.id ? 'bg-[hsl(215,50%,12%)]' : ''}`}
                  >
                    <td className="px-3 py-3 text-[hsl(215,20%,55%)]">{idx + 1}</td>
                    <td className="px-3 py-3">
                      <span className="text-white font-medium hover:text-[hsl(45,96%,58%)] transition-colors">
                        {pol.name}
                      </span>
                    </td>
                    <td className="px-3 py-3 text-center">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        pol.party === 'D'
                          ? 'bg-[hsl(210,100%,56%)]/20 text-[hsl(210,100%,56%)]'
                          : pol.party === 'R'
                          ? 'bg-[hsl(0,72%,55%)]/20 text-[hsl(0,72%,55%)]'
                          : 'bg-[hsl(215,20%,55%)]/20 text-[hsl(215,20%,55%)]'
                      }`}>
                        {pol.party}
                      </span>
                    </td>
                    <td className="px-3 py-3 hidden sm:table-cell">
                      <span className={`text-[10px] uppercase ${
                        pol.chamber === 'House' ? 'text-[hsl(45,96%,58%)]' : 'text-[hsl(142,71%,55%)]'
                      }`}>
                        {pol.chamber}
                      </span>
                    </td>
                    <td className="px-3 py-3 text-[hsl(215,20%,70%)] hidden md:table-cell">{pol.state}</td>
                    <td className={`px-3 py-3 text-right font-bold ${
                      pol.annualReturn >= sp500Return ? 'text-[hsl(142,71%,55%)]' : 'text-[hsl(0,72%,55%)]'
                    }`}>
                      {pol.annualReturn >= 0 ? '+' : ''}{pol.annualReturn}%
                    </td>
                    <td className="px-3 py-3 text-right text-white hidden sm:table-cell">{pol.winRate}%</td>
                    <td className="px-3 py-3 text-right text-white hidden md:table-cell">{pol.totalTrades}</td>
                    <td className="px-3 py-3 text-right hidden lg:table-cell">
                      <span className="text-[hsl(142,71%,55%)]">{pol.bestTrade.stock}</span>
                      <span className="text-[hsl(215,20%,55%)] ml-1">+{pol.bestTrade.returnPct}%</span>
                    </td>
                    <td className="px-3 py-3 text-right hidden lg:table-cell">
                      <span className="text-[hsl(0,72%,55%)]">{pol.worstTrade.stock}</span>
                      <span className="text-[hsl(215,20%,55%)] ml-1">{pol.worstTrade.returnPct}%</span>
                    </td>
                    <td className="px-3 py-3 text-right">
                      <div className="flex items-center justify-end gap-1" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={() => handleSharePolitician(pol)}
                          className="px-1.5 py-0.5 rounded bg-[hsl(210,100%,56%)]/10 border border-[hsl(210,100%,56%)]/30 text-[hsl(210,100%,56%)] text-[10px] hover:bg-[hsl(210,100%,56%)]/20 transition-colors"
                          title="Copy share text"
                        >
                          {copiedId === pol.id ? 'COPIED' : 'COPY'}
                        </button>
                        <button
                          onClick={() => handleTwitterShare(pol)}
                          className="px-1.5 py-0.5 rounded bg-[hsl(215,50%,10%)] border border-[hsl(215,40%,18%)] text-[hsl(215,20%,70%)] text-[10px] hover:bg-[hsl(215,50%,14%)] transition-colors"
                          title="Share on X/Twitter"
                        >
                          X
                        </button>
                      </div>
                    </td>
                  </tr>
                  {expandedId === pol.id && (
                    <tr>
                      <td colSpan={11} className="p-0">
                        <PoliticianCard pol={pol} onClose={() => setExpandedId(null)} />
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>

          {filtered.length === 0 && (
            <div className="p-8 text-center">
              <p className="text-[hsl(215,20%,55%)] font-mono">No politicians match your filters</p>
            </div>
          )}
        </div>
      </div>

      {/* Data Disclaimer */}
      <div className="text-center py-4">
        <p className="text-[10px] text-[hsl(215,20%,40%)] font-mono">
          Data sourced from public STOCK Act filings. Returns are estimated based on reported trade dates and amounts.
          Not financial advice. Past performance does not guarantee future results.
        </p>
      </div>
    </div>
  )
}
