import type { Metadata } from 'next'
import PoliticiansClient from './PoliticiansClient'

// Page-level metadata (not the layout's) so the canonical is not inherited by /politicians/[id].
export const metadata: Metadata = {
  alternates: { canonical: '/politicians' },
}

export default function PoliticiansPage() {
  return <PoliticiansClient />
}
