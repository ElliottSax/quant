#!/usr/bin/env python3
"""Calibration log — the clock (plan story 1.5).

  python -m pipeline.calibration record    # append today's verdicts
  python -m pipeline.calibration verify    # integrity monitor
  python -m pipeline.calibration tenure    # how long each verdict has held

This is the asset a competitor cannot copy by copying the site. Anyone can publish a
tier today; nobody can publish a dated, unbroken record of what they said two years ago.
Every run appends what the engine concluded, stamped with the spec version and data
vintage that produced it.

Two rules make the record worth anything, and both are enforced here rather than trusted:

  APPEND ONLY.   Rows are never updated or deleted. A verdict that changes is a NEW row;
                 the old one stays. Silently correcting the past would make the clock a
                 decoration.
  CHECKSUMMED.   Each row carries a hash of its own content, and `verify` recomputes them.
                 A record nobody can audit is a claim, not evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline import store  # noqa: E402

SCHEMA = """
CREATE TABLE IF NOT EXISTS calibration_log (
    logged_at     TIMESTAMP NOT NULL,
    run_date      DATE      NOT NULL,
    spec_version  VARCHAR   NOT NULL,
    engine        VARCHAR   NOT NULL,
    provider      VARCHAR,
    data_vintage  DATE,
    data_start    DATE,
    universe_hash VARCHAR   NOT NULL,
    symbol        VARCHAR   NOT NULL,
    month         INTEGER   NOT NULL,
    tier          VARCHAR   NOT NULL,
    n             INTEGER   NOT NULL,
    diff          DOUBLE,
    p_perm        DOUBLE,
    q_value       DOUBLE,
    ci_low        DOUBLE,
    ci_high       DOUBLE,
    boundary_rule BOOLEAN,
    row_checksum  VARCHAR   NOT NULL
);
"""

CHECKSUM_FIELDS = ["run_date", "spec_version", "engine", "universe_hash", "data_start",
                   "symbol", "month", "tier", "n", "diff", "p_perm", "q_value"]


def _checksum(row: dict) -> str:
    payload = json.dumps({k: row.get(k) for k in CHECKSUM_FIELDS},
                         sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


def _universe_hash(symbols: list[str]) -> str:
    """Identifies the test family. Spec §5: q-values are not comparable across
    universes, so a change of universe must be visible in the record."""
    return hashlib.sha256("|".join(sorted(symbols)).encode()).hexdigest()[:16]


def record(engine_name: str = "a") -> int:
    if engine_name == "a":
        from pipeline import stats_engine_a as engine
    else:
        from pipeline import stats_engine_b as engine

    con = store.connect()
    con.execute(SCHEMA)

    vintage, data_start, provider = con.execute(
        "SELECT MAX(day), MIN(day), any_value(provider) FROM eod_prices"
    ).fetchone()

    cells = engine.compute_cells()
    symbols = sorted({c["symbol"] for c in cells})
    uhash = _universe_hash(symbols)
    now = datetime.now(timezone.utc)
    today = date.today()

    # Keyed on the data span too, not just the day: two runs on the same date over
    # materially different history are genuinely different conclusions, and the log
    # must be able to hold both. Suppressing the second would hide the fact that the
    # earlier verdict was reached on less evidence.
    already = con.execute(
        "SELECT COUNT(*) FROM calibration_log WHERE run_date = ? AND engine = ? "
        "AND universe_hash = ? AND data_start = ?",
        [today, engine_name, uhash, data_start],
    ).fetchone()[0]
    if already:
        # Not an error: re-running the same day is normal. Appending again would inflate
        # the record without adding information, and the record's value is its integrity.
        print(f"already recorded today ({already} rows) for engine {engine_name} / universe {uhash}")
        return 0

    rows = []
    for c in cells:
        r = {
            "logged_at": now, "run_date": today, "spec_version": engine.SPEC_VERSION,
            "engine": engine_name, "provider": provider, "data_vintage": vintage,
            "data_start": data_start,
            "universe_hash": uhash, "symbol": c["symbol"], "month": c["month"],
            "tier": c["tier"], "n": c["n"], "diff": c["diff"],
            "p_perm": None if c["p_perm"] != c["p_perm"] else c["p_perm"],  # NaN -> NULL
            "q_value": c["q_value"],
            "ci_low": None if c["ci_low"] != c["ci_low"] else c["ci_low"],
            "ci_high": None if c["ci_high"] != c["ci_high"] else c["ci_high"],
            "boundary_rule": c.get("boundary_rule_applied", False),
        }
        r["row_checksum"] = _checksum(r)
        rows.append(tuple(r[k] for k in [
            "logged_at", "run_date", "spec_version", "engine", "provider", "data_vintage",
            "data_start", "universe_hash", "symbol", "month", "tier", "n", "diff", "p_perm",
            "q_value", "ci_low", "ci_high", "boundary_rule", "row_checksum"]))

    con.executemany(
        "INSERT INTO calibration_log VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    print(f"recorded {len(rows)} verdicts | spec {engine.SPEC_VERSION} | "
          f"universe {uhash} | vintage {vintage}")
    return 0


def verify() -> int:
    con = store.connect()
    con.execute(SCHEMA)
    rows = con.execute(
        """SELECT run_date, spec_version, engine, universe_hash, data_start, symbol,
                  month, tier, n, diff, p_perm, q_value, row_checksum FROM calibration_log"""
    ).fetchall()
    if not rows:
        print("calibration log is empty — nothing to verify")
        return 1

    bad = 0
    for r in rows:
        d = dict(zip(CHECKSUM_FIELDS, r[:12]))
        if _checksum(d) != r[12]:
            bad += 1

    run_dates = con.execute(
        "SELECT DISTINCT run_date FROM calibration_log ORDER BY run_date").fetchall()
    dates = [d[0] for d in run_dates]
    gaps = []
    for i in range(1, len(dates)):
        delta = (dates[i] - dates[i - 1]).days
        if delta > 4:  # a long weekend plus a holiday is the widest legitimate gap
            gaps.append((dates[i - 1], dates[i], delta))

    print(f"rows:          {len(rows)}")
    print(f"run dates:     {len(dates)}  ({dates[0]} -> {dates[-1]})" if dates else "run dates: 0")
    print(f"checksum bad:  {bad}")
    print(f"suspect gaps:  {len(gaps)}")
    for a, b, d in gaps[:5]:
        print(f"  {a} -> {b} ({d} days)")

    if bad:
        print("\nINTEGRITY FAILURE — the record has been altered after the fact.")
        return 1
    print("\nintegrity OK")
    return 0


def tenure() -> int:
    """How long each current verdict has held, unbroken, at the same tier.

    This is what a Survivors roster displays. Tenure restarts when the tier changes —
    a demotion is published, not smoothed over (spec §7).
    """
    con = store.connect()
    con.execute(SCHEMA)
    rows = con.execute(
        """
        SELECT symbol, month, run_date, tier FROM calibration_log
         WHERE engine = 'a' ORDER BY symbol, month, run_date
        """
    ).fetchall()
    if not rows:
        print("calibration log is empty")
        return 1

    current: dict[tuple[str, int], tuple[str, date, date]] = {}
    for sym, mo, rdate, tier in rows:
        k = (sym, mo)
        if k not in current or current[k][0] != tier:
            current[k] = (tier, rdate, rdate)  # tier, since, last_seen
        else:
            current[k] = (tier, current[k][1], rdate)

    graded = {k: v for k, v in current.items() if v[0] in ("Robust", "Weak")}
    print(f"tracked cells: {len(current)} | currently graded (Robust/Weak): {len(graded)}")
    if not graded:
        print("\nno Robust or Weak verdicts to track yet — the roster is legitimately empty")
    for (sym, mo), (tier, since, last) in sorted(graded.items(), key=lambda kv: kv[1][1]):
        days = (last - since).days
        print(f"  {sym:5} m{mo:02d}  {tier:9} since {since}  ({days}d unbroken)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["record", "verify", "tenure"])
    ap.add_argument("--engine", default="a", choices=["a", "b"])
    args = ap.parse_args()
    if args.command == "record":
        return record(args.engine)
    if args.command == "verify":
        return verify()
    return tenure()


if __name__ == "__main__":
    raise SystemExit(main())
