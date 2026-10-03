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
