'use client'

// One affiliate link. Client component only because it reports the click to GA4 through the
// window.trackAffiliateClick helper that app/layout.tsx defines. The href is always a real
// tracking URL: PartnerBlock never renders this component without one.

import type { ReactNode } from 'react'

type Tracker = (network: string, toolName: string) => void

export default function PartnerLink({
  href,
  rel,
  target,
  name,
  children,
}: {
  href: string
  rel: string
  target: string
  name: string
  children: ReactNode
}) {
  return (
    <a
      href={href}
      rel={rel}
      target={target}
      className="text-blue-400 hover:text-blue-300 underline"
      onClick={() => {
        const t = (window as unknown as { trackAffiliateClick?: Tracker }).trackAffiliateClick
        if (typeof t === 'function') t('direct', name)
      }}
    >
      {children}
    </a>
  )
}
