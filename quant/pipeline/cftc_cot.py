#!/usr/bin/env python3
"""CFTC Commitments of Traders positioning, z-scored against each market's own history.

    python -m pipeline.cftc_cot --out ../frontend/public/data/cot-positioning.json

Source: the CFTC's own Socrata endpoint for the legacy futures-only report. CFTC data is
a US government work, so unlike every free price API it can be republished on a
commercial site.

The raw COT report is published as a wall of ~130 columns and is close to unreadable as
released. What people actually want from it is one thing: is a group unusually long or
short RIGHT NOW compared with how it is normally positioned. That requires normalising
(a 300,000-contract net position means nothing without knowing the market's size) and
then scoring against the market's own history. Both steps are done here:

  net_pct = (long - short) / open_interest      per group, per week
  z       = (net_pct - mean) / stdev            over a trailing window of that market

Two groups are tracked, and the distinction is the whole point of the report:

  Commercial     hedgers -- producers, processors, users of the physical commodity.
                 They are typically net short a commodity they produce, and their
                 position is driven by hedging need, not by a market view.
  Non-commercial speculators -- managed money and other large traders taking a view.

They are near-mirror images by construction, because every long has a short. A high
z-score therefore says positioning is stretched relative to normal, and nothing more:
it is a description of who holds what, not a signal, and the report is published with a
three-day lag on Friday for the preceding Tuesday.

Nothing is smoothed or filled. A market with too little history for a stable z-score is
reported with its actual observation count rather than given a score that looks precise.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

UA = "QuantEngines/1.0 (https://quantengines.com; elliottsaxton@gmail.com)"
ENDPOINT = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"

# The contracts people actually look up, keyed by CFTC CONTRACT MARKET CODE rather than
# by display name. That matters: the name is not stable. "E-MINI S&P 500 - CHICAGO
# MERCANTILE EXCHANGE" exists only from 2022-02-08, because the same contract was
# previously filed as "E-MINI S&P 500 STOCK INDEX - CHICAGO MERCANTILE EXCHANGE" and
# before that under INTERNATIONAL MONETARY MARKET. Keying on the name silently truncated
# the S&P, Nasdaq and copper histories to ~4 years while gold and yen got 10, so their
# z-scores were being measured against different definitions of "normal". The code
# 13874A spans all three names, 1997 to today.
#
# The code is not perfectly stable either, so each was verified against its actual date
# range rather than assumed: corn trades under 002602 (1998 to today), while 002601 --
# which a name-based lookup returns first, since both filed as 'CORN - CHICAGO BOARD OF
# TRADE' -- was retired in 1997 and yields an empty series.
MARKETS = [
    ("13874A", "S&P 500 (E-mini)", "Equity index"),
    ("209742", "Nasdaq 100 (mini)", "Equity index"),
    ("088691", "Gold", "Metals"),
    ("084691", "Silver", "Metals"),
    ("085692", "Copper", "Metals"),
    ("067411", "Crude oil (WTI)", "Energy"),
    ("099741", "Euro FX", "Currencies"),
    ("097741", "Japanese yen", "Currencies"),
    ("133741", "Bitcoin", "Crypto"),
    ("002602", "Corn", "Agriculture"),
    ("001602", "Wheat (SRW)", "Agriculture"),
]

FIELDS = [
    "report_date_as_yyyy_mm_dd", "open_interest_all", "market_and_exchange_names",
    "comm_positions_long_all", "comm_positions_short_all",
    "noncomm_positions_long_all", "noncomm_positions_short_all",
]

_last = 0.0


def fetch(params: dict) -> list[dict]:
    global _last
    wait = 0.4 - (time.time() - _last)
    if wait > 0:
        time.sleep(wait)
    url = f"{ENDPOINT}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                _last = time.time()
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 2:
                time.sleep(2 ** attempt * 2)
                continue
            raise
    return []


def history(code: str, since: str) -> list[dict]:
    rows = fetch({
        "$select": ",".join(FIELDS),
        "$where": f"cftc_contract_market_code = '{code}' "
                  f"AND report_date_as_yyyy_mm_dd > '{since}'",
        "$order": "report_date_as_yyyy_mm_dd ASC",
        "$limit": "5000",
    })
    out = []
    for r in rows:
        try:
            oi = float(r["open_interest_all"])
            if oi <= 0:
                continue          # a zero open interest makes every ratio meaningless
            out.append({
                "date": r["report_date_as_yyyy_mm_dd"][:10],
                "name": r.get("market_and_exchange_names", ""),
                "oi": oi,
                "comm_net": float(r["comm_positions_long_all"]) - float(r["comm_positions_short_all"]),
                "noncomm_net": float(r["noncomm_positions_long_all"]) - float(r["noncomm_positions_short_all"]),
            })
        except (KeyError, TypeError, ValueError):
            continue              # an incomplete week is skipped, never interpolated
    return out


def zscore(series: list[float]) -> float | None:
    """Z-score of the LAST value against the rest of the series."""
    if len(series) < 30:
        return None
    body = series[:-1]
    sd = statistics.pstdev(body)
    if sd < 1e-9:
        return None               # a flat history has no meaningful scale
    return (series[-1] - statistics.fmean(body)) / sd


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--since", default="2005-01-01",
                    help="Earliest report date to pull. The z-score window is the whole "
                         "pulled history, so this sets what 'normal' means.")
    ap.add_argument("--min-weeks", type=int, default=30,
                    help="Weeks of history required before a z-score is reported at all. "
                         "Below this the score is omitted rather than shown with false "
                         "precision, and the observation count is published instead.")
    args = ap.parse_args()

    print(f"Fetching CFTC COT since {args.since} ...")
    markets = []
    for code, label, group in MARKETS:
        h = history(code, args.since)
        if not h:
            print(f"  {label:<20} no rows")
            markets.append({"code": code, "label": label, "group": group,
                            "weeks": 0, "error": "no rows returned"})
            continue

        comm_pct = [r["comm_net"] / r["oi"] for r in h]
        spec_pct = [r["noncomm_net"] / r["oi"] for r in h]
        latest = h[-1]

        entry = {
            "code": code, "label": label, "group": group,
            "weeks": len(h),
            # Every display name this contract has filed under in the window, so a reader
            # can see the series was stitched across renames rather than wonder about it.
            "filed_as": sorted({r["name"] for r in h if r["name"]}),
            "first": h[0]["date"], "last": latest["date"],
            "open_interest": int(latest["oi"]),
            "commercial_net": int(latest["comm_net"]),
            "noncommercial_net": int(latest["noncomm_net"]),
            "commercial_net_pct": round(comm_pct[-1] * 100, 2),
            "noncommercial_net_pct": round(spec_pct[-1] * 100, 2),
            "commercial_z": None, "noncommercial_z": None,
            "history": [[r["date"], round(c * 100, 2), round(s * 100, 2)]
                        for r, c, s in zip(h, comm_pct, spec_pct)],
        }
        if len(h) >= args.min_weeks:
            cz, sz = zscore(comm_pct), zscore(spec_pct)
            entry["commercial_z"] = None if cz is None else round(cz, 2)
            entry["noncommercial_z"] = None if sz is None else round(sz, 2)

        markets.append(entry)
        print(f"  {label:<20} {len(h):>4} weeks  {h[0]['date']}..{latest['date']}  "
              f"spec net {spec_pct[-1]*100:+6.2f}% (z={entry['noncommercial_z']})")

    ok = [m for m in markets if m.get("weeks")]
    if not ok:
        raise SystemExit("no market returned data; refusing to write an empty artefact")

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": {
            "name": "US Commodity Futures Trading Commission — Commitments of Traders "
                    "(legacy, futures only)",
            "url": ENDPOINT,
            "licence": "US government work, public domain (17 U.S.C. 105).",
            "cadence": "Published each Friday at 15:30 ET for positions held the preceding "
                       "Tuesday, so the newest figure is already three days old on release.",
        },
        "method": {
            "normalisation":
                "Net position (long minus short) divided by that week's total open interest, "
                "so a market's own growth does not read as a positioning change.",
            "z_score":
                "The latest normalised net position scored against the mean and population "
                "standard deviation of every earlier week in the pulled history. It measures "
                "how unusual current positioning is FOR THAT MARKET, not across markets.",
            "min_weeks": args.min_weeks,
            "no_interpolation":
                "Weeks with missing fields or zero open interest are skipped, never filled.",
        },
        "caveats": {
            "not_a_signal":
                "Stretched positioning is a description of who holds what, not a forecast. "
                "Extremes can persist for months and have no reliable turning-point timing.",
            "mirror_image":
                "Commercial and non-commercial nets move nearly opposite by construction: "
                "every long is somebody's short. Treating them as two independent pieces of "
                "evidence double-counts one fact.",
            "commercials_are_hedgers":
                "A commercial short is usually a producer hedging output, not a bearish view. "
                "Reading commercial positioning as a market opinion misreads the category.",
            "legacy_report":
                "This is the legacy futures-only report. The disaggregated and financial "
                "(TFF) reports split these categories further and will not match line for line.",
        },
        "markets": markets,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print(f"\n{len(ok)}/{len(MARKETS)} markets -> {args.out} "
          f"({args.out.stat().st_size/1e6:.2f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
