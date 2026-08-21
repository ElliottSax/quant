/**
 * Is an observed win rate distinguishable from chance, or from a stated
 * baseline (e.g. "I need >52% to beat commissions")? The exact question the
 * site's "evidence bar" thesis is built on: small samples routinely produce
 * win rates that look impressive and are not statistically distinguishable
 * from noise.
 *
 * Wilson score interval — the standard interval recommended over the naive
 * Wald interval for small/moderate samples, since Wald's coverage degrades
 * badly near 0/1 and for small n:
 *   Wilson, E.B. (1927), "Probable Inference, the Law of Succession, and
 *   Statistical Inference", JASA 22(158).
 *   Brown, Cai & DasGupta (2001), "Interval Estimation for a Binomial
 *   Proportion", Statistical Science 16(2) — confirms Wilson's superior
 *   coverage over Wald across sample sizes.
 *
 * Exact two-sided binomial test — sum of all outcome probabilities no more
 * likely than the observed outcome, the same definition used by R's
 * binom.test() default. Computed via the binomial PMF in log-space (Lanczos
 * log-gamma) so it stays numerically stable for any realistic trade count.
 *
 * Pure functions over caller-supplied win/loss counts — no market data.
 */

export interface WinRateInputs {
  wins: number;
  trades: number;
  /** Null-hypothesis win rate to test against, e.g. 0.5 for a coin flip. In (0, 1). */
  nullRate: number;
  /** 0.90, 0.95, or 0.99 */
  confidence: 0.9 | 0.95 | 0.99;
}

export interface WinRateResult {
  observedRate: number;
  wilsonLower: number;
  wilsonUpper: number;
  /** Two-sided exact binomial p-value against nullRate. */
  pValue: number;
  /** True when nullRate falls OUTSIDE the Wilson interval (equivalently, p < 1 - confidence). */
  significant: boolean;
}

const Z_SCORES: Record<WinRateInputs['confidence'], number> = {
  0.9: 1.6448536269514722,
  0.95: 1.9599639845400545,
  0.99: 2.5758293035489004,
};

/** Lanczos approximation, g=7, n=9 — accurate to ~15 significant digits. */
const LANCZOS_G = 7;
const LANCZOS_COEF = [
  0.99999999999980993, 676.5203681218851, -1259.1392167224028,
  771.32342877765313, -176.61502916214059, 12.507343278686905,
  -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7,
];

function logGamma(x: number): number {
  if (x < 0.5) {
    // Reflection formula for x < 0.5.
    return Math.log(Math.PI / Math.sin(Math.PI * x)) - logGamma(1 - x);
  }
  x -= 1;
  let a = LANCZOS_COEF[0];
  const t = x + LANCZOS_G + 0.5;
  for (let i = 1; i < LANCZOS_G + 2; i++) a += LANCZOS_COEF[i] / (x + i);
  return 0.5 * Math.log(2 * Math.PI) + (x + 0.5) * Math.log(t) - t + Math.log(a);
}

function logChoose(n: number, k: number): number {
  return logGamma(n + 1) - logGamma(k + 1) - logGamma(n - k + 1);
}

/** log P(X = k) for X ~ Binomial(n, p). */
function logBinomialPMF(k: number, n: number, p: number): number {
  if (p <= 0) return k === 0 ? 0 : -Infinity;
  if (p >= 1) return k === n ? 0 : -Infinity;
  return logChoose(n, k) + k * Math.log(p) + (n - k) * Math.log(1 - p);
}

/**
 * Two-sided exact binomial test p-value: sum of P(k') for every k' in
 * [0, n] whose probability is <= the observed outcome's probability
 * (within floating-point tolerance), matching R's binom.test() default.
 */
export function exactBinomialTwoSidedPValue(k: number, n: number, p: number): number {
  const logObserved = logBinomialPMF(k, n, p);
  const REL_TOL = 1e-9;
  let total = 0;
  for (let i = 0; i <= n; i++) {
    const logPi = logBinomialPMF(i, n, p);
    if (logPi <= logObserved + REL_TOL) {
      total += Math.exp(logPi);
    }
  }
  return Math.min(1, total);
}

/** Wilson score interval for a binomial proportion, clamped to [0, 1]. */
export function wilsonScoreInterval(k: number, n: number, confidence: WinRateInputs['confidence']) {
  const z = Z_SCORES[confidence];
  const phat = k / n;
  const z2 = z * z;
  const denom = 1 + z2 / n;
  const center = (phat + z2 / (2 * n)) / denom;
  const margin = (z * Math.sqrt((phat * (1 - phat)) / n + z2 / (4 * n * n))) / denom;
  return {
    lower: Math.max(0, center - margin),
    upper: Math.min(1, center + margin),
  };
}

export function validateWinRate(i: WinRateInputs): string | null {
  if (!Number.isFinite(i.trades) || i.trades <= 0 || !Number.isInteger(i.trades)) {
    return 'Total trades must be a whole number greater than 0.';
  }
  if (!Number.isFinite(i.wins) || i.wins < 0 || !Number.isInteger(i.wins)) {
    return 'Wins must be a whole number of 0 or more.';
  }
  if (i.wins > i.trades) return 'Wins cannot exceed total trades.';
  if (!Number.isFinite(i.nullRate) || i.nullRate <= 0 || i.nullRate >= 1) {
    return 'The baseline win rate to test against must be between 0% and 100%, exclusive.';
  }
  return null;
}

export function computeWinRateSignificance(i: WinRateInputs): WinRateResult | null {
  if (validateWinRate(i) !== null) return null;
  const { wins, trades, nullRate, confidence } = i;
  const observedRate = wins / trades;
  const { lower, upper } = wilsonScoreInterval(wins, trades, confidence);
  const pValue = exactBinomialTwoSidedPValue(wins, trades, nullRate);

  const result: WinRateResult = {
    observedRate,
    wilsonLower: lower,
    wilsonUpper: upper,
    pValue,
    significant: nullRate < lower || nullRate > upper,
  };
  if (!Number.isFinite(result.pValue) || !Number.isFinite(result.wilsonLower) || !Number.isFinite(result.wilsonUpper)) {
    return null;
  }
  return result;
}
