// Affiliate partner config. Pure functions, no framework imports, so node's built-in test runner
// can exercise the rules (src/lib/__tests__/affiliate-partners.test.ts).
//
// The rule this file exists to enforce: a partner link renders ONLY when a real tracking URL
// has been supplied through the server environment. No URL, no block, no dead link, no
// placeholder id. Nothing earns until Elliott pastes an approved tracking URL, and the
// disclosure page flips to "live" from the same data in the same deploy, so the disclosure can
// never lag the links it describes (the failure affiliate networks check hardest).
//
// To go live with a partner: set its env var (see PARTNERS[].envVar) in Vercel for the
// quant-analytics-frontend project, then redeploy. Documented in docs/AFFILIATE_PARTNERS.md.

export type PartnerCategory = 'broker' | 'data'

export interface PartnerDef {
  id: string
  name: string
  category: PartnerCategory
  /** Server-side env var holding the full tracking URL from the partner's affiliate dashboard. */
  envVar: string
  /** One factual, non-promotional line. No ratings, bonuses, rankings or performance claims. */
  blurb: string
}

export const PARTNERS: PartnerDef[] = [
  {
    id: 'ibkr',
    name: 'Interactive Brokers',
    category: 'broker',
    envVar: 'AFFILIATE_URL_IBKR',
    blurb: 'Brokerage with an API for programmatic trading.',
  },
  {
    id: 'm1',
    name: 'M1 Finance',
    category: 'broker',
    envVar: 'AFFILIATE_URL_M1',
    blurb: 'Brokerage with automated portfolio rebalancing.',
  },
  {
    id: 'fmp',
    name: 'Financial Modeling Prep',
    category: 'data',
    envVar: 'AFFILIATE_URL_FMP',
    blurb: 'Market-data API used for some of the figures published on this site.',
  },
]

export type Env = Record<string, string | undefined>

export interface LivePartner extends PartnerDef {
  url: string
}

// Strings that mean "somebody pasted a stub", never a real tracking id.
const PLACEHOLDER = /(quant2024|todo|example|placeholder|changeme|change-me|your[_-]?id|xxx|lorem|test123)/i

/** A tracking URL is usable only if it is an https URL on a real host without credentials. */
export function isValidAffiliateUrl(raw: string | undefined | null): boolean {
  if (!raw || typeof raw !== 'string') return false
  const s = raw.trim()
  if (s.length === 0 || s.length > 2048) return false
  if (PLACEHOLDER.test(s)) return false
  let u: URL
  try {
    u = new URL(s)
  } catch {
    return false
  }
  if (u.protocol !== 'https:') return false
  if (u.username || u.password) return false
  if (!u.hostname.includes('.')) return false
  if (u.hostname === 'localhost' || /^\d+\.\d+\.\d+\.\d+$/.test(u.hostname)) return false
  return true
}

export function getLivePartners(env: Env): LivePartner[] {
  const out: LivePartner[] = []
  for (const p of PARTNERS) {
    const raw = env[p.envVar]
    if (isValidAffiliateUrl(raw)) out.push({ ...p, url: (raw as string).trim() })
  }
  return out
}

export interface PartnerBlockModel {
  heading: string
  disclosure: string
  links: Array<{ id: string; name: string; blurb: string; url: string; rel: string; target: string; marker: string }>
}

/** null when nothing is live: the caller renders nothing at all. */
export function partnerBlockModel(env: Env): PartnerBlockModel | null {
  const live = getLivePartners(env)
  if (live.length === 0) return null
  return {
    heading: 'Tools we link to',
    disclosure:
      'These are affiliate links: if you sign up through them we may earn a commission at no extra cost to you. It does not change any result we publish.',
    links: live.map((p) => ({
      id: p.id,
      name: p.name,
      blurb: p.blurb,
      url: p.url,
      rel: 'sponsored noopener noreferrer',
      target: '_blank',
      marker: 'Affiliate link',
    })),
  }
}

export interface DisclosureStatus {
  live: boolean
  partnerNames: string[]
}

export function disclosureStatus(env: Env): DisclosureStatus {
  const live = getLivePartners(env)
  return { live: live.length > 0, partnerNames: live.map((p) => p.name) }
}
