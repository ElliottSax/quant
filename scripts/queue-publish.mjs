#!/usr/bin/env node
/**
 * Dependency-free autopublisher for GitHub Actions (per-repo, self-publishing).
 *
 * Moves the next article(s) from ./article-queue/ into the site's content dir.
 * The queue IS the dedup state: a published file is removed from the queue, so
 * the next run naturally takes the next one — no external state file needed.
 * The workflow commits + pushes the result, which triggers a Vercel deploy.
 *
 * Config: ./article-queue/.publish-config.json
 *   { "contentDir": "content/blog", "format": "flat"|"directory", "domain": "x.com" }
 */
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const QUEUE_DIR = path.join(ROOT, 'article-queue');
const CONFIG_PATH = path.join(QUEUE_DIR, '.publish-config.json');

if (!fs.existsSync(CONFIG_PATH)) {
  console.log('no article-queue/.publish-config.json — nothing to do');
  process.exit(0);
}
const CONFIG = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
const PER_RUN = Number(process.env.ARTICLES_PER_RUN || CONFIG.articlesPerRun || 1);

function normalizeSlug(s) {
  s = String(s).toLowerCase().replace(/&/g, 'and').replace(/['"]/g, '');
  s = s.replace(/[^a-z0-9\-_]+/g, '-').replace(/-+/g, '-').replace(/^[-_]+|[-_]+$/g, '');
  return s.slice(0, 80).replace(/-+$/g, '');
}

function destPath(slug) {
  const base = path.join(ROOT, CONFIG.contentDir);
  return CONFIG.format === 'directory'
    ? path.join(base, slug, 'page.mdx')
    : path.join(base, `${slug}.md`);
}

// Refresh the first `date:` line in the frontmatter to today so published
// articles don't all show a stale generation date.
function freshenDate(text) {
  const today = new Date().toISOString().slice(0, 10);
  return text.replace(/^(date:[ \t]*).*$/m, `$1${today}`);
}

function queueFiles() {
  if (!fs.existsSync(QUEUE_DIR)) return [];
  return fs.readdirSync(QUEUE_DIR).filter(f => f.endsWith('.md')).sort()
    .map(f => path.join(QUEUE_DIR, f));
}

let published = 0;
for (const qf of queueFiles()) {
  if (published >= PER_RUN) break;
  const slug = normalizeSlug(path.basename(qf, '.md'));
  if (!slug) { fs.rmSync(qf); console.log(`drop (empty slug): ${path.basename(qf)}`); continue; }
  const dest = destPath(slug);
  const text = fs.readFileSync(qf, 'utf8');
  if (!/^---\r?\n/.test(text)) { fs.rmSync(qf); console.log(`drop (no frontmatter): ${slug}`); continue; }
  if (fs.existsSync(dest)) { fs.rmSync(qf); console.log(`drop (already published): ${slug}`); continue; }
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.writeFileSync(dest, freshenDate(text));
  fs.rmSync(qf);
  published++;
  console.log(`PUBLISHED ${slug} -> ${path.relative(ROOT, dest)}`);
}
console.log(`done: ${published}/${PER_RUN} published, ${queueFiles().length} left in queue`);
