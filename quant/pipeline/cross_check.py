#!/usr/bin/env python3
"""Cross-check harness for the two stats engines (plan story 3.2).

  python -m pipeline.cross_check

Story 3.2 requires two independently written implementations of docs/STATS_SPEC.md and
this harness between them:

  * tier agreement must be 100%
  * deterministic statistics (means, effect size, Welch t) agree within 1e-9
  * resampling ESTIMATES (permutation p, bootstrap CI bounds) agree within Monte Carlo
    error, not bitwise — spec §8 (v0.3). The original "must match exactly" rule was
    wrong: two independent implementations legitimately use different RNGs, and forcing
    identical draws would mean copying one engine into the other, which is precisely the
    independence this harness exists to preserve.

Any disagreement quarantines BOTH implementations: nothing publishes until it is
reconciled. The point is not that one engine is right, it is that a subtle error in one
is invisible until something independent contradicts it.

Exit code: 0 = agree, 1 = disagreement (or an engine failed to run).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

REL_TOL = 1e-9
N_RESAMPLE = 10_000  # B in the spec; sets the Monte Carlo standard error

# Deterministic functions of the data: these must agree essentially exactly.
NUMERIC_FIELDS = ["mean_month", "mean_other", "diff", "t_stat"]
EXACT_FIELDS = ["n", "tier"]
# Resampling ESTIMATES: compared at Monte Carlo tolerance, per spec §8 (v0.3). Demanding
# bitwise equality here would force one implementation to copy the other's RNG, which
# destroys the independence that makes agreement evidence of anything.
MC_FIELDS = ["p_perm", "ci_low", "ci_high"]
MC_SIGMAS = 4


def mc_tolerance(p_a: float, p_b: float) -> float:
    """Tolerance for the DIFFERENCE of two independent resampling estimates.

    The scale is sqrt(2) x SE, not SE: both engines report noisy estimates, so the
    difference has variance var_A + var_B = 2 x SE^2. The first version of this harness
    compared against a single SE and duly flagged two cells as defects; measuring the
    z-distribution across all 90 gradeable cells showed sd = 1.54 rather than 1.0, which
    is the sqrt(2) factor plus the permutation p-value's mild over-dispersion relative
    to the binomial approximation. The tolerance was wrong, not the engines.
    """
    p = max(min((p_a + p_b) / 2, 1.0), 0.0)
    se = math.sqrt(max(p * (1 - p), 1e-12) / N_RESAMPLE)
    return MC_SIGMAS * math.sqrt(2.0) * se


def close(a, b, tol: float = REL_TOL) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    if isinstance(a, float) and isinstance(b, float):
        if math.isnan(a) and math.isnan(b):
            return True
        return math.isclose(a, b, rel_tol=tol, abs_tol=tol)
    return a == b


def main() -> int:
    try:
        from pipeline import stats_engine_a as A
    except Exception as e:  # noqa: BLE001
        print(f"implementation A failed to import: {e}")
        return 1
    try:
        from pipeline import stats_engine_b as B
    except Exception as e:  # noqa: BLE001
        print(f"implementation B failed to import: {e}")
        return 1

    print("running implementation A ...")
    cells_a = A.compute_cells()
    print("running implementation B ...")
    cells_b = B.compute_cells()

    key = lambda c: (c["symbol"], c["month"])  # noqa: E731
    a_map = {key(c): c for c in cells_a}
    b_map = {key(c): c for c in cells_b}

    only_a = sorted(set(a_map) - set(b_map))
    only_b = sorted(set(b_map) - set(a_map))
    if only_a or only_b:
        print(f"CELL SET MISMATCH — only in A: {only_a[:5]} | only in B: {only_b[:5]}")
        return 1

    tier_disagreements = []
    numeric_disagreements = []
    mc_disagreements = []

    for k in sorted(a_map):
        ca, cb = a_map[k], b_map[k]
        if ca["tier"] != cb["tier"]:
            tier_disagreements.append((k, ca["tier"], cb["tier"]))
        for f in EXACT_FIELDS:
            if f == "tier":
                continue
            if ca.get(f) != cb.get(f):
                numeric_disagreements.append((k, f, ca.get(f), cb.get(f)))
        for f in NUMERIC_FIELDS:
            if not close(ca.get(f), cb.get(f)):
                numeric_disagreements.append((k, f, ca.get(f), cb.get(f)))
        for f in MC_FIELDS:
            va, vb = ca.get(f), cb.get(f)
            if va is None or vb is None or (isinstance(va, float) and math.isnan(va)
                                            and isinstance(vb, float) and math.isnan(vb)):
                continue
            # CI bounds are means of resampled differences, not proportions; scale their
            # tolerance off the interval width so it stays meaningful for either field.
            tol = (mc_tolerance(va, vb) if f == "p_perm"
                   else MC_SIGMAS * abs(ca["ci_high"] - ca["ci_low"]) / math.sqrt(N_RESAMPLE))
            if abs(va - vb) > tol:
                mc_disagreements.append((k, f, va, vb, tol))

    total = len(a_map)
    agree_tiers = total - len(tier_disagreements)
    print(f"\ncells compared:   {total}")
    print(f"tier agreement:   {agree_tiers}/{total} ({100*agree_tiers/total:.1f}%)")
    print(f"numeric mismatch: {len(numeric_disagreements)} field(s) (deterministic)")
    print(f"MC mismatch:      {len(mc_disagreements)} field(s) (beyond {MC_SIGMAS}-sigma resampling error)")

    if tier_disagreements:
        print("\nTIER DISAGREEMENTS (both implementations quarantined):")
        for k, ta, tb in tier_disagreements[:15]:
            print(f"  {k[0]:5} m{k[1]:02d}  A={ta:22} B={tb}")
    if numeric_disagreements:
        print("\nDETERMINISTIC DISAGREEMENTS (these are real defects):")
        for k, f, va, vb in numeric_disagreements[:15]:
            print(f"  {k[0]:5} m{k[1]:02d}  {f:12} A={va!r:>24} B={vb!r}")
    if mc_disagreements:
        print("\nRESAMPLING DISAGREEMENTS BEYOND MONTE CARLO ERROR:")
        for k, f, va, vb, tol in mc_disagreements[:15]:
            print(f"  {k[0]:5} m{k[1]:02d}  {f:10} A={va:.6f} B={vb:.6f} (tol {tol:.6f})")

    if tier_disagreements or numeric_disagreements or mc_disagreements:
        print("\nRESULT: DISAGREEMENT — nothing publishes until reconciled.")
        return 1

    from collections import Counter
    tiers = Counter(c["tier"] for c in cells_a)
    print("\nRESULT: AGREEMENT on every cell and statistic.")
    print("tier distribution (agreed):")
    for t in ["Robust", "Weak", "Folklore", "Insufficient history"]:
        print(f"  {t:22} {tiers.get(t, 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
