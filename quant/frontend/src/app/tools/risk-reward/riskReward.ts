/**
 * Risk/reward arithmetic.
 *
 *   risk   = | entry - stop |
 *   reward = | target - entry |
 *   R      = reward / risk
 *   breakeven win rate = 1 / (1 + R)
 *
 * The breakeven rate is the w solving w*reward = (1-w)*risk, which rearranges
 * to w = 1/(1+R). It is a property of the three prices entered, not an estimate
 * of how often the target would be reached.
 *
 * Pure functions over caller-supplied numbers — no market data is involved.
 */

export interface RiskRewardInputs {
  /** Entry price per share. Must be > 0. */
  entry: number
  /** Stop-loss price per share. Must be > 0 and differ from entry. */
  stop: number
  /** Target price per share. Must be > 0, on the winning side of entry. */
  target: number
  /** Share count for dollar figures, or null to omit them. */
  shares: number | null
}

export interface RiskRewardResult {
  direction: 'long' | 'short'
  risk: number
  reward: number
  /** reward / risk, the R in "1 : R". */
  rrRatio: number
  /** reward as a percentage of entry. */
  gainPct: number
  /** risk as a percentage of entry, expressed positive. */
  lossPct: number
  /** 100 / (1 + R), as a percentage. */
  breakevenWinRate: number
  shares: number | null
  dollarRisk: number | null
  dollarReward: number | null
}

/** Returns a message for inputs outside the domain, or null when they are usable. */
export function validateRiskReward(i: RiskRewardInputs): string | null {
  if (!Number.isFinite(i.entry) || i.entry <= 0) return 'Entry price must be greater than $0.'
  if (!Number.isFinite(i.stop) || i.stop <= 0) return 'Stop-loss price must be greater than $0.'
  if (!Number.isFinite(i.target) || i.target <= 0) return 'Target price must be greater than $0.'
  // Guards the division: a zero stop distance has no finite ratio.
  if (i.entry === i.stop) return 'Entry and stop-loss must differ — a zero stop distance has no ratio.'
  if (i.shares !== null && (!Number.isFinite(i.shares) || i.shares <= 0)) {
    return 'Position size must be a number greater than 0, or left blank.'
  }

  // The target must sit on the winning side of the entry. Without this check,
  // |target - entry| would report a losing exit as a reward.
  const isLong = i.stop < i.entry
  if (isLong && i.target <= i.entry) {
    return 'The stop is below the entry, so this is a long — the target must be above the entry price.'
  }
  if (!isLong && i.target >= i.entry) {
    return 'The stop is above the entry, so this is a short — the target must be below the entry price.'
  }
  return null
}

/** Returns null rather than a NaN-bearing result when inputs are invalid. */
export function computeRiskReward(i: RiskRewardInputs): RiskRewardResult | null {
  if (validateRiskReward(i) !== null) return null

  const { entry, stop, target, shares } = i

  const risk = Math.abs(entry - stop)
  const reward = Math.abs(target - entry)
  const rrRatio = reward / risk

  const result: RiskRewardResult = {
    direction: stop < entry ? 'long' : 'short',
    risk,
    reward,
    rrRatio,
    gainPct: (reward / entry) * 100,
    lossPct: (risk / entry) * 100,
    breakevenWinRate: (1 / (1 + rrRatio)) * 100,
    shares,
    dollarRisk: shares === null ? null : risk * shares,
    dollarReward: shares === null ? null : reward * shares,
  }

  // A non-finite figure is a failure, not a result, and must not reach the UI.
  if (!Number.isFinite(result.rrRatio) || !Number.isFinite(result.breakevenWinRate)) return null
  return result
}
