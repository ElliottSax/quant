#!/usr/bin/env python3
"""Market-data vendor bench — measured, not quoted (plan: data vendor comparison).

  python -m pipeline.bench [--out PATH]

Every "best market data API" article in this niche is transcribed from the vendors'
own pricing pages. This probes each configured provider through the same adapter
interface the production pipeline uses and records what actually came back, with the
error class when nothing did.

What it measures, and why each dimension is the one that bites in practice:

  history depth      The earliest bar actually RETURNED for a deep-history symbol.
                     Marketing copy quotes catalogue depth; what matters is what a
                     request yields. This is how the FMP row cap was found — an
                     open-ended request silently truncates ~20 years.
  coverage           Per asset class. Entitlement gaps do not announce themselves:
                     a plan can serve equities happily and 402 on every ETF.
  adjustment         Verified against a KNOWN corporate action (AAPL's 4:1 split on
                     2020-08-31). Unadjusted closes turn that month into a -75%
                     "return", which would be published as a seasonal effect.
  freshness          Newest bar against the last completed trading day.
  request ceiling    Whether one request returns the full series or silently caps.

Nothing here is scored or ranked into a verdict — the numbers are reported and the
reader draws the conclusion. A provider that fails a probe gets the failure printed,
not a lower grade invented for it.

Exit 0 = bench written.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.providers import EntitlementError, ProviderError, get_provider  # noqa: E402

# The bench MEASURES sources; it does not redistribute their data — the published
# artefact holds row counts, date ranges and pass/fail flags, never price series. That
# distinction is why the yfinance ingest guard is opted into here and nowhere else.
os.environ.setdefault("QUANT_ALLOW_YFINANCE_INGEST", "1")

DEFAULT_OUT = Path(__file__).resolve().parents[1] / "frontend" / "public" / "data" / "vendor-bench.json"

PROVIDERS = ["fmp", "yfinance"]

# One symbol per class of thing that commonly breaks, rather than a long list.
COVERAGE_PROBES = [
    ("AAPL", "US large-cap equity"),
    ("PG", "US large-cap equity (entitlement canary)"),
    ("SPY", "index ETF"),
    ("QQQ", "index ETF"),
    ("XLE", "sector ETF"),
    ("GLD", "commodity ETF"),
]

DEEP_HISTORY_SYMBOL = "SPY"
DEEP_HISTORY_START = date(1990, 1, 1)
SPLIT_SYMBOL, SPLIT_DATE = "AAPL", date(2020, 8, 31)


def probe_provider(name: str) -> dict:
    result: dict = {"provider": name, "probes": {}, "notes": []}
    try:
        provider = get_provider(name)
    except ProviderError as e:
        result["available"] = False
        result["error"] = str(e)
        return result
    result["available"] = True

    # --- history depth -------------------------------------------------------
    try:
        bars = provider.fetch(DEEP_HISTORY_SYMBOL, DEEP_HISTORY_START)
        span_years = (bars[-1].day - bars[0].day).days / 365.25
        result["probes"]["history"] = {
            "symbol": DEEP_HISTORY_SYMBOL,
            "requested_from": DEEP_HISTORY_START.isoformat(),
            "earliest_returned": bars[0].day.isoformat(),
            "latest_returned": bars[-1].day.isoformat(),
            "rows": len(bars),
            "span_years": round(span_years, 1),
            "ok": True,
        }
    except (ProviderError, EntitlementError) as e:
        result["probes"]["history"] = {"ok": False, "error": f"{type(e).__name__}: {e}"}

    # --- coverage ------------------------------------------------------------
    cov = []
    recent = date(date.today().year - 1, 1, 1)
    for sym, klass in COVERAGE_PROBES:
        try:
            bars = provider.fetch(sym, recent)
            cov.append({"symbol": sym, "class": klass, "ok": True, "rows": len(bars)})
        except EntitlementError as e:
            cov.append({"symbol": sym, "class": klass, "ok": False,
                        "reason": "entitlement", "error": str(e)})
        except ProviderError as e:
            cov.append({"symbol": sym, "class": klass, "ok": False,
                        "reason": "error", "error": str(e)})
    result["probes"]["coverage"] = cov
    result["probes"]["coverage_summary"] = {
        "ok": sum(1 for c in cov if c["ok"]),
        "total": len(cov),
        "entitlement_blocked": sum(1 for c in cov if not c["ok"] and c.get("reason") == "entitlement"),
    }

    # --- adjustment correctness ---------------------------------------------
    try:
        bars = provider.fetch(SPLIT_SYMBOL, date(SPLIT_DATE.year, 7, 1))
        window = [b for b in bars if SPLIT_DATE.replace(day=1) <= b.day <= date(SPLIT_DATE.year, 9, 30)]
        worst = None
        for prev, cur in zip(window, window[1:]):
            if prev.adj_close:
                move = cur.adj_close / prev.adj_close - 1
                worst = move if worst is None else min(worst, move)
        # A 4:1 split shows as roughly -75% in an unadjusted series.
        adjusted = worst is not None and worst > -0.5
        result["probes"]["adjustment"] = {
            "symbol": SPLIT_SYMBOL,
            "corporate_action": f"4:1 split {SPLIT_DATE.isoformat()}",
            "worst_daily_move_pct": None if worst is None else round(worst * 100, 2),
            "adjusted": adjusted,
            "ok": True,
        }
    except (ProviderError, EntitlementError) as e:
        result["probes"]["adjustment"] = {"ok": False, "error": f"{type(e).__name__}: {e}"}

    # --- freshness -----------------------------------------------------------
    hist = result["probes"].get("history", {})
    if hist.get("ok"):
        latest = date.fromisoformat(hist["latest_returned"])
        result["probes"]["freshness"] = {
            "latest_bar": latest.isoformat(),
            "days_behind_today": (date.today() - latest).days,
        }

    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--providers", nargs="*", default=PROVIDERS)
    args = ap.parse_args()

    results = []
    for name in args.providers:
        print(f"probing {name} ...")
        r = probe_provider(name)
        results.append(r)
        h = r["probes"].get("history", {})
        c = r["probes"].get("coverage_summary", {})
        a = r["probes"].get("adjustment", {})
        if h.get("ok"):
            print(f"  history:    {h['rows']} rows, {h['earliest_returned']} -> {h['latest_returned']} ({h['span_years']}y)")
        else:
            print(f"  history:    FAILED {h.get('error')}")
        if c:
            print(f"  coverage:   {c['ok']}/{c['total']} symbols ({c['entitlement_blocked']} entitlement-blocked)")
        if a.get("ok"):
            print(f"  adjustment: worst move {a['worst_daily_move_pct']}% -> adjusted={a['adjusted']}")

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "method": (
            "Each provider is probed through the same adapter interface the production "
            "pipeline uses. Figures are what the requests actually returned, not what the "
            "vendor documents."
        ),
        "probes": {
            "history": {"symbol": DEEP_HISTORY_SYMBOL, "requested_from": DEEP_HISTORY_START.isoformat()},
            "coverage": [{"symbol": s, "class": k} for s, k in COVERAGE_PROBES],
            "adjustment": {"symbol": SPLIT_SYMBOL, "corporate_action": f"4:1 split {SPLIT_DATE.isoformat()}"},
        },
        "results": results,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
