"""Seasonality statistics engine — implementation B (story 3.2).

Written independently from `docs/STATS_SPEC.md` (DRAFT v0.3, 2026-08-18). This module
must not read or import implementation A; the point of the exercise is that two
implementations built only from the written spec agree on every tier.

Pipeline, per (symbol, calendar month) cell:

  1. Monthly returns from ADJUSTED closes, consecutive months only, trailing partial
     months excluded (spec section 2).
  2. Permutation test, B = 10,000, two-sided, +1/+1 construction (section 3).
  3. Welch's t as a reported secondary statistic (section 3).
  4. Bootstrap 95% CI for the difference in means, 10,000 resamples (section 3).
  5. Benjamini-Hochberg FDR at q = 0.10 over the WHOLE RUN's gradeable cells (section 5).
  6. Tier assignment after correction, subject to the Monte Carlo boundary rule, plus
     leave-one-year-out stability and the mandatory failure-years list (section 6).


SEEDING SCHEME (documented, so it is reproducible from a clean clone)
---------------------------------------------------------------------
Spec section 3 asks for a per-cell deterministic seed `hash(ticker, month, spec_version)`.
Python's builtin `hash()` is salted per process (PYTHONHASHSEED) and therefore NOT
reproducible, so it cannot be what the spec means. This implementation uses:

    key  = f"{symbol}|{month}|{SPEC_VERSION}|{purpose}"        # purpose in {"perm", "boot"}
    seed = int.from_bytes(blake2b(key.encode("utf-8"), digest_size=8).digest(), "big")
    rng  = numpy.random.default_rng(seed)

`purpose` is appended so the permutation draw and the bootstrap draw do not consume the
same random stream (spec says the bootstrap uses the "same seeding rule", not literally
the same seed; reusing one stream for two different procedures would couple them).

Draw construction, spelled out because exact p-value agreement depends on it:
  - permutation: `rng.permuted(numpy.tile(pooled, (B, 1)), axis=1)`, then the first
    n_M columns of each row are the pseudo-target-month group. This is a genuine
    relabelling that preserves group sizes, as section 3 step 3 requires.
  - bootstrap: `rng.integers(0, n_M, size=(B, n_M))` drawn FIRST, then
    `rng.integers(0, n_O, size=(B, n_O))`; the two groups are resampled with
    replacement independently and the CI is the 2.5 / 97.5 percentiles of the
    resampled differences (numpy default linear interpolation).


MONTE CARLO BOUNDARY RULE (section 6, added spec v0.3)
------------------------------------------------------
A permutation p-value is an estimate carrying its own sampling error. Near p = 0.05 with
B = 10,000 that error is about 0.0022, so two honest runs differ by roughly 0.006 — wider
than the gap that separates Weak from Folklore. Any tier decided inside that width is
noise wearing a verdict's clothes. So when a decision falls within `3 * SE(p)` of its
threshold, with `SE(p) = sqrt(p(1-p)/B)`, the conservative side is taken:

  - within 3*SE of the raw-p threshold 0.05  ->  Folklore rather than Weak;
  - within 3*SE of the BH rejection line     ->  no promotion to Robust (falls to Weak).

Every cell reports `boundary_rule_applied`, True when the rule changed the tier or pinned
it to the conservative side at a boundary, so the reason is inspectable rather than
invisible. This rule was found by the cross-check harness (MSFT April straddled 0.05),
not by review.


SPEC AMBIGUITIES AND HOW THEY WERE RESOLVED
-------------------------------------------
Section 1 of the spec says an implementation should stop and ask rather than choose. The
task brief for this run instead directs: take the most conservative statistical reading
and mark it. Each such point is marked `AMBIGUITY` at its site in the code below. Summary:

A1. RESOLVED IN SPEC v0.2, and the spec adopted this implementation's reading. Trailing
    partial months are excluded: a month counts as complete only if the symbol has data
    strictly after that month's last calendar day, so the "last trading day of month" the
    definition names is actually observed. Kept as written; it is now spec text, not a
    judgement call.

A2. "Same span" for the comparison group O. Read as: all other monthly returns of the
    same symbol available in the same history window, no extra trimming to whole years.
    Trimming to whole years would silently discard data the spec never asks to discard.

A3. Leave-one-year-out. Removing a year removes ALL of that year's observations, from
    both M and O, before recomputing d. (Removing it from M only would leave the two
    groups drawn from different spans.) If a removal would empty either group, the cell
    is marked unstable rather than skipped.

A4/A5. RESOLVED IN SPEC v0.3. Section 6 now states top-down precedence explicitly, and it
    matches what this implementation already did: Robust requires BH rejection AND n >= 25
    AND a CI excluding zero AND leave-one-year-out stability; Weak is BH-rejected while
    failing any Robust condition, OR raw p <= 0.05; Folklore is everything else. A
    BH-rejected cell with n < 25 is Weak.

A6. Failure years. Read as the years in which the target month's own return had the
    STRICTLY opposite sign to `diff`. A zero return is not an opposite sign. If
    `diff == 0` the list is empty.

A7. Permutation tie handling. `|d_perm| >= |d_obs|` is compared with a small absolute
    slack (1e-15) so that floating-point noise cannot drop a genuine tie out of the
    count. Counting ties makes p larger, i.e. more conservative.

A8. NEW, from the v0.3 boundary rule. The spec gives SE in p-space but states the BH half
    of the rule as "a BH decision that is itself inside this band", without saying where
    the BH decision line sits in p-space. Read as the effective BH cutoff
    `p_cut = (k/m) * q`, with k the number of hypotheses BH rejects — that is the actual
    line in p-space, the largest p-value the procedure rejects. When BH rejects nothing
    (k = 0) the line the smallest p would have had to beat, `(1/m) * q`, is used instead,
    so the band is still defined. Only the Robust promotion is gated by this half of the
    rule; a BH-rejected cell inside the band drops to Weak, never below, because BH
    rejection is a stronger statement than the raw-p test and must not be discarded.
    Flagged: a different mapping of the BH decision into p-space could change which cells
    are eligible for Robust.
"""

from __future__ import annotations

import hashlib
import os
from calendar import monthrange
from datetime import date
from pathlib import Path

import duckdb
import numpy as np

# Version of docs/STATS_SPEC.md that produced these numbers. Published field; also an
# input to the per-cell seed, so a spec bump changes the random draws by construction.
SPEC_VERSION = "0.3"

# Fixed before results were seen (spec section 6 forbids post-hoc tuning).
N_MIN_GRADEABLE = 20      # section 2: below this the cell is "Insufficient history"
N_MIN_ROBUST = 25         # section 6: Robust additionally requires n >= 25
FDR_Q = 0.10              # section 5: Benjamini-Hochberg at q = 0.10
ALPHA_RAW = 0.05          # section 6: raw-p threshold separating Weak from Folklore
N_PERM = 10_000           # section 3: B
N_BOOT = 10_000           # section 3: bootstrap resamples
CI_LEVEL = 95.0           # section 3: 95% interval
BOUNDARY_SE_MULT = 3.0    # section 6 v0.3: conservative tier within 3*SE(p) of a threshold

_DEFAULT_DB = Path(
    os.environ.get(
        "QUANT_DB_PATH",
        Path(__file__).resolve().parents[1] / "data" / "market.duckdb",
    )
)

TIER_ROBUST = "Robust"
TIER_WEAK = "Weak"
TIER_FOLKLORE = "Folklore"
TIER_INSUFFICIENT = "Insufficient history"


# --------------------------------------------------------------------------- seeding

def _seed(symbol: str, month: int, purpose: str) -> int:
    """Deterministic 64-bit seed for (symbol, month, spec version, purpose).

    blake2b rather than builtin hash(): builtin hash() is salted per interpreter run
    and would break the spec's reproducibility requirement (section 8).
    """
    key = f"{symbol}|{month}|{SPEC_VERSION}|{purpose}".encode("utf-8")
    return int.from_bytes(hashlib.blake2b(key, digest_size=8).digest(), "big")


def _rng(symbol: str, month: int, purpose: str) -> np.random.Generator:
    return np.random.default_rng(_seed(symbol, month, purpose))


# ------------------------------------------------------------------------ data layer

_MONTH_END_CLOSE_SQL = """
SELECT symbol, y, m, adj_close
FROM (
    SELECT symbol,
           CAST(YEAR(day)  AS INTEGER) AS y,
           CAST(MONTH(day) AS INTEGER) AS m,
           day,
           adj_close,
           ROW_NUMBER() OVER (
               PARTITION BY symbol, YEAR(day), MONTH(day)
               ORDER BY day DESC
           ) AS rn
    FROM eod_prices
    WHERE adj_close IS NOT NULL
)
WHERE rn = 1
ORDER BY symbol, y, m
"""


def _load_month_end_closes(db_path: str | None, symbols: list[str] | None):
    """Last adjusted close of each (symbol, year, month), plus each symbol's last day.

    Opened read-only: this engine never writes, and a read-only handle keeps it from
    fighting the nightly ingest for the database lock.
    """
    path = str(db_path or _DEFAULT_DB)
    con = duckdb.connect(path, read_only=True)
    try:
        rows = con.execute(_MONTH_END_CLOSE_SQL).fetchall()
        last_days = dict(
            con.execute("SELECT symbol, MAX(day) FROM eod_prices GROUP BY symbol").fetchall()
        )
    finally:
        con.close()

    by_symbol: dict[str, list[tuple[int, int, float]]] = {}
    wanted = set(symbols) if symbols else None
    for sym, y, m, close in rows:
        if wanted is not None and sym not in wanted:
            continue
        by_symbol.setdefault(sym, []).append((int(y), int(m), float(close)))
    return by_symbol, last_days


def _monthly_returns(
    month_ends: list[tuple[int, int, float]], last_day: date | None
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Adjacent-month total returns from month-end adjusted closes.

    Returns (years, months, rets) for the END month of each pair. Spec section 2:
        r = adj_close[last trading day of month] / adj_close[last trading day of prior month] - 1
    Only adjacent months qualify; a gap in the series produces no return, rather than a
    silently stretched multi-month return.
    """
    month_ends = sorted(month_ends, key=lambda t: (t[0], t[1]))

    # AMBIGUITY A1: drop a trailing partial month. A month counts as complete only if the
    # symbol has data strictly after that month's last calendar day, so the "last trading
    # day of month" the spec names is actually observed. This never touches interior
    # months (they always have later data) - only the ragged edge of the vintage.
    if last_day is not None:
        complete = []
        for y, m, close in month_ends:
            month_last_calendar_day = date(y, m, monthrange(y, m)[1])
            if last_day > month_last_calendar_day:
                complete.append((y, m, close))
        month_ends = complete

    years: list[int] = []
    months: list[int] = []
    rets: list[float] = []
    for i in range(1, len(month_ends)):
        py, pm, pclose = month_ends[i - 1]
        cy, cm, cclose = month_ends[i]
        if (cy * 12 + cm) - (py * 12 + pm) != 1:      # non-adjacent: no observation
            continue
        if not np.isfinite(pclose) or pclose == 0.0:
            continue
        years.append(cy)
        months.append(cm)
        rets.append(cclose / pclose - 1.0)

    return (
        np.asarray(years, dtype=np.int64),
        np.asarray(months, dtype=np.int64),
        np.asarray(rets, dtype=np.float64),
    )


# ------------------------------------------------------------------------- statistics

def _welch_t(m: np.ndarray, o: np.ndarray) -> float:
    """Welch's t for mean(M) - mean(O). Reported, never decisive (spec section 3)."""
    n_m, n_o = m.size, o.size
    if n_m < 2 or n_o < 2:
        return float("nan")
    se2 = m.var(ddof=1) / n_m + o.var(ddof=1) / n_o
    if se2 <= 0.0:
        return float("nan")
    return float((m.mean() - o.mean()) / np.sqrt(se2))


def _permutation_p(m: np.ndarray, o: np.ndarray, d_obs: float, rng) -> float:
    """Two-sided label-shuffling p-value, vectorised over B = 10,000 draws.

    Pool M and O, relabel preserving group sizes, recompute d. The +1 in numerator and
    denominator is mandatory (spec section 3) - it is what stops a finite resampling from
    ever reporting p = 0.
    """
    n_m, n_o = m.size, o.size
    if n_m == 0 or n_o == 0 or not np.isfinite(d_obs):
        return float("nan")

    pooled = np.concatenate([m, o])
    total = pooled.sum()

    # One relabelling per row; first n_m columns are the pseudo target-month group.
    shuffled = rng.permuted(np.tile(pooled, (N_PERM, 1)), axis=1)
    sum_m = shuffled[:, :n_m].sum(axis=1)
    d_perm = sum_m / n_m - (total - sum_m) / n_o

    # AMBIGUITY A7: tolerant ">=" so float noise cannot silently drop ties (raises p).
    hits = int(np.count_nonzero(np.abs(d_perm) >= abs(d_obs) - 1e-15))
    return (1.0 + hits) / (N_PERM + 1.0)


def _bootstrap_ci(m: np.ndarray, o: np.ndarray, rng) -> tuple[float, float]:
    """Percentile bootstrap 95% CI for mean(M) - mean(O), 10,000 resamples.

    The two groups are resampled with replacement independently; the interval is the
    2.5 / 97.5 percentiles of the resampled differences. A verdict is never rendered
    without its interval (spec section 3).
    """
    n_m, n_o = m.size, o.size
    if n_m == 0 or n_o == 0:
        return float("nan"), float("nan")

    idx_m = rng.integers(0, n_m, size=(N_BOOT, n_m))
    idx_o = rng.integers(0, n_o, size=(N_BOOT, n_o))
    diffs = m[idx_m].mean(axis=1) - o[idx_o].mean(axis=1)

    tail = (100.0 - CI_LEVEL) / 2.0
    lo, hi = np.percentile(diffs, [tail, 100.0 - tail])
    return float(lo), float(hi)


def _loo_year_stable(
    years: np.ndarray, is_target: np.ndarray, rets: np.ndarray, d_obs: float
) -> bool:
    """Leave-one-year-out sign stability (spec section 6).

    Recompute d with each single year removed in turn; if removing any one year flips the
    sign, the effect is one episode wearing a pattern's clothes and cannot be Robust.
    """
    if not np.isfinite(d_obs) or d_obs == 0.0:
        return False
    sign_obs = np.sign(d_obs)

    for year in np.unique(years):
        # AMBIGUITY A3: the year leaves BOTH groups, so M and O still cover one span.
        keep = years != year
        m = rets[keep & is_target]
        o = rets[keep & ~is_target]
        if m.size == 0 or o.size == 0:
            return False        # cannot demonstrate stability -> not stable
        if np.sign(m.mean() - o.mean()) != sign_obs:
            return False
    return True


def _failure_years(years: np.ndarray, is_target: np.ndarray, rets: np.ndarray,
                   diff: float) -> list[int]:
    """Years in which the target month went the other way. Mandatory output (section 6)."""
    if not np.isfinite(diff) or diff == 0.0:
        # AMBIGUITY A6: with no effect direction, nothing can oppose it.
        return []
    sign_diff = np.sign(diff)
    m_years = years[is_target]
    m_rets = rets[is_target]
    opposed = np.sign(m_rets) == -sign_diff       # strictly opposite; zero is not opposite
    return sorted(int(y) for y in m_years[opposed])


def _mc_standard_error(p: float) -> float:
    """SE of a permutation p-value estimate: sqrt(p(1-p)/B) (spec section 6, v0.3)."""
    if not np.isfinite(p):
        return float("nan")
    return float(np.sqrt(max(p * (1.0 - p), 0.0) / N_PERM))


def _within_mc_band(p: float, threshold: float) -> bool:
    """True when a decision at `threshold` is inside this p-value's Monte Carlo noise.

    `|p - threshold| < 3 * SE(p)`. Inside the band the tier would be decided by which
    side the resampling noise happened to land on, which is false precision.
    """
    se = _mc_standard_error(p)
    if not np.isfinite(se) or not np.isfinite(threshold):
        return False
    return abs(p - threshold) < BOUNDARY_SE_MULT * se


def _benjamini_hochberg(p_values: np.ndarray) -> np.ndarray:
    """Standard step-up BH adjusted values (q-values), monotone and capped at 1.

    q_(i) = min over j >= i of (m / j) * p_(j). With this definition `q <= FDR_Q` is
    exactly equivalent to BH's "largest k with p_(k) <= (k/m) * q" rejection set, so the
    tier rule can be written against q alone.
    """
    m = p_values.size
    if m == 0:
        return np.empty(0, dtype=np.float64)

    order = np.argsort(p_values, kind="stable")
    ranks = np.arange(1, m + 1, dtype=np.float64)
    scaled = p_values[order] * m / ranks
    # Running minimum from the largest p downwards enforces monotonicity.
    q_sorted = np.minimum.accumulate(scaled[::-1])[::-1]
    q_sorted = np.minimum(q_sorted, 1.0)

    q = np.empty(m, dtype=np.float64)
    q[order] = q_sorted
    return q


# ------------------------------------------------------------------------------- API

def compute_cells(db_path: str | None = None, symbols: list[str] | None = None) -> list[dict]:
    """Return one dict per (symbol, calendar month) cell, sorted by (symbol, month)."""
    by_symbol, last_days = _load_month_end_closes(db_path, symbols)

    cells: list[dict] = []
    for symbol in sorted(by_symbol):
        years, months, rets = _monthly_returns(by_symbol[symbol], last_days.get(symbol))

        for month in range(1, 13):
            is_target = months == month
            m_group = rets[is_target]
            o_group = rets[~is_target]
            n = int(m_group.size)

            if n == 0 or o_group.size == 0:
                mean_month = float(m_group.mean()) if n else float("nan")
                mean_other = float(o_group.mean()) if o_group.size else float("nan")
                cells.append({
                    "symbol": symbol, "month": month, "n": n,
                    "mean_month": mean_month, "mean_other": mean_other,
                    "diff": float("nan"), "t_stat": float("nan"),
                    "p_perm": float("nan"), "ci_low": float("nan"), "ci_high": float("nan"),
                    "q_value": None, "tier": TIER_INSUFFICIENT,
                    "stable": False, "failure_years": [],
                    "boundary_rule_applied": False,
                })
                continue

            mean_month = float(m_group.mean())
            mean_other = float(o_group.mean())
            diff = mean_month - mean_other

            t_stat = _welch_t(m_group, o_group)
            p_perm = _permutation_p(m_group, o_group, diff, _rng(symbol, month, "perm"))
            ci_low, ci_high = _bootstrap_ci(m_group, o_group, _rng(symbol, month, "boot"))
            stable = _loo_year_stable(years, is_target, rets, diff)
            fails = _failure_years(years, is_target, rets, diff)

            cells.append({
                "symbol": symbol, "month": month, "n": n,
                "mean_month": mean_month, "mean_other": mean_other,
                "diff": float(diff), "t_stat": float(t_stat),
                "p_perm": float(p_perm), "ci_low": ci_low, "ci_high": ci_high,
                "q_value": None,                 # filled in below, after the whole family exists
                "tier": TIER_INSUFFICIENT,       # provisional; overwritten for gradeable cells
                "stable": bool(stable),
                "failure_years": fails,
                "boundary_rule_applied": False,   # set during tier assignment below
            })

    # --- multiple testing, spec section 5 -----------------------------------------
    # THE FAMILY IS THE ENTIRE RUN: every gradeable cell across every symbol, corrected
    # together. Correcting within a symbol (12 tests) is explicitly a specification
    # error. Sub-threshold cells (n < 20) never enter the family at all.
    gradeable = [
        c for c in cells
        if c["n"] >= N_MIN_GRADEABLE and np.isfinite(c["p_perm"])
    ]
    if gradeable:
        q_values = _benjamini_hochberg(np.array([c["p_perm"] for c in gradeable], dtype=np.float64))
        for cell, q in zip(gradeable, q_values):
            cell["q_value"] = float(q)

    # The BH rejection line expressed in p-space, for the boundary rule (AMBIGUITY A8).
    # q <= FDR_Q is equivalent to rank <= k, so k is just the count of rejected cells;
    # the effective cutoff is then (k/m) * q, the largest p the procedure rejects.
    m_family = len(gradeable)
    if m_family:
        k_rejected = sum(1 for c in gradeable if c["q_value"] <= FDR_Q)
        bh_cutoff = (max(k_rejected, 1) / m_family) * FDR_Q
    else:
        bh_cutoff = float("nan")

    # --- tiers, spec section 6, applied only AFTER the correction ------------------
    for cell in cells:
        if cell["n"] < N_MIN_GRADEABLE or cell["q_value"] is None:
            cell["tier"] = TIER_INSUFFICIENT
            cell["q_value"] = None
            cell["boundary_rule_applied"] = False
            continue

        p = cell["p_perm"]
        passes_bh = cell["q_value"] <= FDR_Q
        ci_excludes_zero = (
            np.isfinite(cell["ci_low"]) and np.isfinite(cell["ci_high"])
            and (cell["ci_low"] > 0.0 or cell["ci_high"] < 0.0)
        )

        # Spec v0.3 precedence, top-down (this is what A4/A5 flagged; now spec text).
        if passes_bh and cell["n"] >= N_MIN_ROBUST and ci_excludes_zero and cell["stable"]:
            tier = TIER_ROBUST
        elif passes_bh or p <= ALPHA_RAW:
            tier = TIER_WEAK
        else:
            tier = TIER_FOLKLORE

        # --- Monte Carlo boundary rule, spec section 6 (v0.3) ----------------------
        # A tier decided inside the resampling noise is false precision; take the
        # conservative side and record that we did.
        applied = False

        # (a) No promotion to Robust on a BH decision inside the band. The cell keeps
        #     its BH rejection, so it lands on Weak - never lower (AMBIGUITY A8).
        if tier == TIER_ROBUST and _within_mc_band(p, bh_cutoff):
            tier = TIER_WEAK
            applied = True

        # (b) Folklore over Weak when the raw-p decision straddles 0.05. Only applies
        #     when Weak rests on the raw-p clause: a BH-rejected cell has cleared a
        #     stronger bar than 0.05 and must not be demoted by this half of the rule.
        if not passes_bh and tier in (TIER_WEAK, TIER_FOLKLORE) and _within_mc_band(p, ALPHA_RAW):
            tier = TIER_FOLKLORE      # changed from Weak, or pinned to the safe side
            applied = True

        cell["tier"] = tier
        cell["boundary_rule_applied"] = applied

    cells.sort(key=lambda c: (c["symbol"], c["month"]))
    return cells


# ------------------------------------------------------------------------------ main

def _summarise(cells: list[dict]) -> str:
    from collections import Counter

    tiers = Counter(c["tier"] for c in cells)
    lines = [
        f"stats_engine_b - spec version {SPEC_VERSION}",
        f"cells: {len(cells)}   B(perm)={N_PERM}   B(boot)={N_BOOT}   BH q={FDR_Q}",
        "",
        "tier distribution:",
    ]
    for tier in (TIER_ROBUST, TIER_WEAK, TIER_FOLKLORE, TIER_INSUFFICIENT):
        lines.append(f"  {tier:<22} {tiers.get(tier, 0)}")

    family = [c for c in cells if c["q_value"] is not None]
    touched = [c for c in cells if c["boundary_rule_applied"]]
    lines += [
        "",
        f"BH family size (whole run, gradeable only): {len(family)}",
        f"min raw p: {min((c['p_perm'] for c in family), default=float('nan')):.6f}",
        f"min q:     {min((c['q_value'] for c in family), default=float('nan')):.6f}",
        f"Monte Carlo boundary rule touched {len(touched)} cell(s) "
        f"(3 x SE, SE=sqrt(p(1-p)/{N_PERM})):",
    ]
    for c in touched:
        se = _mc_standard_error(c["p_perm"])
        lines.append(
            f"  {c['symbol']:<5}{c['month']:>3}  p={c['p_perm']:.5f}  "
            f"|p-0.05|={abs(c['p_perm'] - ALPHA_RAW):.5f} < 3*SE={3 * se:.5f}  -> {c['tier']}"
        )
    lines += [
        "",
        f"{'sym':<5}{'mo':>3}{'n':>5}{'mean_m':>10}{'mean_o':>10}{'diff':>10}"
        f"{'t':>8}{'p':>9}{'q':>9}  {'CI':<22}{'st':>3}{'bd':>4}  tier",
    ]
    for c in cells:
        q = "     -   " if c["q_value"] is None else f"{c['q_value']:9.4f}"
        ci = f"[{c['ci_low']:+.4f}, {c['ci_high']:+.4f}]"
        lines.append(
            f"{c['symbol']:<5}{c['month']:>3}{c['n']:>5}"
            f"{c['mean_month']:>10.5f}{c['mean_other']:>10.5f}{c['diff']:>10.5f}"
            f"{c['t_stat']:>8.3f}{c['p_perm']:>9.5f}{q}  {ci:<22}"
            f"{'Y' if c['stable'] else 'N':>3}"
            f"{'*' if c['boundary_rule_applied'] else '.':>4}  {c['tier']}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    db = sys.argv[1] if len(sys.argv) > 1 else None
    print(_summarise(compute_cells(db)))
