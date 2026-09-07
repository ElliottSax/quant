import { NextRequest, NextResponse } from 'next/server'
import Stripe from 'stripe'
import { getStripe } from '@/lib/congress-alerts-billing'
import { getSupabaseAdmin } from '@/lib/supabase-admin'

export const dynamic = 'force-dynamic'

// Server-to-server: no browser session, no CSRF concern. Authenticity comes
// entirely from the Stripe-Signature check below. This is a dedicated
// endpoint URL (register it as its own webhook in the Stripe Dashboard) with
// its own signing secret, STRIPE_CONGRESS_ALERTS_WEBHOOK_SECRET -- separate
// from any webhook secret the legacy backend Stripe code might use, so the
// two products' events can never cross-verify against the wrong secret.
export async function POST(req: NextRequest) {
  const secret = process.env.STRIPE_CONGRESS_ALERTS_WEBHOOK_SECRET
  if (!process.env.STRIPE_SECRET_KEY || !secret) {
    return NextResponse.json({ error: 'Billing is not configured yet.' }, { status: 503 })
  }

  const signature = req.headers.get('stripe-signature')
  if (!signature) {
    return NextResponse.json({ error: 'Missing stripe-signature header.' }, { status: 400 })
  }

  // Must be the raw, unparsed body -- Stripe's signature is computed over the
  // exact bytes sent. App Router route handlers never auto-parse the body, so
  // req.text() already gives the raw payload (see scrum-simulator's
  // src/app/api/stripe/webhook/route.ts, same pattern).
  const rawBody = await req.text()
  const stripe = getStripe()

  let event: Stripe.Event
  try {
    event = stripe.webhooks.constructEvent(rawBody, signature, secret)
  } catch (err) {
    const message = err instanceof Error ? err.message : 'invalid signature'
    return NextResponse.json({ error: `Webhook signature verification failed: ${message}` }, { status: 400 })
  }

  const supabase = getSupabaseAdmin()

  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object as Stripe.Checkout.Session
      const subscriberId = session.client_reference_id || session.metadata?.subscriberId || null
      const customerId = typeof session.customer === 'string' ? session.customer : null
      const subscriptionId = typeof session.subscription === 'string' ? session.subscription : null

      if (!subscriberId || !customerId || !subscriptionId) {
        // Nothing safe to act on -- ack with 200 so Stripe doesn't retry a
        // payload that will never resolve differently, but log loudly since
        // it means checkout was misconfigured and a paying subscriber won't
        // get activated.
        console.error('[congress-alerts webhook] checkout.session.completed missing expected fields', {
          sessionId: session.id,
          subscriberId,
          customerId,
          subscriptionId,
        })
        break
      }

      const { error } = await supabase
        .from('congress_alert_subscribers')
        .update({
          tier: 'pro',
          status: 'active',
          stripe_customer_id: customerId,
          stripe_subscription_id: subscriptionId,
          updated_at: new Date().toISOString(),
        })
        .eq('id', subscriberId)

      if (error) console.error('[congress-alerts webhook] failed to activate subscriber after checkout:', error)
      break
    }

    case 'customer.subscription.updated': {
      const subscription = event.data.object as Stripe.Subscription
      const status = mapStripeStatus(subscription.status)
      const { error } = await supabase
        .from('congress_alert_subscribers')
        .update({ status, updated_at: new Date().toISOString() })
        .eq('stripe_subscription_id', subscription.id)
      if (error) console.error('[congress-alerts webhook] failed to sync subscription.updated:', error)
      break
    }

    case 'customer.subscription.deleted': {
      const subscription = event.data.object as Stripe.Subscription
      const { error } = await supabase
        .from('congress_alert_subscribers')
        // Downgrade to free rather than deleting the row -- keeps the manage
        // token and email alive so they keep getting the free weekly digest
        // instead of silently vanishing.
        .update({ tier: 'free', status: 'active', stripe_subscription_id: null, updated_at: new Date().toISOString() })
        .eq('stripe_subscription_id', subscription.id)
      if (error) console.error('[congress-alerts webhook] failed to downgrade after subscription.deleted:', error)
      break
    }

    case 'invoice.payment_failed': {
      const invoice = event.data.object as Stripe.Invoice
      // Newer Stripe API versions moved this from invoice.subscription to
      // invoice.parent.subscription_details.subscription.
      const rawSubscription = invoice.parent?.subscription_details?.subscription
      const subscriptionId = typeof rawSubscription === 'string' ? rawSubscription : rawSubscription?.id || null
      if (subscriptionId) {
        const { error } = await supabase
          .from('congress_alert_subscribers')
          .update({ status: 'past_due', updated_at: new Date().toISOString() })
          .eq('stripe_subscription_id', subscriptionId)
        if (error) console.error('[congress-alerts webhook] failed to mark past_due:', error)
      }
      break
    }

    default:
      // Unhandled event type -- Stripe requires a 2xx for anything we don't
      // act on, or it retries indefinitely. Not an error condition.
      break
  }

  return NextResponse.json({ received: true })
}

function mapStripeStatus(status: Stripe.Subscription.Status): 'active' | 'past_due' | 'canceled' | 'pending' {
  switch (status) {
    case 'active':
    case 'trialing':
      return 'active'
    case 'past_due':
    case 'unpaid':
      return 'past_due'
    case 'canceled':
    case 'incomplete_expired':
      return 'canceled'
    default:
      return 'pending'
  }
}
