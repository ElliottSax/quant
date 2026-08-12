import { readdirSync, readFileSync } from 'fs';
import { join } from 'path';
import { readFrontmatterValue } from '@/lib/frontmatter';
import { isNoindexDraft } from '@/lib/noindex-drafts';

const SITE_URL = 'https://quantengines.com';
const SITE_NAME = 'QuantEngines';
const SITE_DESCRIPTION = 'Free professional-grade trading tools, congressional trading analytics, backtesting, and quantitative analysis guides.';

function escapeXml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

interface ArticleMeta {
  title: string;
  description: string;
  date: string;
  slug: string;
}

// Returns the raw YAML frontmatter block, or null when there is none.
function frontmatterBlock(content: string): string | null {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  return match ? match[1] : null;
}

function getAllArticles(): ArticleMeta[] {
  const blogDir = join(process.cwd(), 'content', 'blog');
  const articles: ArticleMeta[] = [];

  let entries: string[];
  try {
    entries = readdirSync(blogDir);
  } catch {
    return [];
  }

  for (const entry of entries) {
    if (!entry.endsWith('.md')) continue;

    try {
      const content = readFileSync(join(blogDir, entry), 'utf-8');
      const yaml = frontmatterBlock(content);
      if (!yaml) continue;

      // Values are sanitised (stray quote runs collapsed, YAML line folding
      // honoured) -- see src/lib/frontmatter.ts.
      const title = readFrontmatterValue(yaml, 'title');
      if (!title) continue;

      // The slug MUST come from the filename: that is what /blog/[slug]
      // resolves against and what sitemap.ts publishes. The frontmatter `slug`
      // field disagrees with the filename in 200 of 615 articles (underscored
      // or truncated variants, e.g. `01_covered_call_strategy_...`), so
      // honouring it emitted feed links that 404.
      const slug = entry.replace(/\.md$/, '');

      // Unfinished drafts are not syndicated -- see src/lib/noindex-drafts.ts.
      if (isNoindexDraft(slug, readFrontmatterValue(yaml, 'status'))) continue;

      articles.push({
        title,
        description: readFrontmatterValue(yaml, 'description'),
        // 155 articles carry `published_date` instead of `date`.
        date:
          readFrontmatterValue(yaml, 'date') ||
          readFrontmatterValue(yaml, 'published_date') ||
          '2026-01-01',
        slug,
      });
    } catch {
      // Skip files that can't be read
    }
  }

  return articles;
}

export async function GET() {
  const articles = getAllArticles()
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    .slice(0, 50);

  const items = articles.map((article) => {
    const pubDate = new Date(article.date).toUTCString();
    return `    <item>
      <title>${escapeXml(article.title)}</title>
      <link>${SITE_URL}/blog/${article.slug}</link>
      <guid isPermaLink="true">${SITE_URL}/blog/${article.slug}</guid>
      <description>${escapeXml(article.description)}</description>
      <pubDate>${pubDate}</pubDate>
    </item>`;
  });

  const rss = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>${escapeXml(SITE_NAME)}</title>
    <link>${SITE_URL}</link>
    <description>${escapeXml(SITE_DESCRIPTION)}</description>
    <language>en-us</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    <atom:link href="${SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>
${items.join('\n')}
  </channel>
</rss>`;

  return new Response(rss, {
    headers: {
      'Content-Type': 'text/xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600, s-maxage=3600',
    },
  });
}
