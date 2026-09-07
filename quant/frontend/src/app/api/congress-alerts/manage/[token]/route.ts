import { NextRequest, NextResponse } from 'next/server'
import { getSupabaseAdmin } from '@/lib/supabase-admin'
import { normalizeFilter, maxFiltersForTier, type AlertFilterInput, type AlertTier } from '@/lib/congress-alerts'

export const dynamic = 'force-dynamic'

// Self-serve alert management, addressed by the bearer manage_token mailed in
// every digest -- see supabase-admin.ts for why this product has no login.

export async function GET(_req: NextRequest, { params }: { params: { token: string } }) {
  const supabase = getSupabaseAdmin()
  const { data: subscriber } = await supabase
    .from('congress_alert_subscribers')
    .select('id, email, tier, status, created_at')
    .eq('manage_token', params.token)
    .maybeSingle()

  if (!subscriber) {
    return NextResponse.json({ error: 'This link is invalid or has expired.' }, { status: 404 })
  }

  const { data: filters } = await supabase
    .from('congress_alert_filters')
    .select('id, ticker, member_name, chamber')
    .eq('subscriber_id', subscriber.id)
    .order('created_at', { ascending: true })

  return NextResponse.json({
    email: subscriber.email,
    tier: subscriber.tier,
    status: subscriber.status,
    createdAt: subscriber.created_at,
    filters: filters || [],
    maxFilters: maxFiltersForTier(subscriber.tier as AlertTier),
  })
}

export async function PATCH(req: NextRequest, { params }: { params: { token: string } }) {
  let body: { filters?: AlertFilterInput[] }
  try {
    body = await req.json()
  } catch {
    return NextResponse.json({ error: 'Invalid JSON body.' }, { status: 400 })
  }

  const supabase = getSupabaseAdmin()
  const { data: subscriber } = await supabase
    .from('congress_alert_subscribers')
    .select('id, tier')
    .eq('manage_token', params.token)
    .maybeSingle()

  if (!subscriber) {
    return NextResponse.json({ error: 'This link is invalid or has expired.' }, { status: 404 })
  }

  const filters = (body.filters || []).map(normalizeFilter).filter((f): f is NonNullable<typeof f> => f !== null)
  const maxFilters = maxFiltersForTier(subscriber.tier as AlertTier)
  if (filters.length > maxFilters) {
    return NextResponse.json(
      { error: `Your plan supports up to ${maxFilters} saved filter${maxFilters === 1 ? '' : 's'}.` },
      { status: 400 }
    )
  }

  const { error: deleteError } = await supabase.from('congress_alert_filters').delete().eq('subscriber_id', subscriber.id)
  if (deleteError) {
    console.error('[congress-alerts manage] failed to clear filters:', deleteError)
    return NextResponse.json({ error: 'Could not update filters. Please try again.' }, { status: 500 })
  }

  if (filters.length > 0) {
    const { error: insertError } = await supabase.from('congress_alert_filters').insert(
      filters.map((f) => ({
        subscriber_id: subscriber.id,
        ticker: f.ticker || null,
        member_name: f.memberName || null,
        chamber: f.chamber || null,
      }))
    )
    if (insertError) {
      console.error('[congress-alerts manage] failed to save filters:', insertError)
      return NextResponse.json({ error: 'Could not update filters. Please try again.' }, { status: 500 })
    }
  }

  return NextResponse.json({ status: 'ok' })
}

export async function DELETE(_req: NextRequest, { params }: { params: { token: string } }) {
  const supabase = getSupabaseAdmin()
  const { data: subscriber } = await supabase
    .from('congress_alert_subscribers')
    .select('id, stripe_subscription_id')
    .eq('manage_token', params.token)
    .maybeSingle()

  if (!subscriber) {
    return NextResponse.json({ error: 'This link is invalid or has expired.' }, { status: 404 })
  }

  // Immediate hard-unsubscribe (stops billing right away, no proration) --
  // distinct from the Stripe Customer Portal's "cancel at period end" flow,
  // which is offered separately via /api/congress-alerts/portal for anyone
  // who wants to keep access through what they already paid for.
  if (subscriber.stripe_subscription_id && process.env.STRIPE_SECRET_KEY) {
    try {
      const { getStripe } = await import('@/lib/congress-alerts-billing')
      const stripe = getStripe()
      await stripe.subscriptions.cancel(subscriber.stripe_subscription_id)
    } catch (err) {
      console.error('[congress-alerts manage] failed to cancel Stripe subscription on unsubscribe:', err)
    }
  }

  const { error } = await supabase
    .from('congress_alert_subscribers')
    .update({ status: 'canceled', updated_at: new Date().toISOString() })
    .eq('id', subscriber.id)

  if (error) {
    console.error('[congress-alerts manage] failed to mark unsubscribed:', error)
    return NextResponse.json({ error: 'Could not unsubscribe. Please try again.' }, { status: 500 })
  }

  return NextResponse.json({ status: 'canceled' })
}
