import { Metadata } from 'next'
import Link from 'next/link'
import fs from 'fs'
import path from 'path'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const CONTENT_DIR = path.join(process.cwd(), 'content', 'blog')

interface Frontmatter {
  title: string
  description: string
  date: string
  author: string
  category: string
  tags: string[]
  keywords: string[]
}

interface Article {
  slug: string
  frontmatter: Frontmatter
  body: string
}

function parseFrontmatter(raw: string): { frontmatter: Frontmatter; body: string } {
  const match = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/)
  if (!match) {
    return {
      frontmatter: { title: '', description: '', date: '', author: '', category: '', tags: [], keywords: [] },
      body: raw,
    }
  }

  const yamlBlock = match[1]
  const body = match[2]

  const get = (key: string): string => {
    const m = yamlBlock.match(new RegExp(`^${key}:\\s*"?(.*?)"?\\s*$`, 'm'))
    return m ? m[1].replace(/^"|"$/g, '') : ''
  }

  const getArray = (key: string): string[] => {
    const m = yamlBlock.match(new RegExp(`^${key}:\\s*\\[([^\\]]*)]`, 'm'))
    if (!m) return []
    return m[1]
      .split(',')
      .map((s) => s.trim().replace(/^"|"$/g, ''))
      .filter(Boolean)
  }

  return {
    frontmatter: {
      title: get('title'),
      description: get('description'),
      date: get('date'),
      author: get('author'),
      category: get('category'),
      tags: getArray('tags'),
      keywords: getArray('keywords'),
    },
    body,
  }
}

function getAllArticles(): Article[] {
  if (!fs.existsSync(CONTENT_DIR)) return []
  return fs
    .readdirSync(CONTENT_DIR)
    .filter((f) => f.endsWith('.md'))
    .map((f) => {
      const slug = f.replace(/\.md$/, '')
      const raw = fs.readFileSync(path.join(CONTENT_DIR, f), 'utf-8')
      const { frontmatter, body } = parseFrontmatter(raw)
      return { slug, frontmatter, body }
    })
    .filter((a) => a.frontmatter.title)
    .sort((a, b) => (b.frontmatter.date > a.frontmatter.date ? 1 : -1))
}

function getArticle(slug: string): Article | null {
  const filePath = path.join(CONTENT_DIR, `${slug}.md`)
  if (!fs.existsSync(filePath)) return null
  const raw = fs.readFileSync(filePath, 'utf-8')
  const { frontmatter, body } = parseFrontmatter(raw)
  if (!frontmatter.title) return null
  return { slug, frontmatter, body }
}

// ---------------------------------------------------------------------------
// Markdown -> HTML converter (no external deps)
// ---------------------------------------------------------------------------

function markdownToHtml(md: string): string {
  let html = md

  // Code blocks (fenced) -- must come before inline code
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_match, lang, code) => {
    const escaped = code
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
    const langAttr = lang ? ` data-lang="${lang}"` : ''
    return `<div class="code-block"><div class="code-header"><span class="code-lang">${lang || 'text'}</span></div><pre${langAttr}><code>${escaped}</code></pre></div>`
  })

  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')

  // Tables
  html = html.replace(
    /(?:^|\n)((?:\|.*\|(?:\r?\n|$))+)/g,
    (_match, tableBlock: string) => {
      const rows = tableBlock.trim().split('\n').filter((r) => r.trim())
      if (rows.length < 2) return tableBlock
      // Check if row 2 is a separator
      const isSep = /^\|[\s:-]+\|$/.test(rows[1].trim().replace(/\s+/g, ''))
      if (!isSep) return tableBlock

      const parseRow = (row: string) =>
        row
          .split('|')
          .slice(1, -1)
          .map((c) => c.trim())

      const headerCells = parseRow(rows[0])
      const bodyRows = rows.slice(2)
      let t = '<div class="table-wrap"><table><thead><tr>'
      headerCells.forEach((c) => (t += `<th>${c}</th>`))
      t += '</tr></thead><tbody>'
      bodyRows.forEach((r) => {
        const cells = parseRow(r)
        t += '<tr>'
        cells.forEach((c) => (t += `<td>${c}</td>`))
        t += '</tr>'
      })
      t += '</tbody></table></div>'
      return '\n' + t + '\n'
    },
  )

  // Headers (process line-by-line to avoid mid-word matches)
  html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>')
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>')
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>')
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>')

  // Bold & italic
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')

  // Images
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" class="article-img" loading="lazy" />')

  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="article-link">$1</a>')

  // Horizontal rule
  html = html.replace(/^---$/gm, '<hr />')

  // Unordered lists
  html = html.replace(/((?:^[\t ]*[-*] .+\n?)+)/gm, (block) => {
    const items = block
      .split('\n')
      .filter((l) => l.trim())
      .map((l) => `<li>${l.replace(/^[\t ]*[-*] /, '')}</li>`)
      .join('')
    return `<ul>${items}</ul>`
  })

  // Ordered lists
  html = html.replace(/((?:^\d+\. .+\n?)+)/gm, (block) => {
    const items = block
      .split('\n')
      .filter((l) => l.trim())
      .map((l) => `<li>${l.replace(/^\d+\. /, '')}</li>`)
      .join('')
    return `<ol>${items}</ol>`
  })

  // Blockquotes
  html = html.replace(/((?:^> .+\n?)+)/gm, (block) => {
    const inner = block.replace(/^> /gm, '')
    return `<blockquote>${inner}</blockquote>`
  })

  // Paragraphs -- wrap remaining standalone lines
  html = html
    .split('\n\n')
    .map((block) => {
      const trimmed = block.trim()
      if (!trimmed) return ''
      if (/^<[a-z]/.test(trimmed)) return trimmed
      return `<p>${trimmed.replace(/\n/g, '<br />')}</p>`
    })
    .join('\n')

  return html
}

// ---------------------------------------------------------------------------
// Reading time estimate
// ---------------------------------------------------------------------------

function readingTime(text: string): number {
  const words = text.split(/\s+/).length
  return Math.max(1, Math.round(words / 225))
}

// ---------------------------------------------------------------------------
// Static params
// ---------------------------------------------------------------------------

export async function generateStaticParams() {
  const articles = getAllArticles()
  return articles.map((a) => ({ slug: a.slug }))
}

// ---------------------------------------------------------------------------
// Metadata
// ---------------------------------------------------------------------------

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>
}): Promise<Metadata> {
  const { slug } = await params
  const article = getArticle(slug)
  if (!article) {
    return { title: 'Article Not Found | QuantEngines' }
  }

  const { frontmatter } = article

  return {
    title: `${frontmatter.title} | QuantEngines`,
    description: frontmatter.description,
    keywords: [...frontmatter.keywords, ...frontmatter.tags],
    authors: [{ name: frontmatter.author }],
    openGraph: {
      title: frontmatter.title,
      description: frontmatter.description,
      type: 'article',
      publishedTime: frontmatter.date,
      authors: [frontmatter.author],
      tags: frontmatter.tags,
      url: `https://quantengines.com/blog/${slug}`,
      images: [
        {
          url: `https://quantengines.com/api/og?title=${encodeURIComponent(frontmatter.title)}`,
          width: 1200,
          height: 630,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: frontmatter.title,
      description: frontmatter.description,
    },
    alternates: {
      canonical: `/blog/${slug}`,
    },
  }
}

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

export default async function BlogArticlePage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const article = getArticle(slug)

  if (!article) {
    return (
      <div className="max-w-3xl mx-auto py-20 text-center">
        <h1 className="text-2xl font-bold text-white mb-4">Article Not Found</h1>
        <p className="text-[hsl(210,20%,55%)] mb-6">
          The article you are looking for does not exist or has been moved.
        </p>
        <Link
          href="/blog"
          className="inline-block px-4 py-2 bg-[hsl(45,96%,58%)]/10 border border-[hsl(45,96%,58%)]/30 text-[hsl(45,96%,58%)] rounded hover:bg-[hsl(45,96%,58%)]/20 transition-colors text-sm font-medium"
        >
          Back to Blog
        </Link>
      </div>
    )
  }

  const { frontmatter, body } = article
  const minutes = readingTime(body)
  const htmlContent = markdownToHtml(body)
  const allArticles = getAllArticles()

  // Related articles: same category first, then same tags
  const related = allArticles
    .filter((a) => a.slug !== slug)
    .map((a) => {
      let score = 0
      if (a.frontmatter.category === frontmatter.category) score += 3
      a.frontmatter.tags.forEach((t) => {
        if (frontmatter.tags.includes(t)) score += 1
      })
      return { ...a, score }
    })
    .filter((a) => a.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 4)

  const formattedDate = new Date(frontmatter.date + 'T00:00:00').toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })

  return (
    <>
      {/* JSON-LD structured data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'Article',
            headline: frontmatter.title,
            description: frontmatter.description,
            datePublished: frontmatter.date,
            author: { '@type': 'Person', name: frontmatter.author },
            publisher: { '@type': 'Organization', name: 'QuantEngines' },
            url: `https://quantengines.com/blog/${slug}`,
            keywords: frontmatter.tags.join(', '),
          }),
        }}
      />

      <div className="max-w-4xl mx-auto">
        {/* Breadcrumbs */}
        <nav className="flex items-center gap-2 text-xs font-mono text-[hsl(210,20%,50%)] mb-6">
          <Link href="/" className="hover:text-[hsl(45,96%,58%)] transition-colors">
            Home
          </Link>
          <span className="text-[hsl(215,40%,25%)]">/</span>
          <Link href="/blog" className="hover:text-[hsl(45,96%,58%)] transition-colors">
            Blog
          </Link>
          <span className="text-[hsl(215,40%,25%)]">/</span>
          <span className="text-[hsl(210,20%,65%)] truncate max-w-[300px]">{frontmatter.title}</span>
        </nav>

        {/* Article Header */}
        <header className="mb-8 pb-6 border-b border-[hsl(215,40%,14%)]">
          {/* Category badge */}
          <div className="mb-3">
            <Link
              href={`/blog?category=${encodeURIComponent(frontmatter.category)}`}
              className="inline-block px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider bg-[hsl(210,100%,56%)]/10 border border-[hsl(210,100%,56%)]/30 text-[hsl(210,100%,70%)] rounded hover:bg-[hsl(210,100%,56%)]/20 transition-colors"
            >
              {frontmatter.category}
            </Link>
          </div>

          <h1 className="text-3xl md:text-4xl font-bold text-white leading-tight mb-4">
            {frontmatter.title}
          </h1>

          <p className="text-[hsl(210,20%,60%)] text-lg leading-relaxed mb-5">
            {frontmatter.description}
          </p>

          {/* Author & meta row */}
          <div className="flex flex-wrap items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[hsl(45,96%,58%)] to-[hsl(38,92%,45%)] flex items-center justify-center text-[hsl(220,60%,8%)] font-bold text-xs">
                {frontmatter.author
                  .split(' ')
                  .map((w) => w[0])
                  .join('')
                  .slice(0, 2)}
              </div>
              <div>
                <p className="text-white font-medium text-sm leading-tight">{frontmatter.author}</p>
                <p className="text-[hsl(210,20%,50%)] text-xs">{formattedDate}</p>
              </div>
            </div>
            <span className="text-[hsl(215,40%,25%)]">|</span>
            <span className="text-[hsl(210,20%,55%)] text-xs font-mono">{minutes} min read</span>
          </div>
        </header>

        {/* Article Body */}
        <article
          className="article-content prose-terminal mb-12"
          dangerouslySetInnerHTML={{ __html: htmlContent }}
        />

        {/* Tags */}
        {frontmatter.tags.length > 0 && (
          <div className="mb-10 pb-8 border-b border-[hsl(215,40%,14%)]">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-[hsl(210,20%,50%)] mb-3">
              Tags
            </h3>
            <div className="flex flex-wrap gap-2">
              {frontmatter.tags.map((tag) => (
                <Link
                  key={tag}
                  href={`/blog?tag=${encodeURIComponent(tag)}`}
                  className="px-2.5 py-1 text-xs font-mono bg-[hsl(215,50%,12%)] border border-[hsl(215,40%,18%)] text-[hsl(210,20%,65%)] rounded hover:border-[hsl(45,96%,58%)]/40 hover:text-[hsl(45,96%,58%)] transition-colors"
                >
                  {tag}
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Related Articles */}
        {related.length > 0 && (
          <section className="mb-12">
            <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <span className="w-1 h-5 bg-[hsl(45,96%,58%)] rounded-full" />
              Related Articles
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {related.map((r) => (
                <Link
                  key={r.slug}
                  href={`/blog/${r.slug}`}
                  className="group block p-4 rounded border border-[hsl(215,40%,14%)] bg-[hsl(220,55%,5%)] hover:border-[hsl(45,96%,58%)]/30 hover:bg-[hsl(215,50%,8%)] transition-all"
                >
                  <span className="text-[10px] font-semibold uppercase tracking-wider text-[hsl(210,100%,56%)] mb-1 block">
                    {r.frontmatter.category}
                  </span>
                  <span className="text-sm font-semibold text-white group-hover:text-[hsl(45,96%,58%)] transition-colors line-clamp-2 block">
                    {r.frontmatter.title}
                  </span>
                  <span className="text-xs text-[hsl(210,20%,50%)] mt-1 block">
                    {r.frontmatter.author} &middot; {r.frontmatter.date}
                  </span>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* Back link */}
        <div className="text-center pb-8">
          <Link
            href="/blog"
            className="inline-block px-5 py-2.5 bg-[hsl(45,96%,58%)]/10 border border-[hsl(45,96%,58%)]/30 text-[hsl(45,96%,58%)] rounded hover:bg-[hsl(45,96%,58%)]/20 transition-colors text-sm font-medium"
          >
            Browse All Articles
          </Link>
        </div>
      </div>

      {/* Scoped styles for article content */}
      <style
        dangerouslySetInnerHTML={{
          __html: `
          .article-content h1 {
            font-size: 1.75rem;
            font-weight: 700;
            color: white;
            margin: 2rem 0 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid hsl(215,40%,14%);
          }
          .article-content h2 {
            font-size: 1.4rem;
            font-weight: 700;
            color: white;
            margin: 1.75rem 0 0.75rem;
          }
          .article-content h3 {
            font-size: 1.15rem;
            font-weight: 600;
            color: hsl(210,20%,85%);
            margin: 1.5rem 0 0.5rem;
          }
          .article-content h4 {
            font-size: 1rem;
            font-weight: 600;
            color: hsl(210,20%,80%);
            margin: 1.25rem 0 0.5rem;
          }
          .article-content p {
            color: hsl(210,20%,70%);
            line-height: 1.75;
            margin: 0.75rem 0;
          }
          .article-content strong {
            color: hsl(210,20%,90%);
            font-weight: 600;
          }
          .article-content em {
            color: hsl(210,20%,75%);
            font-style: italic;
          }
          .article-content ul, .article-content ol {
            margin: 0.75rem 0;
            padding-left: 1.5rem;
            color: hsl(210,20%,70%);
          }
          .article-content li {
            margin: 0.35rem 0;
            line-height: 1.7;
          }
          .article-content ul li {
            list-style-type: disc;
          }
          .article-content ol li {
            list-style-type: decimal;
          }
          .article-content blockquote {
            border-left: 3px solid hsl(45,96%,58%);
            padding: 0.75rem 1rem;
            margin: 1rem 0;
            background: hsl(220,55%,5%);
            border-radius: 0 4px 4px 0;
            color: hsl(210,20%,75%);
          }
          .article-content hr {
            border: none;
            border-top: 1px solid hsl(215,40%,14%);
            margin: 2rem 0;
          }
          .article-content .article-link {
            color: hsl(210,100%,70%);
            text-decoration: underline;
            text-underline-offset: 2px;
            transition: color 0.15s;
          }
          .article-content .article-link:hover {
            color: hsl(45,96%,58%);
          }
          .article-content .inline-code {
            background: hsl(215,50%,12%);
            border: 1px solid hsl(215,40%,18%);
            padding: 0.15rem 0.4rem;
            border-radius: 3px;
            font-family: var(--font-mono), monospace;
            font-size: 0.85em;
            color: hsl(45,96%,70%);
          }
          .article-content .code-block {
            margin: 1rem 0;
            border: 1px solid hsl(215,40%,18%);
            border-radius: 6px;
            overflow: hidden;
            background: hsl(220,60%,4%);
          }
          .article-content .code-header {
            background: hsl(215,50%,10%);
            padding: 0.4rem 0.75rem;
            border-bottom: 1px solid hsl(215,40%,18%);
          }
          .article-content .code-lang {
            font-size: 0.7rem;
            font-family: var(--font-mono), monospace;
            color: hsl(210,20%,55%);
            text-transform: uppercase;
            letter-spacing: 0.05em;
          }
          .article-content pre {
            padding: 1rem;
            overflow-x: auto;
            font-family: var(--font-mono), monospace;
            font-size: 0.85rem;
            line-height: 1.6;
            color: hsl(210,20%,75%);
          }
          .article-content .article-img {
            max-width: 100%;
            height: auto;
            border-radius: 6px;
            border: 1px solid hsl(215,40%,18%);
            margin: 1rem 0;
          }
          .article-content .table-wrap {
            overflow-x: auto;
            margin: 1rem 0;
            border: 1px solid hsl(215,40%,18%);
            border-radius: 6px;
          }
          .article-content table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
          }
          .article-content thead {
            background: hsl(215,50%,10%);
          }
          .article-content th {
            padding: 0.6rem 0.75rem;
            text-align: left;
            font-weight: 600;
            color: hsl(210,20%,85%);
            border-bottom: 1px solid hsl(215,40%,18%);
            white-space: nowrap;
          }
          .article-content td {
            padding: 0.5rem 0.75rem;
            color: hsl(210,20%,70%);
            border-bottom: 1px solid hsl(215,40%,10%);
          }
          .article-content tbody tr:hover {
            background: hsl(215,50%,8%);
          }
          `,
        }}
      />
    </>
  )
}
