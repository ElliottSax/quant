/**
 * Value at Risk (VaR) and Conditional VaR / Expected Shortfall (CVaR/ES)
 * from a pasted periodic return series, computed two ways side by side so
 * the gap between them is visible rather than hidden behind one number.
 *
 * 1. Parametric (variance-covariance / delta-normal) VaR — Jorion, P.
 *    (2006), "Value at Risk: The New Benchmark for Managing Financial
 *    Risk", 3rd ed., McGraw-Hill. The standard closed form under the
 *    assumption that periodic returns are i.i.d. normal:
 *      VaR_c = (z_c * sigma - mu) * sqrt(t) * V0
 *    where z_c = Phi^-1(c) is the one-sided standard-normal quantile at
 *    confidence c, mu/sigma are the sample mean/stdev of the return
 *    series, and the sqrt(t) horizon scaling is the same square-root-of-
 *    time convention already used (and cited) for annualization in
 *    riskAdjustedReturn.ts — valid under the same i.i.d. assumption.
 *
 * 2. Parametric CVaR / Expected Shortfall — closed form for the normal
 *    case, McNeil, A.J., Frey, R. & Embrechts, P. (2015), "Quantitative
 *    Risk Management: Concepts, Techniques and Tools", 2nd ed., Princeton
 *    University Press (Prop. 2.16):
 *      CVaR_c = (sigma * phi(z_c) / (1 - c) - mu) * sqrt(t) * V0
 *    Derivation: let L = -R be the loss on a unit position, so
 *    L ~ N(-mu, sigma^2). CVaR is E[L | L >= VaR_c], i.e. sigma times the
 *    mean of a standard normal Z conditioned on its own upper tail,
 *    shifted by -mu. The standard truncated-normal identity for the upper
 *    tail of Z ~ N(0,1) is:
 *      E[Z | Z >= z_c] = phi(z_c) / (1 - Phi(z_c)) = phi(z_c) / (1 - c)
 *    (phi is the standard normal PDF, phi(x) = (1/sqrt(2*pi)) * e^(-x^2/2);
 *    the denominator is 1-c because Phi(z_c) = c by definition of z_c).
 *    Substituting gives the formula above. When sigma = 0 (a constant
 *    return series) both formulas collapse to -mu * sqrt(t) * V0 with no
 *    special-casing needed, since every sigma-scaled term vanishes on its
 *    own.
 *
 * 3. Historical (non-parametric) VaR — no distributional assumption, just
 *    the empirical lower tail of the pasted series:
 *      VaR_c = -Q_(1-c)(returns) * V0
 *    Quantile estimation uses linear interpolation between order
 *    statistics ("Type 7"), Hyndman, R.J. & Fan, Y. (1996), "Sample
 *    Quantiles in Statistical Packages", The American Statistician 50(4)
 *    — the default method in R's quantile() and NumPy's np.percentile.
 *    Stated explicitly because the sample-quantile literature has several
 *    competing conventions that disagree at small n. Unlike the parametric
 *    method, this is NOT scaled by sqrt(t): the sqrt-time rule is a
 *    property of i.i.d. normal returns, not of an empirical sample, so
 *    scaling it here would smuggle the same distributional assumption
 *    this method exists to avoid. It answers the question "how bad was
 *    the worst ~(1-c) share of periods actually in this data," at the
 *    periodicity the data was entered in.
 *
 * 4. Historical CVaR / Expected Shortfall — Rockafellar, R.T. & Uryasev,
 *    S. (2000), "Optimization of Conditional Value-at-Risk", Journal of
 *    Risk 2(3): the mean of every observed return at or below the
 *    historical VaR threshold, negated and scaled by V0.
 *
 * Small-sample handling: with only 5-10% of observations in either tail,
 * a 99% historical VaR/CVaR is estimated from a literal handful of points.
 * `expectedTailCount` (n * (1-c)) is surfaced directly rather than hidden,
 * and `sparseTailWarning` fires when it drops below 1 — the point at which
 * the "99th percentile" is really just an extrapolation from the single
 * worst observation in the sample.
 *
 * Pure functions over a caller-supplied return series and portfolio value
 * — no market data is read.
 */

export interface VarInputs {
  /** Current portfolio value in dollars. Must be > 0. */
  portfolioValue: number;
  /** One-sided confidence level. */
  confidence: 0.9 | 0.95 | 0.99;
  /** Risk horizon in the same periodicity as the return series (e.g. days, if returns are daily). Must be a positive integer. */
  horizonDays: number;
  /** Periodic returns as decimals, e.g. 0.02 for +2%. */
  returns: number[];
}

export interface VarResult {
  n: number;
  meanPerPeriod: number;
  stdevPerPeriod: number;
  /** One-sided standard-normal quantile used for the parametric methods. */
  z: number;
  /** Parametric (variance-covariance) VaR in dollars, scaled to the horizon. */
  parametricVaR: number;
  /** Parametric CVaR / Expected Shortfall in dollars, scaled to the horizon. */
  parametricCVaR: number;
  /** Historical (empirical) VaR in dollars, at the return series' native periodicity. */
  historicalVaR: number;
  /** Historical CVaR / Expected Shortfall in dollars, at the return series' native periodicity. */
  historicalCVaR: number;
  /** The raw (1-c) quantile return used for the historical VaR threshold, as a decimal. */
  historicalThresholdReturn: number;
  /** Expected number of observations in the tail: n * (1 - c). Can be well under 1. */
  expectedTailCount: number;
  /** Actual number of observed returns at or below the historical VaR threshold, used for historical CVaR. */
  actualTailCount: number;
  /** True when n < 20 — flagged rather than silently shown as precise. */
  smallSampleWarning: boolean;
  /** True when expectedTailCount < 1 — the historical tail estimate rests on essentially zero real observations. */
  sparseTailWarning: boolean;
  /**
   * How much larger historical VaR is than parametric VaR, as a fraction
   * (0.20 = 20% larger). Null when parametricVaR <= 0 (no meaningful
   * ratio to take). A large positive value means the data has fatter
   * tails than a normal distribution assumes, and the parametric number
   * is understating real risk.
   */
  fatTailGap: number | null;
}

export function validateVar(i: VarInputs): string | null {
  if (!Number.isFinite(i.portfolioValue) || i.portfolioValue <= 0) {
    return 'Portfolio value must be greater than $0.';
  }
  if (!Number.isFinite(i.horizonDays) || i.horizonDays < 1 || !Number.isInteger(i.horizonDays)) {
    return 'Horizon must be a whole number of periods, 1 or more.';
  }
  if (!Array.isArray(i.returns) || i.returns.length < 2) {
    return 'Enter at least 2 periodic returns.';
  }
  if (i.returns.some((r) => !Number.isFinite(r))) {
    return 'Every return must be a number.';
  }
  if (i.returns.some((r) => r <= -1)) {
    return 'A return of -100% or worse would zero or invert the portfolio value — check your inputs.';
  }
  return null;
}

/** One-sided standard-normal quantiles Phi^-1(c), to double precision. */
const Z_VAR: Record<VarInputs['confidence'], number> = {
  0.9: 1.2815515655446004,
  0.95: 1.6448536269514722,
  0.99: 2.3263478740408408,
};

function mean(xs: number[]): number {
  return xs.reduce((s, x) => s + x, 0) / xs.length;
}

/** Sample standard deviation (n-1 denominator) — the series is a sample, not a population. */
function sampleStdev(xs: number[]): number {
  const m = mean(xs);
  const sumSq = xs.reduce((s, x) => s + (x - m) * (x - m), 0);
  return xs.length > 1 ? Math.sqrt(sumSq / (xs.length - 1)) : 0;
}

/** Standard normal PDF, phi(x) = (1/sqrt(2*pi)) * e^(-x^2/2). */
function stdNormalPdf(x: number): number {
  return Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI);
}

/**
 * Type-7 (linear-interpolation) sample quantile — Hyndman & Fan (1996),
 * the default in R's quantile() and NumPy's np.percentile. `sorted` must
 * already be sorted ascending. p in [0, 1].
 */
function quantileType7(sorted: number[], p: number): number {
  const n = sorted.length;
  const h = (n - 1) * p;
  const lo = Math.floor(h);
  const hi = Math.ceil(h);
  if (lo === hi) return sorted[lo];
  return sorted[lo] + (h - lo) * (sorted[hi] - sorted[lo]);
}

export function computeVar(i: VarInputs): VarResult | null {
  if (validateVar(i) !== null) return null;

  const { portfolioValue, confidence, horizonDays, returns } = i;
  const n = returns.length;
  const z = Z_VAR[confidence];
  const sqrtT = Math.sqrt(horizonDays);

  const meanPerPeriod = mean(returns);
  const stdevPerPeriod = sampleStdev(returns);

  const parametricVaR = (z * stdevPerPeriod - meanPerPeriod) * sqrtT * portfolioValue;
  const parametricCVaR = ((stdevPerPeriod * stdNormalPdf(z)) / (1 - confidence) - meanPerPeriod) * sqrtT * portfolioValue;

  const sorted = [...returns].sort((a, b) => a - b);
  const p = 1 - confidence;
  const historicalThresholdReturn = quantileType7(sorted, p);
  const historicalVaR = -historicalThresholdReturn * portfolioValue;

  const tailReturns = sorted.filter((r) => r <= historicalThresholdReturn);
  const actualTailCount = tailReturns.length;
  const historicalCVaR = -mean(tailReturns) * portfolioValue;

  const expectedTailCount = n * (1 - confidence);

  const result: VarResult = {
    n,
    meanPerPeriod,
    stdevPerPeriod,
    z,
    parametricVaR,
    parametricCVaR,
    historicalVaR,
    historicalCVaR,
    historicalThresholdReturn,
    expectedTailCount,
    actualTailCount,
    smallSampleWarning: n < 20,
    sparseTailWarning: expectedTailCount < 1,
    fatTailGap: parametricVaR > 0 ? historicalVaR / parametricVaR - 1 : null,
  };

  for (const [k, v] of Object.entries(result)) {
    if (typeof v === 'number' && !Number.isFinite(v)) return null;
  }
  return result;
}
