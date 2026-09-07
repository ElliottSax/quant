#!/usr/bin/env python3
"""Congress Trading Alerts -- daily digest sender.

Standalone script (dependency-light: `requests` only), matching the existing
gsc_auto_submit.py / .github/workflows/gsc-daily-submit.yml convention of
running a small script directly in GitHub Actions rather than installing
quant/backend's full dependency tree for one cron job. It talks to three
real, external services -- no mocked or fabricated data anywhere in this
file:

  - Financial Modeling Prep's senate-latest / house-latest endpoints -- the
    SAME live data source quant's frontend already uses in production
    (frontend/src/lib/congress-trades.ts). This script re-fetches it
    server-side in Python (fetch_fmp_trades() mirrors that file's
    fetchChamber()) so the cron job doesn't depend on the Next.js app being
    warm; it is not a second, different data source.
  - Supabase's PostgREST API (SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY) --
    the same congress_alert_subscribers / congress_alert_filters tables the
    Next.js routes under frontend/src/app/api/congress-alerts/ read and
    write (see frontend/supabase/congress_alerts.sql for the schema).
  - Resend's HTTP API (RESEND_API_KEY) -- the same provider and raw-HTTP
    pattern already used by frontend/src/app/api/newsletter/route.ts and
    backend/app/services/email_service.py.

Cadence: Pro subscribers are checked every run (the workflow schedules this
daily). Free subscribers are only mailed once >=7 days have passed since
their last digest (weekly). A run that finds zero new matching disclosures
for a subscriber sends no email and still advances that subscriber's cursor
-- that's an expected quiet day, not a failure.

Freshness is honest, not real-time: FMP's senate-latest/house-latest feed
itself updates on a daily-batch cadence, and the STOCK Act separately gives
members up to 45 days to file after a trade in the first place. This script
can only surface a disclosure once FMP already has it -- it does not, and
cannot, change either of those upstream limits. Digest copy says so
explicitly (see build_digest_email()).
"""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timezone, date
from typing import Any, Optional

import requests

FMP_BASE = "https://financialmodelingprep.com/stable"
RESEND_API = "https://api.resend.com/emails"
SUPABASE_TIMEOUT = 20
FMP_TIMEOUT = 20
RESEND_TIMEOUT = 20

# Free subscribers get a digest at most once every this-many days.
FREE_DIGEST_MIN_DAYS = 7

# Cap on rows listed in one email before falling back to a "+N more" link --
# keeps a subscriber with a very broad filter (or the unfiltered free digest
# on a busy week) from receiving an unreadable wall of a table.
MAX_ROWS_IN_EMAIL = 40


def env(name: str, default: Optional[str] = None, required: bool = False) -> str:
    val = os.environ.get(name, default)
    if required and not val:
        print(f"[congress-alerts-digest] Missing required env var: {name}", file=sys.stderr)
        sys.exit(1)
    return val or ""


def fetch_fmp_trades(api_key: str) -> list[dict[str, Any]]:
    """Python mirror of frontend/src/lib/congress-trades.ts's fetchChamber()."""
    trades: list[dict[str, Any]] = []
    for path, chamber in (("senate-latest", "Senate"), ("house-latest", "House")):
        try:
            res = requests.get(f"{FMP_BASE}/{path}", params={"apikey": api_key}, timeout=FMP_TIMEOUT)
            res.raise_for_status()
            raw = res.json()
        except Exception as exc:  # network error, non-200, bad JSON -- skip this chamber, keep going
            print(f"[congress-alerts-digest] FMP fetch failed for {path}: {exc}", file=sys.stderr)
            continue
        if not isinstance(raw, list):
            continue
        for t in raw:
            symbol = t.get("symbol")
            if not symbol or symbol == "N/A":
                continue
            member = t.get("office") or f"{t.get('firstName', '')} {t.get('lastName', '')}".strip()
            trades.append(
                {
                    "ticker": symbol,
                    "member": member,
                    "chamber": chamber,
                    "transactionDate": t.get("transactionDate", ""),
                    "disclosureDate": t.get("disclosureDate", ""),
                    "assetDescription": t.get("assetDescription", ""),
                    "type": t.get("type", ""),
                    "amount": t.get("amount", ""),
                    "link": t.get("link", ""),
                }
            )
    return trades


def parse_date(s: str) -> Optional[date]:
    try:
        return datetime.strptime((s or "").strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def supabase_headers(service_key: str) -> dict[str, str]:
    return {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
    }


def fetch_active_subscribers(supabase_url: str, service_key: str) -> list[dict[str, Any]]:
    res = requests.get(
        f"{supabase_url}/rest/v1/congress_alert_subscribers",
        headers=supabase_headers(service_key),
        params={"status": "eq.active", "select": "id,email,tier,manage_token,last_digest_sent_at"},
        timeout=SUPABASE_TIMEOUT,
    )
    res.raise_for_status()
    return res.json()


def fetch_all_filters(supabase_url: str, service_key: str) -> dict[str, list[dict[str, Any]]]:
    res = requests.get(
        f"{supabase_url}/rest/v1/congress_alert_filters",
        headers=supabase_headers(service_key),
        params={"select": "subscriber_id,ticker,member_name,chamber"},
        timeout=SUPABASE_TIMEOUT,
    )
    res.raise_for_status()
    by_subscriber: dict[str, list[dict[str, Any]]] = {}
    for row in res.json():
        by_subscriber.setdefault(row["subscriber_id"], []).append(row)
    return by_subscriber


def update_last_sent(supabase_url: str, service_key: str, subscriber_id: str, when: datetime) -> None:
    res = requests.patch(
        f"{supabase_url}/rest/v1/congress_alert_subscribers",
        headers={**supabase_headers(service_key), "Prefer": "return=minimal"},
        params={"id": f"eq.{subscriber_id}"},
        json={"last_digest_sent_at": when.isoformat()},
        timeout=SUPABASE_TIMEOUT,
    )
    if not res.ok:
        print(
            f"[congress-alerts-digest] failed to advance cursor for subscriber {subscriber_id}: "
            f"{res.status_code} {res.text[:200]}",
            file=sys.stderr,
        )


def trade_matches(trade: dict[str, Any], filters: list[dict[str, Any]]) -> bool:
    """No saved filters == match everything (the unfiltered digest). Multiple
    saved filters are OR'd -- a trade matching any one of them is included."""
    if not filters:
        return True
    for f in filters:
        if f.get("ticker") and f["ticker"].upper() != trade["ticker"].upper():
            continue
        if f.get("member_name") and f["member_name"].lower() not in trade["member"].lower():
            continue
        if f.get("chamber") and f["chamber"] != trade["chamber"]:
            continue
        return True
    return False


def build_digest_email(trades: list[dict[str, Any]], manage_token: str, tier: str) -> tuple[str, str, str]:
    site = "https://quantengines.com"
    manage_url = f"{site}/congress-alerts/manage/{manage_token}"
    subject = f"{len(trades)} new congressional trade disclosure{'s' if len(trades) != 1 else ''}"
    cadence_word = "daily" if tier == "pro" else "weekly"

    shown = trades[:MAX_ROWS_IN_EMAIL]
    rows_html = []
    lines_text = []
    for t in shown:
        type_lower = (t["type"] or "").lower()
        action = "Bought" if "purchase" in type_lower or "buy" in type_lower else "Sold" if "sale" in type_lower else (t["type"] or "Trade")
        rows_html.append(
            f"""<tr style="border-bottom:1px solid #1f2937">
  <td style="padding:8px 6px;color:#fff;font-weight:600">{t['ticker']}</td>
  <td style="padding:8px 6px;color:#e5e7eb">{t['member']} <span style="color:#9ca3af;font-size:12px">({t['chamber']})</span></td>
  <td style="padding:8px 6px;color:#e5e7eb">{action}</td>
  <td style="padding:8px 6px;color:#9ca3af">{t['amount']}</td>
  <td style="padding:8px 6px;color:#9ca3af;white-space:nowrap">{t['transactionDate']}</td>
</tr>"""
        )
        lines_text.append(
            f"- {t['ticker']}: {t['member']} ({t['chamber']}) {action} {t['amount']} on {t['transactionDate']}, disclosed {t['disclosureDate']}"
        )

    more_note_html = ""
    more_note_text = ""
    if len(trades) > MAX_ROWS_IN_EMAIL:
        remaining = len(trades) - MAX_ROWS_IN_EMAIL
        more_note_html = (
            f'<p style="color:#9ca3af;font-size:13px">+ {remaining} more -- see the full feed at '
            f'<a href="{site}/congress-stock-trades" style="color:#fbbf24">quantengines.com/congress-stock-trades</a>.</p>'
        )
        more_note_text = f"\n+ {remaining} more -- see {site}/congress-stock-trades\n"

    html = f"""<div style="font-family:Arial,sans-serif;max-width:640px;margin:0 auto;line-height:1.6;color:#e5e7eb;background:#0b1020;padding:24px;border-radius:8px">
  <h1 style="font-size:20px;margin:0 0 12px;color:#fff">New congressional trade disclosures</h1>
  <p style="color:#9ca3af;font-size:13px;margin:0 0 16px">
    Your {cadence_word} digest, based on STOCK Act disclosures as processed by Financial Modeling Prep --
    typically same-day to next-day after a member files, not real-time. Members themselves have up to 45
    days after a trade to file in the first place, and no service (ours included) can see a disclosure
    before it's filed.
  </p>
  <table style="width:100%;border-collapse:collapse;font-size:13px">
    <thead>
      <tr style="text-align:left;color:#9ca3af;border-bottom:1px solid #1f2937">
        <th style="padding:6px">Ticker</th><th style="padding:6px">Member</th><th style="padding:6px">Action</th><th style="padding:6px">Amount</th><th style="padding:6px">Traded</th>
      </tr>
    </thead>
    <tbody>{''.join(rows_html)}</tbody>
  </table>
  {more_note_html}
  <p style="margin-top:24px;padding-top:16px;border-top:1px solid #1f2937;font-size:12px;color:#9ca3af">
    You're receiving this because you saved alert filters at quantengines.com/congress-alerts.
    <a href="{manage_url}" style="color:#9ca3af;text-decoration:underline">Manage your filters or unsubscribe</a>.
  </p>
</div>"""

    text = (
        "New congressional trade disclosures\n"
        f"(Your {cadence_word} digest -- same-day-to-next-day after filing, not real-time. "
        "Members have up to 45 days to file after a trade.)\n\n"
        + "\n".join(lines_text)
        + more_note_text
        + f"\n\nManage your filters or unsubscribe: {manage_url}\n"
    )

    return subject, html, text


def send_email(api_key: str, to_email: str, subject: str, html: str, text: str) -> bool:
    from_addr = env("RESEND_FROM") or f"QuantEngines Congress Alerts <alerts@{env('EMAIL_DOMAIN', 'quantengines.com')}>"
    try:
        res = requests.post(
            RESEND_API,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"from": from_addr, "to": [to_email], "subject": subject, "html": html, "text": text},
            timeout=RESEND_TIMEOUT,
        )
    except Exception as exc:
        print(f"[congress-alerts-digest] Resend request failed for {to_email}: {exc}", file=sys.stderr)
        return False
    if res.ok:
        return True
    print(f"[congress-alerts-digest] Resend rejected send to {to_email}: {res.status_code} {res.text[:200]}", file=sys.stderr)
    return False


def main() -> None:
    supabase_url = env("SUPABASE_URL", required=True).rstrip("/")
    service_key = env("SUPABASE_SERVICE_ROLE_KEY", required=True)
    fmp_key = env("FMP_API_KEY", required=True)
    resend_key = env("RESEND_API_KEY", required=True)

    trades = fetch_fmp_trades(fmp_key)
    if not trades:
        print("[congress-alerts-digest] No trades returned from FMP this run -- nothing to check subscribers against.")
        return
    print(f"[congress-alerts-digest] Fetched {len(trades)} trades from FMP.")

    try:
        subscribers = fetch_active_subscribers(supabase_url, service_key)
        filters_by_subscriber = fetch_all_filters(supabase_url, service_key)
    except Exception as exc:
        print(f"[congress-alerts-digest] Failed to load subscribers/filters from Supabase: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"[congress-alerts-digest] {len(subscribers)} active subscribers.")

    now = datetime.now(timezone.utc)
    sent = 0
    skipped_cadence = 0
    errors = 0

    for sub in subscribers:
        try:
            tier = sub.get("tier", "free")
            last_sent_raw = sub.get("last_digest_sent_at")
            try:
                last_sent = datetime.fromisoformat(last_sent_raw.replace("Z", "+00:00")) if last_sent_raw else now
            except Exception:
                last_sent = now

            if tier != "pro" and (now - last_sent).days < FREE_DIGEST_MIN_DAYS:
                skipped_cadence += 1
                continue

            # Date-only cursor comparison, matching the daily-batch nature of
            # the underlying FMP feed -- see the schema comment in
            # frontend/supabase/congress_alerts.sql for why a finer-grained
            # timestamp comparison wouldn't buy any real freshness.
            cursor_date = last_sent.astimezone(timezone.utc).date()
            subscriber_filters = filters_by_subscriber.get(sub["id"], [])

            matches = [
                t
                for t in trades
                if (d := parse_date(t["disclosureDate"])) is not None
                and d > cursor_date
                and trade_matches(t, subscriber_filters)
            ]
            matches.sort(key=lambda t: t["transactionDate"], reverse=True)

            if matches:
                subject, html, text = build_digest_email(matches, sub["manage_token"], tier)
                if send_email(resend_key, sub["email"], subject, html, text):
                    sent += 1
                    print(f"[congress-alerts-digest] sent {len(matches)}-trade digest to {sub['email']} ({tier})")
                    time.sleep(0.3)  # gentle on Resend's rate limit across a batch send
                else:
                    errors += 1
                    # Don't advance the cursor on a failed send -- these trades
                    # should be retried (or included) next run instead of
                    # silently dropped.
                    continue

            update_last_sent(supabase_url, service_key, sub["id"], now)
        except Exception as exc:
            errors += 1
            print(f"[congress-alerts-digest] Unexpected error processing subscriber {sub.get('id')}: {exc}", file=sys.stderr)
            continue

    print(
        f"[congress-alerts-digest] Done. Sent {sent} digests, "
        f"{skipped_cadence} free subscribers not yet due, {errors} errors."
    )
    if errors > 0 and sent == 0 and len(subscribers) > 0:
        # Everything failed -- surface this as a workflow failure rather than
        # a quiet, misleadingly-successful exit.
        sys.exit(1)


if __name__ == "__main__":
    main()
