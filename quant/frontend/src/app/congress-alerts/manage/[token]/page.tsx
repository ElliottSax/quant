import type { Metadata } from 'next'
import { ManageClient } from './ManageClient'

export const metadata: Metadata = {
  title: 'Manage Your Alerts | QuantEngines',
  robots: { index: false, follow: false },
}

export default function ManageAlertsPage({ params }: { params: { token: string } }) {
  return (
    <div className="container mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-white mb-6">Manage Your Congress Alerts</h1>
      <ManageClient token={params.token} />
    </div>
  )
}
