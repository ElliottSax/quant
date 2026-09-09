import { NextRequest, NextResponse } from 'next/server'

// Was a dynamic `next/og` ImageResponse (per-page title rendered into a
// generated PNG). @vercel/og's runtime needs bundled binary assets (a font
// .ttf plus resvg.wasm/yoga.wasm for the Satori/resvg render pipeline), and
// the OpenNext Cloudflare adapter cannot correctly locate those assets in
// this repo's Windows + npm-workspaces (monorepo) layout -- both the font
// copy step and wrangler's own esbuild asset resolution produced ENOENT
// errors on nested/duplicated absolute paths (a known class of upstream bug:
// https://github.com/opennextjs/opennextjs-cloudflare/issues/545). Rather
// than carry a build-breaking dependency for a nice-to-have per-page share
// image, this now redirects every request to the site's existing static
// fallback OG image (public/og-image.jpg) -- the `title` query param is
// accepted but unused, so every caller in src/app/**/*.tsx that builds an
// `/api/og?title=...` URL keeps working without any change on their end.
// See frontend/CLOUDFLARE_MIGRATION.md for the full writeup and how to
// restore per-page dynamic OG images if this ever needs revisiting off
// Windows (e.g. building from WSL or CI/Linux).
export const dynamic = 'force-dynamic'

export async function GET(request: NextRequest) {
  return NextResponse.redirect(new URL('/og-image.jpg', request.url), { status: 302 })
}
