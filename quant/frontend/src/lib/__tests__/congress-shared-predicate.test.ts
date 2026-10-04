// The sitemap and the per-ticker / per-member pages must share one predicate: a URL
// is only listed if the page's own lookup finds trades for it in the same data.
// Regression for /congress-stock-trades/HON (listed, served as 404).
// Run with `npm run test` (node's built-in runner; no network).

import { test, describe } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import {
  memberSlug, memberSlugs, normalizeTicker, tickerSlugs, tradesForMember, tradesForTicker, type Trade,
} from '../congress-trades.ts'

function trade(ticker: string, member: string): Trade {
  return {
    ticker, member, chamber: 'House', date: new Date(2026, 7, 20), transactionDate: '2026-08-20',
    disclosureDate: '2026-09-01', daysToDisclose: 12, assetDescription: 'X', type: 'Purchase',
    amount: '$1,001 - $15,000', amountMid: 8000, isBuy: true, link: '',
  }
}

const feed: Trade[] = [
  trade('HON', 'Rep A'), trade(' hon ', 'Rep A'), trade('aapl', 'Rep B'), trade('BRK.B', 'Rep C'),
  trade('N/A', 'Rep D'), trade('', 'Rep D'), trade('BAD TICKER', 'Rep E'), trade('A/B', 'Rep E'),
  trade('X'.repeat(30), 'Rep F'), trade('MSFT', ''), trade('MSFT', '   '), trade('MSFT', 'Rep G'),
]

describe('shared sitemap/page predicate', () => {
  test('normalizeTicker trims and upper-cases', () => {
    assert.equal(normalizeTicker(' hon '), 'HON')
    assert.equal(normalizeTicker(''), '')
  })

  test('every ticker slug in the sitemap list resolves to trades on the page', () => {
    const slugs = tickerSlugs(feed)
    assert.ok(slugs.includes('HON') && slugs.includes('AAPL') && slugs.includes('BRK.B'))
    for (const s of slugs) assert.ok(tradesForTicker(feed, s).length > 0, `${s} is listed but the page finds no trades`)
  })

  test('junk symbols never become URLs', () => {
    const slugs = tickerSlugs(feed)
    for (const bad of ['N/A', '', 'BAD TICKER', 'A/B', 'X'.repeat(30)]) assert.ok(!slugs.includes(bad), `${bad} listed`)
    assert.deepEqual(tradesForTicker(feed, 'A/B'), [])
  })

  test('duplicates collapse (HON and " hon " are one URL)', () => {
    assert.equal(tickerSlugs(feed).filter((s) => s === 'HON').length, 1)
    assert.equal(tradesForTicker(feed, 'hon').length, 2)
  })

  test('every member slug in the sitemap list resolves to trades on the page', () => {
    const slugs = memberSlugs(feed)
    assert.ok(slugs.includes(memberSlug('Rep A')))
    for (const s of slugs) assert.ok(tradesForMember(feed, s).length > 0, `${s} is listed but the page finds no trades`)
    assert.ok(!slugs.includes(''))
  })

  test('a ticker absent from the data is not listed and the page lookup is empty', () => {
    const data = feed.filter((t) => normalizeTicker(t.ticker) !== 'HON')
    assert.ok(!tickerSlugs(data).includes('HON'))
    assert.deepEqual(tradesForTicker(data, 'HON'), [])
  })
})

describe('wiring: sitemap and pages use the shared functions', () => {
  const appDir = path.resolve(import.meta.dirname, '..', '..', 'app')
  const read = (rel: string) => fs.readFileSync(path.join(appDir, rel), 'utf8')

  test('sitemap uses tickerSlugs/memberSlugs and refreshes during the day', () => {
    const src = read('sitemap.ts')
    assert.match(src, /tickerSlugs\(/)
    assert.match(src, /memberSlugs\(/)
    assert.match(src, /export const revalidate\s*=\s*\d+/)
  })

  test('ticker and member pages use the shared lookups', () => {
    assert.match(read('congress-stock-trades/[ticker]/page.tsx'), /tradesForTicker\(/)
    assert.match(read('congress-stock-trades/member/[slug]/page.tsx'), /tradesForMember\(/)
  })
})
