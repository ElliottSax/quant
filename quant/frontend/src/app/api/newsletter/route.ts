import { NextResponse } from 'next/server'

// Replaces the old browser-side Supabase insert. The Supabase project it wrote
// to (jznljskfvhlqlshofkvd) no longer exists, so every signup on the site was
// failing DNS resolution and being lost. This route writes to Resend instead.
//
// Deliberately dependency-free (raw fetch, no `resend` package, no `zod`) —
// quant's build has broken before on dependency/gitignore issues, so this adds
// no new install surface.

export const dynamic = 'force-dynamic'

const RESEND_API = 'https://api.resend.com'
const AUDIENCE_NAME = 'QuantEngines'

// Resolved once per warm instance: env var wins, otherwise find-or-create an
// audience by name so the route works before anyone touches the dashboard.
let cachedAudienceId: string | null = null

async function resolveAudienceId(apiKey: string): Promise<string> {
  if (process.env.RESEND_AUDIENCE_ID) return process.env.RESEND_AUDIENCE_ID
  if (cachedAudienceId) return cachedAudienceId

  const headers = { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json' }

  const listRes = await fetch(`${RESEND_API}/audiences`, { headers, cache: 'no-store' })
  if (listRes.ok) {
    const body = await listRes.json()
    const found = (body?.data ?? []).find(
      (a: { id: string; name: string }) => a.name === AUDIENCE_NAME
    )
    if (found?.id) {
      cachedAudienceId = found.id
      return found.id
    }
  }

  const createRes = await fetch(`${RESEND_API}/audiences`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ name: AUDIENCE_NAME }),
  })
  if (!createRes.ok) {
    throw new Error(`Could not resolve a Resend audience (${createRes.status})`)
  }
  const created = await createRes.json()
  if (!created?.id) throw new Error('Resend returned an audience with no id')
  cachedAudienceId = created.id
  return created.id
}

// Best-effort throttle. Serverless instances aren't shared, so this only slows
// a single hot instance — it is not a substitute for real rate limiting, but it
// keeps a trivial script from burning through the Resend quota.
const hits = new Map<string, { count: number; resetAt: number }>()
const WINDOW_MS = 60_000
const MAX_PER_WINDOW = 5

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

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

// Sends a welcome email via Resend. Requires a verified sending domain for the
// EMAIL_FROM address; until quantengines.com verifies, Resend rejects the send
// and this throws — callers invoke it non-blocking so the signup still succeeds.
async function sendWelcomeEmail(apiKey: string, email: string, firstName: string) {
  const from = process.env.EMAIL_FROM || 'QuantEngines <hello@quantengines.com>'
  const hi = firstName ? ` ${firstName}` : ''
  const site = 'https://quantengines.com'
  const res = await fetch(`${RESEND_API}/emails`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from,
      to: [email],
      subject: 'Welcome to QuantEngines',
      text: `Hi${hi},

Thanks for subscribing to QuantEngines — quantitative trading strategies, backtesting, and market insights, weekly.

Start here:
• Backtesting: ${site}/backtesting
• Congressional trades: ${site}/congressional-trades
• Free course: ${site}/courses/backtesting-101

— The QuantEngines Team`,
      html: `<div style="font-family:Arial,sans-serif;max-width:560px;margin:0 auto;line-height:1.6;color:#e5e7eb;background:#0b1020;padding:24px;border-radius:8px">
  <h1 style="font-size:22px;margin:0 0 12px;color:#fff">Welcome to QuantEngines</h1>
  <p>Hi${hi},</p>
  <p>Thanks for subscribing — quantitative trading strategies, backtesting, and market insights, weekly.</p>
  <p style="margin:20px 0"><strong style="color:#fff">Start here:</strong></p>
  <ul style="padding-left:18px">
    <li><a href="${site}/backtesting" style="color:#fbbf24">Backtesting</a></li>
    <li><a href="${site}/congressional-trades" style="color:#fbbf24">Congressional trades</a></li>
    <li><a href="${site}/courses/backtesting-101" style="color:#fbbf24">Free backtesting course</a></li>
  </ul>
  <p style="margin-top:24px">— The QuantEngines Team</p>
</div>`,
    }),
  })
  if (!res.ok) throw new Error(`welcome send ${res.status}: ${(await res.text()).slice(0, 200)}`)
}

export async function POST(request: Request) {
  try {
    const ip =
      request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 'unknown'
    if (rateLimited(ip)) {
      return NextResponse.json(
        { error: 'Too many requests. Please try again in a minute.' },
        { status: 429 }
      )
    }

    const body = await request.json().catch(() => null)
    if (!body || typeof body.email !== 'string') {
      return NextResponse.json({ error: 'An email address is required.' }, { status: 400 })
    }

    const email = body.email.trim().toLowerCase()
    if (email.length > 320 || !EMAIL_RE.test(email)) {
      return NextResponse.json(
        { error: 'Please enter a valid email address.' },
        { status: 400 }
      )
    }

    const firstName =
      typeof body.firstName === 'string' ? body.firstName.trim().slice(0, 50) : ''
    // `source` is kept for the server log only. Resend contacts have no custom
    // metadata field, so per-form attribution lives in the GA4 `email_signup`
    // event that the client fires on success.
    const source = typeof body.source === 'string' ? body.source.slice(0, 60) : 'unknown'

    const apiKey = process.env.RESEND_API_KEY
    if (!apiKey) {
      // Fail loudly rather than pretending success — silently accepting and
      // discarding signups is exactly the bug this route was written to fix.
      console.error('[newsletter] RESEND_API_KEY is not set; signup was NOT saved:', email)
      return NextResponse.json(
        { error: 'Signups are temporarily unavailable. Please try again later.' },
        { status: 503 }
      )
    }

    const audienceId = await resolveAudienceId(apiKey)

    const res = await fetch(`${RESEND_API}/audiences/${audienceId}/contacts`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        first_name: firstName || undefined,
        unsubscribed: false,
      }),
    })

    if (res.ok) {
      console.log(`[newsletter] subscribed ${email} (source: ${source})`)
      // Fire-and-forget welcome email. A failure (e.g. quantengines.com not yet
      // verified in Resend) must never fail the signup response.
      void sendWelcomeEmail(apiKey, email, firstName).catch((err) =>
        console.error('[newsletter] welcome email failed:', err)
      )
      return NextResponse.json({ success: true })
    }

    const errText = await res.text()

    // Resend treats a repeat address as a conflict; that's a normal outcome for
    // a public form, not an error worth alarming the visitor about.
    if (res.status === 409 || /already exists/i.test(errText)) {
      return NextResponse.json({ success: true, alreadySubscribed: true })
    }

    console.error(`[newsletter] Resend rejected ${email}: ${res.status} ${errText}`)
    return NextResponse.json(
      { error: 'Could not complete signup. Please try again.' },
      { status: 502 }
    )
  } catch (error) {
    console.error('[newsletter] unexpected failure:', error)
    return NextResponse.json(
      { error: 'Something went wrong. Please try again.' },
      { status: 500 }
    )
  }
}
