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
 * Ulcer Index / Pain Index — Peter G. Martin (1987). Where max drawdown
 *   captures only the single worst peak-to-trough point, these summarize
 *   the WHOLE drawdown path: Ulcer Index is the root-mean-square of the
 *   percentage-drawdown series (penalizes depth and duration together),
 *   Pain Index is the plain mean of the same series. Two strategies with
 *   identical max drawdown can score very differently here if one
 *   recovers quickly and the other stays underwater a long time.
 *
 * Probabilistic Sharpe Ratio (PSR) — Bailey, D.H. & Lopez de Prado, M.
 *   (2012), "The Sharpe Ratio Efficient Frontier", Journal of Risk 15(2):
 *   PSR(SR*) = Phi[ (SR - SR*)*sqrt(n-1) / sqrt(1 - skew*SR + ((kurt-1)/4)*SR^2) ]
 *   where SR is the PER-PERIOD (non-annualized) Sharpe ratio, SR* is a
 *   benchmark (0 here — "is there any real skill at all"), n is the
 *   number of observations, skew/kurtosis are the POPULATION (biased,
 *   divide-by-n) third/fourth standardized moments of the return series
 *   per the original paper's own convention (kurtosis non-excess — a
 *   normal distribution scores 3) — note this differs from this file's
 *   own sample (n-1) convention for stdevPerPeriod above; both are
 *   individually correct for what they're each computing, they're just
 *   different, well-established statistical conventions. This
 *   implementation was verified before use by reproducing the original
 *   paper's own worked example (SR=0.458, n=29): normal returns
 *   (skew=0, kurtosis=3) -> PSR=0.989; non-normal (skew=-2.448,
 *   kurtosis=10.164) -> PSR=0.934, matching to 3 decimal places.
 *   PSR answers a different question than Sharpe itself: not "how good
 *   is the risk-adjusted return" but "how confident can you be that the
 *   TRUE Sharpe ratio is actually above the benchmark, given how few
 *   observations there are and how non-normal the distribution is." A
 *   short, lumpy, fat-tailed track record can post an impressive Sharpe
 *   ratio and still score a low PSR.
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
  /** Root-mean-square of the percentage-drawdown series (Martin, 1987). */
  ulcerIndex: number;
  /** Mean of the percentage-drawdown series (Martin, 1987). */
  painIndex: number;
  /** Population (biased) skewness of the return series. */
  skewness: number;
  /** Population (biased) non-excess kurtosis of the return series -- a normal distribution scores 3. */
  kurtosis: number;
  /** Probability the TRUE Sharpe ratio exceeds 0, given sample size and distribution shape. Null when sharpe itself is null (zero volatility). */
  probabilisticSharpeRatio: number | null;
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

/** Population (n denominator) standard deviation -- the convention the PSR literature uses for skew/kurtosis. */
function populationStdev(xs: number[], m = mean(xs)): number {
  return Math.sqrt(mean(xs.map((x) => (x - m) ** 2)));
}

/** Standard normal CDF via the Abramowitz & Stegun 7.1.26 approximation (max error ~1.5e-7). */
function normalCdf(z: number): number {
  const sign = z < 0 ? -1 : 1;
  const x = Math.abs(z) / Math.SQRT2;
  const t = 1 / (1 + 0.3275911 * x);
  const y = 1 - ((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x);
  return 0.5 * (1 + sign * y);
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
  // Percentage-drawdown series (<=0), one value per period after the start,
  // for Ulcer Index / Pain Index -- maxDrawdown above only keeps the worst
  // single point, this keeps the whole path.
  const drawdownPct: number[] = [];
  for (const v of equityCurve) {
    if (v > peak) peak = v;
    const dd = (peak - v) / peak;
    if (dd > maxDrawdown) maxDrawdown = dd;
    drawdownPct.push(-dd * 100);
  }
  const ulcerIndex = Math.sqrt(mean(drawdownPct.map((d) => d * d)));
  const painIndex = mean(drawdownPct.map((d) => Math.abs(d)));

  const finalEquity = equityCurve[equityCurve.length - 1];
  const annualizedReturn = finalEquity > 0 ? Math.pow(finalEquity, periodsPerYear / n) - 1 : -1;
  const calmar = maxDrawdown > 0 ? annualizedReturn / maxDrawdown : null;

  // Population skewness/kurtosis of the raw return series, for PSR.
  const popStdev = populationStdev(returns, meanPerPeriod);
  const skewness = popStdev === 0 ? 0 : mean(returns.map((r) => (r - meanPerPeriod) ** 3)) / popStdev ** 3;
  const kurtosis = popStdev === 0 ? 3 : mean(returns.map((r) => (r - meanPerPeriod) ** 4)) / popStdev ** 4;

  // PSR needs the PER-PERIOD Sharpe ratio at the same periodicity as n --
  // recover it from the already-annualized `sharpe` above rather than
  // recomputing a second, potentially-inconsistent Sharpe estimate.
  let probabilisticSharpeRatio: number | null = null;
  if (sharpe !== null) {
    const periodSharpe = sharpe / sqrtAnnualize;
    const psrDenom = Math.sqrt(Math.max(0, 1 - skewness * periodSharpe + ((kurtosis - 1) / 4) * periodSharpe ** 2));
    const psrZ = psrDenom === 0 ? 0 : (periodSharpe * Math.sqrt(n - 1)) / psrDenom;
    probabilisticSharpeRatio = normalCdf(psrZ);
  }

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
    ulcerIndex,
    painIndex,
    skewness,
    kurtosis,
    probabilisticSharpeRatio,
  };

  for (const [k, v] of Object.entries(result)) {
    if (k === 'equityCurve') continue;
    if (typeof v === 'number' && !Number.isFinite(v)) return null;
  }
  return result;
}
