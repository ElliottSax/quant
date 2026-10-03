// A transient FMP failure must never turn into a false 404 on a ticker/member page.
// Strict mode retries then throws; the default (sitemap, index pages) stays tolerant.
// Regression for /congress-stock-trades/HON (in the sitemap, served as 404).
// Run with `npm run test` (node's built-in runner; fetch is mocked, no network).

import { test, describe, beforeEach, afterEach } from 'node:test'
import assert from 'node:assert/strict'
import { getCongressTrades } from '../congress-trades.ts'

const realFetch = globalThis.fetch
const row = {
  symbol: 'HON', disclosureDate: '2026-09-01', transactionDate: '2026-08-20', firstName: 'A', lastName: 'B',
  office: 'Rep A', owner: '', assetDescription: 'Honeywell', assetType: '', type: 'Purchase',
  amount: '$1,001 - $15,000', link: '',
}

describe('getCongressTrades strict mode', () => {
  beforeEach(() => { process.env.FMP_API_KEY = 'test-key' })
  afterEach(() => { globalThis.fetch = realFetch; delete process.env.FMP_API_KEY })

  test('returns null without an API key (data unavailable, not an error)', async () => {
    delete process.env.FMP_API_KEY
    assert.equal(await getCongressTrades({ strict: true }), null)
  })

  test('strict: a rate-limited feed throws instead of returning an empty list', async () => {
    globalThis.fetch = (async () => ({ ok: false, status: 429, json: async () => [] })) as unknown as typeof fetch
    await assert.rejects(() => getCongressTrades({ strict: true }), /failed after 3 attempts: HTTP 429/)
  })

  test('strict: retries and succeeds when the feed recovers', async () => {
    let calls = 0
    globalThis.fetch = (async () => {
      calls++
      return calls <= 2 ? { ok: false, status: 503, json: async () => [] } : { ok: true, status: 200, json: async () => [row] }
    }) as unknown as typeof fetch
    const d = await getCongressTrades({ strict: true })
    assert.ok(d)
    assert.ok(d.trades.some((t) => t.ticker === 'HON'))
  })

  test('default (tolerant) still returns null on failure so the index/sitemap never crash', async () => {
    globalThis.fetch = (async () => ({ ok: false, status: 429, json: async () => [] })) as unknown as typeof fetch
    assert.equal(await getCongressTrades(), null)
  })
})

describe('per-ticker and per-member pages use strict mode', async () => {
  const fs = await import('node:fs')
  const path = await import('node:path')
  const { fileURLToPath } = await import('node:url')
  const app = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', 'app', 'congress-stock-trades')
  for (const rel of ['[ticker]/page.tsx', 'member/[slug]/page.tsx']) {
    test(rel, () => {
      assert.match(fs.readFileSync(path.join(app, rel), 'utf8'), /getCongressTrades\(\{ strict: true \}\)/)
    })
  }
})
