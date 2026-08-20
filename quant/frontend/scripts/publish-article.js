#!/usr/bin/env node
/**
 * Publish an article to quantengines.com.
 *
 *   node scripts/publish-article.js '<json>'   (or a path to a .json file)
 *   json = { title, body, slug?, description?, author?, published_date?, tags? }
 *
 * Writes content/blog/<slug>.md. The blog listing (src/app/blog/page.tsx) reads
 * this dir with readdirSync + a custom frontmatter parser: `key: "value"` and
 * arrays as `key: ["a", "b"]`. No index to regenerate.
 */
const fs = require('fs');
const path = require('path');

const slugify = (s) => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 80);
const oneLine = (s) => String(s || '').replace(/[\r\n]+/g, ' ').replace(/"/g, "'").trim();

const arg = process.argv[2] || '{}';
const raw = (arg && arg.length < 500 && fs.existsSync(arg)) ? fs.readFileSync(arg, 'utf-8') : arg;
const p = JSON.parse(raw);
if (!p.title || !p.body) { console.error('FAIL: title and body are required'); process.exit(1); }

const slug = slugify(p.slug || p.title);
const title = oneLine(p.title);
const description = oneLine(p.description).slice(0, 200);
const author = oneLine(p.author || 'Quant Platform');
const date = oneLine(p.published_date || new Date().toISOString().slice(0, 10));
const tags = (Array.isArray(p.tags) && p.tags.length ? p.tags : ['quantitative trading', 'algorithmic trading'])
  .map((t) => `"${oneLine(t)}"`).join(', ');

const frontmatter = [
  '---',
  `title: "${title}"`,
  `description: "${description}"`,
  `date: "${date}"`,
  `author: "${author}"`,
  `category: "guides"`,
  `tags: [${tags}]`,
  `keywords: [${tags}]`,
  `slug: "${slug}"`,
  '---',
  '',
].join('\n');

const outDir = path.join(process.cwd(), 'content', 'blog');
fs.mkdirSync(outDir, { recursive: true });
const filePath = path.join(outDir, `${slug}.md`);
fs.writeFileSync(filePath, frontmatter + p.body.trim() + '\n');
console.log('WROTE', filePath);
console.log('PUBLISHED', slug, '(content/blog)');
