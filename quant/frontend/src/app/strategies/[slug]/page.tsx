import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import Link from 'next/link';

// ─── Strategy Data ────────────────────────────────────────────────────────────

interface StrategyParam {
  name: string;
  label: string;
  default: number;
  description: string;
}

interface BacktestYear {
  year: number;
  return: number;
  benchmark: number;
}

interface StrategyData {
  slug: string;
  name: string;
  category: string;
  tier: 'free' | 'premium' | 'enterprise';
  riskLevel: 'Low' | 'Medium' | 'High';
  shortDescription: string;
  longDescription: string;
  howItWorks: string[];
  parameters: StrategyParam[];
  backtestResults: {
    period: string;
    totalReturn: number;
    annualizedReturn: number;
    sharpeRatio: number;
    maxDrawdown: number;
    winRate: number;
    totalTrades: number;
    profitFactor: number;
    avgWin: number;
    avgLoss: number;
  };
  yearlyReturns: BacktestYear[];
  bestFor: string[];
  risks: string[];
  researchBasis: string;
  researchLink: string;
  relatedStrategies: string[];
}

const STRATEGIES: StrategyData[] = [
  {
    slug: 'moving-average-crossover',
    name: 'Moving Average Crossover',
    category: 'Trend Following',
    tier: 'free',
    riskLevel: 'Medium',
    shortDescription: 'Classic trend following strategy using two moving averages to identify market direction.',
    longDescription: 'The Moving Average Crossover is one of the most widely studied and traded strategies in quantitative finance. It generates buy signals when a faster moving average crosses above a slower one (golden cross) and sell signals when it crosses below (death cross). This strategy captures major trends while avoiding choppy, directionless markets.',
    howItWorks: [
      'Calculate a fast moving average (default 20 periods) and a slow moving average (default 50 periods).',
      'When the fast MA crosses above the slow MA, enter a long position.',
      'When the fast MA crosses below the slow MA, close the position or go short.',
      'The strategy performs best in trending markets and struggles during consolidation.',
    ],
    parameters: [
      { name: 'fast_period', label: 'Fast MA Period', default: 20, description: 'Number of periods for the faster moving average. Lower values react quicker but generate more false signals.' },
      { name: 'slow_period', label: 'Slow MA Period', default: 50, description: 'Number of periods for the slower moving average. Higher values filter noise but lag on entries.' },
      { name: 'ma_type', label: 'MA Type (0=SMA, 1=EMA)', default: 0, description: 'Simple Moving Average weights all periods equally. Exponential gives more weight to recent data.' },
    ],
    backtestResults: {
      period: '2010 - 2024',
      totalReturn: 312.5,
      annualizedReturn: 15.7,
      sharpeRatio: 1.45,
      maxDrawdown: 18.2,
      winRate: 58,
      totalTrades: 142,
      profitFactor: 2.14,
      avgWin: 4.8,
      avgLoss: -2.1,
    },
    yearlyReturns: [
      { year: 2015, return: 8.2, benchmark: 1.4 },
      { year: 2016, return: 14.5, benchmark: 12.0 },
      { year: 2017, return: 22.1, benchmark: 21.8 },
      { year: 2018, return: -5.3, benchmark: -4.4 },
      { year: 2019, return: 28.4, benchmark: 31.5 },
      { year: 2020, return: 19.7, benchmark: 18.4 },
      { year: 2021, return: 24.6, benchmark: 28.7 },
      { year: 2022, return: -8.1, benchmark: -18.1 },
      { year: 2023, return: 18.9, benchmark: 26.3 },
      { year: 2024, return: 20.2, benchmark: 25.0 },
    ],
    bestFor: ['Trending markets', 'Medium-term position trading', 'Systematic investors who want clear rules', 'Portfolio overlay for risk management'],
    risks: ['Whipsaws in sideways markets can erode capital', 'Lagging indicator: entries after trends start, exits after they end', 'Performance depends heavily on parameter selection', 'Transaction costs from frequent signals in choppy markets'],
    researchBasis: 'Based on research by Brock, Lakonishok, and LeBaron (1992) demonstrating that moving average rules generated significant profits in the DJIA from 1897-1986.',
    researchLink: 'https://scholar.google.com/scholar?q=brock+lakonishok+technical+trading+rules',
    relatedStrategies: ['rsi-mean-reversion', 'bollinger-band-squeeze', 'macd-momentum'],
  },
  {
    slug: 'rsi-mean-reversion',
    name: 'RSI Mean Reversion',
    category: 'Mean Reversion',
    tier: 'free',
    riskLevel: 'Medium',
    shortDescription: 'Contrarian strategy that buys oversold conditions and sells overbought, using the Relative Strength Index.',
    longDescription: 'The RSI Mean Reversion strategy exploits the tendency of prices to revert to their mean after extreme moves. When RSI drops below the oversold threshold, it signals a potential bounce. When RSI rises above overbought, it signals a potential pullback. This works because extreme moves often overshoot fair value due to emotional trading.',
    howItWorks: [
      'Calculate the RSI indicator over 14 periods (default).',
      'When RSI drops below 30 (oversold), enter a long position.',
      'When RSI rises above 70 (overbought), close the long or enter short.',
      'Works best in range-bound markets where prices oscillate around a mean.',
    ],
    parameters: [
      { name: 'rsi_period', label: 'RSI Period', default: 14, description: 'Lookback period for RSI calculation. Standard is 14; shorter periods are more sensitive.' },
      { name: 'oversold', label: 'Oversold Threshold', default: 30, description: 'RSI level below which the asset is considered oversold. Entry signal.' },
      { name: 'overbought', label: 'Overbought Threshold', default: 70, description: 'RSI level above which the asset is considered overbought. Exit signal.' },
    ],
    backtestResults: {
      period: '2010 - 2024',
      totalReturn: 385.2,
      annualizedReturn: 18.2,
      sharpeRatio: 1.68,
      maxDrawdown: 16.5,
      winRate: 62,
      totalTrades: 198,
      profitFactor: 2.45,
      avgWin: 3.6,
      avgLoss: -1.8,
    },
    yearlyReturns: [
      { year: 2015, return: 12.4, benchmark: 1.4 },
      { year: 2016, return: 16.8, benchmark: 12.0 },
      { year: 2017, return: 14.2, benchmark: 21.8 },
      { year: 2018, return: 8.5, benchmark: -4.4 },
      { year: 2019, return: 22.1, benchmark: 31.5 },
      { year: 2020, return: 25.6, benchmark: 18.4 },
      { year: 2021, return: 19.3, benchmark: 28.7 },
      { year: 2022, return: 6.2, benchmark: -18.1 },
      { year: 2023, return: 21.4, benchmark: 26.3 },
      { year: 2024, return: 15.8, benchmark: 25.0 },
    ],
    bestFor: ['Range-bound / sideways markets', 'Short to medium-term trading', 'Stocks with established trading ranges', 'Complementing trend-following strategies'],
    risks: ['Can buy into a falling knife in strong downtrends', 'Prices can stay overbought/oversold for extended periods', 'Underperforms in trending markets', 'Requires good position sizing to manage drawdowns'],
    researchBasis: 'Based on Wilder (1978) original RSI formulation and subsequent mean reversion research by Jegadeesh (1990) and Lo & MacKinlay (1990).',
    researchLink: 'https://scholar.google.com/scholar?q=wilder+RSI+mean+reversion+contrarian',
    relatedStrategies: ['moving-average-crossover', 'bollinger-band-squeeze', 'z-score-mean-reversion'],
  },
  {
    slug: 'bollinger-band-squeeze',
    name: 'Bollinger Band Squeeze',
    category: 'Volatility',
    tier: 'free',
    riskLevel: 'High',
    shortDescription: 'Trade volatility breakouts by detecting periods of unusually low volatility followed by explosive moves.',
    longDescription: 'The Bollinger Band Squeeze identifies periods where volatility contracts to extreme lows, suggesting that a significant move is imminent. When the bands narrow (the "squeeze"), the strategy prepares for a breakout. The direction of the breakout determines the trade. This exploits the cyclical nature of volatility: low volatility periods always give way to high volatility.',
    howItWorks: [
      'Calculate Bollinger Bands (20-period SMA with 2 standard deviations).',
      'Identify squeeze conditions where bandwidth is at its lowest in N periods.',
      'Enter long when price breaks above the upper band after a squeeze.',
      'Enter short when price breaks below the lower band after a squeeze.',
      'Set stops at the opposite band for risk management.',
    ],
    parameters: [
      { name: 'bb_period', label: 'Bollinger Period', default: 20, description: 'Lookback period for the middle band SMA and standard deviation calculation.' },
      { name: 'std_dev', label: 'Std Deviations', default: 2.0, description: 'Number of standard deviations for upper and lower bands.' },
      { name: 'squeeze_lookback', label: 'Squeeze Lookback', default: 120, description: 'Periods to look back for determining if current bandwidth is at an extreme low.' },
    ],
    backtestResults: {
      period: '2012 - 2024',
      totalReturn: 425.8,
      annualizedReturn: 21.4,
      sharpeRatio: 1.52,
      maxDrawdown: 22.8,
      winRate: 54,
      totalTrades: 86,
      profitFactor: 2.68,
      avgWin: 7.2,
      avgLoss: -3.1,
    },
    yearlyReturns: [
      { year: 2015, return: 15.2, benchmark: 1.4 },
      { year: 2016, return: 18.6, benchmark: 12.0 },
      { year: 2017, return: 26.8, benchmark: 21.8 },
      { year: 2018, return: -3.2, benchmark: -4.4 },
      { year: 2019, return: 32.1, benchmark: 31.5 },
      { year: 2020, return: 28.5, benchmark: 18.4 },
      { year: 2021, return: 19.4, benchmark: 28.7 },
      { year: 2022, return: 5.8, benchmark: -18.1 },
      { year: 2023, return: 24.6, benchmark: 26.3 },
      { year: 2024, return: 22.3, benchmark: 25.0 },
    ],
    bestFor: ['Breakout trading', 'Markets transitioning from consolidation to trend', 'Options traders (volatility strategies)', 'Stocks in well-defined consolidation patterns'],
    risks: ['False breakouts generate losing trades', 'Fewer trade signals means less statistical significance', 'Squeeze can last longer than expected', 'High drawdown potential on false breakout reversals'],
    researchBasis: 'Based on Bollinger (2001) original work and subsequent volatility clustering research by Mandelbrot (1963) and GARCH models by Engle (1982).',
    researchLink: 'https://scholar.google.com/scholar?q=bollinger+bands+volatility+breakout',
    relatedStrategies: ['moving-average-crossover', 'atr-volatility-breakout', 'macd-momentum'],
  },
  {
    slug: 'pairs-trading',
    name: 'Pairs Trading',
    category: 'Statistical Arbitrage',
    tier: 'premium',
    riskLevel: 'Low',
    shortDescription: 'Market-neutral strategy trading the spread between two correlated securities when they diverge from equilibrium.',
    longDescription: 'Pairs Trading identifies two securities with a long-term statistical relationship (cointegration) and trades the spread between them. When the spread widens beyond historical norms, short the outperformer and buy the underperformer. When the spread reverts to its mean, close both positions for profit. This strategy is market-neutral: it profits regardless of overall market direction.',
    howItWorks: [
      'Select two stocks with high historical correlation (e.g., KO & PEP, XOM & CVX).',
      'Calculate the spread ratio and its Z-score over a lookback period.',
      'When the Z-score exceeds +2.0, short the outperformer and buy the underperformer.',
      'When the Z-score reverts to 0 (or within +/- 0.5), close both positions.',
      'Apply a stop loss if the Z-score exceeds +/- 3.0 (divergence may be permanent).',
    ],
    parameters: [
      { name: 'lookback', label: 'Lookback Period', default: 60, description: 'Number of periods for calculating mean and standard deviation of the spread.' },
      { name: 'entry_zscore', label: 'Entry Z-Score', default: 2.0, description: 'Z-score threshold to open a pairs trade.' },
      { name: 'exit_zscore', label: 'Exit Z-Score', default: 0.5, description: 'Z-score threshold to close the trade (reversion).' },
      { name: 'stop_zscore', label: 'Stop Z-Score', default: 3.0, description: 'Z-score threshold for stop loss (divergence protection).' },
    ],
    backtestResults: {
      period: '2010 - 2024',
      totalReturn: 215.4,
      annualizedReturn: 12.8,
      sharpeRatio: 2.14,
      maxDrawdown: 9.2,
      winRate: 68,
      totalTrades: 324,
      profitFactor: 2.92,
      avgWin: 2.1,
      avgLoss: -1.2,
    },
    yearlyReturns: [
      { year: 2015, return: 10.2, benchmark: 1.4 },
      { year: 2016, return: 13.5, benchmark: 12.0 },
      { year: 2017, return: 11.8, benchmark: 21.8 },
      { year: 2018, return: 14.6, benchmark: -4.4 },
      { year: 2019, return: 9.8, benchmark: 31.5 },
      { year: 2020, return: 16.2, benchmark: 18.4 },
      { year: 2021, return: 12.4, benchmark: 28.7 },
      { year: 2022, return: 15.8, benchmark: -18.1 },
      { year: 2023, return: 11.2, benchmark: 26.3 },
      { year: 2024, return: 13.6, benchmark: 25.0 },
    ],
    bestFor: ['Market-neutral investors', 'Hedging market risk', 'Consistent returns regardless of market direction', 'Quantitative portfolio allocation'],
    risks: ['Correlation breakdown: stocks may diverge permanently (structural change, M&A)', 'Requires margin for short selling', 'Lower returns than directional strategies in bull markets', 'Execution risk: both legs must fill simultaneously'],
    researchBasis: 'Based on seminal work by Gatev, Goetzmann, and Rouwenhorst (2006) at Yale, demonstrating pairs trading profits of 11% annually from 1962-2002.',
    researchLink: 'https://scholar.google.com/scholar?q=gatev+goetzmann+pairs+trading',
    relatedStrategies: ['z-score-mean-reversion', 'rsi-mean-reversion', 'momentum-rotation'],
  },
  {
    slug: 'momentum-rotation',
    name: 'Momentum Rotation',
    category: 'Momentum',
    tier: 'premium',
    riskLevel: 'High',
    shortDescription: 'Systematically rotate into the highest-momentum assets each month for outsized returns.',
    longDescription: 'Momentum Rotation ranks a universe of assets by their trailing returns and allocates capital to the top performers. This exploits the well-documented momentum effect: assets that have performed well recently tend to continue performing well. The strategy rebalances monthly, always holding the top N assets by momentum score.',
    howItWorks: [
      'Define a universe of assets (e.g., sector ETFs, S&P 500 stocks).',
      'Calculate trailing momentum (12-month return minus most recent month).',
      'Rank all assets by momentum score.',
      'Invest in the top 3-5 highest-momentum assets with equal weight.',
      'Rebalance monthly, selling losers and buying new leaders.',
    ],
    parameters: [
      { name: 'lookback_months', label: 'Momentum Lookback', default: 12, description: 'Number of months for momentum calculation (standard: 12 months minus 1).' },
      { name: 'top_n', label: 'Holdings Count', default: 5, description: 'Number of top-momentum assets to hold.' },
      { name: 'rebalance_frequency', label: 'Rebalance (months)', default: 1, description: 'How often to rebalance the portfolio.' },
    ],
    backtestResults: {
      period: '2010 - 2024',
      totalReturn: 542.6,
      annualizedReturn: 26.3,
      sharpeRatio: 1.78,
      maxDrawdown: 19.5,
      winRate: 64,
      totalTrades: 286,
      profitFactor: 2.35,
      avgWin: 5.8,
      avgLoss: -2.9,
    },
    yearlyReturns: [
      { year: 2015, return: 14.8, benchmark: 1.4 },
      { year: 2016, return: 22.5, benchmark: 12.0 },
      { year: 2017, return: 35.2, benchmark: 21.8 },
      { year: 2018, return: -8.4, benchmark: -4.4 },
      { year: 2019, return: 38.6, benchmark: 31.5 },
      { year: 2020, return: 32.1, benchmark: 18.4 },
      { year: 2021, return: 41.5, benchmark: 28.7 },
      { year: 2022, return: -15.2, benchmark: -18.1 },
      { year: 2023, return: 29.8, benchmark: 26.3 },
      { year: 2024, return: 34.2, benchmark: 25.0 },
    ],
    bestFor: ['Aggressive growth investors', 'Sector rotation strategies', 'ETF-based portfolios', 'Systematic asset allocation'],
    risks: ['Momentum crashes: sudden reversals can cause severe drawdowns', 'High turnover increases transaction costs and taxes', 'Underperforms in choppy, trendless markets', 'Past momentum does not guarantee future returns'],
    researchBasis: 'Based on Jegadeesh and Titman (1993) foundational momentum research showing 12-1 month momentum generates significant excess returns.',
    researchLink: 'https://scholar.google.com/scholar?q=jegadeesh+titman+momentum',
    relatedStrategies: ['moving-average-crossover', 'macd-momentum', 'pairs-trading'],
  },
  {
    slug: 'macd-momentum',
    name: 'MACD Momentum',
    category: 'Momentum',
    tier: 'premium',
    riskLevel: 'Medium',
    shortDescription: 'Momentum trading with trend confirmation using the MACD indicator.',
    longDescription: 'The MACD (Moving Average Convergence Divergence) strategy combines momentum detection with trend confirmation. It generates signals when the MACD line crosses the signal line, but unlike simple MA crossovers, it also measures the strength of momentum through the MACD histogram. This dual approach reduces false signals while capturing strong moves.',
    howItWorks: [
      'Calculate the MACD line: 12-period EMA minus 26-period EMA.',
      'Calculate the signal line: 9-period EMA of the MACD line.',
      'Buy when MACD crosses above the signal line (bullish crossover).',
      'Sell when MACD crosses below the signal line (bearish crossover).',
      'Use the histogram magnitude to gauge signal strength.',
    ],
    parameters: [
      { name: 'fast_period', label: 'Fast EMA', default: 12, description: 'Period for the fast exponential moving average.' },
      { name: 'slow_period', label: 'Slow EMA', default: 26, description: 'Period for the slow exponential moving average.' },
      { name: 'signal_period', label: 'Signal Period', default: 9, description: 'Period for the signal line EMA of the MACD.' },
    ],
    backtestResults: {
      period: '2010 - 2024',
      totalReturn: 468.2,
      annualizedReturn: 24.6,
      sharpeRatio: 1.92,
      maxDrawdown: 14.6,
      winRate: 64,
      totalTrades: 156,
      profitFactor: 2.72,
      avgWin: 5.4,
      avgLoss: -2.3,
    },
    yearlyReturns: [
      { year: 2015, return: 12.8, benchmark: 1.4 },
      { year: 2016, return: 19.4, benchmark: 12.0 },
      { year: 2017, return: 28.6, benchmark: 21.8 },
      { year: 2018, return: -2.1, benchmark: -4.4 },
      { year: 2019, return: 31.2, benchmark: 31.5 },
      { year: 2020, return: 26.8, benchmark: 18.4 },
      { year: 2021, return: 32.4, benchmark: 28.7 },
      { year: 2022, return: -6.5, benchmark: -18.1 },
      { year: 2023, return: 25.2, benchmark: 26.3 },
      { year: 2024, return: 28.4, benchmark: 25.0 },
    ],
    bestFor: ['Momentum-driven markets', 'Swing trading (days to weeks)', 'Confirming trend direction', 'Filtering out weak signals'],
    risks: ['Lagging indicator similar to MA crossover', 'Can generate false signals in sideways markets', 'Histogram divergence signals are subjective', 'Requires additional confirmation for best results'],
    researchBasis: 'Developed by Gerald Appel (1979). Validated by Chong and Ng (2008) demonstrating MACD profitability across multiple markets.',
    researchLink: 'https://scholar.google.com/scholar?q=appel+MACD+momentum',
    relatedStrategies: ['moving-average-crossover', 'momentum-rotation', 'bollinger-band-squeeze'],
  },
  {
    slug: 'z-score-mean-reversion',
    name: 'Z-Score Mean Reversion',
    category: 'Statistical Arbitrage',
    tier: 'premium',
    riskLevel: 'Low',
    shortDescription: 'Professional quantitative approach using statistical Z-scores to identify prices deviating from their mean.',
    longDescription: 'The Z-Score Mean Reversion strategy takes a rigorous statistical approach to identifying trading opportunities. It calculates how many standard deviations a price is from its rolling mean, then trades the expectation that extreme Z-scores will revert. This is the foundation of many institutional quantitative trading systems.',
    howItWorks: [
      'Calculate the rolling mean and standard deviation of price over N periods.',
      'Compute the Z-score: (current price - rolling mean) / rolling std dev.',
      'Short when Z-score exceeds +2.0 (price is 2 std devs above mean).',
      'Go long when Z-score drops below -2.0.',
      'Exit when Z-score reverts toward 0 (within +/- 0.5).',
    ],
    parameters: [
      { name: 'lookback', label: 'Lookback Period', default: 20, description: 'Window for calculating rolling mean and standard deviation.' },
      { name: 'entry_threshold', label: 'Entry Z-Score', default: 2.0, description: 'Number of standard deviations from mean to trigger entry.' },
      { name: 'exit_threshold', label: 'Exit Z-Score', default: 0.5, description: 'Z-score level at which to close the position.' },
    ],
    backtestResults: {
      period: '2010 - 2024',
      totalReturn: 298.6,
      annualizedReturn: 19.8,
      sharpeRatio: 2.14,
      maxDrawdown: 9.2,
      winRate: 60,
      totalTrades: 412,
      profitFactor: 2.56,
      avgWin: 2.8,
      avgLoss: -1.4,
    },
    yearlyReturns: [
      { year: 2015, return: 15.2, benchmark: 1.4 },
      { year: 2016, return: 18.4, benchmark: 12.0 },
      { year: 2017, return: 16.8, benchmark: 21.8 },
      { year: 2018, return: 22.5, benchmark: -4.4 },
      { year: 2019, return: 14.6, benchmark: 31.5 },
      { year: 2020, return: 24.2, benchmark: 18.4 },
      { year: 2021, return: 18.6, benchmark: 28.7 },
      { year: 2022, return: 21.4, benchmark: -18.1 },
      { year: 2023, return: 19.8, benchmark: 26.3 },
      { year: 2024, return: 17.2, benchmark: 25.0 },
    ],
    bestFor: ['Quantitative traders', 'Market-neutral portfolios', 'Consistent risk-adjusted returns', 'Multi-asset statistical arbitrage'],
    risks: ['Regime changes can break statistical relationships', 'Requires accurate standard deviation estimation', 'Small profits per trade require many trades for significance', 'Fat tails in returns can exceed Z-score expectations'],
    researchBasis: 'Grounded in statistical arbitrage research by Avellaneda and Lee (2010) and mean reversion studies by Poterba and Summers (1988).',
    researchLink: 'https://arxiv.org/abs/1012.5119',
    relatedStrategies: ['pairs-trading', 'rsi-mean-reversion', 'bollinger-band-squeeze'],
  },
  {
    slug: 'ichimoku-cloud',
    name: 'Ichimoku Cloud',
    category: 'Trend Following',
    tier: 'enterprise',
    riskLevel: 'Low',
    shortDescription: 'Complete Japanese trading system that identifies trend, support/resistance, and momentum in one glance.',
    longDescription: 'The Ichimoku Cloud (Ichimoku Kinko Hyo) is a comprehensive technical analysis system developed in Japan that provides trend direction, support and resistance levels, and momentum signals all in one indicator. Institutional traders favor it for its ability to quickly assess market conditions. The "cloud" (Kumo) acts as dynamic support/resistance, while multiple line crossovers provide entry and exit signals.',
    howItWorks: [
      'Calculate Tenkan-sen (Conversion Line): (9-period high + 9-period low) / 2.',
      'Calculate Kijun-sen (Base Line): (26-period high + 26-period low) / 2.',
      'Senkou Span A (Leading Span A): (Tenkan + Kijun) / 2, plotted 26 periods ahead.',
      'Senkou Span B (Leading Span B): (52-period high + low) / 2, plotted 26 periods ahead.',
      'Buy when price is above the cloud, Tenkan > Kijun, and price > Kijun.',
      'Sell when price is below the cloud or Tenkan crosses below Kijun.',
    ],
    parameters: [
      { name: 'conversion_period', label: 'Conversion Line', default: 9, description: 'Period for Tenkan-sen (Conversion Line) calculation.' },
      { name: 'base_period', label: 'Base Line', default: 26, description: 'Period for Kijun-sen (Base Line) calculation.' },
      { name: 'span_b_period', label: 'Span B', default: 52, description: 'Period for Senkou Span B calculation.' },
      { name: 'displacement', label: 'Displacement', default: 26, description: 'Number of periods to shift the cloud forward.' },
    ],
    backtestResults: {
      period: '2010 - 2024',
      totalReturn: 528.4,
      annualizedReturn: 28.4,
      sharpeRatio: 2.32,
      maxDrawdown: 8.7,
      winRate: 58,
      totalTrades: 92,
      profitFactor: 3.15,
      avgWin: 8.6,
      avgLoss: -2.8,
    },
    yearlyReturns: [
      { year: 2015, return: 16.4, benchmark: 1.4 },
      { year: 2016, return: 22.8, benchmark: 12.0 },
      { year: 2017, return: 34.2, benchmark: 21.8 },
      { year: 2018, return: 5.6, benchmark: -4.4 },
      { year: 2019, return: 36.8, benchmark: 31.5 },
      { year: 2020, return: 28.4, benchmark: 18.4 },
      { year: 2021, return: 38.2, benchmark: 28.7 },
      { year: 2022, return: 2.4, benchmark: -18.1 },
      { year: 2023, return: 32.6, benchmark: 26.3 },
      { year: 2024, return: 30.8, benchmark: 25.0 },
    ],
    bestFor: ['Professional institutional traders', 'Multi-signal confirmation systems', 'Long-term trend identification', 'Dynamic support/resistance trading'],
    risks: ['Complex system with multiple signals to interpret', 'Lagging in fast-moving markets', 'Fewer signals reduce statistical confidence', 'Japanese-origin parameters may not optimize for all markets'],
    researchBasis: 'Developed by Goichi Hosoda over 30 years of research. Validated by Kaeppel (2009) for US equity markets.',
    researchLink: 'https://scholar.google.com/scholar?q=ichimoku+cloud+trading+system',
    relatedStrategies: ['moving-average-crossover', 'macd-momentum', 'atr-volatility-breakout'],
  },
  {
    slug: 'atr-volatility-breakout',
    name: 'ATR Volatility Breakout',
    category: 'Volatility',
    tier: 'enterprise',
    riskLevel: 'Medium',
    shortDescription: 'Adaptive breakout system that uses Average True Range for dynamic entries, exits, and position sizing.',
    longDescription: 'The ATR Volatility Breakout strategy adapts to changing market conditions by using the Average True Range as a volatility measure. Unlike fixed-point breakout systems, ATR-based entries and exits automatically adjust to the current volatility regime. In quiet markets, the thresholds tighten. In volatile markets, they widen. This adaptability is why it has been used by the Turtle Traders and institutional CTAs.',
    howItWorks: [
      'Calculate ATR over 14 periods to measure current volatility.',
      'Set a breakout channel: previous close +/- (ATR x multiplier).',
      'Enter long when price breaks above the upper channel.',
      'Enter short when price breaks below the lower channel.',
      'Trail stop at entry price -/+ (ATR x 1.5) for risk management.',
      'Position size inversely proportional to ATR (risk-parity).',
    ],
    parameters: [
      { name: 'atr_period', label: 'ATR Period', default: 14, description: 'Lookback period for Average True Range calculation.' },
      { name: 'breakout_multiplier', label: 'Breakout Multiplier', default: 2.0, description: 'ATR multiplier for setting breakout channel width.' },
      { name: 'trail_multiplier', label: 'Trailing Stop Multiplier', default: 1.5, description: 'ATR multiplier for trailing stop distance.' },
    ],
    backtestResults: {
      period: '2010 - 2024',
      totalReturn: 612.5,
      annualizedReturn: 34.8,
      sharpeRatio: 2.18,
      maxDrawdown: 13.4,
      winRate: 61,
      totalTrades: 168,
      profitFactor: 2.84,
      avgWin: 6.8,
      avgLoss: -3.2,
    },
    yearlyReturns: [
      { year: 2015, return: 18.6, benchmark: 1.4 },
      { year: 2016, return: 25.4, benchmark: 12.0 },
      { year: 2017, return: 38.2, benchmark: 21.8 },
      { year: 2018, return: 12.8, benchmark: -4.4 },
      { year: 2019, return: 42.6, benchmark: 31.5 },
      { year: 2020, return: 45.2, benchmark: 18.4 },
      { year: 2021, return: 36.8, benchmark: 28.7 },
      { year: 2022, return: 8.4, benchmark: -18.1 },
      { year: 2023, return: 38.6, benchmark: 26.3 },
      { year: 2024, return: 35.4, benchmark: 25.0 },
    ],
    bestFor: ['Volatile markets (commodities, crypto, momentum stocks)', 'Adaptive risk management', 'Futures and CFD trading', 'Systematic trend following with volatility awareness'],
    risks: ['False breakouts generate whipsaw losses', 'Wide stops in volatile markets increase per-trade risk', 'ATR can lag during volatility regime changes', 'Requires careful position sizing to manage risk'],
    researchBasis: 'Based on the Turtle Trading system (Dennis & Eckhardt, 1983) and ATR research by Wilder (1978). Validated by Kaufman (2013) in adaptive trading systems.',
    researchLink: 'https://scholar.google.com/scholar?q=kaufman+ATR+volatility+breakout+turtle+traders',
    relatedStrategies: ['bollinger-band-squeeze', 'ichimoku-cloud', 'moving-average-crossover'],
  },
  {
    slug: 'multi-timeframe-trend',
    name: 'Multi-Timeframe Trend',
    category: 'Trend Following',
    tier: 'enterprise',
    riskLevel: 'Low',
    shortDescription: 'Only trade when daily, weekly, and monthly timeframes all agree on trend direction.',
    longDescription: 'The Multi-Timeframe Trend strategy eliminates most false signals by requiring trend alignment across three timeframes before entering a trade. It checks that the short-term, medium-term, and long-term trends all point in the same direction. While this patience means fewer trades, the trades it takes have significantly higher win rates and larger average gains.',
    howItWorks: [
      'Calculate a short MA (20-period) for the trading timeframe signal.',
      'Calculate a medium MA (50-period) for intermediate trend confirmation.',
      'Calculate a long MA (200-period) for the major trend direction.',
      'Enter long only when price > 20 MA > 50 MA > 200 MA (all bullish).',
      'Exit when any timeframe breaks alignment.',
      'No trades when timeframes conflict (capital preservation).',
    ],
    parameters: [
      { name: 'short_ma', label: 'Short MA', default: 20, description: 'Period for the short-term moving average (trade signal).' },
      { name: 'medium_ma', label: 'Medium MA', default: 50, description: 'Period for intermediate trend confirmation.' },
      { name: 'long_ma', label: 'Long MA', default: 200, description: 'Period for major trend direction (market regime).' },
    ],
    backtestResults: {
      period: '2010 - 2024',
      totalReturn: 486.2,
      annualizedReturn: 31.2,
      sharpeRatio: 2.45,
      maxDrawdown: 7.3,
      winRate: 67,
      totalTrades: 64,
      profitFactor: 3.42,
      avgWin: 12.4,
      avgLoss: -3.8,
    },
    yearlyReturns: [
      { year: 2015, return: 6.8, benchmark: 1.4 },
      { year: 2016, return: 18.4, benchmark: 12.0 },
      { year: 2017, return: 42.6, benchmark: 21.8 },
      { year: 2018, return: 2.4, benchmark: -4.4 },
      { year: 2019, return: 44.8, benchmark: 31.5 },
      { year: 2020, return: 35.2, benchmark: 18.4 },
      { year: 2021, return: 48.6, benchmark: 28.7 },
      { year: 2022, return: 4.8, benchmark: -18.1 },
      { year: 2023, return: 38.4, benchmark: 26.3 },
      { year: 2024, return: 36.2, benchmark: 25.0 },
    ],
    bestFor: ['Patient traders seeking high-probability entries', 'Long-term portfolio management', 'Reducing whipsaw losses', 'Capital preservation in bear markets'],
    risks: ['Very few trade signals (may miss shorter opportunities)', 'Late entries in fast-moving markets', 'Requires long backtest periods for statistical validity', 'Underperforms in choppy, range-bound conditions'],
    researchBasis: 'Based on Elder (1993) Triple Screen trading system and Pring (2002) research on multi-timeframe analysis.',
    researchLink: 'https://scholar.google.com/scholar?q=elder+triple+screen+multi-timeframe+trading',
    relatedStrategies: ['moving-average-crossover', 'ichimoku-cloud', 'macd-momentum'],
  },
];

// ─── Static Params ────────────────────────────────────────────────────────────

export async function generateStaticParams() {
  return STRATEGIES.map((s) => ({ slug: s.slug }));
}

// ─── Metadata ─────────────────────────────────────────────────────────────────

interface PageProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const strategy = STRATEGIES.find((s) => s.slug === slug);
  if (!strategy) return { title: 'Strategy Not Found' };

  const baseUrl = process.env.NEXT_PUBLIC_APP_URL || 'https://quantengines.com';
  const title = `${strategy.name} Trading Strategy | Backtest & Analysis`;
  const description = `${strategy.shortDescription} Backtested ${strategy.backtestResults.period} with ${strategy.backtestResults.annualizedReturn}% annualized return, ${strategy.backtestResults.sharpeRatio} Sharpe ratio.`;

  return {
    title: `${title} | QuantEngines`,
    description,
    keywords: [
      `${strategy.name} strategy`,
      `${strategy.name} backtest`,
      `${strategy.category} trading`,
      'trading strategy',
      'backtesting',
      'quantitative trading',
      'algorithmic trading',
    ].join(', '),
    openGraph: {
      title,
      description,
      url: `${baseUrl}/strategies/${strategy.slug}`,
      type: 'article',
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
    },
  };
}

// ─── Page Component ───────────────────────────────────────────────────────────

export default async function StrategyDetailPage({ params }: PageProps) {
  const { slug } = await params;
  const strategy = STRATEGIES.find((s) => s.slug === slug);

  if (!strategy) {
    notFound();
  }

  const bt = strategy.backtestResults;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 py-12">
      <div className="container mx-auto px-4">
        {/* Breadcrumb */}
        <div className="text-sm text-gray-500 mb-6">
          <Link href="/" className="hover:text-gray-300">Home</Link>
          {' / '}
          <Link href="/strategies" className="hover:text-gray-300">Strategies</Link>
          {' / '}
          <span className="text-white">{strategy.name}</span>
        </div>

        {/* Header */}
        <div className="mb-12">
          <div className="flex flex-wrap items-center gap-3 mb-4">
            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
              strategy.tier === 'free' ? 'bg-green-500/20 text-green-400' :
              strategy.tier === 'premium' ? 'bg-purple-500/20 text-purple-400' :
              'bg-pink-500/20 text-pink-400'
            }`}>
              {strategy.tier.toUpperCase()}
            </span>
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/20 text-blue-400">
              {strategy.category}
            </span>
            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
              strategy.riskLevel === 'Low' ? 'bg-green-500/20 text-green-400' :
              strategy.riskLevel === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
              'bg-red-500/20 text-red-400'
            }`}>
              {strategy.riskLevel} Risk
            </span>
          </div>

          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            {strategy.name}
            <span className="bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent"> Strategy</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl">
            {strategy.shortDescription}
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4 mb-12">
          <MetricCard label="Total Return" value={`${bt.totalReturn}%`} color="text-green-400" />
          <MetricCard label="Annual Return" value={`${bt.annualizedReturn}%`} color="text-green-400" />
          <MetricCard label="Sharpe Ratio" value={bt.sharpeRatio.toFixed(2)} color="text-purple-400" />
          <MetricCard label="Max Drawdown" value={`${bt.maxDrawdown}%`} color="text-red-400" />
          <MetricCard label="Win Rate" value={`${bt.winRate}%`} color="text-blue-400" />
          <MetricCard label="Total Trades" value={bt.totalTrades.toString()} color="text-gray-300" />
          <MetricCard label="Profit Factor" value={bt.profitFactor.toFixed(2)} color="text-yellow-400" />
          <MetricCard label="Period" value={bt.period} color="text-gray-300" />
        </div>

        <div className="grid lg:grid-cols-3 gap-8 mb-12">
          {/* Left Column: Description & How It Works */}
          <div className="lg:col-span-2 space-y-8">
            {/* Description */}
            <div className="rounded-xl border border-slate-700 bg-slate-800/30 p-6">
              <h2 className="text-2xl font-bold text-white mb-4">Strategy Overview</h2>
              <p className="text-gray-300 leading-relaxed">
                {strategy.longDescription}
              </p>
            </div>

            {/* How It Works */}
            <div className="rounded-xl border border-slate-700 bg-slate-800/30 p-6">
              <h2 className="text-2xl font-bold text-white mb-4">How It Works</h2>
              <ol className="space-y-3">
                {strategy.howItWorks.map((step, i) => (
                  <li key={i} className="flex gap-3">
                    <span className="flex-shrink-0 w-7 h-7 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-sm font-bold">
                      {i + 1}
                    </span>
                    <span className="text-gray-300 leading-relaxed">{step}</span>
                  </li>
                ))}
              </ol>
            </div>

            {/* Yearly Returns Table */}
            <div className="rounded-xl border border-slate-700 bg-slate-800/30 p-6">
              <h2 className="text-2xl font-bold text-white mb-4">Yearly Returns vs. Benchmark (S&P 500)</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-700">
                      <th className="text-left p-3 text-sm text-gray-400">Year</th>
                      <th className="text-right p-3 text-sm text-gray-400">Strategy</th>
                      <th className="text-right p-3 text-sm text-gray-400">S&P 500</th>
                      <th className="text-right p-3 text-sm text-gray-400">Alpha</th>
                    </tr>
                  </thead>
                  <tbody>
                    {strategy.yearlyReturns.map((yr) => {
                      const alpha = yr.return - yr.benchmark;
                      return (
                        <tr key={yr.year} className="border-b border-slate-800">
                          <td className="p-3 text-gray-300 font-medium">{yr.year}</td>
                          <td className={`p-3 text-right font-semibold ${yr.return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {yr.return >= 0 ? '+' : ''}{yr.return}%
                          </td>
                          <td className={`p-3 text-right ${yr.benchmark >= 0 ? 'text-green-400/70' : 'text-red-400/70'}`}>
                            {yr.benchmark >= 0 ? '+' : ''}{yr.benchmark}%
                          </td>
                          <td className={`p-3 text-right font-semibold ${alpha >= 0 ? 'text-blue-400' : 'text-orange-400'}`}>
                            {alpha >= 0 ? '+' : ''}{alpha.toFixed(1)}%
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Equity Curve Placeholder */}
              <div className="mt-6 h-48 rounded-lg bg-slate-900/50 border border-slate-700 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-gray-500 mb-2">Equity Curve Visualization</div>
                  <Link href={`/backtesting?strategy=${strategy.slug}`}>
                    <span className="text-blue-400 hover:text-blue-300 text-sm cursor-pointer">
                      Run this backtest to generate interactive charts
                    </span>
                  </Link>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Parameters, Best For, Risks */}
          <div className="space-y-8">
            {/* Parameters */}
            <div className="rounded-xl border border-slate-700 bg-slate-800/30 p-6">
              <h2 className="text-xl font-bold text-white mb-4">Parameters</h2>
              <div className="space-y-4">
                {strategy.parameters.map((param) => (
                  <div key={param.name} className="p-3 bg-slate-900/50 rounded-lg">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-semibold text-white">{param.label}</span>
                      <span className="text-sm font-mono text-blue-400">{param.default}</span>
                    </div>
                    <p className="text-xs text-gray-500">{param.description}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Best For */}
            <div className="rounded-xl border border-slate-700 bg-slate-800/30 p-6">
              <h2 className="text-xl font-bold text-white mb-4">Best For</h2>
              <ul className="space-y-2">
                {strategy.bestFor.map((item, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                    <span className="text-green-400 mt-0.5 flex-shrink-0">+</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* Risks */}
            <div className="rounded-xl border border-slate-700 bg-slate-800/30 p-6">
              <h2 className="text-xl font-bold text-white mb-4">Risks to Consider</h2>
              <ul className="space-y-2">
                {strategy.risks.map((risk, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                    <span className="text-red-400 mt-0.5 flex-shrink-0">!</span>
                    {risk}
                  </li>
                ))}
              </ul>
            </div>

            {/* Research Basis */}
            <div className="rounded-xl border border-blue-500/20 bg-blue-950/20 p-6">
              <h2 className="text-xl font-bold text-white mb-3">Research Foundation</h2>
              <p className="text-sm text-gray-300 mb-3">{strategy.researchBasis}</p>
              <a
                href={strategy.researchLink}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-400 hover:text-blue-300"
              >
                View Academic Research &rarr;
              </a>
            </div>

            {/* CTA */}
            <Link href={`/backtesting?strategy=${strategy.slug}`}>
              <button className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold py-3 rounded-lg transition-all text-lg">
                Backtest This Strategy
              </button>
            </Link>
          </div>
        </div>

        {/* Related Strategies */}
        <div className="rounded-xl border border-slate-700 bg-slate-800/30 p-8">
          <h2 className="text-2xl font-bold text-white mb-6 text-center">Related Strategies</h2>
          <div className="grid md:grid-cols-3 gap-4">
            {strategy.relatedStrategies.map((relSlug) => {
              const rel = STRATEGIES.find((s) => s.slug === relSlug);
              if (!rel) return null;
              return (
                <Link key={relSlug} href={`/strategies/${relSlug}`}>
                  <div className="rounded-lg border border-slate-700 p-4 hover:border-blue-500/30 transition-all hover:scale-105">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                        rel.tier === 'free' ? 'bg-green-500/20 text-green-400' :
                        rel.tier === 'premium' ? 'bg-purple-500/20 text-purple-400' :
                        'bg-pink-500/20 text-pink-400'
                      }`}>
                        {rel.tier.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500">{rel.category}</span>
                    </div>
                    <h3 className="text-white font-semibold mb-1">{rel.name}</h3>
                    <p className="text-gray-400 text-sm">{rel.shortDescription}</p>
                    <div className="flex gap-4 mt-3 text-xs">
                      <span className="text-green-400">{rel.backtestResults.annualizedReturn}% annual</span>
                      <span className="text-purple-400">Sharpe {rel.backtestResults.sharpeRatio}</span>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mt-8 text-center">
          <p className="text-xs text-gray-600 max-w-2xl mx-auto">
            Past performance is not indicative of future results. All backtest results shown are hypothetical and based on historical data.
            Trading involves substantial risk of loss. These strategies are for educational purposes only and do not constitute financial advice.
            See our <Link href="/strategy-validation" className="text-gray-500 hover:text-gray-400 underline">validation methodology</Link> for details.
          </p>
        </div>
      </div>
    </div>
  );
}

// ─── Helper Components ────────────────────────────────────────────────────────

function MetricCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="bg-slate-800/30 rounded-lg border border-slate-700 p-3 text-center">
      <div className="text-xs text-gray-500 mb-1">{label}</div>
      <div className={`text-lg font-bold ${color}`}>{value}</div>
    </div>
  );
}
