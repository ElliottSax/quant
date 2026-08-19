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
  HASH CHAINED.  Each row hashes its own content AND the previous row's hash. A per-row
                 hash alone only catches accidental corruption: anyone who can rewrite a
                 row can recompute its checksum, and a deleted row leaves no trace at all.
                 Chaining means editing or removing any row breaks every row after it,
                 which is what makes "append only" an enforced property rather than a
                 claim in a docstring. `verify` walks the chain from the beginning.
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
    seq           BIGINT    NOT NULL,
    prev_checksum VARCHAR   NOT NULL,
    row_checksum  VARCHAR   NOT NULL,
    PRIMARY KEY (seq)
);
"""

CHECKSUM_FIELDS = ["seq", "prev_checksum", "run_date", "spec_version", "engine",
                   "universe_hash", "data_start", "data_vintage",
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

    # The clock must never record from a night the ingest gate rejected. Previously this
    # was enforced only by errorlevel chaining in run_daily.cmd, so running `calibration
    # record` by hand bypassed it entirely and wrote a permanent row from stale data.
    last_run = con.execute(
        "SELECT run_id, clean, notes FROM ingest_runs WHERE finished_at IS NOT NULL "
        "ORDER BY finished_at DESC LIMIT 1"
    ).fetchone()
    if not last_run:
        print("refusing to record: no completed ingest run found")
        return 1
    if not last_run[1]:
        print(f"refusing to record: last ingest run {last_run[0]} was NOT clean — {last_run[2]}")
        return 1

    cells = engine.compute_cells()

    # Universe hash comes from the REQUESTED universe, not from the symbols that happen
    # to appear in the output. A symbol with no usable returns is dropped by the engine,
    # so hashing the output produced a hash identical to a run where that symbol was
    # never requested — and §5 requires a change of universe to be visible in the record.
    universe_file = Path(__file__).resolve().parent / "universe.txt"
    requested = []
    if universe_file.exists():
        for line in universe_file.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                requested.append(line.upper())
    symbols = sorted(requested) or sorted({c["symbol"] for c in cells})
    uhash = _universe_hash(symbols)

    missing = sorted(set(symbols) - {c["symbol"] for c in cells})
    if missing:
        print(f"WARNING: requested but absent from engine output: {', '.join(missing)}")
    now = datetime.now(timezone.utc)
    today = date.today()

    # Keyed on the data span too, not just the day: two runs on the same date over
    # materially different history are genuinely different conclusions, and the log
    # must be able to hold both. Suppressing the second would hide the fact that the
    # earlier verdict was reached on less evidence.
    already = con.execute(
        "SELECT COUNT(*) FROM calibration_log WHERE run_date = ? AND engine = ? "
        "AND universe_hash = ? AND data_start = ? AND data_vintage = ? AND spec_version = ?",
        [today, engine_name, uhash, data_start, vintage, engine.SPEC_VERSION],
    ).fetchone()[0]
    if already:
        # Not an error: re-running the same day is normal. Appending again would inflate
        # the record without adding information, and the record's value is its integrity.
        print(f"already recorded today ({already} rows) for engine {engine_name} / universe {uhash}")
        return 0

    seq, prev = con.execute(
        "SELECT COALESCE(MAX(seq), 0), COALESCE(argMax(row_checksum, seq), 'GENESIS') "
        "FROM calibration_log"
    ).fetchone()

    rows = []
    for c in cells:
        seq += 1
        r = {
            "seq": seq, "prev_checksum": prev,
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
        prev = r["row_checksum"]          # chain: each row commits to its predecessor
        rows.append(tuple(r[k] for k in [
            "logged_at", "run_date", "spec_version", "engine", "provider", "data_vintage",
            "data_start", "universe_hash", "symbol", "month", "tier", "n", "diff", "p_perm",
            "q_value", "ci_low", "ci_high", "boundary_rule", "seq", "prev_checksum",
            "row_checksum"]))

    con.executemany(
        "INSERT INTO calibration_log VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    print(f"recorded {len(rows)} verdicts | spec {engine.SPEC_VERSION} | "
          f"universe {uhash} | vintage {vintage}")
    return 0


def verify() -> int:
    con = store.connect()
    con.execute(SCHEMA)
    rows = con.execute(
        """SELECT seq, prev_checksum, run_date, spec_version, engine, universe_hash,
                  data_start, data_vintage, symbol, month, tier, n, diff, p_perm,
                  q_value, row_checksum
             FROM calibration_log ORDER BY seq"""
    ).fetchall()
    if not rows:
        print("calibration log is empty — nothing to verify")
        return 1

    bad = 0
    broken_links = []
    expected_prev = "GENESIS"
    expected_seq = 1
    for r in rows:
        d = dict(zip(CHECKSUM_FIELDS, r[:15]))
        if _checksum(d) != r[15]:
            bad += 1
        # The chain is what makes deletion and back-editing detectable: a removed row
        # leaves a seq hole, and an edited row breaks every successor's prev_checksum.
        if r[1] != expected_prev or r[0] != expected_seq:
            broken_links.append((r[0], expected_seq))
        expected_prev = r[15]
        expected_seq = r[0] + 1

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
    print(f"chain breaks:  {len(broken_links)}")
    print(f"suspect gaps:  {len(gaps)}")
    for got, want in broken_links[:5]:
        detail = f"seq {got}" if got == want else f"seq {got}, expected {want}"
        print(f"  broken at {detail} — a preceding row was edited or removed")
    for a, b, d in gaps[:5]:
        print(f"  {a} -> {b} ({d} days)")

    if bad or broken_links:
        print("\nINTEGRITY FAILURE — the record has been altered after the fact.")
        return 1
    print("\nintegrity OK")
    return 0


def tenure() -> int:
    """How long each current verdict has held, unbroken, at the same tier.

    Scoped to the CURRENT spec version. Spec §7: "if the spec changes, prior rows keep
    their original spec version and a new series begins." Merging versions silently
    absorbed a v0.3 Folklore into a v0.4 Weak run — and because both shared a run_date,
    which tier survived depended on row order, making the roster non-deterministic.
    Tenure restarts when the tier changes; a demotion is published, not smoothed over.
    """
    con = store.connect()
    con.execute(SCHEMA)
    rows = con.execute(
        """
        SELECT symbol, month, run_date, tier, spec_version, seq
          FROM calibration_log
         WHERE engine = 'a' AND spec_version = (
               SELECT spec_version FROM calibration_log ORDER BY seq DESC LIMIT 1)
         ORDER BY symbol, month, seq
        """
    ).fetchall()
    if not rows:
        print("calibration log is empty")
        return 1

    current: dict[tuple[str, int], tuple[str, date, date]] = {}
    for sym, mo, rdate, tier, _spec, _seq in rows:
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
