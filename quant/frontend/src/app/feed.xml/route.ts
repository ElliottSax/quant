import { readdirSync, readFileSync } from 'fs';
import { join } from 'path';

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

function parseFrontmatter(content: string): Record<string, string> {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---/);
  if (!match) return {};
  const frontmatter: Record<string, string> = {};
  const lines = match[1].split('\n');
  for (const line of lines) {
    const m = line.match(/^(\w[\w_]*)\s*:\s*["']?(.*?)["']?\s*$/);
    if (m) {
      frontmatter[m[1]] = m[2];
    }
  }
  return frontmatter;
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
      const fm = parseFrontmatter(content);
      if (fm.title) {
        const slug = fm.slug || entry.replace(/\.md$/, '');
        articles.push({
          title: fm.title,
          description: fm.description || '',
          date: fm.date || '2026-01-01',
          slug,
        });
      }
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
