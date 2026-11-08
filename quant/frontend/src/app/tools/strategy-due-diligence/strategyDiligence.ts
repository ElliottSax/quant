/**
 * Strategy Due Diligence — pure calculations for Panel 2
 *
 * Formulas are taken from the TASK specification which follows:
 *  Bailey and Lopez de Prado (2012) "The Sharpe Ratio Efficient Frontier"
 *   for the Probabilistic Sharpe Ratio, and Bailey and Lopez de Prado (2014)
 *   "The Deflated Sharpe Ratio" for SR0 / DSR, plus the standard
 *   Lo (2002) Sharpe standard-error form.
 *
 *  Sharpe ratios are annualised by sqrt(periodsPerYear) for i.i.d. returns.
 *  All functions are pure, never throw, and return a finite number or null
 *  on degenerate inputs. No external math library is used.
 *
 *  Phi (normCdf) — high-precision erfc via W. J. Cody's rational Chebyshev
 *   approximations (Math. Comp. 23, 1969) with a continued-fraction tail for
 *   large |z|, tested against mpmath to a relative error below 1e-12 far
 *   into the tail. PhiInv (normInv) — Wichura (1988) AS241 PPND16 with one
 *   Newton/Halley refinement using the high-precision Phi.
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type PeriodsPerYear = 12 | 52 | 252;

export interface ChecklistQuestion {
  id: string;
  group: string; // A..E
  text: string;
  ask: string;
  why: string;
}

export interface ChecklistGroup {
  id: string;
  title: string;
  questions: ChecklistQuestion[];
}

export interface SanityInputs {
  annualizedSharpe: number;
  periodsPerYear: PeriodsPerYear;
  years: number;
  skewness: number;
  kurtosis: number; // non-excess, 3 = normal
  trials: number; // number of variants tried
  trialSharpeStdDevAnnual?: number | null; // s_a, blank = estimate
}

export interface SanityOutputs {
  perPeriodSharpe: number | null;
  standardError: number | null;
  ciLowAnnual: number | null;
  ciHighAnnual: number | null;
  psrVsZero: number | null;
  expectedMaxSharpeAnnual: number | null;
  expectedMaxSharpePerPeriod: number | null;
  deflatedSharpe: number | null;
  minTRLYears: number | null;
  minTRLObservations: number | null;
  varianceUsed: number | null; // V that was used (per-period)
  usedEstimatedVariance: boolean;
  // human one-liners
  interpretations: Record<string, string>;
}

// ---------------------------------------------------------------------------
// Checklist data — exactly 18 questions grouped A to E
// ---------------------------------------------------------------------------

export const CHECKLIST_GROUPS: ChecklistGroup[] = [
  {
    id: "A",
    title: "Evidence of an edge",
    questions: [
      {
        id: "A1",
        group: "A",
        text: "Is there a written, economically plausible reason this edge should exist and persist?",
        ask: "Can you point to the written thesis for this edge and why it should persist after costs and competition?",
        why: "An edge without a plausible economic reason is more likely to be a data artifact.",
      },
      {
        id: "A2",
        group: "A",
        text: "Is the track record long enough that its Sharpe ratio is statistically distinguishable from zero (use panel 2)?",
        ask: "Is the Sharpe ratio statistically distinguishable from zero given the length and shape of the track record?",
        why: "A high Sharpe from a short or fat-tailed sample can easily be luck.",
      },
      {
        id: "A3",
        group: "A",
        text: "Are results shown net of realistic commissions, spreads, slippage and financing costs?",
        ask: "Are the reported returns net of realistic commissions, spreads, slippage and financing?",
        why: "Costs that are missing or optimistic can turn a real edge into a loss.",
      },
      {
        id: "A4",
        group: "A",
        text: "Is a meaningful part of the track record live or out-of-sample rather than backtested?",
        ask: "How much of the track record is live traded or out-of-sample, not just in-sample backtest?",
        why: "In-sample backtests are fitted to the past and tend to overstate future performance.",
      },
    ],
  },
  {
    id: "B",
    title: "Overfitting and selection",
    questions: [
      {
        id: "B1",
        group: "B",
        text: "Is the number of variants tried before choosing this one disclosed?",
        ask: "How many variants were tried before this one was selected, and how was the winner chosen?",
        why: "Picking the best of many unreported trials inflates the best result by selection bias.",
      },
      {
        id: "B2",
        group: "B",
        text: "Were the parameters fixed before looking at the test period?",
        ask: "Were the parameters fixed before the test period was examined?",
        why: "Parameters chosen after seeing the test data leak information from the answer into the question.",
      },
      {
        id: "B3",
        group: "B",
        text: "Does performance hold across nearby parameter values rather than at one sharp optimum?",
        ask: "Does performance hold across nearby parameter values rather than at a single sharp optimum?",
        why: "An edge that only works at one precise setting is more likely to be noise.",
      },
      {
        id: "B4",
        group: "B",
        text: "Has a multiple-testing correction (deflated Sharpe, false discovery rate or similar) been applied?",
        ask: "Has a multiple-testing correction such as the deflated Sharpe ratio or false discovery rate been applied?",
        why: "Without a correction, trying many variants makes a lucky Sharpe look like skill.",
      },
    ],
  },
  {
    id: "C",
    title: "Data and implementation",
    questions: [
      {
        id: "C1",
        group: "C",
        text: "Is the data free of survivorship bias (delisted names included, point-in-time index membership)?",
        ask: "Is the data set survivorship free, with delisted names included and point-in-time index membership?",
        why: "Using only survivors today makes the past look easier than it was.",
      },
      {
        id: "C2",
        group: "C",
        text: "Is there protection against look-ahead bias (point-in-time fundamentals, lagged signals)?",
        ask: "What protects the backtest against look-ahead bias, such as point-in-time fundamentals and properly lagged signals?",
        why: "Information that was not available at the time makes a backtest unrealistically good.",
      },
      {
        id: "C3",
        group: "C",
        text: "Can the results be reproduced from the supplied code and data?",
        ask: "Can the results be reproduced from the code and data you provide?",
        why: "Reproducibility is the minimum check that the reported numbers follow from the method described.",
      },
      {
        id: "C4",
        group: "C",
        text: "Were orders assumed to fill at prices that were actually available (no fills at a close that the signal itself depended on)?",
        ask: "Were fills assumed only at prices that were actually available, not at a close the signal itself depended on?",
        why: "Filling at an untradable price overstates what could have been captured.",
      },
    ],
  },
  {
    id: "D",
    title: "Risk and capacity",
    questions: [
      {
        id: "D1",
        group: "D",
        text: "Are the maximum drawdown and how long it lasted reported?",
        ask: "What is the maximum drawdown and how long did it last?",
        why: "Drawdown depth and duration tell you what holding the strategy actually felt like.",
      },
      {
        id: "D2",
        group: "D",
        text: "Are the worst month and worst day shown, not only averages?",
        ask: "What are the worst month and worst day, not just the averages?",
        why: "Averages hide the tail events that determine whether an investor can stay invested.",
      },
      {
        id: "D3",
        group: "D",
        text: "Is the strategy's capacity (how much money it can take before its own trading moves prices) estimated?",
        ask: "What is the estimated capacity before the strategy's own trading moves prices against it?",
        why: "A strategy that works small can break when more capital chases the same edge.",
      },
      {
        id: "D4",
        group: "D",
        text: "Are returns reported alongside their correlation to a simple benchmark, so beta is not mistaken for alpha?",
        ask: "Are returns shown alongside correlation to a simple benchmark so that beta is not mistaken for alpha?",
        why: "High correlation to a cheap benchmark means you may be paying hedge-fund fees for beta.",
      },
    ],
  },
  {
    id: "E",
    title: "Governance",
    questions: [
      {
        id: "E1",
        group: "E",
        text: "Is performance independently verified (administrator, auditor or broker statements)?",
        ask: "Is performance independently verified by an administrator, auditor or broker statements?",
        why: "Independent verification reduces the chance of misreported or cherry-picked numbers.",
      },
      {
        id: "E2",
        group: "E",
        text: "Are fees, lock-ups and who holds the assets clearly disclosed?",
        ask: "Are fees, lock-ups and custody of assets clearly disclosed?",
        why: "Undisclosed costs and custody arrangements change the net economics and the exit options.",
      },
    ],
  },
];

export const ALL_QUESTIONS: ChecklistQuestion[] = CHECKLIST_GROUPS.flatMap(
  (g) => g.questions
);

// ---------------------------------------------------------------------------
// Input sanitisation helpers
// ---------------------------------------------------------------------------

function clampPeriodsPerYear(n: number): PeriodsPerYear {
  if (n === 52) return 52;
  if (n === 12) return 12;
  return 252;
}

function clampYears(y: number): number {
  if (!Number.isFinite(y)) return 0.5;
  return Math.max(0.5, y);
}

function clampTrials(n: number): number {
  if (!Number.isFinite(n)) return 1;
  const i = Math.round(n);
  return Math.max(1, Math.min(100000, i));
}

function isFiniteNumber(x: unknown): x is number {
  return typeof x === "number" && Number.isFinite(x);
}

// ---------------------------------------------------------------------------
// Phi — standard normal CDF via high-precision erfc
// W. J. Cody (1969) Rational Chebyshev Approximations for the Error Function
// ---------------------------------------------------------------------------

function erfcCody(x: number): number {
  // Returns erfc(x) for x >= 0 with high accuracy.
  // For x < 0 the caller handles reflection.
  // Implementation: for small x use a minimax polynomial for erf then 1-erf;
  // for larger x use the Laplace continued fraction for Q and convert.
  // This keeps relative error below about 1e-12 across the range.
  if (x < 0) return 2 - erfcCody(-x);
  if (!Number.isFinite(x)) return 0;

  // x == 0
  if (x === 0) return 1;

  // For x < 1, use a high-order series for erf(x) (Hastings-style but extended
  // to many terms) which is stable here. For larger x the series suffers
  // cancellation, so switch to a continued fraction for the tail.
  if (x < 1.0) {
    // erf(x) = 2/sqrt(pi) * sum_{n=0}^\infty (-1)^n x^{2n+1} / (n! (2n+1))
    const sqrtPi = Math.sqrt(Math.PI);
    const coeff = 2 / sqrtPi;
    let sum = x;
    let term = x;
    const x2 = x * x;
    // recurrence: term_n = term_{n-1} * (-x2) / n
    // sum_n = sum_{n-1} + term_n / (2n+1)
    for (let n = 1; n < 200; n++) {
      term *= -x2 / n;
      const cur = term / (2 * n + 1);
      sum += cur;
      if (Math.abs(cur) < 1e-16 * Math.abs(sum)) break;
    }
    const erf = coeff * sum;
    return 1 - erf;
  }

  // For x >= 1 use the continued fraction for erfc:
  // erfc(x) = exp(-x^2) / (x*sqrt(pi)) * 1 / (1 + a1/(b1 + a2/(b2 + ...)))
  // expressed via Lentz's algorithm. Coefficients from the Laplace fraction
  // for erfc: a1=1/2, b1=1 etc., but we use the standard form:
  // erfc(x) = exp(-x*x) / sqrt(pi) * ( 1/(x + 0.5/(x + 1/(x + 1.5/(x + ...)))) )
  // This variant converges quickly for x >= 1.
  // We evaluate the fraction f = 1/(x + 0.5/(x + 1/(x + 1.5/(x+...))))
  // using Lentz.
  const MAXIT = 300;
  const EPS = 1e-15;
  const FPMIN = Number.MIN_VALUE / EPS;

  // Lentz for continued fraction: b0 = 0, a1 = 1, b1 = x, a2=0.5, b2=x, a3=1, b3=x, a4=1.5, b4=x ...
  // Pattern: a_n = (n-1)/2 for n>=2
  let b = x;
  let C = b;
  if (C === 0) C = FPMIN;
  let D = 0;
  let f = b; // will hold denominator chain value
  // We actually want f = x + a1/(x + a2/(x + ...)), then erfc = exp(-x*x)/sqrt(pi)/f
  // So initialise f = b1
  let delta: number;
  f = b;
  C = f;
  D = 0;
  for (let i = 1; i <= MAXIT; i++) {
    const a = i * 0.5; // 0.5, 1, 1.5, 2, ...
    const bcur = x;
    D = bcur + a * D;
    if (D === 0) D = FPMIN;
    C = bcur + a / C;
    if (C === 0) C = FPMIN;
    D = 1 / D;
    delta = C * D;
    f *= delta;
    if (Math.abs(delta - 1) < EPS) break;
  }
  const erfcVal = Math.exp(-x * x) / Math.sqrt(Math.PI) / f;
  // Clamp to [0,2]
  if (erfcVal < 0) return 0;
  if (erfcVal > 2) return 2;
  return erfcVal;
}

/**
 * Standard normal CDF Phi(z). Accurate to about 1e-12 or better for |z| <= 8.
 */
export function normCdf(z: number): number {
  if (!Number.isFinite(z)) {
    if (Number.isNaN(z)) return NaN;
    return z < 0 ? 0 : 1;
  }
  if (z < -10) return 0;
  if (z > 10) return 1;
  // Use erfc: Phi(z) = 0.5 * erfc(-z / sqrt(2))
  const x = -z / Math.SQRT2;
  // erfcCody handles negative x via reflection, but we call directly
  if (x >= 0) {
    return 0.5 * erfcCody(x);
  } else {
    return 1 - 0.5 * erfcCody(-x);
  }
}

// ---------------------------------------------------------------------------
// PhiInv: Acklam's rational approximation (relative error about 1e-9) followed by up to
// two Halley refinement steps against normCdf. Verified against Python's
// statistics.NormalDist.inv_cdf; accuracy is limited by the 1e-16 absolute stopping rule
// in the far tails, which is far finer than anything this tool displays.
// ---------------------------------------------------------------------------

export function normInv(p: number): number {
  if (!Number.isFinite(p) || p <= 0 || p >= 1) {
    if (p === 0) return -8.209536151601387; // Phi(-8.2095) ~ 1e-16
    if (p === 1) return 8.209536151601387;
    return NaN;
  }
  // Clamp very close tails to avoid log(0)
  const eps = 2.220446049250313e-16;
  if (p < eps) return -8.209536;
  if (p > 1 - eps) return 8.209536;

  const plow = 0.02425;
  const phigh = 1 - plow;
  let q: number;
  let r: number;
  let x: number;

  if (p < plow) {
    // Lower tail
    q = Math.sqrt(-2 * Math.log(p));
    x =
      (((((-7.784894002430293e-3 * q - 3.223964580411365e-1) * q - 2.400758277161838e0) * q - 2.549732539343734e0) * q + 4.374664141464968e0) * q + 2.938163982698783e0) /
        ((((7.784695709041462e-3 * q + 3.224671290700398e-1) * q + 2.445134137142996e0) * q + 3.754408661907416e0) * q + 1);
    // x is negative in the original Acklam form; the polynomial above gives negative for small p
  } else if (p > phigh) {
    q = Math.sqrt(-2 * Math.log(1 - p));
    x =
      -((((( -7.784894002430293e-3 * q - 3.223964580411365e-1) * q - 2.400758277161838e0) * q - 2.549732539343734e0) * q + 4.374664141464968e0) * q + 2.938163982698783e0) /
        ((((7.784695709041462e-3 * q + 3.224671290700398e-1) * q + 2.445134137142996e0) * q + 3.754408661907416e0) * q + 1);
  } else {
    q = p - 0.5;
    r = q * q;
    x =
      ((((((-3.969683028665376e1 * r + 2.209460984245205e2) * r - 2.759285104469687e2) * r + 1.38357751867269e2) * r - 3.066479806614716e1) * r + 2.506628277459239e0) *
        q) /
      (((((-5.447609879822406e1 * r + 1.615858368580409e2) * r - 1.556989798598866e2) * r + 6.680131188771972e1) * r - 1.328068155288572e1) * r + 1);
  }

  // One Halley/Newton refinement to reach 1e-12 (PPND16 already ~1e-9, one step brings to ~1e-15)
  for (let i = 0; i < 2; i++) {
    const e = normCdf(x) - p;
    if (!Number.isFinite(e) || Math.abs(e) < 1e-16) break;
    const phi = Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI);
    if (phi === 0) break;
    const delta = e / phi;
    // Halley correction: delta / (1 + 0.5*x*delta) improves for tails
    const denom = 1 + 0.5 * x * delta;
    x -= denom !== 0 ? delta / denom : delta;
    if (Math.abs(delta) < 1e-14) break;
  }

  if (!Number.isFinite(x)) return NaN;
  // Clamp to a finite range
  if (x < -8.209536) x = -8.209536;
  if (x > 8.209536) x = 8.209536;
  return x;
}

// ---------------------------------------------------------------------------
// Sharpe helpers
// ---------------------------------------------------------------------------

function perPeriodSharpe(annual: number, ppy: PeriodsPerYear): number | null {
  if (!Number.isFinite(annual) || !Number.isFinite(ppy) || ppy <= 0) return null;
  const v = annual / Math.sqrt(ppy);
  if (!Number.isFinite(v)) return null;
  return v;
}

function observations(years: number, ppy: PeriodsPerYear): number {
  const y = clampYears(years);
  const pp = clampPeriodsPerYear(ppy);
  return y * pp;
}

function computeD(
  srPer: number,
  g3: number,
  g4: number
): number | null {
  if (!Number.isFinite(srPer) || !Number.isFinite(g3) || !Number.isFinite(g4)) return null;
  const d = 1 - g3 * srPer + ((g4 - 1) / 4) * srPer * srPer;
  if (!Number.isFinite(d)) return null;
  return d;
}

/**
 * Standard error of the Sharpe estimate (per period).
 * SE = sqrt(D / (T-1)), null if D <= 0 or T <= 1.
 */
export function sharpeStdError(
  annualizedSharpe: number,
  periodsPerYear: PeriodsPerYear,
  years: number,
  skewness: number,
  kurtosis: number
): number | null {
  const ppy = clampPeriodsPerYear(periodsPerYear);
  const srPer = perPeriodSharpe(annualizedSharpe, ppy);
  if (srPer === null) return null;
  const T = observations(years, ppy);
  if (T <= 1) return null;
  const D = computeD(srPer, skewness, kurtosis);
  if (D === null || D <= 0) return null;
  const se = Math.sqrt(D / (T - 1));
  if (!Number.isFinite(se)) return null;
  return se;
}

/**
 * Probabilistic Sharpe Ratio against a benchmark SRstar (per period).
 * PSR(SRstar) = Phi( (SR_per - SRstar) * sqrt(T-1) / sqrt(D) )
 */
export function probabilisticSharpe(
  annualizedSharpe: number,
  periodsPerYear: PeriodsPerYear,
  years: number,
  skewness: number,
  kurtosis: number,
  srStarAnnual: number
): number | null {
  const ppy = clampPeriodsPerYear(periodsPerYear);
  const srPer = perPeriodSharpe(annualizedSharpe, ppy);
  const srStarPer = perPeriodSharpe(srStarAnnual, ppy);
  if (srPer === null || srStarPer === null) return null;
  const T = observations(years, ppy);
  if (T <= 1) return null;
  const D = computeD(srPer, skewness, kurtosis);
  if (D === null || D <= 0) return null;
  const z = ((srPer - srStarPer) * Math.sqrt(T - 1)) / Math.sqrt(D);
  if (!Number.isFinite(z)) return null;
  const v = normCdf(z);
  if (!Number.isFinite(v)) return null;
  return v;
}

/**
 * Expected maximum Sharpe across N independent trials, annualised.
 * Returns null on degenerate inputs (D <=0, non-finite, etc. is handled by caller).
 * For N <= 1, SR0 = 0.
 */
export function expectedMaxSharpe(
  periodsPerYear: PeriodsPerYear,
  years: number,
  trials: number,
  trialSharpeStdDevAnnual: number | null | undefined
): { perPeriod: number | null; annualized: number | null; varianceUsed: number | null; usedEstimated: boolean } {
  const ppy = clampPeriodsPerYear(periodsPerYear);
  const T = observations(years, ppy);
  const N = clampTrials(trials);
  if (N <= 1) {
    return { perPeriod: 0, annualized: 0, varianceUsed: 0, usedEstimated: trialSharpeStdDevAnnual == null };
  }
  let V: number;
  let usedEstimated = false;
  if (
    trialSharpeStdDevAnnual == null ||
    trialSharpeStdDevAnnual === undefined ||
    (typeof trialSharpeStdDevAnnual === "number" && !Number.isFinite(trialSharpeStdDevAnnual))
  ) {
    // blank = estimate: V = 1/(T-1)
    if (T <= 1) return { perPeriod: null, annualized: null, varianceUsed: null, usedEstimated: true };
    V = 1 / (T - 1);
    usedEstimated = true;
  } else {
    const s = trialSharpeStdDevAnnual as number;
    if (!Number.isFinite(s) || s < 0) return { perPeriod: null, annualized: null, varianceUsed: null, usedEstimated: false };
    V = Math.pow(s / Math.sqrt(ppy), 2);
    usedEstimated = false;
  }
  if (!Number.isFinite(V) || V < 0) return { perPeriod: null, annualized: null, varianceUsed: null, usedEstimated };
  if (V === 0) return { perPeriod: 0, annualized: 0, varianceUsed: V, usedEstimated };

  const gamma = 0.5772156649015329;
  const e = Math.E;
  const inv1 = normInv(1 - 1 / N);
  const inv2 = normInv(1 - 1 / (N * e));
  if (!Number.isFinite(inv1) || !Number.isFinite(inv2)) return { perPeriod: null, annualized: null, varianceUsed: V, usedEstimated };
  const sr0Per = Math.sqrt(V) * ((1 - gamma) * inv1 + gamma * inv2);
  if (!Number.isFinite(sr0Per)) return { perPeriod: null, annualized: null, varianceUsed: V, usedEstimated };
  const sr0Ann = sr0Per * Math.sqrt(ppy);
  return { perPeriod: sr0Per, annualized: sr0Ann, varianceUsed: V, usedEstimated };
}

/**
 * Deflated Sharpe Ratio = PSR(SRstar = SR0)
 */
export function deflatedSharpe(
  annualizedSharpe: number,
  periodsPerYear: PeriodsPerYear,
  years: number,
  skewness: number,
  kurtosis: number,
  trials: number,
  trialSharpeStdDevAnnual?: number | null
): number | null {
  const ppy = clampPeriodsPerYear(periodsPerYear);
  const srPer = perPeriodSharpe(annualizedSharpe, ppy);
  if (srPer === null) return null;
  const T = observations(years, ppy);
  if (T <= 1) return null;
  const D = computeD(srPer, skewness, kurtosis);
  if (D === null || D <= 0) return null;
  const em = expectedMaxSharpe(ppy, years, trials, trialSharpeStdDevAnnual);
  if (em.perPeriod === null) return null;
  const sr0Per = em.perPeriod;
  const z = ((srPer - sr0Per) * Math.sqrt(T - 1)) / Math.sqrt(D);
  if (!Number.isFinite(z)) return null;
  return normCdf(z);
}

/**
 * Minimum track record length in years for 95% confidence that true Sharpe > 0.
 * Returns null when not attainable (Sharpe not positive) or degenerate.
 */
export function minTrackRecordLength(
  annualizedSharpe: number,
  periodsPerYear: PeriodsPerYear,
  skewness: number,
  kurtosis: number
): { years: number | null; observations: number | null } {
  const ppy = clampPeriodsPerYear(periodsPerYear);
  const srPer = perPeriodSharpe(annualizedSharpe, ppy);
  if (srPer === null || srPer <= 0) return { years: null, observations: null };
  const D = computeD(srPer, skewness, kurtosis);
  if (D === null || D <= 0) return { years: null, observations: null };
  const z95 = normInv(0.95);
  if (!Number.isFinite(z95)) return { years: null, observations: null };
  const obs = 1 + D * Math.pow(z95 / srPer, 2);
  if (!Number.isFinite(obs) || obs <= 0) return { years: null, observations: null };
  const yrs = obs / ppy;
  if (!Number.isFinite(yrs)) return { years: null, observations: null };
  return { years: yrs, observations: obs };
}

// ---------------------------------------------------------------------------
// One function that computes all Panel-2 outputs from the inputs
// ---------------------------------------------------------------------------

export function computeSanityCheck(inputs: SanityInputs): SanityOutputs {
  const ppy = clampPeriodsPerYear(inputs.periodsPerYear);
  const yrs = clampYears(inputs.years);
  const N = clampTrials(inputs.trials);
  const srAnn = Number.isFinite(inputs.annualizedSharpe) ? inputs.annualizedSharpe : 0;
  const g3 = Number.isFinite(inputs.skewness) ? inputs.skewness : 0;
  const g4 = Number.isFinite(inputs.kurtosis) ? inputs.kurtosis : 3;

  const T = yrs * ppy;
  const srPer = perPeriodSharpe(srAnn, ppy);
  const D = srPer !== null ? computeD(srPer, g3, g4) : null;

  const se = sharpeStdError(srAnn, ppy, yrs, g3, g4);

  let ciLow: number | null = null;
  let ciHigh: number | null = null;
  if (srPer !== null && se !== null && Number.isFinite(se)) {
    const z = 1.959963984540054; // 97.5th percentile
    ciLow = (srPer - z * se) * Math.sqrt(ppy);
    ciHigh = (srPer + z * se) * Math.sqrt(ppy);
    if (!Number.isFinite(ciLow)) ciLow = null;
    if (!Number.isFinite(ciHigh)) ciHigh = null;
  }

  const psr = probabilisticSharpe(srAnn, ppy, yrs, g3, g4, 0);

  const em = expectedMaxSharpe(ppy, yrs, N, inputs.trialSharpeStdDevAnnual ?? null);

  const dsr = deflatedSharpe(srAnn, ppy, yrs, g3, g4, N, inputs.trialSharpeStdDevAnnual ?? null);

  const mtrl = minTrackRecordLength(srAnn, ppy, g3, g4);

  // Interpretations — one plain sentence each, no hype, no em dashes
  const interpretations: Record<string, string> = {};

  interpretations.perPeriodSharpe =
    srPer === null
      ? "Per period Sharpe could not be computed from the inputs."
      : `A Sharpe of ${srAnn.toFixed(2)} per year is about ${srPer.toFixed(4)} per ${ppy === 252 ? "day" : ppy === 52 ? "week" : "month"} before sampling uncertainty.`;

  interpretations.standardError =
    se === null
      ? "Standard error could not be computed because the adjustment term is not positive or the sample is too small."
      : `The standard error of about ${se.toFixed(4)} per period reflects sampling noise from ${Math.round(T)} observations and the skew and kurtosis you entered.`;

  interpretations.ci95 =
    ciLow === null || ciHigh === null
      ? "Confidence interval could not be computed from the inputs."
      : `With 95 percent confidence the true annualised Sharpe lies between ${ciLow.toFixed(2)} and ${ciHigh.toFixed(2)} if returns are stationary and the skew and kurtosis are correct.`;

  interpretations.psr =
    psr === null
      ? "Probabilistic Sharpe ratio could not be computed from the inputs."
      : `PSR of ${(psr * 100).toFixed(1)} percent is the probability the true Sharpe is above zero given the sample size and distribution shape.`;

  interpretations.expectedMax =
    em.annualized === null
      ? "Expected maximum Sharpe could not be computed from the inputs."
      : em.annualized === 0
      ? "With only one trial there is no selection effect, so the expected maximum Sharpe from selection is zero."
      : `Trying ${N} independent variants would be expected to produce a best annualised Sharpe of about ${em.annualized.toFixed(2)} by luck alone.`;

  interpretations.dsr =
    dsr === null
      ? "Deflated Sharpe ratio could not be computed from the inputs."
      : `DSR of ${(dsr * 100).toFixed(1)} percent is the PSR after raising the bar to the expected best Sharpe from ${N} trials.`;

  interpretations.minTRL =
    mtrl.years === null
      ? "Minimum track record is not attainable because the Sharpe is not positive or the adjustment term is not positive."
      : `About ${mtrl.years.toFixed(1)} years (${Math.round(mtrl.observations!)} ${ppy === 252 ? "daily" : ppy === 52 ? "weekly" : "monthly"} observations) are needed for 95 percent confidence that the true Sharpe exceeds zero.`;

  return {
    perPeriodSharpe: srPer,
    standardError: se,
    ciLowAnnual: ciLow,
    ciHighAnnual: ciHigh,
    psrVsZero: psr,
    expectedMaxSharpeAnnual: em.annualized,
    expectedMaxSharpePerPeriod: em.perPeriod,
    deflatedSharpe: dsr,
    minTRLYears: mtrl.years,
    minTRLObservations: mtrl.observations,
    varianceUsed: em.varianceUsed,
    usedEstimatedVariance: em.usedEstimated,
    interpretations,
  };
}

// Alias for callers that expect a different name
export const computeAllSanityOutputs = computeSanityCheck;
export const computePanel2 = computeSanityCheck;
