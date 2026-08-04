import { MetadataRoute } from 'next'
import fs from 'fs'
import path from 'path'
import { getCongressTrades, memberSlug } from '@/lib/congress-trades'

// Get all blog post slugs dynamically from content/blog/*.md
function getBlogSlugs(): string[] {
  try {
    const blogDir = path.join(process.cwd(), 'content', 'blog')
    const files = fs.readdirSync(blogDir)
    return files
      .filter(f => f.endsWith('.md') && f !== 'ARTICLES_COMPLETED.md')
      .map(f => f.replace(/\.md$/, ''))
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
    '/congress-stock-trades',
    '/congress-stock-trades/weekly',
    '/blog',
    '/politicians',
    '/leaderboard',
    '/dashboard',
    '/backtesting',
    '/backtesting/builder',
    '/market-dashboard',
    '/signals',
    '/scanner',
    '/options',
    '/portfolio',
    '/strategies',
    '/pricing',
    '/charts',
    '/network',
    '/discoveries',
    '/resources',
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
