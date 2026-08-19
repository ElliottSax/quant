#!/usr/bin/env python3
"""Publish verdicts as a static JSON artefact for the site (plan story 2.1).

  python -m pipeline.export_verdicts [--out PATH]

The serving plane never touches the database: the site reads this file, generated on
the compute plane. Two properties are enforced rather than assumed, because both are
ways the published page could quietly stop matching reality:

  RECORDED == PUBLISHED.  Every exported tier is checked against the newest calibration
                          log entry for the same cell. A mismatch aborts the export.
                          Otherwise the site could show a verdict that was never entered
                          on the record, which is exactly the claim the clock exists to
                          make unfalsifiable.
  CLEAN DATA ONLY.        Refuses to export when the last ingest run was not clean.

Exit code 0 = written, 1 = refused. A publish step must gate on it.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline import store  # noqa: E402

DEFAULT_OUT = Path(__file__).resolve().parents[1] / "frontend" / "public" / "data" / "seasonality.json"

MONTHS = ["", "January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--allow-unclean", action="store_true",
                    help="export despite an unclean ingest (for local inspection only)")
    args = ap.parse_args()

    con = store.connect()
    from pipeline import stats_engine_a as engine

    last_run = con.execute(
        "SELECT run_id, clean, notes FROM ingest_runs WHERE finished_at IS NOT NULL "
        "ORDER BY finished_at DESC LIMIT 1"
    ).fetchone()
    if not last_run:
        print("refusing to export: no completed ingest run")
        return 1
    if not last_run[1] and not args.allow_unclean:
        print(f"refusing to export: last ingest {last_run[0]} was not clean — {last_run[2]}")
        return 1

    vintage, data_start, provider = con.execute(
        "SELECT MAX(day), MIN(day), any_value(provider) FROM eod_prices"
    ).fetchone()

    cells = engine.compute_cells()

    # Recorded == published. The calibration log is the permanent record; if the page
    # would show something the record does not contain, the record is worthless.
    recorded = dict(con.execute(
        """
        SELECT symbol || '-' || CAST(month AS VARCHAR), tier
          FROM calibration_log
         WHERE engine = 'a' AND spec_version = ?
           AND seq > (SELECT COALESCE(MAX(seq), 0) - 10000 FROM calibration_log)
        QUALIFY ROW_NUMBER() OVER (PARTITION BY symbol, month ORDER BY seq DESC) = 1
        """, [engine.SPEC_VERSION]
    ).fetchall())

    if not recorded:
        print(f"refusing to export: calibration log has no spec {engine.SPEC_VERSION} entries. "
              "Run `python -m pipeline.calibration record` first.")
        return 1

    mismatches = [
        (c["symbol"], c["month"], c["tier"], recorded.get(f"{c['symbol']}-{c['month']}"))
        for c in cells
        if recorded.get(f"{c['symbol']}-{c['month']}") != c["tier"]
    ]
    if mismatches:
        print(f"refusing to export: {len(mismatches)} cell(s) differ from the calibration record")
        for sym, mo, computed, rec in mismatches[:5]:
            print(f"  {sym} m{mo:02d}: computed {computed}, recorded {rec}")
        return 1

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "spec_version": engine.SPEC_VERSION,
        "provider": provider,
        "data_start": str(data_start),
        "data_vintage": str(vintage),
        "universe": sorted({c["symbol"] for c in cells}),
        "family_size": sum(1 for c in cells if c["tier"] != "Insufficient history"),
        "fdr_q": engine.Q_LEVEL,
        "thresholds": {"gradeable_n": engine.GRADEABLE_N, "robust_n": engine.ROBUST_N},
        "cells": [
            {
                "symbol": c["symbol"],
                "month": c["month"],
                "month_name": MONTHS[c["month"]],
                "tier": c["tier"],
                "n": c["n"],
                "diff_pp": None if c["diff"] != c["diff"] else round(c["diff"] * 100, 4),
                "ci_low_pp": None if c["ci_low"] != c["ci_low"] else round(c["ci_low"] * 100, 4),
                "ci_high_pp": None if c["ci_high"] != c["ci_high"] else round(c["ci_high"] * 100, 4),
                "p": None if c["p_perm"] != c["p_perm"] else round(c["p_perm"], 6),
                "q": None if c["q_value"] is None else round(c["q_value"], 6),
                "stable": c["stable"],
                "failure_years": c["failure_years"],
                "boundary_rule_applied": c.get("boundary_rule_applied", False),
            }
            for c in cells
        ],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1), encoding="utf-8")
    from collections import Counter
    tiers = Counter(c["tier"] for c in cells)
    print(f"wrote {args.out}")
    print(f"  {len(out['cells'])} cells | spec {out['spec_version']} | "
          f"{out['data_start']} -> {out['data_vintage']}")
    print(f"  " + " | ".join(f"{t}: {tiers.get(t, 0)}"
                             for t in ["Robust", "Weak", "Folklore", "Insufficient history"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
