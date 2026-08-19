/**
 * Position sizing arithmetic.
 *
 * Standard risk-based sizing:
 *   dollar risk    = account * (risk% / 100)
 *   risk per share = | entry - stop |
 *   shares         = floor(dollar risk / risk per share)
 *   position value = shares * entry
 *
 * The absolute value makes the calculation direction-agnostic: a stop above the
 * entry is a short with the same distance. The floor keeps realised risk at or
 * below the stated limit.
 *
 * Pure functions over caller-supplied numbers — no market data is involved.
 */

export interface PositionSizeInputs {
  /** Total trading capital in dollars. Must be > 0. */
  account: number
  /** Percent of the account to put at risk, e.g. 1 for 1%. Must be in (0, 100]. */
  riskPct: number
  /** Entry price per share. Must be > 0. */
  entry: number
  /** Stop-loss price per share. Must be > 0 and differ from entry. */
  stop: number
}

export interface PositionSizeResult {
  direction: 'long' | 'short'
  /** account * riskPct / 100 — the limit the share count is floored against. */
  targetDollarRisk: number
  riskPerShare: number
  /** riskPerShare as a percentage of entry. */
  stopDistancePct: number
  shares: number
  positionValue: number
  positionPctOfAccount: number
  /** shares * riskPerShare — at or below targetDollarRisk because of the floor. */
  actualDollarRisk: number
  actualRiskPctOfAccount: number
  /** True when the share count costs more than the cash balance entered. */
  needsMargin: boolean
}

/** Returns a message for inputs outside the domain, or null when they are usable. */
export function validatePositionSize(i: PositionSizeInputs): string | null {
  if (!Number.isFinite(i.account) || i.account <= 0) return 'Account size must be greater than $0.'
  if (!Number.isFinite(i.riskPct) || i.riskPct <= 0) return 'Risk per trade must be greater than 0%.'
  if (i.riskPct > 100) return 'Risk per trade cannot exceed 100% of the account.'
  if (!Number.isFinite(i.entry) || i.entry <= 0) return 'Entry price must be greater than $0.'
  if (!Number.isFinite(i.stop) || i.stop <= 0) return 'Stop-loss price must be greater than $0.'
  // Guards the division: a zero stop distance has no finite share count.
  if (i.entry === i.stop) return 'Entry and stop-loss must differ — a zero stop distance has no position size.'
  return null
}

/** Returns null rather than a NaN-bearing result when inputs are invalid. */
export function computePositionSize(i: PositionSizeInputs): PositionSizeResult | null {
  if (validatePositionSize(i) !== null) return null

  const { account, riskPct, entry, stop } = i

  const targetDollarRisk = account * (riskPct / 100)
  const riskPerShare = Math.abs(entry - stop)
  const shares = Math.floor(targetDollarRisk / riskPerShare)
  const positionValue = shares * entry
  const actualDollarRisk = shares * riskPerShare

  const result: PositionSizeResult = {
    direction: stop < entry ? 'long' : 'short',
    targetDollarRisk,
    riskPerShare,
    stopDistancePct: (riskPerShare / entry) * 100,
    shares,
    positionValue,
    positionPctOfAccount: (positionValue / account) * 100,
    actualDollarRisk,
    actualRiskPctOfAccount: (actualDollarRisk / account) * 100,
    needsMargin: positionValue > account,
  }

  // A non-finite figure is a failure, not a result, and must not reach the UI.
  if (
    !Number.isFinite(result.shares) ||
    !Number.isFinite(result.positionValue) ||
    !Number.isFinite(result.actualDollarRisk) ||
    !Number.isFinite(result.positionPctOfAccount)
  ) {
    return null
  }
  return result
}
