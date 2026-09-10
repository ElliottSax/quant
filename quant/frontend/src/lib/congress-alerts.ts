// Shared types/config for the Congress Trading Alerts add-on. Used by the
// signup/manage/webhook API routes and by the signup + manage UI.
//
// This is a separate, additive premium product sold alongside quant's free
// backtesting tool and free congress-trades browser (frontend/src/lib/
// congress-trades.ts) -- it does not gate or replace either of those. See
// /pricing's "no paywalls" commitment, which this does not touch.

export type AlertTier = 'free' | 'pro'
export type BillingCycle = 'monthly' | 'yearly'
export type Chamber = 'House' | 'Senate'

export interface AlertFilterInput {
  ticker?: string
  memberName?: string
  chamber?: Chamber
}

export interface AlertFilterRow {
  id: string
  ticker: string | null
  member_name: string | null
  chamber: Chamber | null
}

// Free plans get one saved filter (or none, for an unfiltered weekly digest of
// everything). Pro plans get a real filter set; 25 is a sanity cap, not a
// marketed limit -- nobody legitimately needs more members/tickers than that
// in one digest.
export const FREE_MAX_FILTERS = 1
export const PRO_MAX_FILTERS = 25

// Cadence, in words, for UI copy -- the actual scheduling lives in
// scripts/congress_alerts_digest.py (free = >=7 days since last send, pro =
// every run of the daily cron).
export const FREE_CADENCE_LABEL = 'Weekly digest'
export const PRO_CADENCE_LABEL = 'Daily digest'

// Concrete price points from the competitive research this feature was scoped
// against (Quiver ~$25-30/mo, Unusual Whales $50+/mo for an unrelated options
// bundle, Capitol Trades free-but-no-alerts). $9/mo undercuts both while still
// being a real, sustainable price for an alerts-only product.
export const PRO_PRICE_MONTHLY_USD = 9
export const PRO_PRICE_YEARLY_USD = 79

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function isValidEmail(email: string): boolean {
  return typeof email === 'string' && email.length > 0 && email.length <= 320 && EMAIL_RE.test(email)
}

// Normalizes one filter row from client input. Returns null for an
// all-blank row (nothing to save) rather than a row satisfying no real
// criterion, which the DB's own check constraint would also reject.
export function normalizeFilter(f: AlertFilterInput): AlertFilterInput | null {
  const ticker = f.ticker?.trim().toUpperCase().slice(0, 10) || undefined
  const memberName = f.memberName?.trim().slice(0, 120) || undefined
  const chamber = f.chamber === 'House' || f.chamber === 'Senate' ? f.chamber : undefined
  if (!ticker && !memberName && !chamber) return null
  return { ticker, memberName, chamber }
}

export function maxFiltersForTier(tier: AlertTier): number {
  return tier === 'pro' ? PRO_MAX_FILTERS : FREE_MAX_FILTERS
}
