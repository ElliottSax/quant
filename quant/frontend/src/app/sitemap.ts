import { MetadataRoute } from 'next'
import fs from 'fs'
import path from 'path'

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

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://quantengines.com'
  const currentDate = new Date()

  // Static tool pages
  const toolPages = [
    '/blog',
    '/politicians',
    '/dashboard',
    '/backtesting',
    '/backtesting/builder',
    '/congressional-trades',
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
    // Blog articles
    ...blogEntries,
  ]
}
