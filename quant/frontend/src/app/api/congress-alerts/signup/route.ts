import { NextResponse } from 'next/server'
import crypto from 'crypto'
import type { SupabaseClient } from '@supabase/supabase-js'
import { getSupabaseAdmin } from '@/lib/supabase-admin'
import { getStripe, proPriceId } from '@/lib/congress-alerts-billing'
import {
  isValidEmail,
  normalizeFilter,
  maxFiltersForTier,
  type AlertFilterInput,
  type AlertTier,
  type BillingCycle,
} from '@/lib/congress-alerts'

export const dynamic = 'force-dynamic'

interface SignupBody {
  email?: string
  tier?: AlertTier
  billingCycle?: BillingCycle
  filters?: AlertFilterInput[]
}

// Best-effort throttle, same shape as frontend/src/app/api/newsletter/route.ts
// -- not a substitute for real rate limiting, just enough to stop a stray
// script from hammering Stripe/Supabase from one hot serverless instance.
const hits = new Map<string, { count: number; resetAt: number }>()
const WINDOW_MS = 60_000
const MAX_PER_WINDOW = 8

function rateLimited(ip: string): boolean {
  const now = Date.now()
  const entry = hits.get(ip)
  if (!entry || now > entry.resetAt) {
    hits.set(ip, { count: 1, resetAt: now + WINDOW_MS })
    if (hits.size > 5000) hits.clear()
    return false
  }
  entry.count += 1
  return entry.count > MAX_PER_WINDOW
}

async function replaceFilters(supabase: SupabaseClient, subscriberId: string, filters: AlertFilterInput[]) {
  await supabase.from('congress_alert_filters').delete().eq('subscriber_id', subscriberId)
  if (filters.length === 0) return
  const { error } = await supabase.from('congress_alert_filters').insert(
    filters.map((f) => ({
      subscriber_id: subscriberId,
      ticker: f.ticker || null,
      member_name: f.memberName || null,
      chamber: f.chamber || null,
    }))
  )
  if (error) throw error
}

export async function POST(request: Request) {
  try {
    const ip = request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 'unknown'
    if (rateLimited(ip)) {
      return NextResponse.json({ error: 'Too many requests. Please try again in a minute.' }, { status: 429 })
    }

    let body: SignupBody
    try {
      body = await request.json()
    } catch {
      return NextResponse.json({ error: 'Invalid JSON body.' }, { status: 400 })
    }

    const email = (body.email || '').trim().toLowerCase()
    if (!isValidEmail(email)) {
      return NextResponse.json({ error: 'Please enter a valid email address.' }, { status: 400 })
    }

    const tier: AlertTier = body.tier === 'pro' ? 'pro' : 'free'
    const filters = (body.filters || [])
      .map(normalizeFilter)
      .filter((f): f is NonNullable<typeof f> => f !== null)

    const maxFilters = maxFiltersForTier(tier)
    if (filters.length > maxFilters) {
      return NextResponse.json(
        {
          error: `${tier === 'pro' ? 'Pro' : 'Free'} plans support up to ${maxFilters} saved filter${
            maxFilters === 1 ? '' : 's'
          }. Leave filters empty for an unfiltered digest of everything.`,
        },
        { status: 400 }
      )
    }

    let supabase: SupabaseClient
    try {
      supabase = getSupabaseAdmin()
    } catch (err) {
      console.error('[congress-alerts] storage not configured:', err)
      return NextResponse.json({ error: 'Alerts are temporarily unavailable. Please try again later.' }, { status: 503 })
    }

    const { data: existing } = await supabase
      .from('congress_alert_subscribers')
      .select('id, tier, status, stripe_customer_id, manage_token')
      .eq('email', email)
      .maybeSingle()

    const alreadyActivePro = existing?.tier === 'pro' && existing?.status === 'active'
    const manageToken = existing?.manage_token || crypto.randomBytes(24).toString('hex')

    if (tier === 'free') {
      // Signing up for the free digest never downgrades an already-active Pro
      // subscriber -- it only updates their saved filters.
      const { data: subscriber, error } = await supabase
        .from('congress_alert_subscribers')
        .upsert(
          {
            email,
            // Signing up for the free digest never downgrades an
            // already-active Pro subscriber's tier -- both branches are
            // 'active' either way, since a brand-new free signup is active
            // immediately (no payment to wait on).
            tier: alreadyActivePro ? 'pro' : 'free',
            status: 'active',
            manage_token: manageToken,
          },
          { onConflict: 'email' }
        )
        .select('id, manage_token, tier')
        .single()

      if (error || !subscriber) {
        console.error('[congress-alerts] free signup failed:', error)
        return NextResponse.json({ error: 'Could not complete signup. Please try again.' }, { status: 500 })
      }

      // Only replace filters for someone actually landing on the free tier --
      // an already-Pro subscriber resubmitting the free form keeps their Pro
      // filter set untouched (they should use /congress-alerts/manage instead).
      if (!alreadyActivePro) {
        try {
          await replaceFilters(supabase, subscriber.id, filters)
        } catch (err) {
          console.error('[congress-alerts] failed to save free-tier filters:', err)
        }
      }

      return NextResponse.json({
        status: 'active',
        tier: subscriber.tier,
        manageUrl: `/congress-alerts/manage/${subscriber.manage_token}`,
      })
    }

    // --- Pro tier: create/reuse the subscriber row, save filters, then start
    // a real Stripe Checkout Session. Nothing is billed until Stripe confirms
    // payment and fires checkout.session.completed at the webhook below.
    const billingCycle: BillingCycle = body.billingCycle === 'yearly' ? 'yearly' : 'monthly'
    const priceId = proPriceId(billingCycle)
    if (!priceId) {
      return NextResponse.json(
        { error: 'Paid alerts are not configured yet. Please check back soon, or sign up for the free digest.' },
        { status: 503 }
      )
    }

    let stripe
    try {
      stripe = getStripe()
    } catch (err) {
      console.error('[congress-alerts] Stripe not configured:', err)
      return NextResponse.json(
        { error: 'Paid alerts are not configured yet. Please check back soon, or sign up for the free digest.' },
        { status: 503 }
      )
    }

    const { data: subscriber, error } = await supabase
      .from('congress_alert_subscribers')
      .upsert(
        {
          email,
          tier: alreadyActivePro ? 'pro' : 'free',
          status: alreadyActivePro ? 'active' : 'pending',
          manage_token: manageToken,
        },
        { onConflict: 'email' }
      )
      .select('id, stripe_customer_id')
      .single()

    if (error || !subscriber) {
      console.error('[congress-alerts] pro signup failed:', error)
      return NextResponse.json({ error: 'Could not start checkout. Please try again.' }, { status: 500 })
    }

    try {
      await replaceFilters(supabase, subscriber.id, filters)
    } catch (err) {
      console.error('[congress-alerts] failed to save pro-tier filters before checkout:', err)
    }

    if (alreadyActivePro) {
      // Already an active paying subscriber -- nothing to check out, just
      // confirm the filters were saved.
      return NextResponse.json({ status: 'active', tier: 'pro', manageUrl: `/congress-alerts/manage/${manageToken}` })
    }

    const origin = new URL(request.url).origin
    const session = await stripe.checkout.sessions.create({
      mode: 'subscription',
      line_items: [{ price: priceId, quantity: 1 }],
      customer: subscriber.stripe_customer_id || undefined,
      customer_email: subscriber.stripe_customer_id ? undefined : email,
      client_reference_id: subscriber.id,
      metadata: { subscriberId: subscriber.id },
      subscription_data: { metadata: { subscriberId: subscriber.id } },
      success_url: `${origin}/congress-alerts?checkout=success`,
      cancel_url: `${origin}/congress-alerts?checkout=cancelled`,
    })

    if (!session.url) {
      return NextResponse.json({ error: 'Stripe did not return a checkout URL.' }, { status: 502 })
    }

    return NextResponse.json({ checkoutUrl: session.url })
  } catch (error) {
    console.error('[congress-alerts] signup unexpected failure:', error)
    return NextResponse.json({ error: 'Something went wrong. Please try again.' }, { status: 500 })
  }
}
