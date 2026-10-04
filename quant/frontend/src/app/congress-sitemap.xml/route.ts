import { getCongressTrades, tickerSlugs, memberSlugs } from '@/lib/congress-trades'

// Congress ticker / member URLs are listed here, NOT in app/sitemap.ts.
// sitemap.ts is prerendered at build time, so it snapshots the FMP feed as it was during
// the build, while the pages render at request time against the feed's later state.
// A ticker (HON) that was in the build-time snapshot but not in the runtime feed was
// listed in the sitemap and served as a 404. This route is rendered at request time and
// goes through the same getCongressTrades() fetch (same URL, same data cache) and the same
// tickerSlugs()/memberSlugs() predicate the pages use, so what it lists is what the pages
// resolve, up to the cache window.
export const dynamic = 'force-dynamic'

const BASE = 'https://quantengines.com'

function xml(urls: string[]): string {
  const now = new Date().toISOString()
  const items = urls
    .map((u) => `<url><loc>${u}</loc><lastmod>${now}</lastmod><changefreq>daily</changefreq><priority>0.6</priority></url>`)
    .join('')
  return `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${items}</urlset>`
}

export async function GET() {
  let urls: string[] = []
  try {
    const trades = (await getCongressTrades())?.trades ?? []
    urls = [
      ...tickerSlugs(trades).map((t) => `${BASE}/congress-stock-trades/${encodeURIComponent(t)}`),
      ...memberSlugs(trades).map((m) => `${BASE}/congress-stock-trades/member/${m}`),
    ]
  } catch {
    urls = [] // a feed problem must not break crawlers: an empty list is safe
  }
  return new Response(xml(urls), {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': 'public, s-maxage=3600, stale-while-revalidate=3600',
    },
  })
}
