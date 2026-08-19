/**
 * Normalisation of backtest payloads for the /backtesting pages.
 *
 * The backend (backend/app/services/backtesting.py, _calculate_metrics) returns:
 *   equity_curve:   [{ timestamp, equity }]
 *   drawdown_curve: [{ timestamp, drawdown, peak }]  — drawdown is a POSITIVE percentage
 *   trades:         [{ symbol, side, quantity, price, timestamp, commission, pnl }]
 * There is no per-point `date` or `drawdown`, no benchmark series, and no per-trade
 * `return_pct` or `profit`.
 *
 * A measured value the API does not report is never replaced with a default here: a
 * defaulted number is a fabricated one. Defaults are exactly what made these pages print
 * "Max Drawdown 0.00%" and "Win Rate 0.0%" on every run — the fields being read did not
 * exist, so every point fell back to zero and every trade to a loss. Entries missing the
 * value that gives them meaning are dropped, and quantities that cannot be measured are
 * reported as absent so the caller can say so on screen.
 */

const isRecord = (v: unknown): v is Record<string, unknown> =>
  typeof v === 'object' && v !== null

const num = (v: unknown): number | null =>
  typeof v === 'number' && Number.isFinite(v) ? v : null

const nonEmptyString = (v: unknown): string | null =>
  typeof v === 'string' && v.length > 0 ? v : null

/** Backend points are keyed by `timestamp`; records saved by these pages use `date`. */
function timestampOf(row: Record<string, unknown>): string | null {
  return nonEmptyString(row.timestamp) ?? nonEmptyString(row.date)
}

/** Calendar day of an ISO timestamp, used only to line trades up with equity points. */
function dayKey(stamp: string | null): string | null {
  if (!stamp) return null
  const iso = stamp.match(/^(\d{4}-\d{2}-\d{2})/)
  if (iso) return iso[1]
  const parsed = new Date(stamp)
  return Number.isNaN(parsed.getTime()) ? null : parsed.toISOString().slice(0, 10)
}

export interface EquityPoint {
  day: number
  date: string | null
  equity: number
  /** <= 0. The drawdown chart draws downwards from zero, the backend reports magnitudes. */
  drawdown: number
  /**
   * The API returns no benchmark series, so there is nothing to plot against the
   * strategy. Left null rather than synthesised from an assumed annual return.
   */
  benchmark: number | null
}

export interface NormalizedEquityCurve {
  points: EquityPoint[]
  /** 'derived' means drawdown was recomputed from the equity curve; disclose it. */
  drawdownSource: 'reported' | 'derived'
}

export function normalizeEquityCurve(
  rawCurve: unknown,
  rawDrawdownCurve: unknown
): NormalizedEquityCurve {
  const rows = (Array.isArray(rawCurve) ? rawCurve : []).filter(isRecord)
  const drawdownRows = (Array.isArray(rawDrawdownCurve) ? rawDrawdownCurve : []).filter(isRecord)

  const drawdownByStamp = new Map<string, number>()
  drawdownRows.forEach((row) => {
    const stamp = timestampOf(row)
    const value = num(row.drawdown)
    if (stamp !== null && value !== null) drawdownByStamp.set(stamp, value)
  })

  const points: EquityPoint[] = []
  const reportedDrawdown: (number | null)[] = []

  rows.forEach((row, index) => {
    const equity = num(row.equity) ?? num(row.value)
    // An equity point with no equity value measures nothing — drop it rather than
    // substitute the initial capital, which would draw a flat line the run never had.
    if (equity === null) return
    const date = timestampOf(row)
    const byStamp = date !== null ? drawdownByStamp.get(date) : undefined
    const byIndex = num(drawdownRows[index]?.drawdown)
    points.push({ day: points.length + 1, date, equity, drawdown: 0, benchmark: null })
    reportedDrawdown.push(byStamp ?? byIndex ?? num(row.drawdown))
  })

  if (points.length === 0) return { points, drawdownSource: 'derived' }

  if (reportedDrawdown.every((value) => value !== null)) {
    // Sign conversion only: the backend reports drawdown as a positive percentage of the
    // running peak, the charts expect it negative. No value is invented.
    points.forEach((point, i) => {
      point.drawdown = -Math.abs(reportedDrawdown[i] as number)
    })
    return { points, drawdownSource: 'reported' }
  }

  // No usable drawdown series. Recompute it from the measured equity curve (running peak)
  // rather than defaulting every point to 0, which would assert the strategy never drew
  // down. This is a transform of measured values, not a stand-in for a missing one.
  let peak = points[0].equity
  points.forEach((point) => {
    if (point.equity > peak) peak = point.equity
    point.drawdown = peak > 0 ? -((peak - point.equity) / peak) * 100 : 0
  })
  return { points, drawdownSource: 'derived' }
}

/**
 * How the per-trade `returnPct` figures should be read. The backend reports realised P&L
 * in account currency and never a per-trade percentage, so when no percentage is reported
 * the trades are expressed as a share of the run's starting capital — an exact transform
 * of two measured numbers. Callers must label which unit is on screen.
 */
export type TradeReturnUnit = 'reported_pct' | 'share_of_initial_capital'

export interface TradeRow {
  day: number
  date: string | null
  side: string | null
  quantity: number | null
  price: number | null
  /** Realised P&L in account currency, exactly as reported (`pnl`). */
  profit: number
  returnPct: number
  isWin: boolean
}

export interface NormalizedTrades {
  /** Realised trades only — fills whose P&L the run actually reported. */
  rows: TradeRow[]
  /** Every fill the API returned, including opening legs that carry no P&L yet. */
  executions: number
  returnUnit: TradeReturnUnit
}

export function normalizeTrades(
  rawTrades: unknown,
  points: EquityPoint[],
  initialCapital: number
): NormalizedTrades {
  const rawRows = (Array.isArray(rawTrades) ? rawTrades : []).filter(isRecord)

  const dayByDate = new Map<string, number>()
  points.forEach((point) => {
    const key = dayKey(point.date)
    if (key !== null && !dayByDate.has(key)) dayByDate.set(key, point.day)
  })

  const candidates = rawRows
    .map((row) => ({
      date: timestampOf(row),
      side: nonEmptyString(row.side),
      quantity: num(row.quantity),
      price: num(row.price),
      // `profit` is the field name used by records these pages saved; the API sends `pnl`.
      pnl: num(row.pnl) ?? num(row.profit),
      reportedPct: num(row.return_pct) ?? num(row.returnPct),
    }))
    // A fill with no realised P&L and no reported return is an opening leg: it has no
    // outcome yet, so it is not a win, not a loss, and not part of the win rate.
    .filter((row) => row.pnl !== null || row.reportedPct !== null)

  const everyPctReported = candidates.length > 0 && candidates.every((c) => c.reportedPct !== null)
  const returnUnit: TradeReturnUnit = everyPctReported ? 'reported_pct' : 'share_of_initial_capital'

  const usable = everyPctReported
    ? candidates
    : initialCapital > 0
      ? candidates.filter((c) => c.pnl !== null)
      : []

  const rows: TradeRow[] = usable.map((c, index) => {
    const pnl = c.pnl ?? 0
    const key = dayKey(c.date)
    return {
      day: (key !== null ? dayByDate.get(key) : undefined) ?? index + 1,
      date: c.date,
      side: c.side,
      quantity: c.quantity,
      price: c.price,
      profit: pnl,
      returnPct: everyPctReported ? (c.reportedPct as number) : (pnl / initialCapital) * 100,
      isWin: c.reportedPct !== null && c.pnl === null ? c.reportedPct > 0 : pnl > 0,
    }
  })

  return { rows, executions: rawRows.length, returnUnit }
}

export interface BacktestMetricsValues {
  finalEquity: number
  totalReturn: number
  maxDrawdown: number
  sharpeRatio: number
  sortinoRatio: number | null
  winRate: number
  avgWin: number
  avgLoss: number
  profitFactor: number
  totalTrades: number
}

/**
 * Callers must not render trade statistics when `trades` is empty: a win rate over zero
 * trades is undefined, and the zeros returned here would read as a measurement.
 */
export function computeBacktestMetrics(
  points: EquityPoint[],
  trades: TradeRow[],
  initialCapital: number
): BacktestMetricsValues {
  const finalEquity = points.length > 0 ? points[points.length - 1].equity : initialCapital
  const totalReturn = initialCapital > 0 ? ((finalEquity - initialCapital) / initialCapital) * 100 : 0
  const maxDrawdown = points.length > 0 ? Math.min(...points.map((p) => p.drawdown)) : 0

  const winners = trades.filter((t) => t.isWin)
  const losers = trades.filter((t) => !t.isWin && t.profit < 0)
  const winRate = trades.length > 0 ? (winners.length / trades.length) * 100 : 0
  const avgWin = winners.length > 0
    ? winners.reduce((sum, t) => sum + t.returnPct, 0) / winners.length
    : 0
  const avgLoss = losers.length > 0
    ? losers.reduce((sum, t) => sum + t.returnPct, 0) / losers.length
    : 0

  // Gross profit over gross loss. With winning trades and no losing trades the ratio is
  // unbounded, not zero: 0.00 reads as "this strategy lost everything", the opposite of
  // what happened. Infinity renders as "Infinity" — undefined, which is the truth.
  const grossProfit = winners.reduce((sum, t) => sum + t.profit, 0)
  const grossLoss = Math.abs(losers.reduce((sum, t) => sum + t.profit, 0))
  const profitFactor = grossLoss > 0
    ? grossProfit / grossLoss
    : grossProfit > 0
      ? Number.POSITIVE_INFINITY
      : 0

  const returns = points
    .map((p, i) => (i > 0 ? (p.equity - points[i - 1].equity) / points[i - 1].equity : 0))
    .slice(1)
  const avgReturn = returns.length > 0 ? returns.reduce((a, b) => a + b, 0) / returns.length : 0
  const stdDev = returns.length > 0
    ? Math.sqrt(returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length)
    : 0
  const sharpeRatio = stdDev > 0 ? (avgReturn * 252) / (stdDev * Math.sqrt(252)) : 0

  // Sortino uses downside deviation (returns below the 0% target only). It is not a fixed
  // multiple of Sharpe — deriving it as one invents a number that happens to flatter the
  // strategy, since downside deviation is by construction no larger than total deviation.
  const downside = returns.filter((r) => r < 0)
  const downsideDev = downside.length > 0
    ? Math.sqrt(downside.reduce((sum, r) => sum + r * r, 0) / downside.length)
    : 0
  const sortinoRatio = downsideDev > 0 ? (avgReturn * 252) / (downsideDev * Math.sqrt(252)) : null

  return {
    finalEquity,
    totalReturn,
    maxDrawdown,
    sharpeRatio,
    sortinoRatio,
    winRate,
    avgWin,
    avgLoss,
    profitFactor,
    totalTrades: trades.length,
  }
}

function monthKey(stamp: string): string | null {
  const iso = stamp.match(/^(\d{4}-\d{2})/)
  if (iso) return iso[1]
  const parsed = new Date(stamp)
  return Number.isNaN(parsed.getTime()) ? null : parsed.toISOString().slice(0, 7)
}

function monthLabel(key: string): string {
  const [year, month] = key.split('-')
  const names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const name = names[Number(month) - 1] ?? month
  return `${name} '${year.slice(2)}`
}

/**
 * One bucket per calendar month the equity curve actually covers, labelled from the data.
 * Twelve fixed Jan–Dec buckets labelled months the run never spanned, and split by
 * `length / 12` (zero for curves shorter than twelve points, which printed twelve
 * identical 0.00% months), described a year that was never tested.
 * Returns [] when the curve carries no dates — the caller must then not claim a month.
 */
export function deriveMonthlyReturns(points: EquityPoint[]): Array<{ month: string; return: number }> {
  const dated = points
    .map((p) => ({ key: p.date !== null ? monthKey(p.date) : null, equity: p.equity }))
    .filter((p): p is { key: string; equity: number } => p.key !== null)
  if (dated.length < 2) return []

  const order: string[] = []
  const lastEquityInMonth = new Map<string, number>()
  dated.forEach((p) => {
    if (!lastEquityInMonth.has(p.key)) order.push(p.key)
    lastEquityInMonth.set(p.key, p.equity)
  })

  // The first bucket is measured from the first point available in that month, so a run
  // starting mid-month reports that partial month, not a full one.
  let base = dated[0].equity
  const out: Array<{ month: string; return: number }> = []
  order.forEach((key) => {
    const end = lastEquityInMonth.get(key) as number
    if (base > 0) {
      out.push({ month: monthLabel(key), return: parseFloat((((end - base) / base) * 100).toFixed(2)) })
    }
    base = end
  })
  return out
}

function niceStep(rough: number): number {
  if (!(rough > 0)) return 0
  const magnitude = Math.pow(10, Math.floor(Math.log10(rough)))
  const scaled = rough / magnitude
  const step = scaled <= 1 ? 1 : scaled <= 2 ? 2 : scaled <= 2.5 ? 2.5 : scaled <= 5 ? 5 : 10
  return step * magnitude
}

function formatBound(value: number, step: number): string {
  const decimals = step >= 1 ? 0 : step >= 0.1 ? 1 : 2
  return value.toFixed(decimals)
}

/**
 * Buckets are derived from the trades in hand. A fixed -15%..25% ladder clamped every
 * outlier into an edge bucket, reporting returns the trades did not have.
 */
export function buildTradeDistribution(
  trades: TradeRow[]
): Array<{ returnRange: string; count: number; value: number }> {
  if (trades.length === 0) return []
  const values = trades.map((t) => t.returnPct)
  const min = Math.min(...values)
  const max = Math.max(...values)
  if (!Number.isFinite(min) || !Number.isFinite(max)) return []

  const step = niceStep((max - min) / 8)
  if (step === 0) {
    return [{ returnRange: `${min.toFixed(2)}%`, count: trades.length, value: min }]
  }

  const start = Math.floor(min / step) * step
  const bins = new Map<number, number>()
  values.forEach((v) => {
    const idx = Math.floor((v - start) / step)
    bins.set(idx, (bins.get(idx) ?? 0) + 1)
  })
  const lastIdx = Math.max(...Array.from(bins.keys()))

  const out: Array<{ returnRange: string; count: number; value: number }> = []
  for (let i = 0; i <= lastIdx; i++) {
    const lo = start + i * step
    out.push({
      returnRange: `${formatBound(lo, step)}%`,
      count: bins.get(i) ?? 0,
      value: lo + step / 2,
    })
  }
  return out
}

export function buildRollingMetrics(
  points: EquityPoint[],
  windowSize: number = 20
): Array<{ day: number; sharpe: number; volatility: number; avgReturn: number }> {
  const out: Array<{ day: number; sharpe: number; volatility: number; avgReturn: number }> = []
  for (let i = windowSize; i < points.length; i++) {
    const window = points.slice(i - windowSize, i)
    const returns = window
      .map((p, idx) => (idx > 0 ? (p.equity - window[idx - 1].equity) / window[idx - 1].equity : 0))
      .slice(1)
    if (returns.length === 0) continue
    const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length
    const stdDev = Math.sqrt(
      returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length
    )
    out.push({
      day: points[i].day,
      sharpe: parseFloat((stdDev > 0 ? (avgReturn * 252) / (stdDev * Math.sqrt(252)) : 0).toFixed(2)),
      volatility: parseFloat((stdDev * Math.sqrt(252) * 100).toFixed(2)),
      avgReturn: parseFloat((avgReturn * 100).toFixed(3)),
    })
  }
  return out
}

export interface BacktestChartData {
  /**
   * Loosely typed at this boundary on purpose: BacktestResultView's props require a
   * numeric `benchmark` on every equity point, and the API returns no benchmark series.
   * The points carry `benchmark: null` rather than an invented one.
   */
  equityData: any[]
  trades: any[]
  monthlyReturns: Array<{ month: string; return: number }>
  tradeDistribution: Array<{ returnRange: string; count: number; value: number }>
  rollingMetrics: Array<{ day: number; sharpe: number; volatility: number }>
}

export interface NormalizedBacktest {
  points: EquityPoint[]
  drawdownSource: 'reported' | 'derived'
  trades: NormalizedTrades
  metrics: BacktestMetricsValues
  chartData: BacktestChartData
}

/** Single entry point: raw payload (or saved record) in, everything the pages render out. */
export function normalizeBacktest(
  rawEquityCurve: unknown,
  rawDrawdownCurve: unknown,
  rawTrades: unknown,
  initialCapital: number
): NormalizedBacktest {
  const { points, drawdownSource } = normalizeEquityCurve(rawEquityCurve, rawDrawdownCurve)
  const trades = normalizeTrades(rawTrades, points, initialCapital)
  const metrics = computeBacktestMetrics(points, trades.rows, initialCapital)
  return {
    points,
    drawdownSource,
    trades,
    metrics,
    chartData: {
      equityData: points,
      trades: trades.rows,
      monthlyReturns: deriveMonthlyReturns(points),
      tradeDistribution: buildTradeDistribution(trades.rows),
      rollingMetrics: buildRollingMetrics(points),
    },
  }
}
