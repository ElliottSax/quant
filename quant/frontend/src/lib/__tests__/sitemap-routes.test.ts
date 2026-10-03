// Every static path listed in app/sitemap.ts must resolve to a real page, and the
// data-driven congress pages must be renderable on demand. Regression for
// /congress-stock-trades/HON: listed in the sitemap (built from live data) but a
// 404 because the page only knew the tickers present at the last build.
// Run with `npm run test` (node's built-in runner, no browser, no network).

import { test, describe } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const appDir = path.resolve(here, '..', '..', 'app')
const sitemapSrc = fs.readFileSync(path.join(appDir, 'sitemap.ts'), 'utf8')

// Quoted absolute paths inside the toolPages / legalPages arrays only
// (comments are stripped first so the "deliberately absent" notes don't count).
function staticPaths(): string[] {
  const code = sitemapSrc.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '')
  const out: string[] = []
  for (const name of ['toolPages', 'legalPages']) {
    const start = code.indexOf(`const ${name} = [`)
    assert.ok(start >= 0, `${name} array not found in sitemap.ts`)
    const body = code.slice(start, code.indexOf(']', start))
    for (const s of body.matchAll(/'(\/[^']*)'/g)) out.push(s[1])
  }
  return out
}

// A route exists if app/<path>/page.(tsx|ts|jsx|js|mdx) exists, allowing route
// groups "(group)" and dynamic segments "[x]" to stand in for a path segment.
function routeExists(urlPath: string, dir = appDir): boolean {
  const segs = urlPath.split('/').filter(Boolean)
  if (segs.length === 0) return /^page\./.test(fs.readdirSync(dir).find((f) => /^page\./.test(f)) ?? '')
  const [head, ...rest] = segs
  const entries = fs.readdirSync(dir, { withFileTypes: true }).filter((e) => e.isDirectory())
  for (const e of entries) {
    const isGroup = /^\(.+\)$/.test(e.name)
    const isDynamic = /^\[.+\]$/.test(e.name)
    const sub = path.join(dir, e.name)
    if (isGroup && routeExists(urlPath, sub)) return true
    if (e.name === head || isDynamic) {
      if (rest.length === 0) {
        if (fs.readdirSync(sub).some((f) => /^page\.(tsx|ts|jsx|js|mdx)$/.test(f))) return true
      } else if (routeExists('/' + rest.join('/'), sub)) return true
    }
  }
  return false
}

describe('sitemap static paths', () => {
  const paths = staticPaths()
  test('found a plausible number of static paths', () => {
    assert.ok(paths.length > 20, `only found ${paths.length}`)
    assert.ok(paths.includes('/congress-stock-trades/late-filers'))
  })
  for (const p of paths) {
    test(`${p} has a page`, () => {
      assert.ok(routeExists(p), `sitemap lists ${p} but no app route serves it`)
    })
  }
})

describe('data-driven congress pages', () => {
  for (const rel of ['congress-stock-trades/[ticker]/page.tsx', 'congress-stock-trades/member/[slug]/page.tsx']) {
    test(`${rel} renders params not known at build time`, () => {
      const src = fs.readFileSync(path.join(appDir, rel), 'utf8')
      assert.ok(!/dynamicParams\s*=\s*false/.test(src), 'dynamicParams = false makes new tickers/members 404 until the next build')
      assert.ok(/notFound\(\)/.test(src), 'absent tickers/members must still return a real 404')
    })
  }
})
