// Verifies a frontmatter repair using the SITE'S OWN reader (src/lib/frontmatter.ts), no build needed:
//   node scripts/verify_blog_frontmatter.mjs            (Node >= 22.18 strips TypeScript types natively)
// For every content/blog/*.md that differs from git HEAD it parses BOTH versions exactly as
// src/app/blog/[slug]/page.tsx does and fails if anything other than an intended change shows up:
//   - title, author, category, tags, keywords, status, date must parse to identical values;
//   - description may change, but must be 60-158 chars, free of quote runs and not just the title again;
//   - the body (everything after the frontmatter) must be identical, and the file must still yield a title.
import { execFileSync } from 'node:child_process'
import { readFileSync } from 'node:fs'
import { readFrontmatterValue, readFrontmatterArray } from '../src/lib/frontmatter.ts'

function parseFrontmatter(raw) {
  const match = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/)
  if (!match) return null
  const y = match[1]
  const get = (k) => readFrontmatterValue(y, k)
  return {
    fm: {
      title: get('title'), description: get('description'), date: get('date') || get('published_date'),
      author: get('author'), category: get('category'), status: get('status'),
      tags: readFrontmatterArray(y, 'tags'), keywords: readFrontmatterArray(y, 'keywords'),
      reading_time: get('reading_time'), last_updated: get('last_updated'),
    },
    body: match[2],
  }
}

const norm = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim()
const changed = execFileSync('git', ['diff', '--name-only', '--relative', '--', 'content/blog'], { encoding: 'utf8' })
  .split('\n').filter(Boolean)

const failures = []
let descChanged = 0
for (const f of changed) {
  const before = execFileSync('git', ['show', `HEAD:./${f}`], { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 })
  const after = readFileSync(f, 'utf8')
  const b = parseFrontmatter(before), a = parseFrontmatter(after)
  if (!a || !b) { failures.push(`${f}: frontmatter no longer matches the page's parser`); continue }
  if (!a.fm.title) failures.push(`${f}: title would be empty (page would 404)`)
  for (const k of ['title', 'author', 'category', 'status', 'date', 'reading_time', 'last_updated']) {
    if (a.fm[k] !== b.fm[k]) failures.push(`${f}: ${k} changed ${JSON.stringify(b.fm[k])} -> ${JSON.stringify(a.fm[k])}`)
  }
  for (const k of ['tags', 'keywords']) {
    if (JSON.stringify(a.fm[k]) !== JSON.stringify(b.fm[k])) failures.push(`${f}: ${k} changed`)
  }
  // Working copies are CRLF (git autocrlf) while `git show HEAD:` returns LF blobs: compare modulo line endings.
  if (a.body.replace(/\r\n/g, '\n') !== b.body.replace(/\r\n/g, '\n')) failures.push(`${f}: BODY changed`)
  const fmEnd = after.indexOf('\n---', 3)
  const fmText = after.slice(0, fmEnd + 4)
  if (/\r\n/.test(fmText) && /(?<!\r)\n/.test(fmText)) failures.push(`${f}: mixed line endings in frontmatter`)
  if (a.fm.description !== b.fm.description) {
    descChanged++
    const d = a.fm.description, t = a.fm.title
    if (d.length < 60 || d.length > 158) failures.push(`${f}: new description length ${d.length}`)
    if (/'{2,}/.test(d)) failures.push(`${f}: new description has quote runs`)
    if (norm(d) === norm(t) || norm(t).startsWith(norm(d))) failures.push(`${f}: new description still echoes the title`)
  }
}

console.log(`changed files checked: ${changed.length} | descriptions replaced: ${descChanged} | failures: ${failures.length}`)
for (const m of failures.slice(0, 40)) console.log('  FAIL', m)
process.exit(failures.length ? 1 : 0)
