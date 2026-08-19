/**
 * What the deployed backtest service will and will not do, and how to say so on screen.
 *
 * Every statement here was checked against https://elliottsax-quant-backend.hf.space/api/v1
 * on 2026-08-19, not inferred from the backend source:
 *
 *   POST /backtesting/demo/run  {symbol AAPL, ma_crossover, 2023-01-01..2024-01-01}
 *     -> 500 {"detail":"Backtest execution failed: 'timestamp'"}
 *   ...identically for rsi and bollinger_breakout, and for MSFT and SPY.
 *
 * The cause is a data-shape mismatch inside the backend, not missing price data.
 * backend/app/api/v1/backtesting.py::_fetch_historical_data returns a DataFrame whose
 * dates live in the *index*, while the engine (backend/app/services/backtesting.py:176)
 * does price_data.sort_values('timestamp') and needs them in a *column*. Both branches of
 * that function -- the real yfinance branch and its synthetic fallback -- return the same
 * wrong shape, so the single-symbol backtest raises KeyError('timestamp') before it reads
 * a single bar. No input can avoid it; there is no such thing as a run that succeeds.
 *
 * Price data itself is available server-side: POST /backtesting/portfolio/demo/run
 * returned 200 with real trading dates (2023-01-03..2023-12-29) over the same window,
 * and GET /data/market/price/AAPL returned 200. So the fix is the column, not a feed.
 *
 * These strings are what a user reads when a run fails. They name the specific missing
 * thing rather than surfacing "Backtest execution failed: 'timestamp'", which tells a
 * reader nothing about whether to retry, change inputs, or wait for a deploy.
 */

import { APIError } from '@/lib/api-client'

/**
 * The only strategies GET /backtesting/demo/strategies advertises (verified 200).
 * Offering more than these produced guaranteed 400s: the run pages previously listed
 * eleven, of which eight the service does not implement at this tier.
 */
export const DEMO_STRATEGIES = [
  { value: 'ma_crossover', label: 'MA Crossover', icon: '📈' },
  { value: 'rsi', label: 'RSI Mean Reversion', icon: '🔄' },
  { value: 'bollinger_breakout', label: 'Bollinger Breakout', icon: '💥' },
] as const

/** Strategy ids the service answers with 403 "requires premium subscription". */
const PREMIUM_STRATEGIES = new Set([
  'momentum',
  'macd',
  'mean_reversion_zscore',
  'triple_ema',
])

export function isPremiumStrategy(id: string): boolean {
  return PREMIUM_STRATEGIES.has(id)
}

export interface BacktestFailure {
  /** Short statement of what happened, used as a heading. */
  headline: string
  /** The specific missing or broken thing, in plain language. */
  detail: string
  /**
   * Whether pressing the button again could plausibly produce a different outcome.
   * False for defects that are deterministic server-side: a retry button on those is a
   * promise the service cannot keep.
   */
  canRetry: boolean
}

/**
 * The engine defect above is deterministic, so it is worth naming as its own case: a user
 * who is told "try again" for it will try forever.
 */
const ENGINE_BROKEN: BacktestFailure = {
  headline: 'The backtest engine cannot run',
  detail:
    'The service fetches the price history but hands it to the engine in the wrong shape: ' +
    'the dates arrive as a row index where the engine expects a "timestamp" column, so ' +
    'every run stops with KeyError(\'timestamp\') before the first bar is processed. This ' +
    'affects every symbol, strategy and date range identically, and needs a fix in the ' +
    'backend (app/api/v1/backtesting.py::_fetch_historical_data must reset the index into ' +
    'a timestamp column). Nothing you can change on this page works around it.',
  canRetry: false,
}

/**
 * Turn whatever the API layer threw into something specific enough to act on.
 * Unrecognised errors are reported verbatim rather than being flattened into a generic
 * message, so a new failure mode stays visible instead of being disguised as a known one.
 */
export function describeBacktestFailure(err: unknown): BacktestFailure {
  if (err instanceof APIError) {
    const detail = err.message || ''

    if (err.status === 500 && /timestamp/i.test(detail)) return ENGINE_BROKEN

    if (err.status === 403) {
      return {
        headline: 'This strategy is not available on the free tier',
        detail:
          `${detail} Choose one of the demo strategies, or sign in with an account that ` +
          'has premium access.',
        canRetry: false,
      }
    }

    if (err.status === 400 && /unknown strategy/i.test(detail)) {
      return {
        headline: 'The service does not implement this strategy',
        detail:
          `${detail} Only ${DEMO_STRATEGIES.map((s) => s.value).join(', ')} are implemented ` +
          'by the deployed service.',
        canRetry: false,
      }
    }

    if (err.status === 401) {
      return {
        headline: 'This backtest needs an account',
        detail: 'The service rejected the request as unauthenticated. Sign in and try again.',
        canRetry: false,
      }
    }

    if (err.status === 408) {
      return {
        headline: 'The backtest timed out',
        detail: 'The service did not respond in time. A shorter date range may complete.',
        canRetry: true,
      }
    }

    if (err.status === 0) {
      return {
        headline: 'The backtest service could not be reached',
        detail: 'The request never got a response. Check your connection and try again.',
        canRetry: true,
      }
    }

    return {
      headline: 'The backtest did not run',
      detail: detail
        ? `The service returned HTTP ${err.status}: ${detail}`
        : `The service returned HTTP ${err.status}.`,
      canRetry: err.status >= 500,
    }
  }

  if (err instanceof Error && err.message) {
    return { headline: 'The backtest did not run', detail: err.message, canRetry: true }
  }

  return {
    headline: 'The backtest did not run',
    detail: 'The backtest service could not be reached.',
    canRetry: true,
  }
}

/**
 * Shown before the user spends time on a form that cannot currently succeed. Stated as a
 * known service condition rather than a guess, because it was measured.
 */
export const ENGINE_OUTAGE_NOTICE =
  'Single-symbol backtests are currently failing server-side for every symbol and ' +
  'strategy: the engine receives the price history with its dates in the wrong position ' +
  'and stops before reading any data. Runs started here will report that error rather ' +
  'than results. Strategy configuration on this page still works and can be saved.'
