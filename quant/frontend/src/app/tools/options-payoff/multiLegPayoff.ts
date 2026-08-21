/**
 * Multi-leg options payoff-at-expiration arithmetic.
 *
 * Each leg's payoff at expiry, per share, before quantity/contract scaling:
 *   long call  =  max(S - K, 0) - premium
 *   short call =  premium - max(S - K, 0)
 *   long put   =  max(K - S, 0) - premium
 *   short put  =  premium - max(K - S, 0)
 * (standard option payoff at expiry; see Hull, "Options, Futures, and Other
 * Derivatives", ch. 11-12). The aggregate payoff is the sum across legs,
 * each scaled by quantity x 100 shares/contract.
 *
 * The aggregate is piecewise-LINEAR with breakpoints exactly at the strikes
 * (each leg's kink activates only at its own strike; between consecutive
 * strikes nothing changes shape) plus the origin S=0 and an unbounded final
 * ray beyond the highest strike. That structure is what makes max profit,
 * max loss, and breakevens exactly solvable rather than needing a numeric
 * search: max/min occur at S=0, at a strike, or -- when the far-right slope
 * is nonzero -- are unlimited in that direction.
 *
 * This is expiration-only payoff math (no time value); pre-expiration
 * theoretical value at a chosen date uses this file's blackScholesValue,
 * which delegates to the site's existing, already-verified Black-Scholes
 * module rather than reimplementing it.
 */

import { blackScholes, type OptionType } from '../../options/blackScholes'

export type LegPosition = 'long' | 'short'

export interface Leg {
  id: string
  type: OptionType
  position: LegPosition
  strike: number
  /** Premium paid (long) or received (short), per share. Must be >= 0. */
  premium: number
  /** Number of contracts (1 contract = 100 shares). Must be > 0. */
  quantity: number
}

export interface PayoffPoint {
  price: number
  payoff: number
}

export interface MultiLegResult {
  /** Net premium: positive = net debit paid, negative = net credit received. */
  netPremium: number
  maxProfit: number | null; // null represents unlimited
  maxLoss: number | null; // null represents unlimited (loss magnitude unbounded)
  breakevens: number[];
  curve: PayoffPoint[];
}

export function validateLeg(l: Leg): string | null {
  if (!Number.isFinite(l.strike) || l.strike <= 0) return 'Strike must be greater than $0.'
  if (!Number.isFinite(l.premium) || l.premium < 0) return 'Premium must be $0 or more.'
  if (!Number.isFinite(l.quantity) || l.quantity <= 0) return 'Quantity must be at least 1 contract.'
  return null
}

function legPayoffPerShare(leg: Leg, S: number): number {
  const intrinsic = leg.type === 'call' ? Math.max(S - leg.strike, 0) : Math.max(leg.strike - S, 0)
  return leg.position === 'long' ? intrinsic - leg.premium : leg.premium - intrinsic
}

function aggregatePayoff(legs: Leg[], S: number): number {
  return legs.reduce((sum, leg) => sum + legPayoffPerShare(leg, S) * leg.quantity * 100, 0)
}

/** Net per-share slope of the aggregate payoff as S -> +infinity (puts contribute 0 in the limit). */
function slopeAtInfinity(legs: Leg[]): number {
  return legs.reduce((sum, leg) => {
    if (leg.type !== 'call') return sum
    const sign = leg.position === 'long' ? 1 : -1
    return sum + sign * leg.quantity * 100
  }, 0)
}

export function computeMultiLegPayoff(legs: Leg[], curvePriceRange: [number, number], curvePoints = 120): MultiLegResult | null {
  if (legs.length === 0) return null
  for (const leg of legs) if (validateLeg(leg) !== null) return null

  const netPremium = legs.reduce((sum, leg) => sum + (leg.position === 'long' ? leg.premium : -leg.premium) * leg.quantity * 100, 0)

  const strikes = Array.from(new Set(legs.map((l) => l.strike))).sort((a, b) => a - b)
  const breakpoints = [0, ...strikes]
  const values = breakpoints.map((S) => aggregatePayoff(legs, S))
  const rightSlope = slopeAtInfinity(legs)

  const interiorMax = Math.max(...values)
  const interiorMin = Math.min(...values)
  const maxProfit = rightSlope > 0 ? null : interiorMax
  const maxLoss = rightSlope < 0 ? null : interiorMin

  // Breakevens: scan each finite linear segment for a sign change, then the
  // final unbounded ray if its slope is nonzero.
  const breakevens: number[] = []
  for (let i = 0; i < breakpoints.length - 1; i++) {
    const a = breakpoints[i]
    const b = breakpoints[i + 1]
    const va = values[i]
    const vb = values[i + 1]
    if (va === 0) breakevens.push(a)
    if (va !== 0 && vb !== 0 && Math.sign(va) !== Math.sign(vb)) {
      const root = a + (0 - va) * ((b - a) / (vb - va))
      breakevens.push(root)
    }
  }
  const lastIdx = breakpoints.length - 1
  const lastVal = values[lastIdx]
  const lastStrike = breakpoints[lastIdx]
  if (lastVal === 0) {
    breakevens.push(lastStrike)
  } else if (rightSlope !== 0 && Math.sign(rightSlope) !== Math.sign(lastVal)) {
    breakevens.push(lastStrike - lastVal / rightSlope)
  }
  const uniqueBreakevens = Array.from(new Set(breakevens.map((b) => Math.round(b * 100) / 100))).sort((a, b) => a - b)

  const [lo, hi] = curvePriceRange
  const curve: PayoffPoint[] = []
  for (let i = 0; i <= curvePoints; i++) {
    const price = lo + ((hi - lo) * i) / curvePoints
    curve.push({ price, payoff: aggregatePayoff(legs, price) })
  }

  return {
    netPremium,
    maxProfit,
    maxLoss,
    breakevens: uniqueBreakevens,
    curve,
  }
}

/**
 * Optional pre-expiration theoretical value of the whole position, at a
 * chosen number of days remaining, delegating entirely to the site's
 * existing Black-Scholes module (no new pricing logic here).
 */
export function preExpirationValue(
  legs: Leg[],
  S: number,
  daysRemaining: number,
  r: number,
  sigma: number
): number | null {
  if (daysRemaining <= 0) return aggregatePayoff(legs, S)
  let total = 0
  for (const leg of legs) {
    const bs = blackScholes({ S, K: leg.strike, T: daysRemaining / 365, r, sigma, type: leg.type })
    if (bs === null) return null
    const legValue = leg.position === 'long' ? bs.price - leg.premium : leg.premium - bs.price
    total += legValue * leg.quantity * 100
  }
  return total
}
