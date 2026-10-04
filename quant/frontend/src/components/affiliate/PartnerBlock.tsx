// Server component. Renders NOTHING unless at least one partner has a valid tracking URL in the
// server environment (see src/lib/affiliate-partners.ts). With no URL there is no markup at all:
// no heading, no empty box, no dead link.

import Link from 'next/link'
import { partnerBlockModel } from '@/lib/affiliate-partners'
import PartnerLink from './PartnerLink'

export default function PartnerBlock() {
  const model = partnerBlockModel(process.env)
  if (!model) return null
  return (
    <section aria-labelledby="partner-heading" className="glass-card p-6 text-sm text-slate-400 max-w-4xl">
      <h2 id="partner-heading" className="text-lg font-bold text-white mb-2">
        {model.heading}
      </h2>
      <p className="mb-3">
        {model.disclosure}{' '}
        <Link href="/affiliate-disclosure" className="text-blue-400 hover:text-blue-300 underline">
          Affiliate disclosure
        </Link>
        .
      </p>
      <ul className="space-y-2">
        {model.links.map((l) => (
          <li key={l.id}>
            <PartnerLink href={l.url} rel={l.rel} target={l.target} name={l.name}>
              {l.name}
            </PartnerLink>{' '}
            <span className="text-xs uppercase tracking-wide text-slate-500">({l.marker})</span>
            <span className="block text-slate-400">{l.blurb}</span>
          </li>
        ))}
      </ul>
    </section>
  )
}
