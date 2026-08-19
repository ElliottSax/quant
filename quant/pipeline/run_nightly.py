#!/usr/bin/env python3
"""Nightly EOD ingest (plan story 1.2).

  python -m pipeline.run_nightly [--universe FILE] [--start YYYY-MM-DD] [--full]

Exit code is the contract: 0 = clean night, 1 = not clean. The Task Scheduler job and
any downstream publish step must gate on it. A night that is not clean must NOT publish
— stale or partial data rendered as current is the same class of error as fabricating it.

"Clean" is defined as the plan specifies, with the staleness test as a floor:
  * every requested symbol returned usable rows, AND
  * EVERY requested symbol's newest day is no older than the last completed trading day
    (per symbol, not a single global maximum — one current symbol must not vouch for a
    stale one), AND
  * the store contains no interior gap wider than a long weekend.

Weekends and US market holidays are accounted for; a run on a Saturday expects Friday.
The floor (rather than equality) exists because vendors publish the current session's
bar intraday — the store being one day ahead is normal, being behind never is.
"""

from __future__ import annotations

import argparse
import sys
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline import store  # noqa: E402
from pipeline.providers import EntitlementError, ProviderError, get_provider  # noqa: E402

DEFAULT_UNIVERSE = Path(__file__).resolve().parent / "universe.txt"

# How far back the nightly interior-gap scan looks. Covers any plausible missed-run
# outage while staying clear of genuine historical market closures.
GAP_SCAN_DAYS = 120

# US market holidays that fall on weekdays. Kept explicit rather than pulling a
# calendar dependency; extend yearly. An unlisted holiday makes the run look unclean,
# which fails loudly instead of silently accepting stale data — the safe direction.
HOLIDAYS_2026 = {
    date(2026, 1, 1), date(2026, 1, 19), date(2026, 2, 16), date(2026, 4, 3),
    date(2026, 5, 25), date(2026, 6, 19), date(2026, 7, 3), date(2026, 9, 7),
    date(2026, 11, 26), date(2026, 12, 25),
}


def last_trading_day(today: date | None = None) -> date:
    """The most recent trading day strictly before `today`.

    This is a staleness FLOOR, not an equality target. Vendors legitimately publish
    the current session's bar intraday, so the store may be one day ahead of this;
    requiring equality would fail every run made after the close. What must never
    pass is data older than this — that is stale data being served as current.
    """
    d = (today or date.today()) - timedelta(days=1)
    while d.weekday() >= 5 or d in HOLIDAYS_2026:
        d -= timedelta(days=1)
    return d


def load_universe(path: Path) -> list[str]:
    if not path.exists():
        raise SystemExit(f"universe file not found: {path}")
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            out.append(line.upper())
    if not out:
        raise SystemExit(f"universe file is empty: {path}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--universe", type=Path, default=DEFAULT_UNIVERSE)
    ap.add_argument("--start", type=date.fromisoformat, default=date(1990, 1, 1),
                    help="earliest day to request; vendors cap this in practice")
    ap.add_argument("--db", type=Path, default=None)
    ap.add_argument("--full", action="store_true",
                    help="request full history rather than a recent window")
    args = ap.parse_args()

    symbols = load_universe(args.universe)
    start = args.start if args.full else max(args.start, date.today() - timedelta(days=10))

    run_id = f"{datetime.now().strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:6]}"
    provider = get_provider()
    con = store.connect(args.db)
    store.start_run(con, run_id, provider.name, len(symbols))

    print(f"run {run_id} | provider={provider.name} | {len(symbols)} symbols | from {start}")

    ok, failed, rows_written = 0, [], 0
    for sym in symbols:
        try:
            bars = provider.fetch(sym, start)
            rows_written += store.write_bars(con, bars, provider.name, run_id)
            ok += 1
            print(f"  {sym:6} {len(bars):>5} bars  {bars[0].day} -> {bars[-1].day}")
        except EntitlementError as e:
            failed.append((sym, f"ENTITLEMENT: {e}"))
            print(f"  {sym:6} NOT COVERED BY PLAN — {e}")
        except ProviderError as e:
            failed.append((sym, str(e)))
            print(f"  {sym:6} FAILED — {e}")

    expected = last_trading_day()
    notes = []
    if failed:
        notes.append(f"{len(failed)} symbol(s) failed: " + "; ".join(f"{s}({m})" for s, m in failed[:8]))

    # Staleness is PER SYMBOL. A single global MAX(day) passes as long as any one symbol
    # is current, so a vendor that quietly stops updating one ticker (delisting, ticker
    # change, coverage drop) returns HTTP 200 with old bars, raises nothing, and the night
    # is declared clean while a month-old series feeds the verdicts.
    per_symbol = dict(con.execute(
        "SELECT symbol, MAX(day) FROM eod_prices WHERE symbol IN "
        "(SELECT UNNEST(?)) GROUP BY symbol", [symbols]
    ).fetchall())
    stale = {s: per_symbol.get(s) for s in symbols if per_symbol.get(s) is None or per_symbol[s] < expected}
    if stale:
        notes.append("stale symbols: " + "; ".join(f"{s}(newest {d})" for s, d in list(stale.items())[:8]))

    # Interior gaps. Incremental runs only request the last 10 days, so an outage longer
    # than that leaves a permanent hole that no MAX(day) check can see. If such a hole
    # covers a month's last trading day, that month's close silently becomes an earlier
    # day and its return is mis-measured with no error anywhere.
    #
    # Scoped to the recent window on purpose. The threat is a missed scheduled run, which
    # is always recent; scanning all history instead flags genuine market closures — the
    # first version of this check fired on 2001-09-10 -> 2001-09-17, which is the week the
    # exchanges were shut after September 11. Deep-history integrity belongs to the
    # supervised backfill, not to a nightly gate that would then cry wolf every night.
    gap_window_start = date.today() - timedelta(days=GAP_SCAN_DAYS)
    gaps = con.execute(
        """
        WITH d AS (SELECT DISTINCT day FROM eod_prices WHERE day >= ?),
             s AS (SELECT day, lag(day) OVER (ORDER BY day) AS prev FROM d)
        SELECT prev, day FROM s
         WHERE prev IS NOT NULL AND date_diff('day', prev, day) > 5
         ORDER BY day DESC LIMIT 5
        """, [gap_window_start]
    ).fetchall()
    if gaps:
        notes.append("interior gaps: " + "; ".join(f"{a}->{b}" for a, b in gaps))

    max_day = max((d for d in per_symbol.values() if d), default=None)
    clean = not failed and not stale and not gaps
    store.finish_run(con, run_id, symbols_ok=ok, symbols_failed=len(failed),
                     rows_written=rows_written, max_day=max_day, clean=clean,
                     notes=" | ".join(notes) or "clean")

    print(f"\nrows written: {rows_written} | ok: {ok} | failed: {len(failed)}")
    print(f"newest day: {max_day} | staleness floor: {expected} | stale symbols: {len(stale)} | interior gaps: {len(gaps)}")
    if clean:
        print("CLEAN NIGHT")
        return 0

    # Loud failure: this text is what the operator sees in the scheduler log / alert.
    print("NOT A CLEAN NIGHT — publish must not proceed")
    for n in notes:
        print(f"  - {n}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
