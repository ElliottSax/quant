/**
 * Kelly criterion sizing arithmetic.
 *
 * Binary-outcome model (Kelly 1956; Thorp's trading formulation):
 *   f*      = W - (1 - W) / R
 *   growth  = W * ln(1 + f*R) + (1 - W) * ln(1 - f)   for 0 <= f < 1
 *
 * where W is win probability and R is the win/loss ratio (average win size
 * divided by average loss size, both in the same units — e.g. R dollars per
 * dollar risked). f* is the bankroll fraction that maximises the expected
 * long-run geometric growth rate of the account.
 *
 * This is a two-outcome simplification: every trade is treated as either a
 * win of R units or a loss of 1 unit, at fixed probabilities. Real trade
 * distributions are continuous and R is rarely fixed run to run, so f* here
 * is only correct if a trader's win rate and average win/loss ratio are
 * stable and accurately estimated — the growth curve exists specifically to
 * show how quickly overestimating either one turns growth negative.
 *
 * Pure functions over caller-supplied numbers — no market data is involved.
 */

export interface KellyInputs {
  /** Win probability as a percentage, e.g. 55 for 55%. Must be in (0, 100). */
  winProbPct: number
  /** Average win size divided by average loss size. Must be > 0. */
  winLossRatio: number
  /** Total trading capital in dollars. Must be > 0. */
  account: number
  /**
   * Fraction of full Kelly actually staked, as a percentage — e.g. 50 for
   * half Kelly. Must be > 0. Values over 100 are allowed (over-betting) so
   * the growth curve can show why that is worse, not just different.
   */
  kellyFractionPct: number
}

export interface GrowthPoint {
  /** Bankroll fraction staked per trade, as a percentage of full Kelly. */
  ofFullKellyPct: number
  /** Bankroll fraction staked per trade, 0-100+, in absolute terms. */
  fPct: number
  /** Expected log-growth rate per trade, as a percentage. */
  growthPct: number
}

export interface KellyResult {
  /** f* = W - (1-W)/R, as a percentage. Negative means no edge — bet nothing. */
  fullKellyPct: number
  /** Win probability at which f* is exactly zero: W = 1 / (1 + R). */
  breakEvenWinProbPct: number
  /** Expected value per dollar staked at the given inputs: W*R - (1-W). */
  edgePerDollar: number
  hasEdge: boolean
  /** kellyFractionPct applied to fullKellyPct. Zero (not negative) when there is no edge. */
  stakedPct: number
  dollarAllocation: number
  /** Expected log-growth rate per trade at the staked fraction, as a percentage. */
  expectedGrowthPct: number
  /** Growth curve from 0% to 200% of full Kelly, for charting. Empty when there is no edge. */
  growthCurve: GrowthPoint[]
}

export function validateKelly(i: KellyInputs): string | null {
  if (!Number.isFinite(i.winProbPct) || i.winProbPct <= 0 || i.winProbPct >= 100) {
    return 'Win probability must be between 0% and 100%, exclusive.'
  }
  if (!Number.isFinite(i.winLossRatio) || i.winLossRatio <= 0) {
    return 'Win/loss ratio must be greater than 0.'
  }
  if (!Number.isFinite(i.account) || i.account <= 0) {
    return 'Account size must be greater than $0.'
  }
  if (!Number.isFinite(i.kellyFractionPct) || i.kellyFractionPct <= 0) {
    return 'Kelly fraction must be greater than 0%.'
  }
  return null
}

/** Expected log-growth rate per trade for bankroll fraction f (0 <= f < 1), in the two-outcome model. */
function growthRate(w: number, r: number, f: number): number {
  if (f <= 0) return 0
  if (f >= 1) return -Infinity // total ruin on the first loss
  return w * Math.log(1 + f * r) + (1 - w) * Math.log(1 - f)
}

export function computeKelly(i: KellyInputs): KellyResult | null {
  if (validateKelly(i) !== null) return null

  const { account, kellyFractionPct } = i
  const w = i.winProbPct / 100
  const r = i.winLossRatio

  const fullKelly = w - (1 - w) / r // fraction, can be negative
  const fullKellyPct = fullKelly * 100
  const breakEvenWinProbPct = (1 / (1 + r)) * 100
  const edgePerDollar = w * r - (1 - w)
  const hasEdge = fullKelly > 0

  const stakedFraction = hasEdge ? fullKelly * (kellyFractionPct / 100) : 0
  const stakedPct = stakedFraction * 100
  // Cap the modelled stake below 100% of the bankroll — ln(1-f) is undefined at f=1
  // (total ruin on a single loss) and negative beyond it; the UI surfaces this instead
  // of computing through it.
  const clampedStakedFraction = Math.min(stakedFraction, 0.999)
  const dollarAllocation = account * clampedStakedFraction
  const expectedGrowthPct = growthRate(w, r, clampedStakedFraction) * 100

  const growthCurve: GrowthPoint[] = []
  if (hasEdge) {
    const maxF = Math.min(0.99, fullKelly * 2)
    const steps = 40
    for (let s = 0; s <= steps; s++) {
      const f = (maxF * s) / steps
      growthCurve.push({
        ofFullKellyPct: (f / fullKelly) * 100,
        fPct: f * 100,
        growthPct: growthRate(w, r, f) * 100,
      })
    }
  }

  const result: KellyResult = {
    fullKellyPct,
    breakEvenWinProbPct,
    edgePerDollar,
    hasEdge,
    stakedPct,
    dollarAllocation,
    expectedGrowthPct,
    growthCurve,
  }

  if (
    !Number.isFinite(result.fullKellyPct) ||
    !Number.isFinite(result.breakEvenWinProbPct) ||
    !Number.isFinite(result.edgePerDollar)
  ) {
    return null
  }
  return result
}
