#!/usr/bin/env python3
"""Publish recent price history as a static artefact for the site (plan story 2.1).

  python -m pipeline.export_prices [--years 3] [--out PATH]

Why static rather than an API call: the deployed backend has no historical-price
endpoint at all — only single-ticker spot lookups — so a chart could never be drawn
from it, which is why /charts fell back to invented data for so long. The compute plane
already holds 36 years of adjusted bars, and the architecture wants the serving plane
reading artefacts rather than querying a database, so the history is published here.

Refuses to write unless the last ingest run was clean. Bars are ADJUSTED, matching the
series every published statistic is computed from — mixing adjusted statistics with raw
chart prices would make the two disagree for no visible reason.

Exit 0 = written, 1 = refused.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline import store  # noqa: E402

DEFAULT_OUT = Path(__file__).resolve().parents[1] / "frontend" / "public" / "data" / "prices.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", type=int, default=3)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--allow-unclean", action="store_true")
    args = ap.parse_args()

    con = store.connect()
    last_run = con.execute(
        "SELECT run_id, clean, notes FROM ingest_runs WHERE finished_at IS NOT NULL "
        "ORDER BY finished_at DESC LIMIT 1"
    ).fetchone()
    if not last_run:
        print("refusing to export: no completed ingest run")
        return 1
    if not last_run[1] and not args.allow_unclean:
        print(f"refusing to export: last ingest {last_run[0]} not clean — {last_run[2]}")
        return 1

    cutoff = date.today() - timedelta(days=int(args.years * 365.25))
    provider = con.execute("SELECT any_value(provider) FROM eod_prices").fetchone()[0]

    symbols = [r[0] for r in con.execute(
        "SELECT DISTINCT symbol FROM eod_prices ORDER BY symbol").fetchall()]

    series = {}
    latest = {}
    for sym in symbols:
        rows = con.execute(
            """
            SELECT day, adj_open, adj_high, adj_low, adj_close, volume
              FROM eod_prices WHERE symbol = ? AND day >= ? ORDER BY day
            """, [sym, cutoff]
        ).fetchall()
        if len(rows) < 2:
            # A symbol with no usable window is omitted rather than padded. The page
            # renders what exists; it never invents a series to fill a gap.
            print(f"  skip {sym}: {len(rows)} bar(s) in window")
            continue
        # Compact positional rows keep the artefact small enough to ship in the bundle.
        series[sym] = [
            [str(d), round(o, 4), round(h, 4), round(l, 4), round(c, 4), int(v or 0)]
            for d, o, h, l, c, v in rows
        ]
        prev_close = rows[-2][4]
        last_close = rows[-1][4]
        latest[sym] = {
            "day": str(rows[-1][0]),
            "close": round(last_close, 4),
            "change": round(last_close - prev_close, 4),
            "change_pct": round((last_close / prev_close - 1) * 100, 4) if prev_close else None,
        }

    if not series:
        print("refusing to export: no symbol had a usable window")
        return 1

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "provider": provider,
        "adjusted": True,
        "years": args.years,
        "columns": ["date", "open", "high", "low", "close", "volume"],
        "symbols": sorted(series),
        "latest": latest,
        "series": series,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    total = sum(len(v) for v in series.values())
    size_kb = args.out.stat().st_size / 1024
    print(f"wrote {args.out}")
    print(f"  {len(series)} symbols | {total} bars | {size_kb:.0f} KB | provider {provider}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
