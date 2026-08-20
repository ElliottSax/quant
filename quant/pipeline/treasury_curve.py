#!/usr/bin/env python3
"""Daily Treasury par yield curve, and every inversion episode it contains.

    python -m pipeline.treasury_curve --out ../frontend/public/data/treasury-curve.json

Source: the US Treasury's own daily par yield curve CSV export, one request per year.
Treasury publishes these as a US government work, so unlike every free equity price API
the series can be republished on a commercial site without a licence problem.

The commodity version of this page is a chart of today's curve, which a dozen sites
already have. What is not commonly published is the measured record: every episode in
which the 10-year yield sat below the 2-year (or the 3-month), with its start, end,
duration and deepest point, derived from the daily series rather than recalled from
memory. Inversion dates are widely repeated and widely wrong; these are computed.

An episode is a maximal run of consecutive OBSERVATIONS with a negative spread. Treasury
publishes on business days only, so a run spans weekends and holidays without being
broken by them -- but a genuine multi-day return to positive territory does end an
episode. Brief single-day flickers are common near the zero line, so episodes shorter
than --min-episode-days are recorded separately rather than mixed in with the sustained
ones; both counts are exported.

Nothing is interpolated. A tenor missing on a date (the 20-year was discontinued between
1987 and 1993, the 30-year between 2002 and 2006) yields no spread for that date rather
than a filled-forward one.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

UA = "QuantEngines/1.0 (https://quantengines.com; elliottsaxton@gmail.com)"
CSV_URL = (
    "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
    "daily-treasury-rates.csv/{year}/all"
    "?type=daily_treasury_yield_curve&field_tdr_date_value={year}&page&_format=csv"
)

# The column headings Treasury uses, mapped to the tenor in months. Their CSV has varied
# over the years ("1 Mo" appeared in 2001, "1.5 Month" and "4 Mo" much later), so parsing
# is by header name and missing columns are simply absent rather than an error.
TENORS = {
    "1 Mo": 1, "1.5 Month": 1.5, "2 Mo": 2, "3 Mo": 3, "4 Mo": 4, "6 Mo": 6,
    "1 Yr": 12, "2 Yr": 24, "3 Yr": 36, "5 Yr": 60, "7 Yr": 84,
    "10 Yr": 120, "20 Yr": 240, "30 Yr": 360,
}

SPREADS = {
    "10y2y": ("10 Yr", "2 Yr"),
    "10y3m": ("10 Yr", "3 Mo"),
}


def fetch_year(year: int) -> list[dict]:
    req = urllib.request.Request(CSV_URL.format(year=year), headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                text = r.read().decode("utf-8-sig")
                break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return []
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
    else:
        return []

    rows = []
    for rec in csv.DictReader(io.StringIO(text)):
        raw_date = (rec.get("Date") or "").strip()
        if not raw_date:
            continue
        try:
            d = datetime.strptime(raw_date, "%m/%d/%Y").date()
        except ValueError:
            continue
        yields = {}
        for col, _months in TENORS.items():
            v = (rec.get(col) or "").strip()
            if v in ("", "N/A", "NA"):
                continue          # not published that day -- left absent, never filled
            try:
                yields[col] = float(v)
            except ValueError:
                continue
        if yields:
            rows.append({"date": d.isoformat(), "y": yields})
    return rows


def episodes(series: list[tuple[str, float]], min_days: int) -> tuple[list[dict], list[dict]]:
    """Maximal runs of negative spread, split into sustained and brief.

    `series` must be sorted ascending by date. Runs are over consecutive observations,
    which is what makes weekends and holidays transparent: Treasury simply does not
    publish on those days, and a gap in publication is not a return to positive.
    """
    sustained, brief = [], []
    run: list[tuple[str, float]] = []

    def close(run: list[tuple[str, float]]) -> None:
        if not run:
            return
        start = date.fromisoformat(run[0][0])
        end = date.fromisoformat(run[-1][0])
        deepest = min(run, key=lambda x: x[1])
        ep = {
            "start": run[0][0],
            "end": run[-1][0],
            "trading_days": len(run),
            "calendar_days": (end - start).days + 1,
            "deepest_bp": round(deepest[1] * 100, 1),
            "deepest_on": deepest[0],
        }
        (sustained if ep["calendar_days"] >= min_days else brief).append(ep)

    for d, v in series:
        if v < 0:
            run.append((d, v))
        else:
            close(run)
            run = []
    close(run)
    return sustained, brief


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--start-year", type=int, default=1990)
    ap.add_argument("--min-episode-days", type=int, default=10,
                    help="Calendar days an inversion must persist to count as sustained. "
                         "Shorter runs are kept but reported separately: the spread crosses "
                         "zero repeatedly near the boundary, and counting each crossing as an "
                         "'inversion' inflates the count without adding information.")
    args = ap.parse_args()

    end_year = date.today().year
    print(f"Fetching Treasury daily par yield curve {args.start_year}-{end_year} ...")
    rows: list[dict] = []
    for year in range(args.start_year, end_year + 1):
        got = fetch_year(year)
        rows.extend(got)
        print(f"  {year}: {len(got):>4} observations")
        time.sleep(0.3)

    rows.sort(key=lambda r: r["date"])
    if not rows:
        raise SystemExit("no observations returned; refusing to write an empty artefact")

    # Per-day spreads, only where BOTH legs were published.
    spread_series: dict[str, list[tuple[str, float]]] = {k: [] for k in SPREADS}
    for r in rows:
        for name, (long_leg, short_leg) in SPREADS.items():
            a, b = r["y"].get(long_leg), r["y"].get(short_leg)
            if a is not None and b is not None:
                spread_series[name].append((r["date"], round(a - b, 4)))

    out_spreads = {}
    for name, series in spread_series.items():
        sustained, brief = episodes(series, args.min_episode_days)
        out_spreads[name] = {
            "label": f"{SPREADS[name][0]} minus {SPREADS[name][1]}",
            "observations": len(series),
            "first": series[0][0] if series else None,
            "last": series[-1][0] if series else None,
            "current_bp": round(series[-1][1] * 100, 1) if series else None,
            "inverted_now": bool(series and series[-1][1] < 0),
            "days_inverted": sum(1 for _, v in series if v < 0),
            "sustained_episodes": sustained,
            "brief_episodes_count": len(brief),
            "brief_episodes_days": sum(e["calendar_days"] for e in brief),
        }

    latest = rows[-1]
    curve_today = sorted(
        ({"tenor": k, "months": TENORS[k], "yield": v} for k, v in latest["y"].items()),
        key=lambda x: x["months"],
    )

    # A compact daily history for charting: date plus the two spreads, nothing else.
    history = []
    idx = {name: dict(series) for name, series in spread_series.items()}
    for r in rows:
        d = r["date"]
        history.append([d, idx["10y2y"].get(d), idx["10y3m"].get(d)])

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": {
            "name": "US Department of the Treasury — Daily Treasury Par Yield Curve Rates",
            "url": CSV_URL.format(year=end_year),
            "licence": "US government work, public domain (17 U.S.C. 105).",
            "note": "Par yields, not zero-coupon. Treasury publishes on business days only.",
        },
        "coverage": {
            "first_date": rows[0]["date"],
            "last_date": rows[-1]["date"],
            "observations": len(rows),
            "years_requested": [args.start_year, end_year],
        },
        "method": {
            "episode_definition":
                "A maximal run of consecutive published observations with a negative spread. "
                "Weekends and holidays are not publication days and so do not break a run; a "
                "genuine return to a positive spread does.",
            "min_episode_calendar_days": args.min_episode_days,
            "no_interpolation":
                "Where either leg of a spread was not published on a date, that date has no "
                "spread rather than a carried-forward one.",
        },
        "latest": {"date": latest["date"], "curve": curve_today},
        "spreads": out_spreads,
        "history": history,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print(f"\n{len(rows):,} observations {rows[0]['date']} -> {rows[-1]['date']} "
          f"({args.out.stat().st_size/1e6:.2f} MB)")
    for name, s in out_spreads.items():
        print(f"  {name}: now {s['current_bp']:+.1f}bp, inverted={s['inverted_now']}, "
              f"{len(s['sustained_episodes'])} sustained episodes, "
              f"{s['days_inverted']:,} inverted days of {s['observations']:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
