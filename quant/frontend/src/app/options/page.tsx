/**
 * Options Calculator Page
 * Black-Scholes pricing, Greeks calculator, and options strategy builder
 */

'use client'

import { useState, useEffect } from 'react'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'

// Black-Scholes calculation
function normalCDF(x: number): number {
  const t = 1 / (1 + 0.2316419 * Math.abs(x))
  const d = 0.3989423 * Math.exp(-x * x / 2)
  const prob = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))))
  return x > 0 ? 1 - prob : prob
}

function blackScholes(
  S: number,
  K: number,
  T: number,
  r: number,
  sigma: number,
  type: 'call' | 'put'
) {
  const d1 = (Math.log(S / K) + (r + sigma * sigma / 2) * T) / (sigma * Math.sqrt(T))
  const d2 = d1 - sigma * Math.sqrt(T)

  let price, delta, gamma, vega, theta, rho

  if (type === 'call') {
    price = S * normalCDF(d1) - K * Math.exp(-r * T) * normalCDF(d2)
    delta = normalCDF(d1)
    rho = K * T * Math.exp(-r * T) * normalCDF(d2) / 100
  } else {
    price = K * Math.exp(-r * T) * normalCDF(-d2) - S * normalCDF(-d1)
    delta = normalCDF(d1) - 1
    rho = -K * T * Math.exp(-r * T) * normalCDF(-d2) / 100
  }

  gamma = Math.exp(-d1 * d1 / 2) / (S * sigma * Math.sqrt(2 * Math.PI * T))
  vega = S * Math.exp(-d1 * d1 / 2) * Math.sqrt(T) / Math.sqrt(2 * Math.PI) / 100
  theta = -(S * Math.exp(-d1 * d1 / 2) * sigma / (2 * Math.sqrt(2 * Math.PI * T))) -
          (type === 'call' ? 1 : -1) * r * K * Math.exp(-r * T) * normalCDF(type === 'call' ? d2 : -d2)
  theta = theta / 365 // Daily theta

  return { price, delta, gamma, vega, theta, rho }
}

export default function OptionsPage() {
  // Option parameters
  const [spotPrice, setSpotPrice] = useState(100)
  const [strikePrice, setStrikePrice] = useState(100)
  const [daysToExpiry, setDaysToExpiry] = useState(30)
  const [volatility, setVolatility] = useState(25)
  const [riskFreeRate, setRiskFreeRate] = useState(5)
  const [optionType, setOptionType] = useState<'call' | 'put'>('call')

  const T = daysToExpiry / 365
  const r = riskFreeRate / 100
  const sigma = volatility / 100

  const greeks = blackScholes(spotPrice, strikePrice, T, r, sigma, optionType)

  // Generate payoff diagram data
  const generatePayoffData = () => {
    const data = []
    const range = spotPrice * 0.5
    for (let price = spotPrice - range; price <= spotPrice + range; price += range / 50) {
      const intrinsic = optionType === 'call'
        ? Math.max(0, price - strikePrice)
        : Math.max(0, strikePrice - price)

      const currentGreeks = blackScholes(price, strikePrice, T, r, sigma, optionType)

      data.push({
        stockPrice: parseFloat(price.toFixed(2)),
        intrinsic,
        theoretical: currentGreeks.price,
        profit: currentGreeks.price - greeks.price,
      })
    }
    return data
  }

  // Generate Greeks surface data
  const generateGreeksSurface = (greek: 'delta' | 'gamma' | 'vega' | 'theta') => {
    const data = []
    for (let days = 1; days <= 90; days += 3) {
      const T_temp = days / 365
      const result = blackScholes(spotPrice, strikePrice, T_temp, r, sigma, optionType)
      data.push({
        days,
        value: result[greek],
      })
    }
    return data
  }

  // Generate volatility smile data
  const generateVolSmile = () => {
    const data = []
    for (let moneyness = 0.7; moneyness <= 1.3; moneyness += 0.02) {
      const K = spotPrice * moneyness
      const impliedVol = volatility + (Math.abs(1 - moneyness) * 50) // Simplified smile
      data.push({
        strike: parseFloat(K.toFixed(2)),
        moneyness: parseFloat((moneyness * 100).toFixed(1)),
        iv: parseFloat(impliedVol.toFixed(2)),
      })
    }
    return data
  }

  const payoffData = generatePayoffData()
  const volSmileData = generateVolSmile()

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold mb-2 gradient-text">Options Calculator</h1>
        <p className="text-muted-foreground text-lg">
          Black-Scholes pricing, Greeks analysis, and options strategy builder
        </p>
      </div>

      {/* Calculator Input */}
      <div className="glass-strong rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Option Parameters</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div>
            <label className="text-xs font-semibold text-muted-foreground mb-2 block">
              SPOT PRICE
            </label>
            <input
              type="number"
              value={spotPrice}
              onChange={(e) => setSpotPrice(Number(e.target.value))}
              className="input-field"
              step={0.01}
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-muted-foreground mb-2 block">
              STRIKE PRICE
            </label>
            <input
              type="number"
              value={strikePrice}
              onChange={(e) => setStrikePrice(Number(e.target.value))}
              className="input-field"
              step={0.01}
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-muted-foreground mb-2 block">
              DAYS TO EXPIRY
            </label>
            <input
              type="number"
              value={daysToExpiry}
              onChange={(e) => setDaysToExpiry(Number(e.target.value))}
              className="input-field"
              min={1}
              max={365}
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-muted-foreground mb-2 block">
              VOLATILITY (%)
            </label>
            <input
              type="number"
              value={volatility}
              onChange={(e) => setVolatility(Number(e.target.value))}
              className="input-field"
              step={0.1}
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-muted-foreground mb-2 block">
              RISK-FREE RATE (%)
            </label>
            <input
              type="number"
              value={riskFreeRate}
              onChange={(e) => setRiskFreeRate(Number(e.target.value))}
              className="input-field"
              step={0.1}
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-muted-foreground mb-2 block">
              OPTION TYPE
            </label>
            <select
              value={optionType}
              onChange={(e) => setOptionType(e.target.value as 'call' | 'put')}
              className="input-field"
            >
              <option value="call">Call</option>
              <option value="put">Put</option>
            </select>
          </div>
        </div>
      </div>

      {/* Calculated Price & Greeks */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="glass-strong rounded-xl p-6">
          <p className="text-xs text-muted-foreground mb-1">THEORETICAL PRICE</p>
          <p className="text-3xl font-bold text-gradient-green">
            ${greeks.price.toFixed(3)}
          </p>
          <p className="text-xs text-green-400 mt-1">
            {((greeks.price / spotPrice) * 100).toFixed(2)}% of spot
          </p>
        </div>

        <div className="glass-strong rounded-xl p-6">
          <p className="text-xs text-muted-foreground mb-1">DELTA (Δ)</p>
          <p className="text-3xl font-bold text-gradient-blue">
            {greeks.delta.toFixed(4)}
          </p>
          <p className="text-xs text-blue-400 mt-1">
            ${(greeks.delta * spotPrice).toFixed(2)} hedge
          </p>
        </div>

        <div className="glass-strong rounded-xl p-6">
          <p className="text-xs text-muted-foreground mb-1">GAMMA (Γ)</p>
          <p className="text-3xl font-bold text-gradient-purple">
            {greeks.gamma.toFixed(4)}
          </p>
          <p className="text-xs text-purple-400 mt-1">
            Delta change/$1
          </p>
        </div>

        <div className="glass-strong rounded-xl p-6">
          <p className="text-xs text-muted-foreground mb-1">VEGA (ν)</p>
          <p className="text-3xl font-bold text-gradient-cyan">
            {greeks.vega.toFixed(4)}
          </p>
          <p className="text-xs text-cyan-400 mt-1">
            Per 1% IV change
          </p>
        </div>

        <div className="glass-strong rounded-xl p-6">
          <p className="text-xs text-muted-foreground mb-1">THETA (Θ)</p>
          <p className="text-3xl font-bold text-gradient-red">
            {greeks.theta.toFixed(4)}
          </p>
          <p className="text-xs text-red-400 mt-1">
            Daily time decay
          </p>
        </div>

        <div className="glass-strong rounded-xl p-6">
          <p className="text-xs text-muted-foreground mb-1">RHO (ρ)</p>
          <p className="text-3xl font-bold text-gradient-orange">
            {greeks.rho.toFixed(4)}
          </p>
          <p className="text-xs text-orange-400 mt-1">
            Per 1% rate change
          </p>
        </div>
      </div>

      {/* Payoff Diagram */}
      <div className="glass-strong rounded-xl p-6">
        <h2 className="text-2xl font-bold mb-4">Payoff Diagram</h2>
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={payoffData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis
              dataKey="stockPrice"
              stroke="#94a3b8"
              tick={{ fontSize: 12 }}
              label={{ value: 'Stock Price at Expiry', position: 'bottom', fill: '#94a3b8' }}
            />
            <YAxis
              stroke="#94a3b8"
              tick={{ fontSize: 12 }}
              label={{
                value: 'Profit / Loss',
                angle: -90,
                position: 'insideLeft',
                fill: '#94a3b8',
              }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #334155',
                borderRadius: '8px',
              }}
              formatter={(value: any) => `$${value.toFixed(2)}`}
            />
            <Legend />
            <ReferenceLine y={0} stroke="#6b7280" strokeDasharray="3 3" />
            <ReferenceLine x={spotPrice} stroke="#3b82f6" strokeDasharray="3 3" label="Current" />
            <ReferenceLine x={strikePrice} stroke="#f59e0b" strokeDasharray="3 3" label="Strike" />
            <Area
              type="monotone"
              dataKey="profit"
              stroke="#10b981"
              fill="#10b981"
              fillOpacity={0.3}
              name="P&L"
            />
            <Line
              type="monotone"
              dataKey="intrinsic"
              stroke="#6b7280"
              strokeWidth={2}
              dot={false}
              strokeDasharray="5 5"
              name="Intrinsic Value"
            />
          </AreaChart>
        </ResponsiveContainer>

        <div className="grid grid-cols-4 gap-4 mt-6">
          <div className="glass rounded-lg p-4">
            <p className="text-xs text-muted-foreground mb-1">Max Profit</p>
            <p className="text-lg font-bold text-green-400">
              {optionType === 'call' ? 'Unlimited' : `$${strikePrice.toFixed(2)}`}
            </p>
          </div>
          <div className="glass rounded-lg p-4">
            <p className="text-xs text-muted-foreground mb-1">Max Loss</p>
            <p className="text-lg font-bold text-red-400">
              ${greeks.price.toFixed(2)}
            </p>
          </div>
          <div className="glass rounded-lg p-4">
            <p className="text-xs text-muted-foreground mb-1">Breakeven</p>
            <p className="text-lg font-bold text-blue-400">
              ${(optionType === 'call'
                ? strikePrice + greeks.price
                : strikePrice - greeks.price).toFixed(2)}
            </p>
          </div>
          <div className="glass rounded-lg p-4">
            <p className="text-xs text-muted-foreground mb-1">Moneyness</p>
            <p className="text-lg font-bold text-purple-400">
              {spotPrice > strikePrice ? 'ITM' : spotPrice < strikePrice ? 'OTM' : 'ATM'}
            </p>
          </div>
        </div>
      </div>

      {/* Greeks Visualization */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Delta Over Time */}
        <div className="glass-strong rounded-xl p-6">
          <h2 className="text-xl font-bold mb-4">Delta Decay</h2>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={generateGreeksSurface('delta')}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis
                dataKey="days"
                stroke="#94a3b8"
                tick={{ fontSize: 12 }}
                label={{ value: 'Days to Expiry', position: 'bottom', fill: '#94a3b8' }}
              />
              <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                }}
              />
              <Area
                type="monotone"
                dataKey="value"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Gamma Over Time */}
        <div className="glass-strong rounded-xl p-6">
          <h2 className="text-xl font-bold mb-4">Gamma Profile</h2>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={generateGreeksSurface('gamma')}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis
                dataKey="days"
                stroke="#94a3b8"
                tick={{ fontSize: 12 }}
                label={{ value: 'Days to Expiry', position: 'bottom', fill: '#94a3b8' }}
              />
              <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                }}
              />
              <Area
                type="monotone"
                dataKey="value"
                stroke="#8b5cf6"
                fill="#8b5cf6"
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Implied Volatility Smile */}
      <div className="glass-strong rounded-xl p-6">
        <h2 className="text-2xl font-bold mb-4">Implied Volatility Smile</h2>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={volSmileData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis
              dataKey="moneyness"
              stroke="#94a3b8"
              tick={{ fontSize: 12 }}
              label={{ value: 'Moneyness (%)', position: 'bottom', fill: '#94a3b8' }}
            />
            <YAxis
              stroke="#94a3b8"
              tick={{ fontSize: 12 }}
              label={{
                value: 'Implied Volatility (%)',
                angle: -90,
                position: 'insideLeft',
                fill: '#94a3b8',
              }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #334155',
                borderRadius: '8px',
              }}
            />
            <ReferenceLine x={100} stroke="#f59e0b" strokeDasharray="3 3" label="ATM" />
            <Line
              type="monotone"
              dataKey="iv"
              stroke="#10b981"
              strokeWidth={3}
              dot={{ fill: '#10b981', r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Strategy Builder */}
      <div className="glass-strong rounded-xl p-6">
        <h2 className="text-2xl font-bold mb-4">Popular Options Strategies</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            {
              name: 'Covered Call',
              description: 'Own stock + Sell call',
              risk: 'Limited upside',
              reward: 'Premium income',
              complexity: 'Beginner',
            },
            {
              name: 'Protective Put',
              description: 'Own stock + Buy put',
              risk: 'Premium paid',
              reward: 'Downside protection',
              complexity: 'Beginner',
            },
            {
              name: 'Bull Call Spread',
              description: 'Buy call + Sell higher call',
              risk: 'Limited to spread',
              reward: 'Limited profit',
              complexity: 'Intermediate',
            },
            {
              name: 'Iron Condor',
              description: 'Sell OTM put/call spreads',
              risk: 'Limited',
              reward: 'Net premium',
              complexity: 'Advanced',
            },
            {
              name: 'Straddle',
              description: 'Buy call + Buy put (same strike)',
              risk: 'Premium paid',
              reward: 'Unlimited both ways',
              complexity: 'Intermediate',
            },
            {
              name: 'Butterfly Spread',
              description: '3 strikes, 4 options',
              risk: 'Limited',
              reward: 'Limited',
              complexity: 'Advanced',
            },
          ].map((strategy) => (
            <div
              key={strategy.name}
              className="border border-border rounded-lg p-4 hover:border-primary/50 transition-all cursor-pointer group"
            >
              <h3 className="font-bold mb-1 group-hover:text-primary transition-colors">
                {strategy.name}
              </h3>
              <p className="text-sm text-muted-foreground mb-3">{strategy.description}</p>
              <div className="space-y-1 text-xs">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Risk:</span>
                  <span className="font-semibold">{strategy.risk}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Reward:</span>
                  <span className="font-semibold">{strategy.reward}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Level:</span>
                  <span
                    className={`font-semibold ${
                      strategy.complexity === 'Beginner'
                        ? 'text-green-400'
                        : strategy.complexity === 'Intermediate'
                        ? 'text-yellow-400'
                        : 'text-red-400'
                    }`}
                  >
                    {strategy.complexity}
                  </span>
                </div>
              </div>
              <button className="w-full mt-3 px-3 py-1.5 rounded-lg bg-primary/10 text-primary text-xs font-semibold hover:bg-primary/20 transition-colors">
                Calculate Strategy →
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Lead Magnet */}
      <div className="glass-strong rounded-xl p-8 text-center">
        <h3 className="text-2xl font-bold mb-2">Master Options Trading</h3>
        <p className="text-muted-foreground mb-6">
          Download: "Complete Guide to Options Greeks & Strategies" + Excel Calculator
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button className="btn-primary">
            📚 Download Free Guide + Calculator
          </button>
          <button className="btn-secondary">
            🎓 Take Free Options Course
          </button>
        </div>
      </div>
    </div>
  )
}
