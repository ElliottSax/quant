// Unit tests for the congress-alerts signup validation path -- the exact
// functions frontend/src/app/api/congress-alerts/{signup,manage/[token]}/
// route.ts call before ever touching Supabase or Stripe. No credentials
// needed. Run with `npm run test` (node's built-in test runner, Node 20+ --
// no framework installed on purpose, matching this repo's frontend having no
// existing JS test setup to extend).

import { test, describe } from 'node:test'
import assert from 'node:assert/strict'
import { isValidEmail, normalizeFilter, maxFiltersForTier, FREE_MAX_FILTERS, PRO_MAX_FILTERS } from '../congress-alerts.ts'

describe('isValidEmail', () => {
  test('accepts a normal address', () => {
    assert.equal(isValidEmail('elliott@example.com'), true)
  })

  test('rejects missing @', () => {
    assert.equal(isValidEmail('not-an-email'), false)
  })

  test('rejects empty string', () => {
    assert.equal(isValidEmail(''), false)
  })

  test('rejects non-string input the API route could receive from raw JSON', () => {
    // SignupBody.email is typed as string, but request.json() can hand the
    // route handler any JSON value at runtime -- a number, null, an array.
    assert.equal(isValidEmail(null as unknown as string), false)
    assert.equal(isValidEmail(undefined as unknown as string), false)
    assert.equal(isValidEmail(12345 as unknown as string), false)
  })

  test('rejects an address over the 320-char RFC limit', () => {
    const local = 'a'.repeat(316)
    const address = `${local}@b.co`
    assert.equal(address.length, 321)
    assert.equal(isValidEmail(address), false)
  })

  test('accepts an address at exactly the 320-char limit', () => {
    const local = 'a'.repeat(315)
    const address = `${local}@b.co`
    assert.equal(address.length, 320)
    assert.equal(isValidEmail(address), true)
  })

  test('rejects embedded whitespace/newlines (header-injection-shaped input)', () => {
    assert.equal(isValidEmail('a@b.com\nBcc: evil@x.com'), false)
    assert.equal(isValidEmail('a b@c.com'), false)
  })
})

describe('normalizeFilter', () => {
  test('returns null for an all-blank row', () => {
    assert.equal(normalizeFilter({}), null)
    assert.equal(normalizeFilter({ ticker: '  ', memberName: '' }), null)
  })

  test('uppercases and trims the ticker, caps its length', () => {
    const f = normalizeFilter({ ticker: '  aapl' })
    assert.equal(f?.ticker, 'AAPL')

    const long = normalizeFilter({ ticker: 'abcdefghijklmnop' })
    assert.equal(long?.ticker?.length, 10)
  })

  test('caps member name length at 120 chars', () => {
    const f = normalizeFilter({ memberName: 'x'.repeat(500) })
    assert.equal(f?.memberName?.length, 120)
  })

  test('only accepts the literal chamber values House/Senate', () => {
    assert.equal(normalizeFilter({ chamber: 'House' } as any)?.chamber, 'House')
    assert.equal(normalizeFilter({ chamber: 'senate' as any })?.chamber, undefined)
    assert.equal(normalizeFilter({ chamber: "'; drop table congress_alert_filters; --" as any })?.chamber, undefined)
  })

  test('a bogus chamber alone (no ticker/member) still normalizes to null', () => {
    assert.equal(normalizeFilter({ chamber: 'nope' as any }), null)
  })
})

describe('maxFiltersForTier', () => {
  test('free tier caps at FREE_MAX_FILTERS', () => {
    assert.equal(maxFiltersForTier('free'), FREE_MAX_FILTERS)
  })

  test('pro tier caps at PRO_MAX_FILTERS', () => {
    assert.equal(maxFiltersForTier('pro'), PRO_MAX_FILTERS)
  })

  test('an unrecognized tier value falls back to the free cap, not unlimited', () => {
    assert.equal(maxFiltersForTier('enterprise' as any), FREE_MAX_FILTERS)
  })
})
