import { MetadataRoute } from 'next'
import fs from 'fs'
import path from 'path'
import { getCongressTrades, memberSlug } from '@/lib/congress-trades'
import { readFrontmatterValue } from '@/lib/frontmatter'
import { isNoindexDraft } from '@/lib/noindex-drafts'

// Get all publishable blog post slugs from content/blog/*.md.
// Unfinished drafts -- placeholder-bearing bodies and articles declaring
// `status: template` -- are excluded; see src/lib/noindex-drafts.ts.
/** A publishable slug plus the date it actually claims to have been updated. */
interface BlogEntry {
  slug: string
  lastModified: Date
}

/**
 * Every post's REAL last-modified date, not today's.
 *
 * Stamping `new Date()` on all 493 URLs tells Google the entire site changed this
 * morning, every morning. Google discounts a lastmod that always says "now", so a
 * uniformly-fresh sitemap is worth less than an honest one -- and it destroys the signal
 * for the handful of pages that genuinely did change.
 *
 * The date is taken from the post's own frontmatter (`last_updated`, then `updated`, then
 * `date`, then `published_date`), falling back to the file's mtime and only then to now.
 */
function getBlogEntries(): BlogEntry[] {
  try {
    const blogDir = path.join(process.cwd(), 'content', 'blog')
    const files = fs.readdirSync(blogDir)
    return files
      .filter(f => f.endsWith('.md') && f !== 'ARTICLES_COMPLETED.md')
      .map(f => {
        const slug = f.replace(/\.md$/, '')
        const filePath = path.join(blogDir, f)
        let status = ''
        let lastModified: Date | null = null
        try {
          const raw = fs.readFileSync(filePath, 'utf-8')
          const fm = raw.match(/^---\r?\n([\s\S]*?)\r?\n---/)
          if (fm) {
            status = readFrontmatterValue(fm[1], 'status')
            for (const key of ['last_updated', 'updated', 'date', 'published_date']) {
              const v = readFrontmatterValue(fm[1], key)
              if (!v) continue
              const d = new Date(v)
              // A frontmatter date in the future is a generation artefact, not a real
              // edit; using it would advertise a modification that has not happened.
              if (!Number.isNaN(d.getTime()) && d.getTime() <= Date.now()) {
                lastModified = d
                break
              }
            }
          }
          if (!lastModified) lastModified = fs.statSync(filePath).mtime
        } catch {
          // Unreadable file -- keep the slug, fall back below.
        }
        return { slug, status, lastModified: lastModified ?? new Date() }
      })
      .filter(e => !isNoindexDraft(e.slug, e.status))
      .map(({ slug, lastModified }) => ({ slug, lastModified }))
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
    '/tools/max-sharpe',
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
    '/data-vendors',
    '/pandas-ta-columns',
    '/statsmodels-imports',
    '/indicator-formulas',
    '/backtrader-vs-vectorbt',
    '/fundamentals',
    '/yield-curve',
    '/cot-report',
    // Deliberately absent: /leaderboard, /signals, /portfolio, /showcase, /discoveries,
    // /compare. Each was replaced with an in-development page carrying
    // robots.index = false after its contents were found to be browser-generated rather
    // than measured. A noindex page listed in the sitemap sends Google contradictory
    // instructions, so they are added back here only when the real page ships. Before
    // adding any page below, check its `robots` metadata.
    '/courses',
    '/courses/backtesting-101',
  ]

  const toolEntries = toolPages.map(page => ({
    url: `${baseUrl}${page}`,
    lastModified: currentDate,
    changeFrequency: 'weekly' as const,
    priority: 0.9,
  }))

  // Trust and compliance pages. These change rarely and are not the reason anyone
  // visits, hence the low priority and monthly frequency — but they must be
  // crawlable and listed: affiliate networks and ad partners check that a site
  // publishes its disclosure, privacy, terms and contact details, and an
  // unlisted page is one they may not find. All are indexable (no `robots`
  // override on any of them).
  const legalPages = [
    '/about',
    '/contact',
    '/disclaimer',
    '/privacy',
    '/terms',
    '/affiliate-disclosure',
  ]

  const legalEntries = legalPages.map(page => ({
    url: `${baseUrl}${page}`,
    lastModified: currentDate,
    changeFrequency: 'monthly' as const,
    priority: 0.4,
  }))

  // Dynamically generated blog post URLs, each carrying its own real date.
  const blogEntries = getBlogEntries().map(({ slug, lastModified }) => ({
    url: `${baseUrl}/blog/${slug}`,
    lastModified,
    changeFrequency: 'monthly' as const,
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
    // Trust and compliance pages
    ...legalEntries,
    // Per-ticker congressional-trade pages
    ...tickerEntries,
    // Blog articles
    ...blogEntries,
  ]
}
