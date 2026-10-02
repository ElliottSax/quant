// Fails if scripts/generate-blog-manifest.mjs would read a DIFFERENT noindex set than src/lib/noindex-drafts.ts.
//   node scripts/check_noindex_parse.mjs      (Node >= 22.18 strips TypeScript types natively)
// The generator re-parses the TS source with a regex; apostrophes in comments once made it miss ~200 of 293 slugs.
import { readFileSync } from 'node:fs'
import { NOINDEX_DRAFT_SLUGS } from '../src/lib/noindex-drafts.ts'

const gen = readFileSync(new URL('./generate-blog-manifest.mjs', import.meta.url), 'utf8')
const src = readFileSync(new URL('../src/lib/noindex-drafts.ts', import.meta.url), 'utf8')
// reuse the generator's exact preprocessing + regex so this check cannot drift from it
if (!gen.includes(".replace(/\\/\\*[\\s\\S]*?\\*\\//g, '')") || !gen.includes(".replace(/^\\s*\\/\\/.*$/gm, '')")) {
  console.error('generate-blog-manifest.mjs no longer strips comments before parsing the noindex set'); process.exit(1)
}
const stripped = src.replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '')
const m = stripped.match(/NOINDEX_DRAFT_SLUGS[\s\S]*?Set\(\[([\s\S]*?)\]\)/)
const parsed = new Set(m ? [...m[1].matchAll(/'([^']+)'/g)].map((x) => x[1]) : [])
const missing = [...NOINDEX_DRAFT_SLUGS].filter((s) => !parsed.has(s))
const extra = [...parsed].filter((s) => !NOINDEX_DRAFT_SLUGS.has(s))
console.log(`real set: ${NOINDEX_DRAFT_SLUGS.size} | generator parse: ${parsed.size} | missing: ${missing.length} | extra: ${extra.length}`)
if (missing.length || extra.length) { console.error({ missing: missing.slice(0, 5), extra: extra.slice(0, 5) }); process.exit(1) }
console.log('OK: generator and site read the same noindex set')
