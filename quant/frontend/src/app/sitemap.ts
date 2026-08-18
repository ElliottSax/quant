import { MetadataRoute } from 'next'
import fs from 'fs'
import path from 'path'
import { getCongressTrades, memberSlug } from '@/lib/congress-trades'
import { readFrontmatterValue } from '@/lib/frontmatter'
import { isNoindexDraft } from '@/lib/noindex-drafts'

// Get all publishable blog post slugs from content/blog/*.md.
// Unfinished drafts -- placeholder-bearing bodies and articles declaring
// `status: template` -- are excluded; see src/lib/noindex-drafts.ts.
function getBlogSlugs(): string[] {
  try {
    const blogDir = path.join(process.cwd(), 'content', 'blog')
    const files = fs.readdirSync(blogDir)
    return files
      .filter(f => f.endsWith('.md') && f !== 'ARTICLES_COMPLETED.md')
      .map(f => f.replace(/\.md$/, ''))
      .filter(slug => {
        let status = ''
        try {
          const raw = fs.readFileSync(path.join(blogDir, `${slug}.md`), 'utf-8')
          const fm = raw.match(/^---\r?\n([\s\S]*?)\r?\n---/)
          if (fm) status = readFrontmatterValue(fm[1], 'status')
        } catch {
          // Unreadable file -- fall back to the slug list alone.
        }
        return !isNoindexDraft(slug, status)
      })
  } catch {
    return []
  }
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = 'https://quantengines.com'
  const currentDate = new Date()

  // Per-ticker congressional-trade pages (the actively-traded symbols in the
  // current data). Guarded so a data hiccup can't break the sitemap.
  let tickerEntries: MetadataRoute.Sitemap = []
  try {
    const congress = await getCongressTrades()
    const trades = congress?.trades ?? []
    const tickers = new Set(trades.map((t) => t.ticker.toUpperCase()))
    const members = new Set(trades.map((t) => memberSlug(t.member)).filter(Boolean))
    tickerEntries = [
      ...[...tickers].map((tk) => ({
        url: `${baseUrl}/congress-stock-trades/${tk}`,
        lastModified: currentDate, changeFrequency: 'daily' as const, priority: 0.6,
      })),
      ...[...members].map((m) => ({
        url: `${baseUrl}/congress-stock-trades/member/${m}`,
        lastModified: currentDate, changeFrequency: 'daily' as const, priority: 0.6,
      })),
    ]
  } catch {
    tickerEntries = []
  }

  // Static tool pages
  const toolPages = [
    '/tools',
    '/tools/position-size',
    '/tools/risk-reward',
    '/congress-stock-trades',
    '/congress-stock-trades/weekly',
    '/blog',
    '/politicians',
    '/dashboard',
    '/backtesting',
    '/backtesting/builder',
    '/market-dashboard',
    '/scanner',
    '/options',
    '/strategies',
    '/pricing',
    '/charts',
    '/network',
    '/resources',
    // Deliberately absent: /leaderboard, /signals, /portfolio, /showcase, /discoveries.
    // Each was replaced with an in-development page carrying robots.index = false after
    // its contents were found to be browser-generated rather than measured. A noindex
    // page listed in the sitemap sends Google contradictory instructions, so they are
    // added back here only when the real page ships.
    '/courses',
    '/courses/backtesting-101',
  ]

  const toolEntries = toolPages.map(page => ({
    url: `${baseUrl}${page}`,
    lastModified: currentDate,
    changeFrequency: 'weekly' as const,
    priority: 0.9,
  }))

  // Dynamically generated blog post URLs
  const blogSlugs = getBlogSlugs()
  const blogEntries = blogSlugs.map(slug => ({
    url: `${baseUrl}/blog/${slug}`,
    lastModified: currentDate,
    changeFrequency: 'weekly' as const,
    priority: 0.7,
  }))

  return [
    // Homepage
    {
      url: baseUrl,
      lastModified: currentDate,
      changeFrequency: 'daily',
      priority: 1,
    },
    // Tool pages
    ...toolEntries,
    // Per-ticker congressional-trade pages
    ...tickerEntries,
    // Blog articles
    ...blogEntries,
  ]
}
