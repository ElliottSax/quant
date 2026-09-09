// OpenNext Cloudflare adapter config -- see frontend/CLOUDFLARE_MIGRATION.md
// for why this exists (Vercel Hobby tier paused for CPU overage; this is the
// alternate free-tier deploy target). @cloudflare/next-on-pages, which the
// original migration brief named, is officially deprecated in favor of this
// adapter (https://github.com/cloudflare/next-on-pages README).
//
// Pinned to @opennextjs/cloudflare@1.15.1 -- the last version whose peer
// range still covers this app's Next 14.2.35 (1.16+ requires Next 15/16).
import { defineCloudflareConfig } from '@opennextjs/cloudflare'

export default defineCloudflareConfig({
  // No incremental cache override: this app has no ISR-heavy ecommerce-style
  // routes that need R2-backed caching (its only `revalidate` usage is the
  // congress-stock-trades pages' 86400s tag, which functions fine against
  // OpenNext's default in-memory/edge-cache behavior for a preview
  // deployment). Revisit with r2IncrementalCache if that changes.
})
