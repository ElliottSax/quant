// Reads a single blog post's full raw markdown (frontmatter + body) at
// RUNTIME, without depending on a real filesystem being present.
//
// WHY THIS EXISTS: blog/page.tsx and blog/[slug]/page.tsx used to read
// content/blog/*.md directly via `fs` on every request. That works on Vercel
// (a serverless function's deployment bundle includes the repo's files) but
// not on Cloudflare Workers, which has no runtime filesystem at all -- see
// frontend/CLOUDFLARE_MIGRATION.md for the full story (this was the actual
// cause of a live 404 on every /blog/<slug> URL after the first Cloudflare
// deploy).
//
// The fix: `scripts/generate-blog-manifest.mjs` runs at BUILD time (real fs,
// real disk) and (a) writes src/data/blog-manifest.generated.json --
// frontmatter-only metadata for every publishable post, imported directly as
// a JS module wherever only title/description/date/tags/etc. are needed
// (the blog index, generateStaticParams, related-articles, sitemap-style
// listings) -- and (b) copies every publishable post's full raw .md into
// public/blog-content/<slug>.md, which OpenNext then ships as an ordinary
// static asset alongside every other file in public/.
//
// getArticleBody() below is the only thing that still needs a FULL post body
// (blog/[slug]/page.tsx rendering the actual article). On Cloudflare it
// fetches that static asset through the Worker's ASSETS binding (exposed via
// @opennextjs/cloudflare's getCloudflareContext()) -- the supported way to
// read a bundled static file from within a Worker at request time, since
// there is no `fs` to fall back to there. Outside Cloudflare (local `next
// dev`/`next start`, or a future non-Cloudflare deploy target) it falls back
// to a plain `fs.readFileSync` against content/blog/ directly, so nothing
// about local development changes.

import path from 'path'

const CONTENT_ASSET_PATH = (slug: string) => `/blog-content/${slug}.md`

async function readViaCloudflareAssets(slug: string): Promise<string | null> {
  // Only ever import/execute this on the server; dynamic import keeps
  // @opennextjs/cloudflare out of any client bundle analysis.
  const { getCloudflareContext } = await import('@opennextjs/cloudflare')
  const { env } = await getCloudflareContext({ async: true })
  if (!env?.ASSETS) return null
  const res = await env.ASSETS.fetch(new URL(CONTENT_ASSET_PATH(slug), 'http://assets.internal'))
  if (!res.ok) return null
  return res.text()
}

function readViaFs(slug: string): string | null {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const fs = require('fs') as typeof import('fs')
  const filePath = path.join(process.cwd(), 'content', 'blog', `${slug}.md`)
  if (!fs.existsSync(filePath)) return null
  return fs.readFileSync(filePath, 'utf-8')
}

/**
 * Returns the full raw markdown (frontmatter + body) for one post, or null
 * if it doesn't exist. Tries the Cloudflare ASSETS binding first; falls back
 * to `fs` when not running on Cloudflare (local dev, or a non-Cloudflare
 * deploy target) or when the binding isn't available for any other reason.
 */
export async function getArticleRaw(slug: string): Promise<string | null> {
  try {
    const viaAssets = await readViaCloudflareAssets(slug)
    if (viaAssets !== null) return viaAssets
  } catch {
    // Not running on Cloudflare (getCloudflareContext throws outside a
    // Workers request), or the ASSETS binding isn't configured -- fall
    // through to fs below.
  }
  try {
    return readViaFs(slug)
  } catch {
    return null
  }
}
