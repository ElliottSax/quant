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
  // 2026-10-04 second sweep: name-free posts with invented congress-wide aggregates (win rates, profits, volumes)
  'congress-options-trading-analysis', 'congress-stock-trades-before-earnings',
  'congress-stock-trades-vs-hedge-funds', 'congress-tech-stock-buying-spree-2026',
  'congress-ai-stock-investments-2026',
  // 2026-10-04 third sweep: named senators/representatives with trades no source backs
  'congress-signals-retail-weakness-selling-consumer-stocks-2026-03-15',
  // 2026-10-04 pass 7 (persona leads): invented congress-wide aggregates with no named member
  // (87%/89% of each party "purchased" NVDA, $523M, 294 purchasers, correlation 0.89, "253% outperformance")
  'bipartisan-stock-picks-what-both-parties-buy',
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

// 2026-10-04 pass 9: posts removed for invented content whose readers belong on a different live page
// (not the congress tracker). The destination must be a post that still exists.
const REMOVED_TO: Record<string, string> = {
  'butterfly-spreads-long-vs-short-variants': '05-butterfly-spread-options-strategy-low-risk',
  'black-litterman-model-incorporating-market-views': 'black-litterman-model',
  'cross-validation-for-trading-systems-walk-forward-analysis': 'cross-validation-trading-models',
}

test('removed non-congress posts stay removed and redirect to a live post', async () => {
  const cfg = (await import('../../../next.config.js')).default
  const redirects = await cfg.redirects()
  for (const [s, dest] of Object.entries(REMOVED_TO)) {
    assert.ok(!FILES.includes(`${s}.md`), `${s} is back`)
    assert.ok(FILES.includes(`${dest}.md`), `${dest} missing`)
    assert.ok(redirects.some((r: any) => r.source === `/blog/${s}` && r.destination === `/blog/${dest}`), s)
  }
})

// Congress-wide performance aggregates have no source: a PTR reports an amount band, never a return,
// so a "win rate", "outperformance" or realised profit for Congress as a group cannot be derived from filings.
test('no blog line states an unsourced congress-wide win rate, outperformance or realised profit', () => {
  const GROUP = /\b(?:congress(?:ional)?|lawmakers|legislators|politicians)\b/i
  const CLAIM = /\b(?:win rate|outperform\w*|beat the market|alpha|sharpe|annuali[sz]ed|realised profit|realized profit|average return|profits? of)\b/i
  const NUM = /\d+(?:\.\d+)?\s?%|\$\s?\d[\d,.]*\s?(?:[KMB]\b|thousand|million|billion)/i
  const hits: string[] = []
  for (const f of FILES) {
    if (!/congress|politician|stock-act/i.test(f)) continue
    let fenced = false
    fs.readFileSync(path.join(BLOG_DIR, f), 'utf-8').split(/\r?\n/).forEach((line, i) => {
      if (line.trimStart().startsWith('```')) { fenced = !fenced; return }
      if (fenced || /^>\s*\*\*Note on figures/.test(line)) return
      if (GROUP.test(line) && CLAIM.test(line) && NUM.test(line.replace(BAND, ''))) hits.push(`${f}:${i + 1}: ${line.slice(0, 100)}`)
    })
  }
  assert.deepEqual(hits, [])
})

// "The following table ..." with no table behind it reads as a missing result. Several posts had their
// invented result tables removed but kept the sentence introducing them (and sentences "as shown in the table").
test('no blog post points at a table or chart that is not there', () => {
  const REF = /\b(?:the following (?:table|chart)|(?:table|chart) below|(?:as )?shown in the table|(?:table|chart) above|as the table shows)\b/i
  const hits: string[] = []
  for (const f of FILES) {
    const text = fs.readFileSync(path.join(BLOG_DIR, f), 'utf-8')
    if (/^\s*\|.*\|\s*$/m.test(text) || /<table|<img|!\[/i.test(text)) continue
    text.split(/\r?\n/).forEach((line, i) => { if (REF.test(line)) hits.push(`${f}:${i + 1}: ${line.slice(0, 100)}`) })
  }
  assert.deepEqual(hits, [])
})

test('no blog post lists unsourced "Average winner/loser" percentages', () => {
  const hits: string[] = []
  for (const f of FILES) {
    fs.readFileSync(path.join(BLOG_DIR, f), 'utf-8').split(/\r?\n/).forEach((line, i) => {
      if (/\*\*Average (?:winner|loser)\*\*:\s*-?\d/i.test(line)) hits.push(`${f}:${i + 1}: ${line.slice(0, 100)}`)
    })
  }
  assert.deepEqual(hits, [])
})

// 2026-10-05 pass 10: attributions to studies and surveys that cannot be identified. A real citation names
// the paper, author and year; "a survey by GARP found that 85% of FRM holders ..." names none, and the
// statistics attached to it were invented. Generated tables of "Effectiveness" or "Accuracy Improvement"
// percentages have no method behind them either.
test('no blog post cites an unidentifiable study or survey with a precise figure', () => {
  const FAKE = [
    /\b(?:a|the) (?:survey|study)(?: conducted)? by (?:GARP|the Global Association of Risk Professionals)\b/i,
    /\ba (?:survey|study) of quantitative traders found\b/i,
    /\bAccording to (?:a study by |data from )?the (?:Federal Reserve Bank of New York|Chicago Mercantile Exchange|Securities and Exchange Commission|Chicago Board Options Exchange)\b[^.]{0,120}\d/i,
    /\bQuantopian or Zipline\b/i,
    // "a study/survey/report by <vague body> found that ... 71%": an attribution with no paper, author or year
    /\b(?:a|the|one) (?:survey|study|report|poll)(?: conducted| published| released)? by (?:the )?[A-Z][A-Za-z&. ]{2,60}? (?:found|showed|revealed|reported|estimated)(?: that)?[^.]{0,120}?\d+(?:\.\d+)?\s?%/,
  ]
  const hits: string[] = []
  for (const f of FILES) {
    const text = fs.readFileSync(path.join(BLOG_DIR, f), 'utf-8')
    for (const block of text.split(/\r?\n\r?\n/)) {
      const rows = block.split(/\r?\n/).filter((l) => l.startsWith('|'))
      if (rows.length > 2 && /\|\s*(?:Effectiveness|Accuracy Improvement)\s*\|\s*$/i.test(rows[0]) && rows.slice(2).some((r) => /\d+%\s*\|\s*$/.test(r))) {
        hits.push(`${f}: percentage-valued Effectiveness/Accuracy table`)
      }
    }
    text.split(/\r?\n/).forEach((line, i) => {
      if (FAKE.some((re) => re.test(line))) hits.push(`${f}:${i + 1}: ${line.slice(0, 100)}`)
    })
  }
  assert.deepEqual(hits, [])
})
