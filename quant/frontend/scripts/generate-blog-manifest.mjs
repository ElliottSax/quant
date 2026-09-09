#!/usr/bin/env node
// Generates two build artifacts from content/blog/*.md so the blog pages
// never need runtime `fs` access -- see frontend/CLOUDFLARE_MIGRATION.md.
// Cloudflare Workers has no runtime filesystem, so reading content/blog at
// REQUEST time (the previous approach) 404s or 500s in production there,
// even though it works fine on Vercel (serverless functions ship the repo's
// files). This script runs at BUILD time (real fs access, real disk) and
// produces:
//
//   1. src/data/blog-manifest.generated.json -- frontmatter-only metadata for
//      every publishable post (small, ~a few hundred KB), imported directly
//      as a JS module by blog listing/detail pages and generateStaticParams.
//      No runtime fs OR fetch needed for this -- it's just bundled JS.
//
//   2. public/blog-content/<slug>.md -- the full raw markdown body for every
//      publishable post, copied verbatim so OpenNext ships them as static
//      assets. At runtime, src/lib/blog-content.ts fetches these via the
//      Cloudflare Worker's ASSETS binding (or plain fs when not running on
//      Cloudflare, e.g. local dev) to get a single post's full body text.
//
// Both are gitignored and regenerated on every build (see package.json's
// `build`/`cf:preview`/`cf:deploy` scripts).

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.join(__dirname, '..')
const CONTENT_DIR = path.join(ROOT, 'content', 'blog')
const MANIFEST_OUT = path.join(ROOT, 'src', 'data', 'blog-manifest.generated.json')
const CONTENT_ASSETS_DIR = path.join(ROOT, 'public', 'blog-content')

// --- Minimal reimplementation of src/lib/frontmatter.ts's sanitizer -------
// (kept in sync by hand; this script runs standalone under plain Node, not
// through the TS/webpack pipeline, so it can't import the .ts file directly.)

function cleanFrontmatterValue(raw) {
  if (!raw) return ''
  let v = raw.replace(/\s+/g, ' ').trim()
  v = v.replace(/'{2,}/g, "'")
  v = v.replace(/"{2,}/g, '"')
  v = v.replace(/^[\s'"]+/, '').replace(/[\s'"]+$/, '')
  return v.replace(/\s+/g, ' ').trim()
}

function readFrontmatterValue(yamlBlock, key) {
  const m = yamlBlock.match(new RegExp(`^${key}:[ \\t]*(.*(?:\\r?\\n[ \\t]+\\S.*)*)$`, 'm'))
  return m ? cleanFrontmatterValue(m[1]) : ''
}

function readFrontmatterArray(yamlBlock, key) {
  const m = yamlBlock.match(new RegExp(`^${key}:\\s*\\[([^\\]]*)]`, 'm'))
  if (!m) return []
  return m[1].split(',').map((s) => cleanFrontmatterValue(s)).filter(Boolean)
}

// --- Minimal reimplementation of src/lib/noindex-drafts.ts's slug set -----
// Imported as JSON so this script and the real TS module can't drift.
const noindexDraftsSrc = fs.readFileSync(path.join(ROOT, 'src', 'lib', 'noindex-drafts.ts'), 'utf-8')
const slugListMatch = noindexDraftsSrc.match(/NOINDEX_DRAFT_SLUGS[\s\S]*?Set\(\[([\s\S]*?)\]\)/)
const NOINDEX_DRAFT_SLUGS = new Set(
  slugListMatch
    ? [...slugListMatch[1].matchAll(/'([^']+)'/g)].map((m) => m[1])
    : []
)

function isNoindexDraft(slug, status) {
  if (NOINDEX_DRAFT_SLUGS.has(slug)) return true
  return (status ?? '').trim().toLowerCase() === 'template'
}

function parseFrontmatter(raw) {
  const match = raw.match(/^---\r?\n([\s\S]*?)\r?\n---/)
  if (!match) return null
  const yamlBlock = match[1]
  const get = (key) => readFrontmatterValue(yamlBlock, key)
  return {
    title: get('title'),
    description: get('description'),
    date: get('date') || get('published_date'),
    author: get('author'),
    category: get('category'),
    tags: readFrontmatterArray(yamlBlock, 'tags'),
    keywords: readFrontmatterArray(yamlBlock, 'keywords'),
    status: get('status'),
  }
}

function main() {
  if (!fs.existsSync(CONTENT_DIR)) {
    console.error(`[generate-blog-manifest] content dir not found: ${CONTENT_DIR}`)
    fs.mkdirSync(path.dirname(MANIFEST_OUT), { recursive: true })
    fs.writeFileSync(MANIFEST_OUT, '[]\n')
    return
  }

  fs.mkdirSync(CONTENT_ASSETS_DIR, { recursive: true })
  fs.mkdirSync(path.dirname(MANIFEST_OUT), { recursive: true })

  const files = fs.readdirSync(CONTENT_DIR).filter((f) => f.endsWith('.md'))
  const entries = []
  let skippedNoTitle = 0
  let skippedDraft = 0

  for (const file of files) {
    const slug = file.replace(/\.md$/, '')
    const raw = fs.readFileSync(path.join(CONTENT_DIR, file), 'utf-8')
    const frontmatter = parseFrontmatter(raw)
    if (!frontmatter || !frontmatter.title) {
      skippedNoTitle++
      continue
    }
    // Copy the full raw file (frontmatter + body) for EVERY post with a
    // title, draft or not -- matches the old fs-based getArticle(), which
    // was deliberately unfiltered: a noindex-draft's own URL still resolves
    // (it just ships `robots: noindex`), only listings/related-articles/
    // generateStaticParams exclude it. Only the manifest below (used for
    // those listing surfaces) applies the draft filter.
    fs.copyFileSync(path.join(CONTENT_DIR, file), path.join(CONTENT_ASSETS_DIR, file))
    if (isNoindexDraft(slug, frontmatter.status)) {
      skippedDraft++
      continue
    }
    entries.push({ slug, frontmatter })
  }

  entries.sort((a, b) => (b.frontmatter.date > a.frontmatter.date ? 1 : -1))

  fs.writeFileSync(MANIFEST_OUT, JSON.stringify(entries, null, 0))
  console.log(
    `[generate-blog-manifest] wrote ${entries.length} posts to ${path.relative(ROOT, MANIFEST_OUT)} ` +
      `and public/blog-content/ (skipped ${skippedNoTitle} no-title, ${skippedDraft} noindex-draft)`
  )
}

main()
