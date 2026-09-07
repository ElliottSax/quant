import { createClient, type SupabaseClient } from '@supabase/supabase-js'

// Server-only privileged Supabase client for the congress-alerts tables
// (frontend/supabase/congress_alerts.sql). Uses the service-role key, which
// bypasses Row Level Security -- this file must never be imported from a
// 'use client' component, and SUPABASE_SERVICE_ROLE_KEY must never be
// prefixed NEXT_PUBLIC_ or it would ship to the browser bundle.
//
// Lazy singleton (mirrors the pattern scrum-simulator's src/lib/billing.ts
// uses for its Stripe client): importing this module must stay safe even
// before Elliott provisions a real Supabase project for this feature. Only
// throws once a route handler actually tries to use it.

let _client: SupabaseClient | null = null

export function getSupabaseAdmin(): SupabaseClient {
  const url = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY
  if (!url || !key) {
    throw new Error(
      'SUPABASE_URL (or NEXT_PUBLIC_SUPABASE_URL) and SUPABASE_SERVICE_ROLE_KEY must be set -- congress alerts storage is not configured yet.'
    )
  }
  if (!_client) {
    _client = createClient(url, key, { auth: { persistSession: false } })
  }
  return _client
}
