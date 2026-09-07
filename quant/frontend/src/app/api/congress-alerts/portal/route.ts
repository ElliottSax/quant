import { NextRequest, NextResponse } from 'next/server'
import { getStripe } from '@/lib/congress-alerts-billing'
import { getSupabaseAdmin } from '@/lib/supabase-admin'

export const dynamic = 'force-dynamic'

// Opens Stripe's hosted Customer Portal (update card, view invoices, cancel at
// period end) for a Pro subscriber, identified by their manage token rather
// than a site login -- this product has no account system, matching the rest
// of congress-alerts (see supabase-admin.ts's comment on manage_token).
export async function POST(req: NextRequest) {
  let body: { token?: string }
  try {
    body = await req.json()
  } catch {
    return NextResponse.json({ error: 'Invalid JSON body.' }, { status: 400 })
  }

  const token = (body.token || '').trim()
  if (!token) {
    return NextResponse.json({ error: 'Missing manage token.' }, { status: 400 })
  }

  if (!process.env.STRIPE_SECRET_KEY) {
    return NextResponse.json({ error: 'Billing is not configured yet.' }, { status: 503 })
  }

  const supabase = getSupabaseAdmin()
  const { data: subscriber } = await supabase
    .from('congress_alert_subscribers')
    .select('stripe_customer_id')
    .eq('manage_token', token)
    .maybeSingle()

  if (!subscriber?.stripe_customer_id) {
    return NextResponse.json({ error: 'No billing account found for this link. Are you on the free plan?' }, { status: 404 })
  }

  const stripe = getStripe()
  const portalSession = await stripe.billingPortal.sessions.create({
    customer: subscriber.stripe_customer_id,
    return_url: `${req.nextUrl.origin}/congress-alerts/manage/${token}`,
  })

  return NextResponse.json({ url: portalSession.url })
}
