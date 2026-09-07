-- Congress Trading Alerts -- subscriber + saved-filter tables.
--
-- This is a NEW, self-contained schema for the paid alerts add-on described in
-- frontend/src/app/congress-alerts/. It does not touch anything the free
-- backtesting tool or the free congress-trades browser reads from.
--
-- Run this once (Supabase SQL editor, or `supabase db execute -f this-file`)
-- against the Postgres project referenced by SUPABASE_URL /
-- SUPABASE_SERVICE_ROLE_KEY. Nothing here has been run against a live
-- database -- see the human setup steps in the delivery report.

create extension if not exists pgcrypto; -- gen_random_uuid() / gen_random_bytes()

create table if not exists congress_alert_subscribers (
  id uuid primary key default gen_random_uuid(),
  email text not null unique,
  tier text not null default 'free' check (tier in ('free', 'pro')),
  -- 'pending' = a Pro checkout was started but Stripe hasn't confirmed payment yet
  -- (webhook flips it to 'active'). Free signups go straight to 'active'.
  status text not null default 'active' check (status in ('pending', 'active', 'canceled', 'past_due')),
  stripe_customer_id text unique,
  stripe_subscription_id text unique,
  -- Bearer token for the self-serve "manage my alerts" / unsubscribe link mailed
  -- in every digest. Deliberately not a real user-account system -- this product
  -- doesn't need one, and quant's real login/register flow is documented
  -- elsewhere in this repo as broken end-to-end.
  manage_token text not null unique default encode(gen_random_bytes(24), 'hex'),
  -- Cursor the digest cron reads/advances. Only the DATE portion is compared
  -- (see scripts/congress_alerts_digest.py) to match the daily-batch nature of
  -- the underlying FMP feed -- there's no sub-day freshness to gain from a
  -- finer-grained cursor.
  last_digest_sent_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists congress_alert_filters (
  id uuid primary key default gen_random_uuid(),
  subscriber_id uuid not null references congress_alert_subscribers(id) on delete cascade,
  -- All three are optional per-row, but a row must set at least one (enforced
  -- below) -- a filter with nothing set would silently match everything, which
  -- is what an EMPTY filter LIST already means (see trade_matches() in the
  -- digest script), so a same-meaning row would just be confusing duplication.
  ticker text,
  member_name text,
  chamber text check (chamber in ('House', 'Senate')),
  created_at timestamptz not null default now(),
  constraint congress_alert_filter_has_criterion check (
    ticker is not null or member_name is not null or chamber is not null
  )
);

create index if not exists idx_congress_alert_filters_subscriber on congress_alert_filters(subscriber_id);
create index if not exists idx_congress_alert_subscribers_status_tier on congress_alert_subscribers(status, tier);

-- Deny-by-default: only SUPABASE_SERVICE_ROLE_KEY (used exclusively in server-side
-- Next.js route handlers and the digest cron script, never shipped to the
-- browser) can read or write these tables. If the Supabase anon/public key is
-- ever used against this project, it gets zero rows from either table.
alter table congress_alert_subscribers enable row level security;
alter table congress_alert_filters enable row level security;
