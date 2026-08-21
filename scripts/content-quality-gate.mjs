#!/usr/bin/env node
/**
 * Rejects boilerplate before it reaches the site.
 *
 *   node scripts/content-quality-gate.mjs <file.md> [--content-dir quant/frontend/content/blog]
 *   node scripts/content-quality-gate.mjs --audit <dir>     # score a whole directory
 *
 * Exit 0 = publishable, exit 1 = rejected (reason on stderr).
 *
 * WHY THIS EXISTS
 * ---------------
 * A large share of the published corpus was produced by template scripts in
 * ../content-engine (36 of them at last count) that make no model call at all:
 * they take a topic title, split it on ": ", and substitute the halves into a
 * fixed f-string. `final_expansion.py` is the clearest example, and its own
 * success message -- "All 50 articles regenerated with 1500+ word content" --
 * shows the quality bar it was working to.
 *
 * The result on dividendengines: 1,903 published articles, 93% carrying the
 * identical sentence "This article provides valuable insights and information",
 * and only 124 distinct opening paragraphs across a 200-file sample. That site
 * now excludes them from its sitemap and serves them noindex -- which is an
 * admission that they should never have been published.
 *
 * Word count cannot detect this; a mail-merged article is long by construction.
 * Overlap against what is already published can, because the whole method is
 * reuse.
 *
 * HOW IT DECIDES
 * --------------
 * Every article is reduced to the set of its 8-word shingles. A candidate is
 * scored on how many of its shingles ALREADY EXIST in the published corpus. An
 * original article shares stock phrases and little else; a template fill shares
 * nearly everything but the substituted nouns.
 */

import fs from 'node:fs'
import path from 'node:path'

const SHINGLE = 8

// Tuned against this repo's real corpus -- see the --audit output in the commit
// that added this. Genuine articles score well under 0.30; template fills score
// far above it. The gap is wide, so the exact cut is not delicate.
const MAX_OVERLAP = 0.45

// Sentences that only a template produces. Cheap to check and unambiguous.
const FILLER = [
  'this article provides valuable insights and information',
  'offers valuable insights for better investment decisions',
  'this comprehensive guide provides everything needed to understand',
]

function splitFrontmatter(raw) {
  if (!raw.startsWith('---')) return { front: '', body: raw }
  const end = raw.indexOf('\n---', 3)
  if (end === -1) return { front: '', body: raw }
  return { front: raw.slice(3, end), body: raw.slice(end + 4) }
}

function stripFrontmatter(raw) {
  return splitFrontmatter(raw).body
}

export function normalise(raw) {
  return stripFrontmatter(raw)
    .toLowerCase()
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

export function shingles(text, n = SHINGLE) {
  const words = text.split(' ').filter(Boolean)
  const out = new Set()
  for (let i = 0; i + n <= words.length; i++) out.add(words.slice(i, i + n).join(' '))
  return out
}

/** Every shingle appearing anywhere in `dir`, so a candidate can be scored against it. */
export function corpusShingles(dir) {
  const seen = new Set()
  if (!fs.existsSync(dir)) return seen
  for (const f of fs.readdirSync(dir)) {
    if (!f.endsWith('.md') && !f.endsWith('.mdx')) continue
    const text = normalise(fs.readFileSync(path.join(dir, f), 'utf8'))
    for (const s of shingles(text)) seen.add(s)
  }
  return seen
}

export function score(candidateText, corpus) {
  const mine = shingles(normalise(candidateText))
  if (mine.size === 0) return { overlap: 1, shingles: 0 }
  let hits = 0
  for (const s of mine) if (corpus.has(s)) hits++
  return { overlap: hits / mine.size, shingles: mine.size }
}

export function check(file, contentDir, corpus) {
  const raw = fs.readFileSync(file, 'utf8')
  const lower = normalise(raw)

  // Check the frontmatter as well as the body. The commonest fingerprint in this
  // corpus is not in the body at all: 788 of 911 queued articles carry the
  // identical `description: This article provides valuable insights and
  // information.` Stripping frontmatter before scanning -- as the first version of
  // this did -- misses every one of them, and an identical meta description across
  // 788 pages is its own SEO problem whatever the body contains.
  const front = splitFrontmatter(raw).front.toLowerCase()
  for (const phrase of FILLER) {
    if (lower.includes(phrase)) {
      return { ok: false, reason: `body contains template filler: "${phrase}"` }
    }
    if (front.includes(phrase)) {
      return { ok: false, reason: `frontmatter contains template filler: "${phrase}"` }
    }
  }

  const { overlap, shingles: n } = score(raw, corpus ?? corpusShingles(contentDir))
  if (n < 120) return { ok: false, reason: `too short to assess (${n} shingles)` }
  if (overlap > MAX_OVERLAP) {
    return {
      ok: false,
      reason: `${(overlap * 100).toFixed(1)}% of its 8-word phrases already exist in published content (limit ${(MAX_OVERLAP * 100).toFixed(0)}%)`,
    }
  }
  return { ok: true, overlap }
}

// --- CLI ---------------------------------------------------------------
const args = process.argv.slice(2)
if (args[0] === '--audit') {
  const dir = args[1]
  const contentDir = args[2] || 'quant/frontend/content/blog'
  // Accumulate as we go, so this simulates what actually happens: each article is
  // published into the content dir and becomes part of the corpus the NEXT one is
  // judged against. Scoring every candidate against a frozen corpus makes a batch
  // of articles that are near-identical to each OTHER all look original -- which
  // is exactly the failure this corpus exhibits (median intra-queue overlap 94%).
  const corpus = corpusShingles(contentDir)
  const files = fs.readdirSync(dir).filter((f) => f.endsWith('.md')).sort()
  const rows = files.map((f) => {
    const full = path.join(dir, f)
    const r = check(full, contentDir, corpus)
    if (r.ok) {
      for (const sh of shingles(normalise(fs.readFileSync(full, 'utf8')))) corpus.add(sh)
    }
    return { f, ...r }
  })
  const bad = rows.filter((r) => !r.ok)
  console.log(`audited ${rows.length} files against ${contentDir} (${corpus.size} corpus shingles)`)
  console.log(`  would publish: ${rows.length - bad.length}`)
  console.log(`  would reject:  ${bad.length}`)
  const byReason = {}
  for (const b of bad) {
    const key = b.reason.replace(/[\d.]+%/g, 'N%').replace(/\(\d+ shingles\)/, '(N shingles)')
    byReason[key] = (byReason[key] || 0) + 1
  }
  for (const [k, v] of Object.entries(byReason)) console.log(`    ${v}\t${k}`)
  const ok = rows.filter((r) => r.ok)
  if (ok.length) {
    const avg = ok.reduce((a, r) => a + r.overlap, 0) / ok.length
    console.log(`  mean overlap of passing files: ${(avg * 100).toFixed(1)}%`)
  }
  process.exit(0)
}

if (args.length && !args[0].startsWith('--')) {
  const file = args[0]
  const dirFlag = args.indexOf('--content-dir')
  const contentDir = dirFlag !== -1 ? args[dirFlag + 1] : 'quant/frontend/content/blog'
  const result = check(file, contentDir)
  if (!result.ok) {
    console.error(`REJECTED ${path.basename(file)}: ${result.reason}`)
    process.exit(1)
  }
  console.log(`OK ${path.basename(file)} (${(result.overlap * 100).toFixed(1)}% overlap)`)
  process.exit(0)
}
