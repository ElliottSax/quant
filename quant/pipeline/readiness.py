#!/usr/bin/env python3
"""Data readiness against the statistical spec (docs/STATS_SPEC.md).

  python -m pipeline.readiness

Answers one question before any verdict work begins: given what is actually in the
store, how many (symbol, calendar month) cells could clear the spec's thresholds?

  n >= 20  gradeable at all (below this the cell is excluded from the test family)
  n >= 25  eligible for Robust

This is the honest gate on the whole seasonality product. If nothing is gradeable, the
answer is more history — not a looser threshold. Loosening the floor to fit the data on
hand is precisely the p-hacking the spec exists to prevent.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline import store  # noqa: E402

GRADEABLE_N = 20
ROBUST_N = 25


def main() -> int:
    con = store.connect()

    total = con.execute("SELECT COUNT(*) FROM eod_prices").fetchone()[0]
    if not total:
        print("store is empty — run pipeline.run_nightly first")
        return 1

    # One observation per (symbol, calendar month, year): the monthly return.
    cells = con.execute(
        """
        WITH monthly AS (
            SELECT symbol, YEAR(day) AS yr, MONTH(day) AS mo,
                   last(adj_close ORDER BY day) AS close
              FROM eod_prices
             GROUP BY symbol, yr, mo
        ),
        with_prev AS (
            SELECT symbol, yr, mo, close,
                   lag(close) OVER (PARTITION BY symbol ORDER BY yr, mo) AS prev
              FROM monthly
        )
        SELECT symbol, mo, COUNT(*) AS n
          FROM with_prev
         WHERE prev IS NOT NULL
         GROUP BY symbol, mo
        """
    ).fetchall()

    gradeable = [c for c in cells if c[2] >= GRADEABLE_N]
    robust_eligible = [c for c in cells if c[2] >= ROBUST_N]
    max_n = max((c[2] for c in cells), default=0)

    symbols = con.execute("SELECT COUNT(DISTINCT symbol) FROM eod_prices").fetchone()[0]
    span = con.execute("SELECT MIN(day), MAX(day) FROM eod_prices").fetchone()

    print(f"store:            {total:,} bars | {symbols} symbols | {span[0]} -> {span[1]}")
    print(f"cells:            {len(cells)} (symbol x calendar month)")
    print(f"max observations: {max_n} per cell")
    print()
    print(f"gradeable (n>={GRADEABLE_N}):      {len(gradeable):>4} / {len(cells)}")
    print(f"Robust-eligible (n>={ROBUST_N}): {len(robust_eligible):>4} / {len(cells)}")
    print()

    if not gradeable:
        print("VERDICT: NOT READY. No cell reaches the gradeable floor, so the test")
        print("family would be empty and no page could carry a tier badge.")
        print(f"Need ~{GRADEABLE_N + 1} complete years per symbol; the store holds {max_n + 1}.")
        return 1
    if not robust_eligible:
        print("VERDICT: PARTIAL. Cells are gradeable but none can reach Robust, so")
        print("The Survivors roster would launch empty. Publishable as null results only.")
        return 1

    print("VERDICT: READY for the verdict engine at the current thresholds.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
