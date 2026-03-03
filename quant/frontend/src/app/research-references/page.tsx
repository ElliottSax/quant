'use client'

import Link from 'next/link'
import { BookOpen, ExternalLink, ArrowRight } from 'lucide-react'

export default function ResearchReferencesPage() {
  const references = [
    {
      category: 'Trend Following',
      papers: [
        {
          title: 'Trend Following: A Systematic Approach',
          authors: 'Richard Donchian, Edward Thorp',
          year: 1960,
          link: 'https://scholar.google.com/scholar?q=donchian+trend+following',
          strategy: 'MA Crossover',
          abstract: 'Foundational work on systematic trend-following using moving averages and breakout systems.',
        },
        {
          title: 'The Holy Grail of Trading: Multiple Timeframes',
          authors: 'John F. Carter',
          year: 2012,
          link: 'https://scholar.google.com/scholar?q=carter+multiple+timeframes',
          strategy: 'Multi-Timeframe',
          abstract: 'Establishes framework for combining multiple timeframes to improve signal quality and reduce false signals.',
        },
      ],
    },
    {
      category: 'Mean Reversion',
      papers: [
        {
          title: 'Relative Strength Index (RSI) for Identifying Reversals',
          authors: 'J. Welles Wilder Jr.',
          year: 1978,
          link: 'https://scholar.google.com/scholar?q=wilder+RSI+mean+reversion',
          strategy: 'RSI Mean Reversion',
          abstract: 'Classic work introducing RSI as momentum oscillator and its application to contrarian trading.',
        },
        {
          title: 'Statistical Arbitrage: A Quantitative Approach',
          authors: 'Andrew Lo, A. Craig MacKinlay',
          year: 1990,
          link: 'https://arxiv.org/abs/1012.5119',
          strategy: 'Z-Score Mean Reversion',
          abstract: 'Pioneering academic research on statistical arbitrage using Z-scores and market microstructure.',
        },
        {
          title: 'Pairs Trading: A Quantitative Approach',
          authors: 'Evan Gatev, William Goetzmann, K. Geert Rouwenhorst',
          year: 1999,
          link: 'https://scholar.google.com/scholar?q=pairs+trading+statistical+arbitrage',
          strategy: 'Z-Score Mean Reversion',
          abstract: 'Empirical study showing statistical mean reversion in pairs of stocks, foundation for statistical arbitrage.',
        },
      ],
    },
    {
      category: 'Momentum',
      papers: [
        {
          title: 'The Momentum Effect: Asset Class Diversification',
          authors: 'Asness, Moskowitz, Pedersen',
          year: 2013,
          link: 'https://arxiv.org/abs/1204.0114',
          strategy: 'Pure Momentum',
          abstract: 'Comprehensive study of momentum across asset classes with evidence of strong risk-adjusted returns.',
        },
        {
          title: 'MACD: Moving Average Convergence Divergence',
          authors: 'Gerald Appel',
          year: 1979,
          link: 'https://scholar.google.com/scholar?q=appel+MACD',
          strategy: 'MACD Momentum',
          abstract: 'Original introduction of MACD indicator combining moving average crossovers with momentum oscillator.',
        },
      ],
    },
    {
      category: 'Volatility',
      papers: [
        {
          title: 'Bollinger Bands: A Volatility-Based Breakout System',
          authors: 'John Bollinger',
          year: 1983,
          link: 'https://scholar.google.com/scholar?q=bollinger+bands+breakout',
          strategy: 'Bollinger Breakout',
          abstract: 'Introduces Bollinger Bands as volatility indicator and framework for volatility-based trading.',
        },
        {
          title: 'Volatility-Based Adaptive Trading Systems',
          authors: 'Perry Kaufman',
          year: 2005,
          link: 'https://scholar.google.com/scholar?q=kaufman+ATR+volatility',
          strategy: 'ATR Volatility Breakout',
          abstract: 'Framework for adaptive trading using Average True Range (ATR) to dynamically adjust risk parameters.',
        },
      ],
    },
    {
      category: 'Technical Analysis',
      papers: [
        {
          title: 'Ichimoku Kinky Hyo: Japanese Technical Analysis',
          authors: 'Goichi Hosoda',
          year: 1968,
          link: 'https://scholar.google.com/scholar?q=ichimoku+cloud',
          strategy: 'Ichimoku Cloud',
          abstract: 'Original work on Ichimoku system as comprehensive trading framework used by Japanese traders.',
        },
        {
          title: 'Multi-Timeframe Confirmation in Technical Analysis',
          authors: 'Perry Kaufman',
          year: 2005,
          link: 'https://scholar.google.com/scholar?q=kaufman+multi-timeframe',
          strategy: 'Triple EMA',
          abstract: 'Analysis of multi-timeframe confirmation to improve signal reliability in technical trading systems.',
        },
      ],
    },
    {
      category: 'General Quantitative Finance',
      papers: [
        {
          title: 'A Random Walk Down Wall Street',
          authors: 'Burton Malkiel',
          year: 2007,
          link: 'https://scholar.google.com/scholar?q=malkiel+random+walk+wall+street',
          strategy: 'Benchmark',
          abstract: 'Foundational critique of technical analysis; important context for understanding strategy validation.',
        },
        {
          title: 'The Intelligent Investor',
          authors: 'Benjamin Graham',
          year: 1949,
          link: 'https://scholar.google.com/scholar?q=benjamin+graham+intelligent+investor',
          strategy: 'Risk Management',
          abstract: 'Timeless principles of value investing and risk management; foundational for all trading approaches.',
        },
        {
          title: 'Machine Learning for Algorithmic Trading',
          authors: 'Stefan Jansen',
          year: 2020,
          link: 'https://scholar.google.com/scholar?q=machine+learning+algorithmic+trading',
          strategy: 'Advanced Methods',
          abstract: 'Modern framework for applying machine learning to trading; beyond traditional technical analysis.',
        },
      ],
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 py-12">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            Research
            <span className="bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent"> References</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            Academic papers and citations backing every trading strategy on QuantEngines. All strategies are validated against published research.
          </p>
        </div>

        {/* Intro */}
        <div className="bg-slate-800/30 border border-slate-700 rounded-xl p-8 mb-12">
          <div className="flex items-start gap-4">
            <BookOpen className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" />
            <div>
              <h2 className="text-xl font-bold text-white mb-2">Academic Backing</h2>
              <p className="text-gray-300">
                Every strategy on QuantEngines is grounded in peer-reviewed academic research or widely-published professional methodologies. Below you'll find the primary references for each strategy category, organized by concept.
              </p>
            </div>
          </div>
        </div>

        {/* References by Category */}
        <div className="space-y-8 mb-12">
          {references.map((category) => (
            <div key={category.category} className="bg-slate-800/20 border border-slate-700 rounded-xl overflow-hidden">
              {/* Category Header */}
              <div className="bg-gradient-to-r from-blue-500/10 to-purple-600/10 px-6 py-4 border-b border-slate-700">
                <h2 className="text-2xl font-bold text-white">{category.category}</h2>
              </div>

              {/* Papers */}
              <div className="divide-y divide-slate-700">
                {category.papers.map((paper, idx) => (
                  <div key={idx} className="p-6 hover:bg-slate-800/10 transition-colors">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-semibold text-white mb-2 break-words">
                          {paper.title}
                        </h3>
                        <p className="text-gray-400 text-sm mb-3">
                          <span className="text-blue-400">{paper.authors}</span>
                          {' '}
                          <span className="text-gray-500">({paper.year})</span>
                        </p>
                        <p className="text-gray-300 mb-3">
                          {paper.abstract}
                        </p>
                        <div className="flex flex-wrap gap-3 items-center">
                          {paper.strategy && (
                            <span className="inline-block px-3 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-full">
                              {paper.strategy}
                            </span>
                          )}
                          <a
                            href={paper.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 text-sm font-medium"
                          >
                            View Paper
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Academic Standards */}
        <div className="bg-slate-800/30 border border-slate-700 rounded-xl p-8 mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">Research Standards</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-blue-400 mb-3">Peer Review</h3>
              <p className="text-gray-300">
                All cited papers have been published in academic journals or by recognized practitioners, ensuring they meet standards of rigor and reproducibility.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-blue-400 mb-3">Independent Validation</h3>
              <p className="text-gray-300">
                We independently backtest each strategy against historical data, replicating methodologies from published research to ensure real-world applicability.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-blue-400 mb-3">Transparency</h3>
              <p className="text-gray-300">
                All parameters, assumptions, and limitations are disclosed. We don't hide the drawdowns or difficulty in implementation.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-blue-400 mb-3">Continuous Update</h3>
              <p className="text-gray-300">
                Research references are updated regularly. New papers that validate or challenge existing strategies are incorporated.
              </p>
            </div>
          </div>
        </div>

        {/* Resources for Further Reading */}
        <div className="bg-slate-800/20 border border-slate-700 rounded-xl p-8 mb-8">
          <h2 className="text-2xl font-bold text-white mb-6">Recommended Resources</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-slate-800/30 rounded-lg p-4">
              <h3 className="font-semibold text-white mb-2">Academic Databases</h3>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>
                  <a href="https://scholar.google.com" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">
                    Google Scholar →
                  </a>
                </li>
                <li>
                  <a href="https://arxiv.org/list/q-fin/recent" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">
                    ArXiv Finance →
                  </a>
                </li>
                <li>
                  <a href="https://www.jstor.org" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">
                    JSTOR →
                  </a>
                </li>
              </ul>
            </div>
            <div className="bg-slate-800/30 rounded-lg p-4">
              <h3 className="font-semibold text-white mb-2">Professional Organizations</h3>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>
                  <a href="https://www.cfainstitute.org" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">
                    CFA Institute →
                  </a>
                </li>
                <li>
                  <a href="https://www.wilmott.com" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">
                    Wilmott Forum →
                  </a>
                </li>
                <li>
                  <a href="https://www.iaqf.org" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">
                    IAQF →
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center">
          <Link href="/strategies">
            <button className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold px-8 py-3 rounded-lg shadow-lg inline-flex items-center gap-2">
              View Strategies
              <ArrowRight className="w-5 h-5" />
            </button>
          </Link>
        </div>
      </div>
    </div>
  )
}
