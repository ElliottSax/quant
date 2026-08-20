#!/usr/bin/env python3
"""Cross-sectional fundamental signals from SEC XBRL `frames`, for the whole US market.

    python -m pipeline.edgar_fundamentals --out ../frontend/public/data/edgar-screener.json

Why this source: the `frames` API returns one XBRL fact for EVERY filer in a period in a
single request — ~6,300 companies' total assets in one 800 KB call. That makes a
cross-sectional screen possible with a handful of requests and no vendor at all. SEC data
is public domain, so unlike every free price API this can be published on a commercial
site without a licence problem.

Three signals are computed, each a documented and independently replicated accounting
anomaly, and each computable from EDGAR alone with no price data:

  asset_growth   Assets_t / Assets_{t-1} - 1
                 Cooper, Gulen & Schill (2008), "Asset Growth and the Cross-Section of
                 Stock Returns". Firms that expand their balance sheets fastest have
                 historically gone on to underperform.

  accruals       (NetIncome - OperatingCashFlow) / average total assets
                 Sloan (1996), "Do Stock Prices Fully Reflect Information in Accruals and
                 Cash Flows About Future Earnings?". Earnings that are not backed by cash
                 have historically mean-reverted.

  net_issuance   SharesIssued_t / SharesIssued_{t-1} - 1
                 Pontiff & Woodgate (2008). Firms issuing shares have historically
                 underperformed those buying them back.

WHAT THIS IS NOT: `frames` returns each company's MOST RECENTLY REPORTED value for a
period, so restatements overwrite the original figure. The series is therefore NOT
point-in-time and must not be used to backtest — doing so leaks information that was not
available on the date being tested. It is a screen of what the filings say now. That
caveat is exported in the artefact and rendered on the page, because it is the single
most important thing to know about this dataset and it is routinely ignored.

Nothing is inferred or filled in. A company missing any input for a signal gets null for
that signal, and the count of companies dropped at each stage is recorded in the artefact
so the coverage is auditable rather than asserted.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# SEC requires a descriptive User-Agent with contact details. The default urllib agent is
# blocked outright, and the rate limit (10 req/s) is enforced by IP.
UA = "QuantEngines/1.0 (https://quantengines.com; elliottsaxton@gmail.com)"
FRAMES = "https://data.sec.gov/api/xbrl/frames/us-gaap/{tag}/{unit}/{period}.json"
TICKERS = "https://www.sec.gov/files/company_tickers.json"

# Well below the published 10 req/s ceiling. This job makes fewer than a dozen requests,
# so there is nothing to gain from running close to the limit.
REQUEST_INTERVAL_S = 0.5

_last_request = 0.0


def fetch(url: str) -> dict | list:
    global _last_request
    wait = REQUEST_INTERVAL_S - (time.time() - _last_request)
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip, deflate"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                _last_request = time.time()
                raw = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    import gzip
                    raw = gzip.decompress(raw)
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 2:
                time.sleep(2 ** attempt * 2)
                continue
            raise
    raise RuntimeError("unreachable")


def frame(tag: str, unit: str, period: str) -> dict[int, dict]:
    """CIK -> {val, end, start?, name} for one XBRL concept in one period.

    The dates are kept, not discarded. A `CY2024Q4I` frame does not hold one common
    balance-sheet date: it holds each filer's period end that falls in (or near) calendar
    Q4, which in practice spans roughly October to January. Whether a company's annual
    flow window lines up with those balance-sheet dates is measurable from these fields,
    and is measured below rather than assumed.
    """
    d = fetch(FRAMES.format(tag=tag, unit=unit, period=period))
    out = {}
    for row in d["data"]:  # type: ignore[index]
        out[row["cik"]] = {
            "val": float(row["val"]),
            "end": row["end"],
            "start": row.get("start"),
            "name": row["entityName"].strip(),
        }
    return out


def days_between(a: str, b: str) -> int:
    fmt = "%Y-%m-%d"
    return abs((datetime.strptime(a, fmt) - datetime.strptime(b, fmt)).days)


def safe_div(num: float, den: float) -> float | None:
    """Ratios are only reported where the denominator is meaningfully non-zero.

    A near-zero denominator produces an enormous ratio that looks like a signal and is
    an artefact of the accounting, so it is dropped rather than published.
    """
    if den is None or num is None or abs(den) < 1.0:
        return None
    return num / den


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--year", type=int, default=2024, help="Fiscal year t (compared against t-1)")
    ap.add_argument("--min-assets", type=float, default=100e6,
                    help="Exclude filers below this total-assets figure. Shell companies and "
                         "micro-caps dominate the extremes of every ratio purely through small "
                         "denominators; the cut and the count dropped are both recorded.")
    ap.add_argument("--match-tolerance-days", type=int, default=21,
                    help="How far a balance-sheet date may sit from the fiscal year end it is "
                         "matched to. Filers report a few days either side of a quarter end, so "
                         "some slack is needed; beyond this the two are different periods and "
                         "the company is dropped rather than mismatched.")
    args = ap.parse_args()

    y, p = args.year, args.year - 1
    cur_i, prev_i = f"CY{y}Q4I", f"CY{p}Q4I"   # instantaneous (balance sheet), for provenance
    cur_d = f"CY{y}"                            # duration (income / cash flow)

    print(f"Fetching XBRL frames for FY{y} vs FY{p} ...")
    ni_t = frame("NetIncomeLoss", "USD", cur_d)
    cfo_t = frame("NetCashProvidedByUsedInOperatingActivities", "USD", cur_d)

    # Every calendar quarter of both years, so each company's balance sheet can be matched
    # to its OWN fiscal year end rather than to calendar Q4. Without this a
    # September-year-end filer like Apple gets an annual flow divided by a December
    # balance sheet -- a denominator spanning a different twelve months than the
    # numerator. The extra requests are cheap; the SEC rate limit has ample room.
    #
    # Collected as per-CIK LISTS, not dicts: a company appears in several quarters and the
    # point is to choose among them, not to let the last one overwrite the rest.
    assets_hist: dict[int, list[dict]] = {}
    shares_hist: dict[int, list[dict]] = {}
    for year in (p - 1, p, y):
        for q in (1, 2, 3, 4):
            for cik, rec in frame("Assets", "USD", f"CY{year}Q{q}I").items():
                assets_hist.setdefault(cik, []).append(rec)
            for cik, rec in frame("CommonStockSharesIssued", "shares", f"CY{year}Q{q}I").items():
                shares_hist.setdefault(cik, []).append(rec)

    print(f"  netincome={len(ni_t):,}  cfo={len(cfo_t):,}")
    print(f"  quarterly history: {len(assets_hist):,} CIKs across 12 quarters "
          f"({sum(len(v) for v in assets_hist.values()):,} balance sheets)")

    tick_raw = fetch(TICKERS)
    tickers = {int(v["cik_str"]): v["ticker"] for v in tick_raw.values()}  # type: ignore[union-attr]
    print(f"  ticker map: {len(tickers):,} CIKs")

    def nearest(recs: list[dict] | None, target: str, tol_days: int) -> dict | None:
        """The record whose period end is closest to `target`, if within `tol_days`.

        Returns None rather than the closest-available when nothing is close enough — a
        balance sheet six months from the date wanted is not a substitute for the one
        wanted, and silently substituting it is how a screener starts comparing two
        different things.
        """
        if not recs:
            return None
        best = min(recs, key=lambda r: days_between(r["end"], target))
        return best if days_between(best["end"], target) <= tol_days else None

    dropped = {"no_flows": 0, "flow_windows_differ": 0, "no_fye_balance_sheet": 0,
               "no_prior_balance_sheet": 0, "below_min_assets": 0, "no_ticker": 0,
               "nonpositive_assets": 0}
    rows = []

    for cik in sorted(ni_t):
        ni, cfo = ni_t.get(cik), cfo_t.get(cik)
        if ni is None or cfo is None or ni.get("start") is None:
            dropped["no_flows"] += 1
            continue
        # Their difference is only an accrual if both flows cover the same window.
        if ni["start"] != cfo["start"] or ni["end"] != cfo["end"]:
            dropped["flow_windows_differ"] += 1
            continue

        fye = ni["end"]                       # this company's own fiscal year end
        prior_fye = ni["start"]               # and the day its fiscal year opened
        at = nearest(assets_hist.get(cik), fye, args.match_tolerance_days)
        ap = nearest(assets_hist.get(cik), prior_fye, args.match_tolerance_days)
        if at is None:
            dropped["no_fye_balance_sheet"] += 1
            continue
        if ap is None:
            dropped["no_prior_balance_sheet"] += 1
            continue

        a_t, a_p = at["val"], ap["val"]
        if a_t <= 0 or a_p <= 0:
            dropped["nonpositive_assets"] += 1
            continue
        if a_t < args.min_assets:
            dropped["below_min_assets"] += 1
            continue
        tk = tickers.get(cik)
        if tk is None:
            # No ticker means it does not trade publicly under a symbol (many filers are
            # bond-only issuers or subsidiaries). A screener row without a symbol is not
            # actionable, so it is excluded and counted.
            dropped["no_ticker"] += 1
            continue

        s_t = nearest(shares_hist.get(cik), fye, args.match_tolerance_days)
        s_p = nearest(shares_hist.get(cik), prior_fye, args.match_tolerance_days)

        # Rounded on the way out: these are ratios displayed to two decimal places, and
        # full float precision would triple the artefact for digits nobody reads.
        def r5(v: float | None) -> float | None:
            return None if v is None else round(v, 5)

        rows.append({
            "cik": cik,
            "ticker": tk,
            "name": at["name"],
            "assets_musd": round(a_t / 1e6),
            "fy_start": prior_fye,
            "fy_end": fye,
            "asset_growth": r5(safe_div(a_t - a_p, a_p)),
            "accruals": r5(safe_div(ni["val"] - cfo["val"], (a_t + a_p) / 2)),
            "net_issuance": r5(safe_div(s_t["val"] - s_p["val"], s_p["val"])
                               if s_t is not None and s_p is not None else None),
        })

    coverage = {k: sum(1 for r in rows if r[k] is not None)
                for k in ("asset_growth", "accruals", "net_issuance")}

    # Percentile rank within the screened universe, computed per signal over the
    # companies that actually have that signal. Ranking against a different denominator
    # per signal is the honest option: imputing a missing value to keep one denominator
    # would invent data.
    for key in ("asset_growth", "accruals", "net_issuance"):
        vals = sorted(r[key] for r in rows if r[key] is not None)
        n = len(vals)
        for r in rows:
            v = r[key]
            if v is None:
                r[key + "_pct"] = None
            else:
                import bisect
                r[key + "_pct"] = round(100.0 * bisect.bisect_left(vals, v) / max(n - 1, 1), 1)

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fiscal_year": y,
        "compared_against": p,
        "method": {
            "flow_period": cur_d,
            "balance_sheets_searched": [f"CY{yr}Q{q}I" for yr in (p - 1, p, y) for q in (1, 2, 3, 4)],
            "matching":
                "Each company's annual flow window (from the NetIncomeLoss frame) defines its own "
                "fiscal year. The balance sheets used are the ones whose period ends fall closest "
                f"to that window's start and end, within {args.match_tolerance_days} days. This "
                "is why a September-year-end filer is measured on September balance sheets rather "
                "than December ones, and why the accrual denominator covers the same twelve "
                "months as its numerator.",
        },
        "source": {
            "name": "SEC EDGAR XBRL frames API",
            "urls": [
                FRAMES.format(tag="Assets", unit="USD", period=cur_i),
                FRAMES.format(tag="NetIncomeLoss", unit="USD", period=cur_d),
                FRAMES.format(tag="NetCashProvidedByUsedInOperatingActivities", unit="USD", period=cur_d),
                FRAMES.format(tag="CommonStockSharesIssued", unit="shares", period=cur_i),
                TICKERS,
            ],
            "licence": "US government work, public domain (17 U.S.C. 105).",
        },
        "universe": {
            "filers_reporting_annual_flows": len(ni_t),
            "screened": len(rows),
            "dropped": dropped,
            "min_assets_usd": args.min_assets,
        },
        "signal_coverage": coverage,
        "caveats": {
            "not_point_in_time":
                "The frames API returns each company's most recently reported value for a "
                "period, so restatements overwrite the figure originally filed. These series "
                "are therefore not point-in-time and must not be used to backtest — a "
                "backtest would use numbers that were not knowable on the test date.",
            "fiscal_alignment":
                "Companies are measured on their own fiscal years, not on a common date. A "
                "September-year-end filer's figures cover October to September; a December "
                "filer's cover the calendar year. Every ratio is therefore internally "
                "consistent, but two companies in the same ranking may be describing "
                "twelve-month windows that overlap only partly.",
            "no_industry_adjustment":
                "Financials and REITs carry balance sheets that are not comparable to operating "
                "companies on these ratios. No industry classification is applied, because SIC "
                "codes are not in the frames response; the ranks are raw cross-sectional ranks.",
            "anomalies_are_historical":
                "Every signal here is a published historical association, measured on past "
                "decades of data by its authors. None is a prediction, and several documented "
                "anomalies have weakened or vanished since publication.",
        },
        "signals": {
            "asset_growth": {
                "label": "Asset growth",
                "formula": "Assets_t / Assets_{t-1} − 1",
                "citation": "Cooper, Gulen & Schill (2008), Journal of Finance 63(4)",
                "direction": "Historically, LOW asset growth was associated with higher subsequent returns.",
            },
            "accruals": {
                "label": "Accruals",
                "formula": "(Net income − Operating cash flow) / average total assets",
                "citation": "Sloan (1996), The Accounting Review 71(3)",
                "direction": "Historically, LOW accruals were associated with higher subsequent returns.",
            },
            "net_issuance": {
                "label": "Net share issuance",
                "formula": "Shares issued_t / Shares issued_{t-1} − 1",
                "citation": "Pontiff & Woodgate (2008), Journal of Finance 63(2)",
                "direction": "Historically, share repurchasers outperformed issuers.",
            },
        },
        "rows": sorted(rows, key=lambda r: -r["assets_musd"]),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    size = args.out.stat().st_size
    print(f"\n{len(rows):,} companies screened -> {args.out} ({size/1e6:.2f} MB)")
    print(f"  coverage: " + ", ".join(f"{k}={v:,}" for k, v in coverage.items()))
    print(f"  dropped:  " + ", ".join(f"{k}={v:,}" for k, v in dropped.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
