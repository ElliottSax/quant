# Cloudflare Workers migration

Vercel paused the `elliotts-projects-0031cc74` team (300% over the Hobby
tier's Fluid Active CPU allowance), taking quantengines.com down. This is
the alternate free-tier deploy target: Cloudflare Workers via
`@opennextjs/cloudflare`.

Deployed preview (not the live domain): **https://quant-analytics-frontend.elliottsaxton.workers.dev**

`@cloudflare/next-on-pages` — what the original migration brief named — is
upstream-deprecated: "please use the OpenNext Cloudflare adapter instead"
(https://github.com/cloudflare/next-on-pages README). OpenNext deploys to
Cloudflare **Workers**, not classic Pages, so the preview is a
`*.workers.dev` URL rather than `*.pages.dev`. Functionally equivalent for
this purpose.

## Build / deploy

```
cd quant/frontend
npm run cf:preview   # opennextjs-cloudflare build && opennextjs-cloudflare preview (local)
npm run cf:deploy     # opennextjs-cloudflare build && opennextjs-cloudflare deploy (real Worker)
```

Both run `npm run build` internally, which runs the `prebuild` hook
(`scripts/generate-blog-manifest.mjs`) first automatically.

Set production-matching env vars before building if testing locally:
```
NEXT_PUBLIC_API_URL=https://elliottsax-quant-backend.hf.space/api/v1
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-PHX6T0R1Y1
```

On a low-memory machine, `next build` can OOM (674 blog posts to
prerender-attempt + a large app). Pass `NODE_OPTIONS="--max-old-space-size=3072"`
(or higher) if it dies with "process out of memory" / "Zone Allocation failed".

## KNOWN GOTCHA: a node_modules patch does not survive `npm install`

`@opennextjs/cloudflare` 1.14.x/1.15.x (the versions that still support
Next 14 — see below) has a real upstream bug on Windows:
`patch-vercel-og-library.js`'s font-file rename step ENOENTs because the
font is never actually copied to the location it tries to rename from. This
only matters if a route uses `next/og`'s `ImageResponse` (this app's did —
see "next/og removed" below, so as of this migration it no longer matters
for a fresh install). If a future PR reintroduces `next/og` anywhere,
either patch `node_modules/@opennextjs/cloudflare/dist/cli/build/patches/ast/patch-vercel-og-library.js`
again by hand (add a `copyFileSync` fallback before the `renameSync`, using
the traced source path from the `.nft.json` file) or set this up properly
with `patch-package` so the fix survives a reinstall. It was NOT set up
that way here (time-boxed fix to unblock the deploy) — this note is the
only record of it.

The same build also hit a second, related bug when the `next/og` route was
still in place: wrangler's own esbuild step produced a doubled/duplicated
absolute path trying to resolve `resvg.wasm`/`yoga.wasm` (matches
https://github.com/opennextjs/opennextjs-cloudflare/issues/545, "Tries to
access wrong paths in a monorepo" — this repo's npm workspace root is
`quant/quant`, one level above `frontend/`, which is exactly what triggers
it). No workaround was found for this one; see "next/og removed" below.

## next/og removed from src/app/api/og/route.tsx

Because of the above, `/api/og` no longer dynamically renders a per-page
OG image via `next/og`'s `ImageResponse`. It now 302-redirects to the
existing static `public/og-image.jpg`. All 5 existing callers
(`layout.tsx`, `blog/[slug]/page.tsx`, `api-docs/page.tsx`,
`congress-alerts/page.tsx`, `congress-stock-trades/late-filers/page.tsx`)
keep working unchanged since the URL (`/api/og?title=...`) didn't change —
the `title` param is just unused now. If per-page OG images are wanted back,
the real fix is generating them at BUILD time (write PNGs to `public/` from
a prebuild script, same pattern as the blog manifest below) rather than at
request time, which sidesteps both adapter bugs entirely.

## Blog pages: the fs-at-runtime bug (this was a REAL live 404, not
## hypothetical)

`src/app/blog/page.tsx` and `src/app/blog/[slug]/page.tsx` used to read
`content/blog/*.md` via `fs` at request time. That works on Vercel
(serverless functions ship the repo's files) but Cloudflare Workers has no
runtime filesystem at all. First deploy: every `/blog/<slug>` URL 404'd
(confirmed for 3 different definitely-real slugs) while `/blog` itself
loaded (empty of any real problem-signal, since it degrades to an empty
list rather than throwing).

Root cause was actually two-layered:
1. `fs.readFileSync` doesn't work in a Worker at all.
2. Independent of (1): this app's root layout (`src/app/layout.tsx`) sets
   `export const dynamic = 'force-dynamic'` for the whole app (live-API
   pages crash prerendering against empty data). That turned out to still
   win over a child route's own `force-static` / `generateStaticParams` for
   *actual* prerendering in this Next version — confirmed directly by
   checking `.next/prerender-manifest.json` after a plain `next build`: it
   had **zero** entries for `/blog/[slug]`, `/strategies/[slug]`,
   `/congress-stock-trades/[ticker]`, etc., despite the build CLI printing
   all of them with the "●" (SSG) marker and example paths. That marker is
   cosmetically misleading here — it reflects the presence of
   `generateStaticParams`, not whether the route was actually written as
   static output. Combined with the `dynamicParams = false` this code
   briefly had, that meant every blog slug 404'd immediately (rejected by
   Next's own routing before the page function ever ran), not 500'd from a
   failed `fs` call as you'd otherwise expect.

Fix (`scripts/generate-blog-manifest.mjs`, runs as `prebuild`):
- Reads every `content/blog/*.md` at BUILD time (real fs, real disk).
- Writes `src/data/blog-manifest.generated.json` (gitignored,
  frontmatter-only, ~240KB for 582 publishable posts) — imported directly as
  a plain JS module by the blog listing, `generateStaticParams`, and the
  related-articles list. No fs, no fetch, just bundled JSON.
- Copies every post (including noindex-drafts, deliberately — see the
  script's comments) into `public/blog-content/<slug>.md` (gitignored),
  which OpenNext then ships as an ordinary static asset.
- `src/lib/blog-content.ts` (new) reads a SINGLE post's full body at
  runtime: tries the Cloudflare Worker's `ASSETS` binding
  (`getCloudflareContext().env.ASSETS.fetch(...)`) first, falls back to
  plain `fs` when not running on Cloudflare (local `next dev`/`next start`,
  or if this ever deploys somewhere else again). Local dev behavior is
  unchanged.

The manifest generator re-implements (rather than imports)
`src/lib/frontmatter.ts`'s sanitizer and `src/lib/noindex-drafts.ts`'s
filter, because it runs as plain Node before the TS/webpack pipeline exists.
If either of those files changes, check whether the reimplementation in
`scripts/generate-blog-manifest.mjs` needs the same change — they are
NOT automatically kept in sync.

## @opennextjs/cloudflare version pin

Pinned to **1.15.1** (`devDependencies`). This is the last version whose
peer range covers Next 14.2.35 — 1.16.0+ requires Next 15/16, and this app
is on Next 14. If/when this app upgrades to Next 15+, revisit the pin (and
re-check whether the `next/og` bugs above are fixed upstream by then, in
case per-page OG images are worth restoring).

## Env vars

Pulled from Vercel production via `vercel env pull` (from `C:\projects\quant`,
the `.vercel/project.json`-linked directory) before doing anything else.
Real production only had 5 app-level vars set:

- `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_GA_MEASUREMENT_ID`, `EMAIL_FROM` —
  non-secret, copied into `wrangler.jsonc`'s `vars` (committed).
- `FMP_API_KEY`, `RESEND_API_KEY` — pushed as Worker secrets via
  `wrangler secret put` (NOT committed; re-run that command if the Worker
  is ever recreated from scratch).

`STRIPE_SECRET_KEY`, `STRIPE_CONGRESS_ALERTS_*`, `SUPABASE_URL`,
`SUPABASE_SERVICE_ROLE_KEY` were **not** set in Vercel production either —
the congress-alerts Stripe/Supabase routes already 503 gracefully without
them (see `src/lib/congress-alerts-billing.ts` / `src/lib/supabase-admin.ts`).
Nothing to carry over there; set them the same way (`wrangler secret put`)
if/when that product actually launches.

GA tracking (`NEXT_PUBLIC_GA_MEASUREMENT_ID=G-PHX6T0R1Y1`) already reads
from an env var in `src/app/layout.tsx`, not hardcoded — that was fixed in
an earlier session (2026-09-05, see this repo's `CLAUDE.md`). Nothing to do
here beyond making sure the Worker has the same value, which it does.

## Known pre-existing bug NOT fixed here (out of scope, needs Elliott)

`/settings/referral` calls `/api/v1/subscription/referral/code` on the
external backend (`elliottsax-quant-backend.hf.space`) — 404s, confirmed by
curling the backend directly (both singular and plural paths 404 for this
specific endpoint). Same root cause class as `/settings/subscription`,
which Elliott already fixed directly (commit `a3d6290`) by replacing that
page's dead UI with a static "free forever" message — referral wasn't
touched in that fix and still calls the dead route. This sits inside the
paused free-forever-vs-paid pricing decision (see the root `CLAUDE.md`),
which needs Elliott's sign-off, not a drive-by fix during a hosting
migration. It reproduces identically on Vercel or Cloudflare either way,
since it's a backend contract issue, not a hosting issue.

## Cutting quantengines.com over (NOT done — Elliott's call)

`quantengines.com`'s nameservers are currently at Porkbun (own DNS, A
record `76.76.21.21` = Vercel), not Cloudflare. Cloudflare Workers Custom
Domains need the zone on Cloudflare's own nameservers (it's not a simple
CNAME add). Steps, once Elliott approves:

1. In the Cloudflare dashboard (account: `elliottsaxton@gmail.com`, account
   ID `964567d3181cc1f711808f9a8c384d44`), add `quantengines.com` as a new
   site/zone.
2. At Porkbun, change `quantengines.com`'s nameservers from
   `maceio/salvador/curitiba/fortaleza.ns.porkbun.com` to the pair
   Cloudflare assigns when the zone is created.
3. Once the zone is active (DNS propagation, can take a few hours), go to
   Workers & Pages → `quant-analytics-frontend` → Settings → Domains &
   Routes → Add Custom Domain → `quantengines.com`. Cloudflare creates the
   proxied DNS record automatically.
4. Re-verify the same pages/checks this migration ran, against the real
   domain this time.
5. Only after that's confirmed working: decide whether to also cancel/
   downgrade the paused Vercel project, or leave it paused as a rollback
   option.
