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

// Third pass (2026-10-04): headings such as "Mean Reversion Strategy (68% Win Rate)", FAQ answers
// such as "typically achieve win rates of 55-65%" / "expect 45-55%" and "expect 30-40% degradation"
// were still shipping under the figures note. Headings and FAQ answers must not carry them.
const THIRD_PASS: [string, RegExp][] = [
  ['win-rate number in a heading', /^#{2,4} .*\(\s*\d+(?:-\d+)?%\s*win rate/im],
  ['"expect NN-NN%" win-rate or degradation answer', /expect\s+\d{1,2}(?:\.\d)?-\d{1,2}(?:\.\d)?%\s*(?:degradation|lower|performance|with proper|\()/i],
  ['"degrade by NN-NN%"', /degrade by \d{1,2}-\d{1,2}%/i],
  ['"NN-NN% lower than the backtest"', /\d{1,2}-\d{1,2}% lower than the backtest/i],
  ['typical/realistic win-rate range', /(?:win rates? of|trend-following strategies:|mean reversion:|market making:)\s*\d{2}-\d{2}%/i],
]

for (const [name, re] of THIRD_PASS) {
  test(`no ${name}`, () => {
    const hits = BLOG.filter((f) => {
      const text = proseLines(fs.readFileSync(path.join(ROOT, f), 'utf-8')).join(String.fromCharCode(10))
      return re.test(text)
    })
    assert.deepEqual(hits, [])
  })
}

// Fourth pass (2026-10-04): 400+ posts still showed specific results that nothing in the repo
// computes: numeric result tables (Sharpe 1.35 / Win Rate 53.2% / Max Drawdown -7.8%), "- Win rate: 68.4%"
// bullets (including invented statistics about Congress), "the strategy's 1.5 Sharpe ratio and 62.5% win
// rate demonstrate consistent outperformance", a cost block whose numbers contradicted each other
// (1 trade/day cost 1.9% a year, 5 trades/week cost 0.7%), and "a study by the Journal of Financial
// Economics found ..." with no year, author or title. A banner that says "illustrative" does not make
// them honest, so they are banned outright outside posts that document a method under "## Sources".
const METRIC_WORDS = /sharpe ratio|sortino|calmar|win[- ]?rate|annuali[sz]ed return|annual return|total return|max(?:imum)? drawdown|profit factor|cagr/i
const NUMERIC_CELL = /\|\s*[-+~]?\$?\d[\d.,]*\s*(?:%|:1|x)?\s*(?:\||$)/

function tableBlocks(lines: string[]): string[][] {
  const blocks: string[][] = []
  let cur: string[] = []
  for (const l of lines) {
    if (l.trim().startsWith('|')) cur.push(l)
    else {
      if (cur.length) blocks.push(cur)
      cur = []
    }
  }
  if (cur.length) blocks.push(cur)
  return blocks
}

const SOURCED = (text: string) => text.includes('## Sources')

test('no numeric performance result tables outside documented posts', () => {
  const hits = BLOG.filter((f) => {
    const text = fs.readFileSync(path.join(ROOT, f), 'utf-8')
    if (SOURCED(text)) return false
    return tableBlocks(proseLines(text)).some((b) => {
      const joined = b.join('\n')
      if (/required|break-?even|needed to/i.test(b[0])) return false
      return METRIC_WORDS.test(joined) && b.slice(2).some((r) => NUMERIC_CELL.test(r))
    })
  })
  assert.deepEqual(hits, [])
})

const BULLET_METRIC = /^\s*[-*]\s+(?:\*\*)?(?:win[- ]?rate|success rate|average return(?: per trade)?|sharpe(?: ratio)?|total return|annuali[sz]ed return|annual return|max(?:imum)? drawdown|profit factor)(?:\*\*)?\s*(?:\([^)]*\))?\s*[:=]\s*(?:\*\*)?[-+~]?\$?\d/i

test('no bullet stating a specific performance metric value', () => {
  const hits = BLOG.filter((f) => {
    const text = fs.readFileSync(path.join(ROOT, f), 'utf-8')
    if (SOURCED(text)) return false
    return proseLines(text).some((l) => BULLET_METRIC.test(l))
  })
  assert.deepEqual(hits, [])
})

const FOURTH_PASS: [string, RegExp][] = [
  ['"the strategy\'s N Sharpe ratio and N% win rate" conclusion', /\d(?:\.\d+)?\s+Sharpe(?: ratio)?\s+and\s+\d{2}(?:\.\d+)?%\s+win rate/i],
  ['templated commission-impact numbers', /\d+ trades?\/(?:day|week) at 0\.05% commission\*\*:\s*-?\d/i],
  ['templated "Impact on annual return: N%" line', /^Impact on (?:annual return|Sharpe ratio): [\d.]+/m],
  ['templated regime-aware Sharpe improvement', /Regime-aware strategies can achieve 20-40% Sharpe/],
  ['templated "34-160% Sharpe ratio improvement"', /34-160% Sharpe ratio improvement/],
  ['templated daily-retraining Sharpe gain', /Daily retraining improves Sharpe ratios by 2-8%/],
  ['templated "Risk-Return Trade-offs ... improved 33.5%"', /Risk-Return Trade-offs\*\*: While maximum drawdown improved/],
  ['"our backtest(s)" result with a number and no code', /\bin our (?:own )?back-?tests?\b[^.\n]*\d/i],
]

for (const [name, re] of FOURTH_PASS) {
  test(`no ${name}`, () => {
    const hits = BLOG.filter((f) => {
      const text = fs.readFileSync(path.join(ROOT, f), 'utf-8')
      if (SOURCED(text)) return false
      return re.test(proseLines(text).join(String.fromCharCode(10)))
    })
    assert.deepEqual(hits, [])
  })
}

test('no study cited by journal name alone (no year, no author)', () => {
  const hits = BLOG.filter((f) => {
    const text = fs.readFileSync(path.join(ROOT, f), 'utf-8')
    if (SOURCED(text)) return false
    return proseLines(text).some(
      (l) => /\b(?:study|survey|research|report|paper)s? (?:by|from|published in) (?:the )?Journal of \w+/i.test(l) && !/\b(?:19|20)\d\d\b/.test(l)
    )
  })
  assert.deepEqual(hits, [])
})
