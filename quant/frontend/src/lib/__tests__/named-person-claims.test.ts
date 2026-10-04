// No invented performance, holdings or trades may be attached to a named real person.
// 2026-10-04: 15 congress-* posts gave exact returns, win rates, holdings and "Q1 2026" profit to named
// members of Congress -- including Dianne Feinstein (died 2023) and Richard Burr (left the Senate in
// 2023) as 2026 traders. PTRs only report broad amount ranges, never returns, so those figures had no
// source. Live disclosure data belongs on /congress-stock-trades, not in blog prose.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const ROOT = path.resolve(import.meta.dirname, '..', '..', '..')
const BLOG_DIR = path.join(ROOT, 'content', 'blog')
const FILES = fs.readdirSync(BLOG_DIR).filter((f) => f.endsWith('.md'))

const REMOVED = [
  'congress-bank-stock-trades-during-crisis', 'congress-big-tech-antitrust-trading',
  'congress-crypto-investments-analysis', 'congress-energy-sector-trades-2026',
  'congress-etf-buying-patterns', 'congress-green-energy-investment-trends',
  'congress-healthcare-stock-trades-analysis', 'congress-insider-trading-vs-sp500-returns',
  'congress-international-stock-investments', 'congress-members-best-stock-traders',
  'congress-military-contractor-investments', 'congress-pharmaceutical-trades-before-votes',
  'congress-real-estate-investments-2026', 'congress-semiconductor-stock-trades',
  'congress-small-cap-stock-picks',
]

const TITLE = /\b(?:Sen\.|Rep\.|Senator|Representative|Congressman|Congresswoman)\s+[A-Z][a-z]+|\((?:R|D|I)-[A-Z][A-Za-z]*\)/
const NAMES = /\b(?:Pelosi|Feinstein|Burr|Tuberville|McCaul|Crenshaw|McHenry|Gottheimer|Khanna|Manchin|Walden|Emmer|Hickenlooper|Loeffler|Perdue|Inhofe|Sinema|Ossoff|Spanberger)\b/
// a return, rate or holding: 12.3%, $4.2M, $847K, $1.2 million
const FIGURE = /\d+(?:\.\d+)?\s?%|\$\s?\d[\d,.]*\s?(?:[KMB]\b|thousand|million|billion)/i
// A disclosed amount band such as "$50K-$100K" is what a PTR really reports, so it is allowed.
const BAND = /\$\s?\d[\d,.]*\s?[KMB]?\s?(?:-|–|to)\s?\$\s?\d[\d,.]*\s?[KMB]?/gi

function offending(): string[] {
  const hits: string[] = []
  for (const f of FILES) {
    let fenced = false
    fs.readFileSync(path.join(BLOG_DIR, f), 'utf-8').split(/\r?\n/).forEach((line, i) => {
      if (line.trimStart().startsWith('```')) { fenced = !fenced; return }
      if (fenced) return
      if (!(TITLE.test(line) || NAMES.test(line))) return
      if (FIGURE.test(line.replace(BAND, ''))) hits.push(`${f}:${i + 1}: ${line.slice(0, 100)}`)
    })
  }
  return hits
}

test('no blog line pairs a named legislator with a return, rate or dollar holding', () => {
  assert.deepEqual(offending(), [])
})

test('removed named-person posts stay removed', () => {
  assert.deepEqual(REMOVED.filter((s) => FILES.includes(`${s}.md`)), [])
})

test('every removed post redirects to the live tracker', async () => {
  const cfg = (await import('../../../next.config.js')).default
  const redirects = await cfg.redirects()
  for (const s of REMOVED) {
    assert.ok(redirects.some((r: any) => r.source === `/blog/${s}` && r.destination === '/congress-stock-trades'), s)
  }
})
