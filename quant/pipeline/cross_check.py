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
N_RESAMPLE_REFINED = 100_000  # spec §6 v0.4 adaptive precision
# Mandatory §6 outputs that must match exactly. Omitting these let the engines disagree
# on failure years or leave-one-year-out stability while the harness reported 100%.
EXACT_LIST_FIELDS = ["stable", "failure_years", "boundary_rule_applied"]


def _both_nan(a, b) -> bool:
    return (isinstance(a, float) and math.isnan(a)) and (isinstance(b, float) and math.isnan(b))


def _one_nan(a, b) -> bool:
    """Exactly one side is NaN/None — one engine refused to produce a value while the
    other published one. That is the most severe disagreement possible, and the original
    guard skipped it: NaN comparisons are always False, so `abs(nan - 0.003) > tol` never
    fired and the harness reported agreement."""
    a_missing = a is None or (isinstance(a, float) and math.isnan(a))
    b_missing = b is None or (isinstance(b, float) and math.isnan(b))
    return a_missing != b_missing


def mc_tolerance(p_a: float, p_b: float, n_resample: int = N_RESAMPLE) -> float:
    """Tolerance for the DIFFERENCE of two independent resampling estimates.

    The scale is sqrt(2) x SE, not SE: both engines report noisy estimates, so the
    difference has variance var_A + var_B = 2 x SE^2. The first version of this harness
    compared against a single SE and duly flagged two cells as defects; measuring the
    z-distribution across all 90 gradeable cells showed sd = 1.54 rather than 1.0, which
    is the sqrt(2) factor plus the permutation p-value's mild over-dispersion relative
    to the binomial approximation. The tolerance was wrong, not the engines.
    """
    p = max(min((p_a + p_b) / 2, 1.0), 0.0)
    se = math.sqrt(max(p * (1 - p), 1e-12) / n_resample)
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
        for f in EXACT_LIST_FIELDS:
            if f in ca or f in cb:
                if ca.get(f) != cb.get(f):
                    numeric_disagreements.append((k, f, ca.get(f), cb.get(f)))

        for f in MC_FIELDS:
            va, vb = ca.get(f), cb.get(f)
            if _one_nan(va, vb):
                # Never silently skipped: this is a real, severe disagreement.
                numeric_disagreements.append((k, f + " (one side missing)", va, vb))
                continue
            if va is None or vb is None or _both_nan(va, vb):
                continue
            # CI bounds are means of resampled differences, not proportions; scale their
            # tolerance off the interval width so it stays meaningful for either field.
            # Refined cells ran at 10x the permutations, so their true SE is ~3.2x
            # smaller; applying the B=10,000 tolerance there would be 3.2x too generous
            # on exactly the near-threshold cells §6 v0.4 exists to protect.
            b_used = max(int(ca.get("perm_b") or 0), int(cb.get("perm_b") or 0)) or N_RESAMPLE
            width = abs(ca["ci_high"] - ca["ci_low"])
            tol = (mc_tolerance(va, vb, b_used) if f == "p_perm"
                   else MC_SIGMAS * width / math.sqrt(N_RESAMPLE))
            if f != "p_perm" and not math.isfinite(tol):
                numeric_disagreements.append((k, f + " (tolerance not computable)", va, vb))
                continue
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
