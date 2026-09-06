# Dormant: orphaned content directory

Renamed from `content/articles/` on 2026-09-06 during a dead-code/bloat audit.

## Why this is dormant, not deleted
This directory sits next to the live `content/blog/` (705 files) that
`quant/frontend/src/app/blog/page.tsx` and `[slug]/page.tsx` actually read
(`CONTENT_DIR = path.join(process.cwd(), 'content', 'blog')`). Nothing in
`quant/frontend/src` references `content/articles` — grepped for the literal
path with zero hits. No script, workflow, or build step reads this directory
either.

One file (`arbitrage-opportunities.md`) duplicates a filename already
published in `content/blog`. The other 7 do not overlap by name, and at
least one (`algorithmic-execution-system-v2.md`) reads as real, non-templated
strategy content rather than generator filler — unlike the confirmed-junk
directories removed in the same pass (`generated-articles/`, `posts/`,
`marketing/`, root `app/blog/`), so this was renamed and flagged instead of
deleted outright.

## Decision still needed
- **Finish and launch**: review these 8 articles for accuracy/quality: if
  they clear the same bar as published posts, move them into
  `content/blog/` (checking each slug doesn't collide) and drop this
  directory.
- **Delete**: if a read confirms they're not worth publishing, `git rm -r`
  this directory.

Not deleted or merged automatically — do that only with Elliott's sign-off,
same as the other dormant clusters flagged this session.
