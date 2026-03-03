'use client'

import Link from 'next/link'
import { CheckCircle, AlertCircle, BarChart3, TrendingUp, Shield } from 'lucide-react'

export default function StrategyValidationPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 py-12">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            Strategy Validation
            <span className="bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent"> Methodology</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            Understanding how we validate and backtest trading strategies with rigorous academic standards and transparent reporting.
          </p>
        </div>

        {/* Backtesting Methodology */}
        <div className="grid lg:grid-cols-2 gap-8 mb-12">
          <div className="bg-slate-800/30 border border-slate-700 rounded-xl p-8">
            <div className="flex items-start gap-4">
              <BarChart3 className="w-8 h-8 text-blue-400 flex-shrink-0 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-white mb-4">Backtesting Framework</h2>
                <ul className="space-y-3 text-gray-300">
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                    <span><strong>Historical Period:</strong> 2010-2024 (14 years of data)</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                    <span><strong>Universe:</strong> S&P 500 constituents with high liquidity</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                    <span><strong>Data Quality:</strong> OHLC (Open, High, Low, Close) daily bars</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                    <span><strong>Commissions:</strong> 0.05%-0.15% (realistic execution costs)</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                    <span><strong>Slippage:</strong> Conservative estimates included</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-slate-800/30 border border-slate-700 rounded-xl p-8">
            <div className="flex items-start gap-4">
              <Shield className="w-8 h-8 text-purple-400 flex-shrink-0 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-white mb-4">Risk Reporting</h2>
                <ul className="space-y-3 text-gray-300">
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                    <span><strong>Maximum Drawdown:</strong> Peak-to-trough loss percentage</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                    <span><strong>Win Rate:</strong> % of profitable trades</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                    <span><strong>Sharpe Ratio:</strong> Risk-adjusted return metric</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                    <span><strong>Avg Return:</strong> Expected annual return (compound)</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                    <span><strong>Full Transparency:</strong> All parameters disclosed</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Metrics Explained */}
        <div className="bg-slate-800/20 border border-slate-700 rounded-xl p-8 mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">Understanding Performance Metrics</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-blue-400 mb-3">Win Rate (%)</h3>
              <p className="text-gray-300 mb-3">
                The percentage of trades that result in a profit. A 60% win rate means 6 out of 10 trades are profitable.
              </p>
              <p className="text-sm text-gray-400">
                Higher win rates reduce psychological stress but don't guarantee profitability if winning trades are smaller than losing trades.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-blue-400 mb-3">Average Return (%)</h3>
              <p className="text-gray-300 mb-3">
                The annualized percentage return generated by the strategy over the backtest period, including all gains and losses.
              </p>
              <p className="text-sm text-gray-400">
                Returns are gross of slippage and commissions already factored into performance. Past performance ≠ future results.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-blue-400 mb-3">Sharpe Ratio</h3>
              <p className="text-gray-300 mb-3">
                Measures risk-adjusted returns. Calculated as (return - risk-free rate) / volatility. Higher is better.
              </p>
              <p className="text-sm text-gray-400">
                A Sharpe ratio above 1.0 is good, above 2.0 is excellent. Compares risk taken per unit of return.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-blue-400 mb-3">Maximum Drawdown (%)</h3>
              <p className="text-gray-300 mb-3">
                The largest peak-to-trough decline during the backtest period. Shows the worst-case scenario you would have experienced.
              </p>
              <p className="text-sm text-gray-400">
                A 20% drawdown means if you invested $10,000, it could have dropped to $8,000 at the worst point.
              </p>
            </div>
          </div>
        </div>

        {/* Academic Basis */}
        <div className="bg-slate-800/30 border border-slate-700 rounded-xl p-8 mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">Academic Foundation</h2>
          <p className="text-gray-300 mb-6">
            All strategies are based on published academic research and are validated using peer-reviewed methodologies:
          </p>
          <ul className="space-y-4 text-gray-300">
            <li className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span>Strategies cited in research papers from top universities (Stanford, MIT, Yale)</span>
            </li>
            <li className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span>Backtesting follows rigorous standards from Pring, Kaufman, and CFA Institute</span>
            </li>
            <li className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span>Each strategy includes reference to original research paper</span>
            </li>
            <li className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span>Forward-testing results available for recent periods (compare to historical backtests)</span>
            </li>
          </ul>
        </div>

        {/* Important Disclaimers */}
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-8 mb-8">
          <div className="flex items-start gap-4">
            <AlertCircle className="w-6 h-6 text-red-400 flex-shrink-0 mt-1" />
            <div>
              <h2 className="text-xl font-bold text-white mb-4">Important Risk Disclosures</h2>
              <ul className="space-y-2 text-gray-300">
                <li className="flex items-start gap-2">
                  <span className="text-red-400 mt-1">•</span>
                  <span><strong>Past performance does not guarantee future results.</strong> Market conditions, correlations, and volatility change over time.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-400 mt-1">•</span>
                  <span><strong>Backtesting can be subject to bias.</strong> Overfitting, data snooping, and survivorship bias can all inflate reported returns.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-400 mt-1">•</span>
                  <span><strong>Real-world execution is harder.</strong> Slippage, market impact, and psychological factors are greater than in simulation.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-400 mt-1">•</span>
                  <span><strong>All strategies can lose money.</strong> Use proper position sizing, risk management, and diversification.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-400 mt-1">•</span>
                  <span><strong>Not financial advice.</strong> Consult a financial advisor before trading with real money.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center">
          <Link href="/strategies">
            <button className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold px-8 py-3 rounded-lg shadow-lg inline-flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              View All Strategies
            </button>
          </Link>
        </div>
      </div>
    </div>
  )
}
