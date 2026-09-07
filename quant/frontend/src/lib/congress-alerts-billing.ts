import Stripe from 'stripe'
import type { BillingCycle } from './congress-alerts'

// Dedicated Stripe wiring for the congress-alerts product. Deliberately NOT
// the backend's quant/backend/app/services/subscription_service.py /
// api/v1/subscriptions.py -- that code is tangled up in the paused
// free-forever-vs-paid decision for the CORE backtesting tool (see this
// repo's CLAUDE.md) and, per audit, is missing a real Checkout Session flow
// besides. This is a separate product with its own Stripe Customers,
// Subscriptions, and webhook endpoint, so it gets its own small, complete
// integration instead of inheriting that one's gaps and its unrelated
// pricing decision.

let _stripe: Stripe | null = null

export function getStripe(): Stripe {
  const secretKey = process.env.STRIPE_SECRET_KEY
  if (!secretKey) {
    throw new Error('STRIPE_SECRET_KEY is not set -- congress alerts billing is not configured yet.')
  }
  if (!_stripe) {
    // No apiVersion pinned on purpose -- same reasoning as scrum-simulator's
    // src/lib/billing.ts: the installed SDK's types require the exact literal
    // string for its bundled default, and hand-pinning a different one risks
    // a mismatch the type checker won't catch. Omitting it uses the SDK's
    // built-in default, which Stripe recommends absent a specific need.
    _stripe = new Stripe(secretKey)
  }
  return _stripe
}

/** Stripe Price id for the Pro plan at the given billing cycle, or null if
 *  that price hasn't been configured in env vars yet. */
export function proPriceId(cycle: BillingCycle): string | null {
  const envVar = cycle === 'yearly' ? 'STRIPE_CONGRESS_ALERTS_PRICE_YEARLY' : 'STRIPE_CONGRESS_ALERTS_PRICE_MONTHLY'
  return process.env[envVar] || null
}
