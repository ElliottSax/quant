// Keeps invented audience figures and performance promises out of pages and blog
// content. A live crawl of the sitemap on 2026-10-03 found each of these shipping:
// a "10,000+ Active Members" badge with no community behind it, "50,000+ traders"
// attributed to a Discord, third-party user counts, posts promising "risk-free
// profit" or "65-75% win rates", and ~10 titles promising a "High Success Rate".
import { test } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const ROOT = path.resolve(import.meta.dirname, '..', '..', '..')
const FILES = [
  ...fs.readdirSync(path.join(ROOT, 'content', 'blog')).filter((f) => f.endsWith('.md')).map((f) => path.join('content', 'blog', f)),
  path.join('src', 'app', 'resources', 'page.tsx'),
]

const FORBIDDEN: [string, RegExp][] = [
  ['invented community size', /10,000\+ Active Members|50,000\+ traders|community of 10,000\+ traders|over 10,000 users and \$1 billion/i],
  ['risk-free profit promise', /^(?!keywords:).*risk[- ]free profit(?!\s+from price discrepancies)|^title:.*risk free profits/im],
  ['promised win rate in a description', /^description:.*(?:achieve|achieves|deliver|delivers)[^\n]*\d+(?:-\d+)?% win rates?/im],
  ['"High Success Rate" in a title or heading', /^(?:title:|# ).*high success rate/im],
]

for (const [name, re] of FORBIDDEN) {
  test(`no ${name}`, () => {
    const hits = FILES.filter((f) => re.test(fs.readFileSync(path.join(ROOT, f), 'utf-8')))
    assert.deepEqual(hits, [])
  })
}

test('scans the blog corpus', () => {
  assert.ok(FILES.length > 400, `only ${FILES.length} files`)
})

// Second pass (2026-10-03): ~340 posts shipped identical templated "backtest result" tables
// (e.g. "Win Rate 52.3%", "Sharpe 0.72") with no code or data behind them, and a templated
// "High success rate: 60-70%" / "achieved 1:4 actual" / "expect 4-8% annual returns" family.
// Rule now: a post may only show performance numbers if it carries the figures note, or if it
// documents its method under a "## Sources" heading (the posts with measured results).
const BLOG = FILES.filter((f) => f.startsWith(path.join('content', 'blog')))
const FIGURES_NOTE = '**Note on figures:**'
const CLAIM_LINES: RegExp[] = [
  /^\s*[-*]?\s*(?:\*\*)?(?:win|success|hit) rate(?:\*\*)?\s*:\s*(?:\*\*)?~?\d/i,
  /\b\d{2}(?:\.\d)?%\s+win rates?\b/i,
  /\bwin rates? (?:of|was|is|at|around)\s*~?\d{2}/i,
  /\bsharpe(?: ratio)?\s*(?:of|was|=|:|reaches|reached)\s*-?\d/i,
  /\|\s*(?:sharpe ratio|win rate|annuali[sz]ed return|total return|max(?:imum)? drawdown)\s*\|\s*-?\d/i,
  /\b(?:average|annuali[sz]ed|annual|total) returns? of (?:about |approximately |roughly )?-?\d/i,
]

function proseLines(text: string): string[] {
  let fenced = false
  const out: string[] = []
  for (const line of text.split(/\r?\n/)) {
    if (line.trimStart().startsWith('```')) { fenced = !fenced; continue }
    if (!fenced) out.push(line)
  }
  return out
}

test('posts that show performance numbers carry the figures note or document their method', () => {
  const offenders = BLOG.filter((f) => {
    const text = fs.readFileSync(path.join(ROOT, f), 'utf-8')
    if (text.includes('## Sources') || text.includes(FIGURES_NOTE)) return false
    return proseLines(text).some((l) => CLAIM_LINES.some((re) => re.test(l)))
  })
  assert.deepEqual(offenders, [])
})

const TEMPLATE_PHRASES: [string, RegExp][] = [
  ['templated success-rate bullet', /^\s*-\s*(?:High success rate|Moderate success|Low success)\s*:\s*\d/im],
  ['"achieved 1:4 actual"', /achieved 1:4 actual/i],
  ['templated expected-return sentence', /should expect 4-8% annual returns/i],
  ['templated 15-30% annual returns FAQ', /generates 15-30% annual returns/i],
  ['"proven technical principles used by institutional traders"', /proven technical principles used by institutional traders/i],
  ['templated 0.72 Sharpe conclusion', /The 0\.72 Sharpe ratio and 52% win rate/],
]

for (const [name, re] of TEMPLATE_PHRASES) {
  test(`no ${name}`, () => {
    const hits = BLOG.filter((f) => re.test(fs.readFileSync(path.join(ROOT, f), 'utf-8')))
    assert.deepEqual(hits, [])
  })
}

test('strategy pages do not render hardcoded performance figures', () => {
  for (const f of [path.join('src', 'app', 'strategies', 'page.tsx'), path.join('src', 'app', 'strategies', '[slug]', 'page.tsx')]) {
    const src = fs.readFileSync(path.join(ROOT, f), 'utf-8')
    assert.doesNotMatch(src, /strategy\.(?:winRate|avgReturn|sharpeRatio)/, f)
    assert.doesNotMatch(src, /bt\.(?:totalReturn|annualizedReturn|sharpeRatio|winRate|profitFactor)/, f)
    assert.doesNotMatch(src, /strategy\.yearlyReturns|annualizedReturn\}% annualized/, f)
  }
})
