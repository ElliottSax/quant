# Cloudflare migration: what actually happened

**Date:** 2026-09-13
**Scope:** read-only investigation. Nothing was fixed, changed, deployed, or reverted.
**Question:** git log claims a migration to Cloudflare Workers, but production traffic for
quantengines.com is demonstrably served by Vercel. Reverted? Abandoned mid-way? Or is
Cloudflare doing something else (DNS/CDN in front of Vercel)?

---

## TL;DR

**None of the three hypotheses. The migration was *completed and verified*, then deliberately
never promoted to production.** It was built as a parallel deploy target during a Vercel outage,
and the final DNS-cutover step was explicitly gated on Elliott's approval — an approval that
never came. The Cloudflare Worker is real and still live today, but frozen at its 2026-09-09
build. Meanwhile the outage that motivated the migration resolved itself, so Vercel resumed
serving production and has kept deploying since.

Cloudflare is **not** proxying, CDN-ing, or fronting quantengines.com in any way. DNS is at
Porkbun; the A record points straight at Vercel; responses carry `Server: Vercel` and no
`CF-RAY`.

The one genuinely surprising finding is a **side effect**: the migration's compatibility fixes
live in *shared application code*, so they shipped to Vercel production through normal deploys
even though the migration never went live. Most visibly, **every page on quantengines.com lost
its per-page dynamic OG share image** and now serves one static fallback — a downgrade Vercel
never needed and only inherited from a Cloudflare workaround. See §5.

---

## 1. The migration commit

### `ac2aa9c` — "quant frontend: migrate to Cloudflare Workers (Vercel Hobby paused for CPU overage)"

- **Author:** Elliott <elliottsaxton@gmail.com>, `Co-Authored-By: Claude Sonnet 5`
- **Date:** Wed Sep 9 14:34:31 2026 -0500
- **Size:** 11 files, +14,004 / −7,341 (dominated by `quant/package-lock.json`, 20,751 lines)

**Motivation (from the commit body):** Vercel paused the `elliotts-projects-0031cc74` team for
exceeding the free Hobby tier's Fluid Active CPU allowance by 300%, taking quantengines.com down.

**The load-bearing sentence — the commit itself already discloses the answer:**

> DNS/production cutover NOT touched -- quantengines.com still points at Vercel.

So this was never presented as a production cutover. It added a *deployment path* and proved it
worked, then stopped short of the DNS change.

**Approach:** Cloudflare Workers via `@opennextjs/cloudflare` (OpenNext), *not*
`@cloudflare/next-on-pages` — the latter is what the original brief named, but it is
upstream-deprecated in favour of OpenNext. Consequence: the result is a Worker with a
`*.workers.dev` URL, not a classic Pages project with `*.pages.dev`.

**Deployed and verified at:** `https://quant-analytics-frontend.elliottsaxton.workers.dev`

**Compatibility fixes it had to make (all in shared app code):**

| Change | Why |
|---|---|
| `src/app/api/og/route.tsx` — dropped `next/og`'s `ImageResponse`, now 302-redirects to static `public/og-image.jpg` | The adapter couldn't locate the bundled font/`resvg.wasm`/`yoga.wasm` assets in this Windows + npm-workspaces monorepo layout (upstream bug class: `opennextjs/opennextjs-cloudflare#545`). All 5 callers keep working — the URL is unchanged, the `title` param is just ignored now. |
| `scripts/generate-blog-manifest.mjs` (new `prebuild` step) + `src/lib/blog-content.ts` (new) | Blog pages read `content/blog/*.md` via `fs` **at request time**. That works on Vercel (serverless functions ship repo files) but Workers have no runtime filesystem — this produced a **live 404 on every `/blog/<slug>`** on the first Cloudflare deploy. Fix: build-time frontmatter manifest imported as JS, raw markdown copied into `public/blog-content/` and read at runtime through the Worker's `ASSETS` binding, with an `fs` fallback off-Cloudflare. |
| *(documented, not changed)* root `layout.tsx`'s `dynamic = 'force-dynamic'` | Confirmed via `.next/prerender-manifest.json` that it still overrides a child route's own `force-static`/`generateStaticParams` for *actual* prerendering in Next 14.2.35 — the build CLI's "●" (SSG) marker is cosmetically misleading. Left alone (legitimate reason it's there); the blog fix sidesteps it instead. |

**Env vars carried over** (pulled via `vercel env pull`; real production had only 5 app-level vars):
- non-secret → `wrangler.jsonc` `vars`: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_GA_MEASUREMENT_ID`, `EMAIL_FROM`
- secrets → `wrangler secret put` (not committed): `FMP_API_KEY`, `RESEND_API_KEY`
- `STRIPE_*` / `SUPABASE_*` were not set in Vercel production either; those features already 503
  gracefully without them, so nothing to carry over.

### `455829b` — "quant frontend: document the Cloudflare migration"

Two minutes later (Sep 9 14:36:04). Adds `quant/frontend/CLOUDFLARE_MIGRATION.md` (194 lines),
which was referenced by code comments in `ac2aa9c` but didn't exist yet. Its final section is
titled **"Cutting quantengines.com over (NOT done — Elliott's call)"** and lists the 5 DNS steps
that were never executed.

---

## 2. Is the Workers config still present? Live or abandoned?

**Present, coherent, and deployable — but dormant.** Not a stub, not half-finished, and not
rolled back.

`quant/frontend/wrangler.jsonc` (31 lines, committed in `ac2aa9c`):

```jsonc
"name": "quant-analytics-frontend",
"main": ".open-next/worker.js",
"compatibility_date": "2024-12-30",
"compatibility_flags": ["nodejs_compat", "global_fetch_strictly_public"],
"assets": { "directory": ".open-next/assets", "binding": "ASSETS" },
"observability": { "enabled": true },
"vars": {
  "NEXT_PUBLIC_API_URL": "https://elliottsax-quant-backend.hf.space/api/v1",
  "NEXT_PUBLIC_GA_MEASUREMENT_ID": "G-PHX6T0R1Y1",
  "EMAIL_FROM": "QuantEngines <hello@quantengines.com>"
}
```

Supporting artifacts all still at HEAD: `open-next.config.ts`, `scripts/generate-blog-manifest.mjs`,
`src/lib/blog-content.ts`, and `package.json` scripts `cf:preview` / `cf:deploy`.

**But it is wired into nothing.** Grepping all 12 workflows in `.github/workflows/` for
`vercel|cloudflare|wrangler`: every deploy-related hit is **Vercel**.

- `deploy.yml` ("Deploy to Railway and Vercel") → `npm install -g vercel && vercel --prod --yes --token $VERCEL_TOKEN`
- `frontend-ci.yml` → `amondnet/vercel-action@v25` for preview deploys
- `autopublish-quant.yml`, `daily-sitemap-update.yml` → commit-and-let-Vercel-auto-deploy
- **Zero** Cloudflare references anywhere in CI.

So `npm run cf:deploy` is a manual, from-a-dev-machine action with no automation behind it —
which is exactly why the Worker has silently gone stale (§4).

### Minor doc/code drift found while checking this

`CLOUDFLARE_MIGRATION.md` states the adapter is *"Pinned to **1.15.1** (`devDependencies`)"*.
Reality:

- `package.json` devDependencies: `"@opennextjs/cloudflare": "^1.14.10"`
- `quant/package-lock.json` resolves `frontend/node_modules/@opennextjs/cloudflare` → **`1.14.10`**
  (`https://registry.npmjs.org/@opennextjs/cloudflare/-/cloudflare-1.14.10.tgz`)

The documented pin does not match the lockfile. The *rationale* in the doc is still sound
(1.16+ requires Next 15/16; this app is on Next 14), but `^1.14.10` is a floating caret range,
not a pin — a fresh `npm install` could resolve higher than the version actually tested. Not
fixed here (read-only), just flagged.

---

## 3. `wrangler whoami` / `wrangler deployments list` — could not run

Neither command was executed, because the CLI is neither installed nor authenticated. Per
instruction, I did **not** install it or attempt to log in.

- No global `wrangler` on `PATH` (`which wrangler` → not found; `wrangler: command not found`)
- `npx --no-install wrangler` refused: *"canceled due to missing packages and no YES option:
  `["wrangler@4.131.1"]`"*
- No `node_modules` in the repo at all — both `node_modules/wrangler` and
  `quant/frontend/node_modules/wrangler` are absent, i.e. dependencies aren't installed
- No Cloudflare credentials: `~/.wrangler`, `%APPDATA%/.wrangler`, `%LOCALAPPDATA%/.wrangler`
  all absent; zero `CLOUDFLARE*` env vars

**I substituted direct HTTP probing of the deployed Worker**, which answers the underlying
question ("does the Cloudflare deployment exist and is it live?") without needing auth — see §4.

For a dashboard check, `CLOUDFLARE_MIGRATION.md` records the account: `elliottsaxton@gmail.com`,
account ID `964567d3181cc1f711808f9a8c384d44`, Worker `quant-analytics-frontend`.

---

## 4. Conclusion and evidence

**Verdict: the migration was completed and verified as a parallel deploy path, then intentionally
left un-promoted. Not reverted. Not abandoned mid-way. Cloudflare is not fronting Vercel.**

### Nothing was reverted

- `git log --grep='revert' -i` across all history → **no results**
- `git log ac2aa9c..HEAD -- wrangler.jsonc open-next.config.ts generate-blog-manifest.mjs blog-content.ts`
  → **empty**; none of the four Cloudflare artifacts has been touched since it landed
- `git log -- quant/frontend/wrangler.jsonc` → exactly **one** commit in its entire history (`ac2aa9c`)
- All Cloudflare files, scripts, and devDependencies still present at HEAD

### Cloudflare is not in front of the domain

```
quantengines.com       → A 76.76.21.21              (Vercel's documented A record)
www.quantengines.com   → CNAME cname.vercel-dns.com  (→ 76.76.21.61, 66.33.60.130)
NS quantengines.com    → curitiba / fortaleza / maceio / salvador .ns.porkbun.com
```

Nameservers are **Porkbun**, not Cloudflare — matching the doc's note that a Workers Custom
Domain requires moving the whole zone onto Cloudflare's nameservers, so this was never "a simple
CNAME edit."

`curl -I https://quantengines.com/` → `200 OK` with:

```
Server: Vercel
X-Vercel-Id: cle1::iad1::cf2r2-1789320068289-af3138d73f0b
X-Vercel-Cache: MISS
X-Matched-Path: /
```

**No `CF-RAY`, no `Server: cloudflare`.** Hypothesis (4c) — Cloudflare as DNS/CDN in front of
Vercel — is ruled out.

> **Red herring worth flagging.** The Porkbun *nameservers* themselves resolve into Cloudflare IP
> ranges (`173.245.58.37`, `162.159.8.140`, `2400:cb00:2049:1::…`) because Porkbun runs its DNS
> infrastructure on Cloudflare. A traceroute- or whois-based check would surface "Cloudflare" here
> and could easily be misread as the app being on Cloudflare. It isn't — that's the registrar's
> DNS plumbing, not the origin.

### The Worker is live but stale — and here's the proof

`https://quant-analytics-frontend.elliottsaxton.workers.dev/` → `200 OK` with `Server: cloudflare`,
`x-opennext: 1`, `CF-RAY: a3a8d39cfdc18f48-ORD`. Same app, same `<title>`, same CSP, and the same
GA ID (`G-PHX6T0R1Y1` present on both hosts). It exists and it works.

**The decisive test.** `/support` was added in `066fd8b` (2026-09-09**T21:26**), roughly seven
hours *after* the Cloudflare deploy commit `ac2aa9c` (2026-09-09**T14:34**). `git ls-tree ac2aa9c`
confirms `src/app/support/page.tsx` did not exist in the tree that was deployed to the Worker; it
does exist at HEAD.

| Route | quantengines.com (Vercel) | workers.dev (Cloudflare) |
|---|---|---|
| `/` | 200 | 200 |
| `/support` | **200** (63,504 bytes) | **404** |
| `/api/og?title=probe` | 302 → `/og-image.jpg` | 302 → `/og-image.jpg` |
| `/settings/referral` | 200 | 200 |

⇒ Vercel has deployed `066fd8b` or later. The Worker has **not been redeployed since
2026-09-09 ~14:34**, four days ago. It is a frozen snapshot, kept warm on `workers.dev`.

*(Careful reading of that table: `/settings/referral` returning 200 on **both** is expected and is
not a counter-signal. That route existed before Sep 9; `7c6f37f` only changed its content, and the
original bug was a failing **backend fetch** to `/api/v1/subscription/referral/code`, not a missing
page. `/support` is the reliable discriminator precisely because it is a wholly new route.)*

### Vercel is unpaused and healthy again

The premise of the migration no longer holds: the team was paused and the site was down on Sep 9,
but quantengines.com serves a real `200` from Vercel today with full Next.js headers and the
production CSP. Whatever paused it was resolved, and normal deploy flow (`deploy.yml`,
git-push-triggers-Vercel) resumed. That removes the urgency that motivated the Cloudflare path and
is the most likely reason the cutover was never prioritised.

### One unverified detail

The root `.vercel/project.json` (uncommitted, gitignored) links this directory to Vercel project
`quant-analytics-frontend`, org `team_0G0YO0SMviyf6mdqW6xGkFm3`. The commit message names the
paused team as `elliotts-projects-0031cc74`. I could not confirm whether that slug and that org ID
are the same team without Vercel API access — flagging rather than assuming. Note the Cloudflare
Worker and the Vercel project share the identical name `quant-analytics-frontend`, which is a
mild additional source of confusion when reading logs or dashboards.

---

## 5. Side effect worth Elliott's attention: Cloudflare's workarounds are live on Vercel

The migration's fixes were made in **shared application code**, not behind a Cloudflare-only
branch. They were committed to `main` and have therefore been deployed to Vercel production by
every deploy since Sep 9 — even though the Cloudflare migration itself never went live.

Verified on both hosts:

```
https://quantengines.com/api/og?title=probe
  → HTTP/1.1 302 Found
    Location: https://quantengines.com/og-image.jpg
    Server: Vercel
```

**Consequence:** `/api/og` no longer renders per-page OG images anywhere. Every shareable page on
quantengines.com — all 582+ blog posts, `/api-docs`, `/congress-alerts`,
`/congress-stock-trades/late-filers` — now advertises the *same* static `og-image.jpg` in social
previews, because the `title` param is accepted but ignored. Vercel had no technical need for this
change; it was purely a workaround for an OpenNext-on-Windows asset-resolution bug
(`opennextjs-cloudflare#545`). This is a real, user-visible SEO/social regression on production
that arrived as a passenger on an unshipped migration.

Second, smaller effect: `vercel.json`'s `buildCommand` is `npm run build`, which triggers the new
`prebuild` hook. So **every Vercel build now also runs `scripts/generate-blog-manifest.mjs`** —
generating a ~240KB manifest and copying every blog post into `public/blog-content/` — work that
only the Cloudflare Worker's `ASSETS` binding actually consumes. On Vercel it is dead weight in
build time and output size (harmless functionally, since `src/lib/blog-content.ts` prefers the
`ASSETS` binding only when running on Cloudflare and falls back to `fs` otherwise).

The migration doc does name the proper long-term fix for the OG images — generate the PNGs at
**build** time from a prebuild script (same pattern as the blog manifest) rather than at request
time, which sidesteps both adapter bugs and would work on Vercel *and* Cloudflare. That was
explicitly left undone.

---

## 6. Open decisions for Elliott (not acted on)

1. **Restore per-page OG images?** Either revert `/api/og` to `next/og`'s `ImageResponse` (Vercel
   handles it fine; only the Cloudflare build breaks) or implement the build-time PNG generation
   the doc recommends, which fixes it on both targets. Doing nothing keeps the current
   one-static-image-for-the-whole-site behaviour.
2. **Keep or retire the Cloudflare path?** It is a working, zero-cost rollback/alternate target,
   but with no CI behind it the Worker will keep drifting further from `main` (already 4 days / 2
   commits stale). If it's meant to be a real fallback, it needs either a deploy workflow or an
   acceptance that it must be rebuilt before it could be trusted in an outage. If it's dead, the
   `cf:*` scripts, `wrangler.jsonc`, `open-next.config.ts`, and the two devDependencies are
   removable — though note the blog-manifest `prebuild` step is now load-bearing for the blog
   pages' data flow, so it must **not** be removed along with them.
3. **Reconcile the version-pin doc drift** (§2): `CLOUDFLARE_MIGRATION.md` claims `1.15.1`;
   `package.json`/lockfile say `^1.14.10` / `1.14.10`.
4. **GA4 hostname hygiene.** Both builds embed the same measurement ID `G-PHX6T0R1Y1`, so any
   traffic to the `workers.dev` URL reports into the *same* GA4 property. Filter by hostname when
   reading analytics — and note this is also what makes the "production is on Vercel" GA4 evidence
   reliable: those sessions carry the `quantengines.com` hostname, which only Vercel serves.

---

## Appendix: how each claim was checked

```bash
# commit contents & messages
git log -1 --format='%H%n%an <%ae>%n%ad%n%n%B' ac2aa9c
git show --stat --format='' ac2aa9c
git show --stat --format='' 455829b

# nothing reverted / nothing touched since
git log --oneline --grep='revert' -i
git log --oneline ac2aa9c..HEAD -- quant/frontend/wrangler.jsonc \
  quant/frontend/open-next.config.ts quant/frontend/scripts/generate-blog-manifest.mjs \
  quant/frontend/src/lib/blog-content.ts
git log --oneline -- quant/frontend/wrangler.jsonc

# Cloudflare artifacts at HEAD, and the version drift
git show HEAD:quant/frontend/package.json
grep -n 'opennextjs' quant/package-lock.json

# no Cloudflare in CI
grep -rniE 'vercel|cloudflare|wrangler' .github/workflows/

# wrangler absent / unauthenticated
which wrangler; npx --no-install wrangler --version
ls node_modules/wrangler quant/frontend/node_modules/wrangler
ls -la "$HOME/.wrangler" "$APPDATA/.wrangler" "$LOCALAPPDATA/.wrangler"
env | grep -i '^CLOUDFLARE'

# DNS: Vercel origin, Porkbun nameservers
nslookup quantengines.com; nslookup www.quantengines.com; nslookup -type=NS quantengines.com

# origin headers (Server: Vercel, no CF-RAY) vs Worker (Server: cloudflare, x-opennext: 1)
curl -s -o /dev/null -D - https://quantengines.com/
curl -s -o /dev/null -D - https://quant-analytics-frontend.elliottsaxton.workers.dev/

# the /support staleness discriminator
curl -s -o /dev/null -w "%{http_code}\n" https://quantengines.com/support                       # 200
curl -s -o /dev/null -w "%{http_code}\n" https://quant-analytics-frontend.elliottsaxton.workers.dev/support  # 404
git ls-tree -r --name-only ac2aa9c -- quant/frontend/src/app | grep -i support                   # absent
git ls-tree -r --name-only HEAD    -- quant/frontend/src/app | grep -i support                   # present
git show --stat --format='%h %ad' --date=iso-strict 066fd8b

# shared-code side effect live on Vercel
curl -s -o /dev/null -D - "https://quantengines.com/api/og?title=probe"
```

All checks run 2026-09-13 from `C:\projects\quant`, branch `autopublish` (at `7c6f37f`, level
with `origin/main`). Pre-existing uncommitted working-tree changes (`.gitignore`, five
`public/data/*.json` files, `congress_alerts_digest.py`, two untracked test dirs) were left
untouched and are unrelated to this investigation.
