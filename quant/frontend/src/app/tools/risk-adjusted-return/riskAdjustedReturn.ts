/**
 * Risk-adjusted return ratios from a pasted periodic return series.
 *
 * Sharpe ratio — Sharpe, W.F. (1966), "Mutual Fund Performance",
 *   Journal of Business 39(1). Excess return per unit of total volatility.
 * Sortino ratio — Sortino, F.A. & Price, L.N. (1994), "Performance
 *   Measurement in a Downside Risk Framework", Journal of Investing 3(3).
 *   Excess return per unit of DOWNSIDE volatility only — upside variance
 *   is not penalized.
 * Calmar ratio — Young, T.W. (1991), "Calmar Ratio: A Smoother Tool",
 *   Futures 20(1). Annualized return divided by maximum drawdown.
 *
 * Conventions used (stated explicitly since the literature has variants):
 *  - Sample standard deviation (n-1 denominator) for Sharpe, the usual
 *    choice when the return series is itself a sample, not a full
 *    population.
 *  - Downside deviation uses the FULL period count n in its denominator
 *    (target-downside-deviation per Sortino & Price 1994), not just the
 *    count of losing periods — a common source of ratio inflation when
 *    implemented incorrectly.
 *  - Annualization multiplies the periodic ratio by sqrt(periodsPerYear),
 *    the standard scaling for i.i.d. returns (mean scales linearly with
 *    time, standard deviation with its square root).
 *  - Calmar's "annualized return" is the CAGR of the full entered series
 *    (equity_end^(periodsPerYear/n) - 1), not a fixed trailing window.
 *
 * Pure functions over a caller-supplied return series — no market data.
 */

export interface RiskAdjustedInputs {
  /** Periodic returns as decimals, e.g. 0.02 for +2%. */
  returns: number[];
  /** Annual risk-free rate as a decimal, e.g. 0.04 for 4%. */
  riskFreeAnnual: number;
  /** Periods per year for annualization, e.g. 252 (daily), 52 (weekly), 12 (monthly). */
  periodsPerYear: number;
}

export interface RiskAdjustedResult {
  n: number;
  meanPerPeriod: number;
  stdevPerPeriod: number;
  annualizedReturn: number;
  annualizedVolatility: number;
  sharpe: number | null;
  sortino: number | null;
  maxDrawdown: number;
  calmar: number | null;
  equityCurve: number[];
}

export function validateReturns(i: RiskAdjustedInputs): string | null {
  if (!Array.isArray(i.returns) || i.returns.length < 2) return 'Enter at least 2 periodic returns.';
  if (i.returns.some((r) => !Number.isFinite(r))) return 'Every return must be a number.';
  if (i.returns.some((r) => r <= -1)) return 'A return of -100% or worse would zero or invert the equity curve — check your inputs.';
  if (!Number.isFinite(i.riskFreeAnnual)) return 'Risk-free rate must be a number.';
  if (!Number.isFinite(i.periodsPerYear) || i.periodsPerYear <= 0) return 'Periods per year must be greater than 0.';
  return null;
}

function mean(xs: number[]): number {
  return xs.reduce((s, x) => s + x, 0) / xs.length;
}

/** Sample standard deviation (n-1 denominator). */
function sampleStdev(xs: number[]): number {
  const m = mean(xs);
  const sumSq = xs.reduce((s, x) => s + (x - m) * (x - m), 0);
  return xs.length > 1 ? Math.sqrt(sumSq / (xs.length - 1)) : 0;
}

export function computeRiskAdjustedReturn(i: RiskAdjustedInputs): RiskAdjustedResult | null {
  if (validateReturns(i) !== null) return null;

  const { returns, riskFreeAnnual, periodsPerYear } = i;
  const n = returns.length;
  const riskFreePerPeriod = riskFreeAnnual / periodsPerYear;
  const excess = returns.map((r) => r - riskFreePerPeriod);

  const meanPerPeriod = mean(returns);
  const stdevPerPeriod = sampleStdev(returns);
  const annualizedVolatility = stdevPerPeriod * Math.sqrt(periodsPerYear);

  const meanExcess = mean(excess);
  const stdevExcess = sampleStdev(excess);
  const sqrtAnnualize = Math.sqrt(periodsPerYear);
  const sharpe = stdevExcess > 0 ? (meanExcess / stdevExcess) * sqrtAnnualize : null;

  // Target-downside-deviation: floor each excess return at 0 (no downside), square, average over ALL n periods.
  const downsideSumSq = excess.reduce((s, e) => s + Math.min(e, 0) ** 2, 0);
  const downsideDeviation = Math.sqrt(downsideSumSq / n);
  const sortino = downsideDeviation > 0 ? (meanExcess / downsideDeviation) * sqrtAnnualize : null;

  // Equity curve from compounding, starting at 1.0.
  const equityCurve: number[] = [1];
  for (const r of returns) equityCurve.push(equityCurve[equityCurve.length - 1] * (1 + r));

  let peak = equityCurve[0];
  let maxDrawdown = 0;
  for (const v of equityCurve) {
    if (v > peak) peak = v;
    const dd = (peak - v) / peak;
    if (dd > maxDrawdown) maxDrawdown = dd;
  }

  const finalEquity = equityCurve[equityCurve.length - 1];
  const annualizedReturn = finalEquity > 0 ? Math.pow(finalEquity, periodsPerYear / n) - 1 : -1;
  const calmar = maxDrawdown > 0 ? annualizedReturn / maxDrawdown : null;

  const result: RiskAdjustedResult = {
    n,
    meanPerPeriod,
    stdevPerPeriod,
    annualizedReturn,
    annualizedVolatility,
    sharpe,
    sortino,
    maxDrawdown,
    calmar,
    equityCurve,
  };

  for (const [k, v] of Object.entries(result)) {
    if (k === 'equityCurve') continue;
    if (typeof v === 'number' && !Number.isFinite(v)) return null;
  }
  return result;
}
