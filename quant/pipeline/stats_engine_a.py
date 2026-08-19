#!/usr/bin/env python3
"""Seasonality verdict engine — implementation A (plan story 3.2).

Implements docs/STATS_SPEC.md v0.4. A second, independently written implementation
lives in stats_engine_b.py; `cross_check.py` requires them to agree on every tier and
to within 1e-9 on every statistic. Two implementations exist because a single one that
is subtly wrong is indistinguishable from a correct one — the agreement IS the test.

Nothing here is a forecast. Every number describes what the historical record contains.
"""

from __future__ import annotations

import hashlib
import math
import sys
from calendar import monthrange
from datetime import date
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline import store  # noqa: E402

SPEC_VERSION = "0.4"
GRADEABLE_N = 20
ROBUST_N = 25
Q_LEVEL = 0.10
N_PERM = 10_000
N_BOOT = 10_000
N_PERM_REFINE = 100_000   # spec §6 v0.4: 10x precision for near-threshold cells
REFINE_SIGMAS = 6         # recompute when |p - threshold| is within this many SE


def _rng(symbol: str, month: int, purpose: str) -> np.random.Generator:
    """Deterministic per-cell seeding, per spec §3.

    The seed is a digest of (symbol, month, spec_version, purpose) so a rerun on any
    machine reproduces the same p-value exactly. `purpose` separates the permutation
    stream from the bootstrap stream so they cannot share draws.
    """
    key = f"{symbol}|{month}|{SPEC_VERSION}|{purpose}".encode()
    seed = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
    return np.random.default_rng(seed)


def monthly_returns(con, symbol: str) -> list[tuple[int, int, float]]:
    """(year, month, return) from adjusted closes, consecutive complete months only."""
    rows = con.execute(
        """
        WITH m AS (
            SELECT YEAR(day) AS yr, MONTH(day) AS mo,
                   last(adj_close ORDER BY day) AS close
              FROM eod_prices
             WHERE symbol = ?
             GROUP BY yr, mo
        )
        SELECT yr, mo, close FROM m ORDER BY yr, mo
        """,
        [symbol],
    ).fetchall()

    # Spec §2 (v0.2): a month counts only when the symbol has data strictly after that
    # month's last calendar day, so the month-end close is actually observed. Without
    # this, a mid-month vintage contributes an 18-day return as if it were a monthly one
    # — and it lands in every other cell's "other months" pool too.
    last_day = con.execute(
        "SELECT MAX(day) FROM eod_prices WHERE symbol = ?", [symbol]
    ).fetchone()[0]
    if last_day is not None:
        rows = [
            (y, m, c) for y, m, c in rows
            if last_day > date(y, m, monthrange(y, m)[1])
        ]

    out: list[tuple[int, int, float]] = []
    for i in range(1, len(rows)):
        py, pm, pc = rows[i - 1]
        y, mo, c = rows[i]
        # Only consecutive calendar months; a gap would make the "monthly" return span
        # more than a month and quietly corrupt the cell.
        if (py * 12 + pm) + 1 != (y * 12 + mo) or not pc:
            continue
        out.append((y, mo, c / pc - 1.0))
    return out


def welch_t(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return float("nan")
    va, vb = a.var(ddof=1), b.var(ddof=1)
    denom = np.sqrt(va / na + vb / nb)
    return float((a.mean() - b.mean()) / denom) if denom > 0 else float("nan")


def permutation_p(month_vals: np.ndarray, other_vals: np.ndarray, symbol: str, month: int,
                  n_perm: int = N_PERM, stream: str = "perm") -> float:
    """Two-sided label-shuffling p-value, spec §3."""
    pooled = np.concatenate([month_vals, other_vals])
    n_m = len(month_vals)
    d_obs = abs(month_vals.mean() - other_vals.mean())

    rng = _rng(symbol, month, stream)

    # Chunked. A single (n_perm x len(pooled)) argsort materialises three arrays of that
    # size at once — measured at 706 MB of resident growth for one refined cell at
    # B = 100,000 — which fails on a modest container and takes the whole family down
    # with it. Chunking bounds peak memory without changing the draws consumed.
    n_total = len(pooled)
    total = float(pooled.sum())
    count = 0
    CHUNK = 5_000
    done = 0
    while done < n_perm:
        size = min(CHUNK, n_perm - done)
        idx = np.argsort(rng.random((size, n_total)), axis=1)
        # Only the target-group sum is needed; the complement follows from the pooled
        # total, so the full permuted matrix never has to be built.
        sum_m = np.take_along_axis(np.broadcast_to(pooled, (size, n_total)),
                                   idx[:, :n_m], axis=1).sum(axis=1)
        means_m = sum_m / n_m
        means_o = (total - sum_m) / (n_total - n_m)
        # Ratified reading (spec §6 open questions): 1e-15 slack so floating-point noise
        # cannot drop a tie. It raises p and is therefore the conservative direction —
        # without it a perfectly flat series manufactures a p-value out of rounding.
        count += int(np.count_nonzero(np.abs(means_m - means_o) >= d_obs - 1e-15))
        done += size

    # +1 top and bottom: a finite resampling can never justify p = 0 (spec §3).
    return float((1 + count) / (n_perm + 1))


def bootstrap_ci(month_vals: np.ndarray, other_vals: np.ndarray, symbol: str, month: int) -> tuple[float, float]:
    rng = _rng(symbol, month, "boot")
    bm = rng.choice(month_vals, size=(N_BOOT, len(month_vals)), replace=True).mean(axis=1)
    bo = rng.choice(other_vals, size=(N_BOOT, len(other_vals)), replace=True).mean(axis=1)
    diffs = bm - bo
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return float(lo), float(hi)


def leave_one_year_out_stable(records: list[tuple[int, int, float]], month: int, diff: float) -> bool:
    """True if no single year's removal flips the sign of the effect (spec §6)."""
    years = sorted({y for y, m, _ in records})
    sign = np.sign(diff)
    if sign == 0:
        return False
    for drop in years:
        kept = [(y, m, r) for y, m, r in records if y != drop]
        mv = np.array([r for _, m, r in kept if m == month])
        ov = np.array([r for _, m, r in kept if m != month])
        if len(mv) < 2 or len(ov) < 2:
            continue
        if np.sign(mv.mean() - ov.mean()) != sign:
            return False
    return True


def benjamini_hochberg(pvals: list[float], q: float = Q_LEVEL) -> tuple[list[float], set[int]]:
    """Return (adjusted q-values in input order, set of rejected indices).

    The family is every gradeable cell in the run — across all symbols, not within one.
    Correcting per-symbol would be a specification error (spec §5).
    """
    m = len(pvals)
    if m == 0:
        return [], set()
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    prev = 1.0
    # Step-up from the largest p-value, enforcing monotonicity.
    for rank in range(m, 0, -1):
        i = order[rank - 1]
        val = min(prev, pvals[i] * m / rank)
        adj[i] = val
        prev = val

    rejected: set[int] = set()
    for rank in range(m, 0, -1):
        i = order[rank - 1]
        if pvals[i] <= (rank / m) * q:
            rejected = {order[r - 1] for r in range(1, rank + 1)}
            break
    return adj, rejected


def compute_cells(db_path: str | None = None, symbols: list[str] | None = None) -> list[dict]:
    con = store.connect(db_path)
    if symbols is None:
        symbols = [r[0] for r in con.execute(
            "SELECT DISTINCT symbol FROM eod_prices ORDER BY symbol").fetchall()]

    cells: list[dict] = []
    for sym in symbols:
        records = monthly_returns(con, sym)
        if not records:
            continue
        for month in range(1, 13):
            mv = np.array([r for _, m, r in records if m == month], dtype=float)
            ov = np.array([r for _, m, r in records if m != month], dtype=float)
            n = len(mv)

            base = {
                "symbol": sym, "month": month, "n": n,
                "mean_month": float(mv.mean()) if n else float("nan"),
                "mean_other": float(ov.mean()) if len(ov) else float("nan"),
            }
            base["diff"] = base["mean_month"] - base["mean_other"]

            if n < GRADEABLE_N or len(ov) < 2:
                # Spec §2 (v0.3): an under-powered cell still reports its DETERMINISTIC
                # descriptive statistics — they are honest and cheap. What it must not
                # carry is a resampling estimate, a q-value or a tier, because those
                # would invite reading a verdict into a cell the spec refuses to grade.
                cells.append({**base,
                              "t_stat": welch_t(mv, ov) if (n >= 2 and len(ov) >= 2) else float("nan"),
                              "p_perm": float("nan"),
                              "ci_low": float("nan"), "ci_high": float("nan"),
                              "q_value": None, "tier": "Insufficient history",
                              "stable": False, "failure_years": [],
                              "boundary_rule_applied": False})
                continue

            t = welch_t(mv, ov)
            p = permutation_p(mv, ov, sym, month)

            # Spec §6 (v0.4): spend computation where the decision is close, rather than
            # relocating the knife-edge. The v0.3 band merely moved the coin-flip from
            # p = 0.05 out to p = 0.05 +/- 3*SE, where two honest implementations still
            # disagreed (WMT March). Refining shrinks the ambiguous radius instead.
            se0 = math.sqrt(max(p * (1 - p), 1e-12) / N_PERM)
            if abs(p - 0.05) < REFINE_SIGMAS * se0:
                p = permutation_p(mv, ov, sym, month, n_perm=N_PERM_REFINE, stream="perm-refine")
                refined = True
            else:
                refined = False
            lo, hi = bootstrap_ci(mv, ov, sym, month)
            stable = leave_one_year_out_stable(records, month, base["diff"])
            sign = np.sign(base["diff"])
            failure_years = sorted(y for y, m, r in records if m == month and np.sign(r) != sign and r != 0)

            cells.append({**base, "t_stat": t, "p_perm": p, "ci_low": lo, "ci_high": hi,
                          "q_value": None, "tier": "", "stable": bool(stable),
                          "failure_years": failure_years,
                          "boundary_rule_applied": False, "_refined": refined})

    # Family-wide correction across every gradeable cell in the run (spec §5).
    gradeable_idx = [i for i, c in enumerate(cells) if c["tier"] != "Insufficient history"]
    qvals, rejected = benjamini_hochberg([cells[i]["p_perm"] for i in gradeable_idx])
    rejected_global = {gradeable_idx[i] for i in rejected}

    for pos, i in enumerate(gradeable_idx):
        c = cells[i]
        c["q_value"] = float(qvals[pos])
        ci_excludes_zero = (c["ci_low"] > 0) or (c["ci_high"] < 0)
        p = c["p_perm"]

        # Spec §6 precedence (v0.3), top-down and exhaustive.
        if i in rejected_global and c["n"] >= ROBUST_N and ci_excludes_zero and c["stable"]:
            tier = "Robust"
        elif i in rejected_global or p <= 0.05:
            tier = "Weak"
        else:
            tier = "Folklore"

        # Spec §6 Monte Carlo boundary rule (v0.3): a p-value is an estimate. Within
        # 3 standard errors of the threshold the tier would be decided by sampling
        # noise, so take the conservative side rather than publish false precision.
        b_used = N_PERM_REFINE if c.get("_refined") else N_PERM
        se = math.sqrt(max(p * (1 - p), 1e-12) / b_used)
        boundary = abs(p - 0.05) < 3 * se
        if boundary and tier == "Weak" and i not in rejected_global:
            tier = "Folklore"
        c["boundary_rule_applied"] = bool(boundary)
        c["tier"] = tier

    for c in cells:
        c.pop("_refined", None)   # internal only; the returned schema is the documented set
    cells.sort(key=lambda c: (c["symbol"], c["month"]))
    return cells


def main() -> int:
    cells = compute_cells()
    from collections import Counter
    tiers = Counter(c["tier"] for c in cells)
    print(f"implementation A | spec {SPEC_VERSION} | {len(cells)} cells")
    for tier in ["Robust", "Weak", "Folklore", "Insufficient history"]:
        print(f"  {tier:22} {tiers.get(tier, 0)}")

    interesting = sorted((c for c in cells if c["tier"] in ("Robust", "Weak")),
                         key=lambda c: c["p_perm"])[:10]
    if interesting:
        print("\nlowest p-values among graded cells:")
        for c in interesting:
            print(f"  {c['symbol']:5} m{c['month']:02d}  n={c['n']:>3}  diff={c['diff']*100:+6.2f}%  "
                  f"p={c['p_perm']:.4f}  q={c['q_value']:.3f}  {c['tier']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
