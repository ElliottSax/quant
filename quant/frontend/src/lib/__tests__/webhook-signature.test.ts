// Tests that the Stripe webhook signature check used by
// frontend/src/app/api/congress-alerts/webhook/route.ts actually verifies
// authenticity rather than just trusting whatever arrives.
//
// route.ts itself imports 'next/server', which needs a Next.js request
// runtime this bare `node --test` process doesn't have -- so instead of
// importing the route handler directly, this exercises the real
// `stripe.webhooks.constructEvent()` call it delegates to, with the exact
// same three inputs (raw body, signature header, signing secret) and
// asserts the same pass/fail behavior the route relies on. No network call,
// no real Stripe account -- constructEvent is a local HMAC verification
// against the given secret, and Stripe's own SDK is what's under test here,
// not a mock of it.

import { test, describe } from 'node:test'
import assert from 'node:assert/strict'
import Stripe from 'stripe'

const REAL_SECRET = 'whsec_test_congress_alerts_secret_abc123'
const WRONG_SECRET = 'whsec_test_wrong_secret_xyz789'

function stripeForSecretCheckOnly() {
  // constructEvent/generateTestHeaderString never make a network call, so a
  // syntactically-valid placeholder key is enough to construct the client.
  return new Stripe('sk_test_placeholder_no_network_call')
}

function signedPayload(payload: string, secret: string) {
  const stripe = stripeForSecretCheckOnly()
  return stripe.webhooks.generateTestHeaderString({ payload, secret })
}

describe('congress-alerts Stripe webhook signature verification', () => {
  const payload = JSON.stringify({
    id: 'evt_test_1',
    type: 'checkout.session.completed',
    data: { object: { id: 'cs_test_1', client_reference_id: 'sub_row_1' } },
  })

  test('a correctly signed payload verifies and parses', () => {
    const stripe = stripeForSecretCheckOnly()
    const signature = signedPayload(payload, REAL_SECRET)
    const event = stripe.webhooks.constructEvent(payload, signature, REAL_SECRET)
    assert.equal(event.type, 'checkout.session.completed')
  })

  test('a payload signed with the wrong secret is rejected -- this is what stops a forged request', () => {
    const stripe = stripeForSecretCheckOnly()
    const signature = signedPayload(payload, WRONG_SECRET)
    assert.throws(() => stripe.webhooks.constructEvent(payload, signature, REAL_SECRET))
  })

  test('a tampered body (valid signature, altered payload) is rejected', () => {
    const stripe = stripeForSecretCheckOnly()
    const signature = signedPayload(payload, REAL_SECRET)
    const tamperedPayload = payload.replace('checkout.session.completed', 'customer.subscription.deleted')
    assert.throws(() => stripe.webhooks.constructEvent(tamperedPayload, signature, REAL_SECRET))
  })

  test('a missing/garbage signature header is rejected outright', () => {
    const stripe = stripeForSecretCheckOnly()
    assert.throws(() => stripe.webhooks.constructEvent(payload, 'not-a-real-signature', REAL_SECRET))
  })

  test('an expired timestamp outside the tolerance window is rejected (replay protection)', () => {
    const stripe = stripeForSecretCheckOnly()
    const staleTimestamp = Math.floor(Date.now() / 1000) - 60 * 60 * 24 // 24h old
    const signature = stripe.webhooks.generateTestHeaderString({
      payload,
      secret: REAL_SECRET,
      timestamp: staleTimestamp,
    })
    assert.throws(() => stripe.webhooks.constructEvent(payload, signature, REAL_SECRET))
  })
})
