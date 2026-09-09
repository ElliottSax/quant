// This page used to read content/blog/*.md via `fs` at request time, which
// only works where a real filesystem exists -- Cloudflare Workers has none
// (see frontend/CLOUDFLARE_MIGRATION.md). It now imports a build-time-
// generated manifest instead (scripts/generate-blog-manifest.mjs), which
// needs no fs/fetch at runtime at all -- it's just bundled JSON. Kept as
// 'force-static': the root layout (src/app/layout.tsx) sets 'force-dynamic'
// for the whole app by default (live-API pages crash prerendering with empty
// data), so this leaf explicitly opts back into static generation to
// override that default. It has no real per-request dynamic behavior of its
// own (no searchParams are actually read; filtering happens client-side).
export const dynamic = 'force-static'

import { Metadata } from 'next'
import Link from 'next/link'
import blogManifest from '@/data/blog-manifest.generated.json'

// ---------------------------------------------------------------------------
// Helpers (frontmatter parsing shared with [slug]/page.tsx via @/lib/frontmatter)
// ---------------------------------------------------------------------------

interface Frontmatter {
  title: string
  description: string
  date: string
  author: string
  category: string
  tags: string[]
  keywords: string[]
  status: string
}

interface Article {
  slug: string
  frontmatter: Frontmatter
}

// The manifest already has the noindex-draft filter and sort order applied
// (scripts/generate-blog-manifest.mjs mirrors src/lib/noindex-drafts.ts) --
// no fs, no re-filtering needed here.
function getAllArticles(): Article[] {
  return blogManifest as Article[]
}

// ---------------------------------------------------------------------------
// Metadata
// ---------------------------------------------------------------------------

export const metadata: Metadata = {
  title: 'Blog - Quantitative Trading Guides & Research | QuantEngines',
  description:
    'In-depth articles on quantitative trading strategies, backtesting, technical analysis, options, statistical arbitrage, and more. Free research for systematic traders.',
  openGraph: {
    title: 'QuantEngines Blog - Trading Research & Strategy Guides',
    description:
      'In-depth articles on quantitative trading strategies, backtesting, and systematic trading.',
    url: 'https://quantengines.com/blog',
  },
  alternates: {
    canonical: '/blog',
  },
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function BlogIndexPage() {
  // A `searchParams` prop used to be declared here for category/tag
  // filtering, but its value was never actually read (filtering happens
  // client-side) -- and merely declaring that prop is enough for Next.js to
  // treat the whole page as dynamically rendered, which defeats the static
  // prerendering this page needs for Cloudflare (see the file-top comment).
  // Removed as dead code.
  const allArticles = getAllArticles()

  // Collect unique categories & tags for sidebar
  const categories = Array.from(new Set(allArticles.map((a) => a.frontmatter.category).filter(Boolean))).sort()
  const tagCounts: Record<string, number> = {}
  allArticles.forEach((a) =>
    a.frontmatter.tags.forEach((t) => {
      tagCounts[t] = (tagCounts[t] || 0) + 1
    }),
  )
  const topTags = Object.entries(tagCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 20)

  return (
    <div className="max-w-6xl mx-auto">
      {/* Page Header */}
      <header className="mb-8">
        <nav className="flex items-center gap-2 text-xs font-mono text-[hsl(210,20%,50%)] mb-4">
          <Link href="/" className="hover:text-[hsl(45,96%,58%)] transition-colors">
            Home
          </Link>
          <span className="text-[hsl(215,40%,25%)]">/</span>
          <span className="text-[hsl(210,20%,65%)]">Blog</span>
        </nav>

        <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">
          Trading Research & Strategy Guides
        </h1>
        <p className="text-[hsl(210,20%,55%)] text-lg">
          {allArticles.length} articles on quantitative trading, backtesting, and systematic strategies.
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Main: Article List */}
        <div className="lg:col-span-3">
          {/* Category filter bar */}
          <div className="flex flex-wrap gap-2 mb-6 pb-4 border-b border-[hsl(215,40%,14%)]">
            <Link
              href="/blog"
              className="px-3 py-1 text-xs font-medium rounded bg-[hsl(45,96%,58%)]/10 border border-[hsl(45,96%,58%)]/30 text-[hsl(45,96%,58%)] hover:bg-[hsl(45,96%,58%)]/20 transition-colors"
            >
              All ({allArticles.length})
            </Link>
            {categories.map((cat) => {
              const count = allArticles.filter((a) => a.frontmatter.category === cat).length
              return (
                <Link
                  key={cat}
                  href={`/blog?category=${encodeURIComponent(cat)}`}
                  className="px-3 py-1 text-xs font-medium rounded border border-[hsl(215,40%,18%)] text-[hsl(210,20%,65%)] hover:border-[hsl(210,100%,56%)]/40 hover:text-[hsl(210,100%,70%)] transition-colors"
                >
                  {cat} ({count})
                </Link>
              )
            })}
          </div>

          {/* Article cards */}
          <div className="space-y-4">
            {allArticles.map((article) => (
              <Link
                key={article.slug}
                href={`/blog/${article.slug}`}
                className="group block p-5 rounded-lg border border-[hsl(215,40%,14%)] bg-[hsl(220,55%,5%)] hover:border-[hsl(45,96%,58%)]/30 hover:bg-[hsl(215,50%,8%)] transition-all"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider bg-[hsl(210,100%,56%)]/10 text-[hsl(210,100%,70%)] rounded">
                        {article.frontmatter.category}
                      </span>
                      <span className="text-[10px] text-[hsl(210,20%,45%)] font-mono">
                        {article.frontmatter.date}
                      </span>
                    </div>
                    <h2 className="text-base font-semibold text-white group-hover:text-[hsl(45,96%,58%)] transition-colors mb-1.5 line-clamp-2">
                      {article.frontmatter.title}
                    </h2>
                    <p className="text-sm text-[hsl(210,20%,55%)] line-clamp-2 mb-2">
                      {article.frontmatter.description}
                    </p>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-[hsl(210,20%,50%)]">
                        By {article.frontmatter.author}
                      </span>
                      <div className="flex gap-1.5">
                        {article.frontmatter.tags.slice(0, 3).map((tag) => (
                          <span
                            key={tag}
                            className="px-1.5 py-0.5 text-[10px] font-mono bg-[hsl(215,50%,12%)] border border-[hsl(215,40%,16%)] text-[hsl(210,20%,55%)] rounded"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="hidden sm:flex items-center justify-center w-8 h-8 rounded bg-[hsl(215,50%,12%)] text-[hsl(210,20%,50%)] group-hover:text-[hsl(45,96%,58%)] group-hover:bg-[hsl(45,96%,58%)]/10 transition-colors flex-shrink-0 mt-4">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Sidebar */}
        <aside className="lg:col-span-1 space-y-6">
          {/* Popular Tags */}
          <div className="p-4 rounded-lg border border-[hsl(215,40%,14%)] bg-[hsl(220,55%,5%)]">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-[hsl(45,96%,58%)] mb-3">
              Popular Topics
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {topTags.map(([tag, count]) => (
                <Link
                  key={tag}
                  href={`/blog?tag=${encodeURIComponent(tag)}`}
                  className="px-2 py-1 text-[10px] font-mono bg-[hsl(215,50%,10%)] border border-[hsl(215,40%,16%)] text-[hsl(210,20%,60%)] rounded hover:border-[hsl(45,96%,58%)]/40 hover:text-[hsl(45,96%,58%)] transition-colors"
                >
                  {tag} ({count})
                </Link>
              ))}
            </div>
          </div>

          {/* Quick links */}
          <div className="p-4 rounded-lg border border-[hsl(215,40%,14%)] bg-[hsl(220,55%,5%)]">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-[hsl(45,96%,58%)] mb-3">
              Quick Links
            </h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/backtesting" className="text-[hsl(210,20%,65%)] hover:text-[hsl(45,96%,58%)] transition-colors">
                  Backtesting Engine
                </Link>
              </li>
              <li>
                <Link href="/strategies" className="text-[hsl(210,20%,65%)] hover:text-[hsl(45,96%,58%)] transition-colors">
                  Strategy Library
                </Link>
              </li>
              <li>
                <Link href="/signals" className="text-[hsl(210,20%,65%)] hover:text-[hsl(45,96%,58%)] transition-colors">
                  Trading Signals
                </Link>
              </li>
              <li>
                <Link href="/politicians" className="text-[hsl(210,20%,65%)] hover:text-[hsl(45,96%,58%)] transition-colors">
                  Congressional Trades
                </Link>
              </li>
            </ul>
          </div>

          {/* Stats */}
          <div className="p-4 rounded-lg border border-[hsl(215,40%,14%)] bg-[hsl(220,55%,5%)]">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-[hsl(45,96%,58%)] mb-3">
              Library Stats
            </h3>
            <div className="space-y-2 text-sm font-mono">
              <div className="flex justify-between">
                <span className="text-[hsl(210,20%,55%)]">Articles</span>
                <span className="text-[hsl(142,71%,55%)]">{allArticles.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[hsl(210,20%,55%)]">Categories</span>
                <span className="text-[hsl(142,71%,55%)]">{categories.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[hsl(210,20%,55%)]">Topics</span>
                <span className="text-[hsl(142,71%,55%)]">{Object.keys(tagCounts).length}</span>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}
