#!/usr/bin/env python3
"""Indicator formulas, implemented from the definition and cross-checked against pandas_ta.

    python -m pipeline.indicator_verify --out ../frontend/public/data/indicator-formulas.json

Every "RSI formula" page on the internet states a formula. Almost none demonstrate that
the formula, as written, reproduces what a real library computes -- and for several
indicators it does NOT, because the published formula omits a smoothing convention that
the library applies. That gap is why people implement RSI from a blog post, get numbers
that disagree with their charting platform, and cannot tell which is wrong.

So this does the thing those pages skip. For each indicator it:

  1. implements the formula independently here, from the definition, in plain NumPy;
  2. computes the same indicator with pandas_ta;
  3. compares them on REAL daily bars and publishes the maximum absolute difference.

Agreement is evidence the formula on the page is the formula the library implements.
Disagreement is a finding, and is published as one -- with the reason where it is known,
because "these disagree and here is why" is more useful than either number alone.

This is the same two-independent-implementation discipline used in pipeline/cross_check.py
for the seasonality engines. It is the only way to make a formula page trustworthy, and
it is not something a site without a price store and a library harness can do.
"""

from __future__ import annotations

import argparse
import json
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")


# --------------------------------------------------------------------- primitives
def wilder_smooth(x: np.ndarray, n: int) -> np.ndarray:
    """Wilder's smoothing (RMA): the seed is a simple average, then y = y + (x - y)/n.

    This is the convention almost every published formula omits. It is equivalent to an
    EMA with alpha = 1/n rather than the standard 2/(n+1), which is why an RSI built on a
    plain EMA disagrees with every charting platform.
    """
    out = np.full_like(x, np.nan, dtype=float)
    if len(x) < n:
        return out
    out[n - 1] = np.nanmean(x[:n])
    for i in range(n, len(x)):
        out[i] = out[i - 1] + (x[i] - out[i - 1]) / n
    return out


def ema(x: np.ndarray, n: int) -> np.ndarray:
    alpha = 2.0 / (n + 1.0)
    out = np.full_like(x, np.nan, dtype=float)
    if len(x) < n:
        return out
    out[n - 1] = np.nanmean(x[:n])
    for i in range(n, len(x)):
        out[i] = alpha * x[i] + (1 - alpha) * out[i - 1]
    return out


def sma(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full_like(x, np.nan, dtype=float)
    c = np.cumsum(np.insert(x, 0, 0.0))
    out[n - 1:] = (c[n:] - c[:-n]) / n
    return out


def true_range(h: np.ndarray, l: np.ndarray, c: np.ndarray) -> np.ndarray:
    prev = np.roll(c, 1)
    prev[0] = np.nan
    return np.nanmax(np.vstack([h - l, np.abs(h - prev), np.abs(l - prev)]), axis=0)


# ------------------------------------------------------------------- own versions
def own_rsi(c: np.ndarray, n: int = 14) -> np.ndarray:
    d = np.diff(c, prepend=np.nan)
    gain = np.where(d > 0, d, 0.0)
    loss = np.where(d < 0, -d, 0.0)
    gain[0] = loss[0] = np.nan
    ag = wilder_smooth(gain[1:], n)
    al = wilder_smooth(loss[1:], n)
    rs = np.divide(ag, al, out=np.full_like(ag, np.inf), where=al != 0)
    out = 100.0 - 100.0 / (1.0 + rs)
    return np.concatenate([[np.nan], out])


def own_atr(h, l, c, n: int = 14) -> np.ndarray:
    return wilder_smooth(true_range(h, l, c), n)


def own_adx(h, l, c, n: int = 14) -> dict[str, np.ndarray]:
    up = h - np.roll(h, 1)
    dn = np.roll(l, 1) - l
    up[0] = dn[0] = np.nan
    plus_dm = np.where((up > dn) & (up > 0), up, 0.0)
    minus_dm = np.where((dn > up) & (dn > 0), dn, 0.0)

    atr = wilder_smooth(true_range(h, l, c), n)
    plus_di = 100.0 * wilder_smooth(plus_dm, n) / atr
    minus_di = 100.0 * wilder_smooth(minus_dm, n) / atr
    denom = plus_di + minus_di
    dx = 100.0 * np.abs(plus_di - minus_di) / np.where(denom == 0, np.nan, denom)
    # ADX is Wilder's smoothing OF the DX series, seeded once DX exists.
    valid = ~np.isnan(dx)
    adx = np.full_like(dx, np.nan)
    idx = np.flatnonzero(valid)
    if len(idx) >= n:
        s = idx[0]
        adx[s + n - 1] = np.nanmean(dx[s:s + n])
        for i in range(s + n, len(dx)):
            adx[i] = (adx[i - 1] * (n - 1) + dx[i]) / n
    return {"ADX": adx, "DMP": plus_di, "DMN": minus_di}


def own_macd(c, fast=12, slow=26, signal=9) -> dict[str, np.ndarray]:
    line = ema(c, fast) - ema(c, slow)
    valid = ~np.isnan(line)
    sig = np.full_like(line, np.nan)
    idx = np.flatnonzero(valid)
    if len(idx) >= signal:
        s = idx[0]
        sub = ema(line[s:], signal)
        sig[s:] = sub
    return {"MACD": line, "MACDs": sig, "MACDh": line - sig}


def own_bbands(c, n=5, k=2.0, ddof=1) -> dict[str, np.ndarray]:
    """Bollinger bands. `ddof` selects the standard-deviation convention.

    This is measured, not assumed: pandas_ta computes the bands with pandas' .std(),
    which defaults to ddof=1 (the SAMPLE standard deviation), whereas Bollinger's own
    definition and most charting platforms use the population form (ddof=0). Both are
    computed below and compared, because "which one does this library use" is the
    question that actually costs people time.
    """
    mid = sma(c, n)
    sd = np.full_like(c, np.nan, dtype=float)
    for i in range(n - 1, len(c)):
        sd[i] = np.std(c[i - n + 1:i + 1], ddof=ddof)
    return {"BBL": mid - k * sd, "BBM": mid, "BBU": mid + k * sd}


def own_stoch(h, l, c, k=14, d=3, smooth_k=3) -> dict[str, np.ndarray]:
    ll = np.full_like(c, np.nan, dtype=float)
    hh = np.full_like(c, np.nan, dtype=float)
    for i in range(k - 1, len(c)):
        ll[i] = np.min(l[i - k + 1:i + 1])
        hh[i] = np.max(h[i - k + 1:i + 1])
    rng = hh - ll
    raw = 100.0 * (c - ll) / np.where(rng == 0, np.nan, rng)
    kk = sma_nan(raw, smooth_k)
    dd = sma_nan(kk, d)
    return {"STOCHk": kk, "STOCHd": dd}


def sma_nan(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full_like(x, np.nan, dtype=float)
    for i in range(n - 1, len(x)):
        w = x[i - n + 1:i + 1]
        if not np.isnan(w).any():
            out[i] = w.mean()
    return out


# --------------------------------------------------------------------- comparison
TOL = 1e-6


def compare(mine: np.ndarray, theirs: np.ndarray) -> dict:
    """Compare two implementations, separating FORMULA from WARM-UP.

    This distinction is the whole point. Wilder's smoothing is a recursive filter, so a
    different seeding convention produces a large difference in the first bars that then
    DECAYS toward zero. Reporting one max-absolute-difference over the whole series
    conflates "the formula is wrong" with "the first twenty bars are seeded differently",
    which are completely different findings for someone implementing this.

    So two numbers are reported: the agreement on the converged region, which tests the
    formula, and the bar index after which the two never again diverge, which measures
    how long the warm-up actually lasts.
    """
    m = np.asarray(mine, dtype=float)
    t = np.asarray(theirs, dtype=float)
    n = min(len(m), len(t))
    m, t = m[-n:], t[-n:]
    both = ~np.isnan(m) & ~np.isnan(t)
    if both.sum() == 0:
        return {"comparable_points": 0, "agrees": False, "converged": False,
                "note": "no overlapping non-NaN points"}

    idx = np.flatnonzero(both)
    diff = np.abs(m - t)
    scale = max(float(np.nanmax(np.abs(t[both]))), 1e-12)
    rel = diff / scale

    # The first index from which every subsequent comparable point is within tolerance.
    converged_at = None
    over = idx[rel[idx] >= TOL]
    if len(over) == 0:
        converged_at = int(idx[0])
    elif over[-1] < idx[-1]:
        converged_at = int(idx[idx > over[-1]][0])

    tail = idx[idx >= converged_at] if converged_at is not None else np.array([], dtype=int)

    # A practical threshold alongside the strict one. Machine-precision convergence is the
    # right test of the formula, but "how many bars until my numbers match the platform to
    # two decimal places" is the question someone implementing this actually has.
    practical = {}
    for thresh in (0.1, 0.01):
        over_t = idx[diff[idx] >= thresh]
        if len(over_t) == 0:
            practical[str(thresh)] = 0
        elif over_t[-1] < idx[-1]:
            practical[str(thresh)] = int(idx[idx > over_t[-1]][0] - idx[0])
        else:
            practical[str(thresh)] = None      # never gets there within this sample

    return {
        "bars_to_within": practical,
        "comparable_points": int(both.sum()),
        "max_abs_diff_overall": float(np.max(diff[both])),
        "max_rel_diff_overall": float(np.max(rel[both])),
        "converged": converged_at is not None,
        "converged_at_bar": converged_at,
        "bars_before_convergence": (None if converged_at is None
                                    else int(converged_at - idx[0])),
        "max_abs_diff_after_convergence": (float(np.max(diff[tail])) if len(tail) else None),
        "points_after_convergence": int(len(tail)),
        "first_valid_mine": int(np.argmax(~np.isnan(m))) if (~np.isnan(m)).any() else -1,
        "first_valid_theirs": int(np.argmax(~np.isnan(t))) if (~np.isnan(t)).any() else -1,
        # "agrees" means the FORMULA matches: identical once both have warmed up.
        "agrees": bool(converged_at is not None),
        "exact_throughout": bool(np.max(rel[both]) < TOL),
    }


SPECS = [
    {
        "key": "rsi",
        "name": "RSI",
        "full_name": "Relative Strength Index",
        "params": "length = 14",
        "formula": [
            "gain_t = max(close_t - close_{t-1}, 0)",
            "loss_t = max(close_{t-1} - close_t, 0)",
            "avg_gain = Wilder(gain, 14),  avg_loss = Wilder(loss, 14)",
            "RS = avg_gain / avg_loss",
            "RSI = 100 - 100 / (1 + RS)",
        ],
        "gotcha":
            "The averages are WILDER's smoothing, not a simple or standard exponential "
            "average. Wilder's is an EMA with alpha = 1/n, while a standard EMA uses "
            "2/(n+1) -- for n = 14 that is 0.0714 against 0.1333, nearly double. An RSI "
            "built on a plain EMA looks right, moves right, and disagrees with every "
            "charting platform. This is the single most common RSI implementation bug. "
            "Second, because Wilder's smoothing is recursive the SEED persists far longer "
            "than the 14-bar window suggests -- see the measured warm-up below.",
    },
    {
        "key": "atr",
        "name": "ATR",
        "full_name": "Average True Range",
        "params": "length = 14",
        "formula": [
            "TR_t = max(high_t - low_t, |high_t - close_{t-1}|, |low_t - close_{t-1}|)",
            "ATR = Wilder(TR, 14)",
        ],
        "gotcha":
            "True range uses the PREVIOUS close, which is what makes it capture overnight "
            "gaps -- a high-minus-low range cannot. The smoothing is Wilder's again, not a "
            "simple moving average of TR.",
    },
    {
        "key": "adx",
        "name": "ADX",
        "full_name": "Average Directional Index",
        "params": "length = 14",
        "formula": [
            "up = high_t - high_{t-1},  down = low_{t-1} - low_t",
            "+DM = up   if up > down and up > 0   else 0",
            "-DM = down if down > up and down > 0 else 0",
            "+DI = 100 * Wilder(+DM, 14) / ATR,  -DI = 100 * Wilder(-DM, 14) / ATR",
            "DX  = 100 * |+DI - -DI| / (+DI + -DI)",
            "ADX = Wilder(DX, 14)",
        ],
        "gotcha":
            "ADX is smoothed TWICE -- once into the DI values and again over DX -- so it "
            "needs roughly 2n bars before it means anything, and implementations differ in "
            "where they seed the second pass. Note also that only ONE of +DM and -DM can "
            "be non-zero on any bar; computing both from the raw moves without that "
            "exclusive rule is a frequent error.",
    },
    {
        "key": "macd",
        "name": "MACD",
        "full_name": "Moving Average Convergence Divergence",
        "params": "fast = 12, slow = 26, signal = 9",
        "formula": [
            "MACD  = EMA(close, 12) - EMA(close, 26)",
            "signal = EMA(MACD, 9)",
            "histogram = MACD - signal",
        ],
        "gotcha":
            "These are standard EMAs with alpha = 2/(n+1), NOT Wilder's -- the opposite of "
            "RSI and ATR. The signal line is an EMA of the MACD line, not of price, and "
            "how its warm-up is seeded is where implementations diverge slightly in the "
            "first few dozen bars.",
    },
    {
        "key": "bbands",
        "name": "Bollinger Bands",
        "full_name": "Bollinger Bands",
        "params": "length = 5, stdev = 2 (pandas_ta defaults)",
        "formula": [
            "middle = SMA(close, n)",
            "upper  = middle + k * stdev(close, n)",
            "lower  = middle - k * stdev(close, n)",
        ],
        "gotcha":
            "Which standard deviation? Bollinger's own definition and most charting "
            "platforms use the POPULATION form (ddof = 0); pandas_ta computes the bands "
            "with pandas' .std(), which defaults to the SAMPLE form (ddof = 1). That was "
            "measured here, not assumed -- the bands were computed both ways against the "
            "same library output, and only ddof = 1 matched. Because the sample form has "
            "the smaller divisor it gives a larger deviation, so pandas_ta's bands are "
            "slightly WIDER than the classical definition, and the gap grows as the window "
            "shrinks. NumPy's np.std defaults the other way (ddof = 0), so hand-rolled "
            "NumPy code and pandas_ta disagree by default. Note also that pandas_ta 0.4.x "
            "defaults to length 5, not the conventional 20.",
    },
    {
        "key": "stoch",
        "name": "Stochastic",
        "full_name": "Stochastic Oscillator",
        "params": "k = 14, d = 3, smooth_k = 3",
        "formula": [
            "raw %K = 100 * (close - lowest_low(n)) / (highest_high(n) - lowest_low(n))",
            "%K = SMA(raw %K, smooth_k)",
            "%D = SMA(%K, d)",
        ],
        "gotcha":
            "What most references call %K is already SMOOTHED -- the unsmoothed version is "
            "'raw %K' or 'fast %K'. Reading the formula literally and comparing to a "
            "platform's %K compares two different series. The extremes also use the "
            "period's high and low, not closes.",
    },
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--db", default=str(Path(__file__).resolve().parents[1] / "data" / "market.duckdb"))
    ap.add_argument("--symbol", default="AAPL")
    ap.add_argument("--bars", type=int, default=750)
    args = ap.parse_args()

    import duckdb
    import pandas as pd
    import pandas_ta as ta

    con = duckdb.connect(args.db, read_only=True)
    df = con.execute(
        """SELECT day AS date, adj_open AS open, adj_high AS high, adj_low AS low,
                  adj_close AS close, volume
             FROM eod_prices WHERE symbol = ? ORDER BY day""", [args.symbol]).df()
    con.close()
    if df.empty:
        raise SystemExit(f"no rows for {args.symbol}")
    df = df.tail(args.bars).reset_index(drop=True)

    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)

    mine = {
        "rsi": {"RSI": own_rsi(c, 14)},
        "atr": {"ATR": own_atr(h, l, c, 14)},
        "adx": own_adx(h, l, c, 14),
        "macd": own_macd(c),
        "bbands": own_bbands(c, 5, 2.0),
        "stoch": own_stoch(h, l, c),
    }

    def ta_frame(name: str):
        fn = getattr(df.ta, name)
        out = fn()
        return out if isinstance(out, pd.DataFrame) else out.to_frame()

    theirs_raw = {
        "rsi": ta_frame("rsi"), "atr": ta_frame("atr"), "adx": ta_frame("adx"),
        "macd": ta_frame("macd"), "bbands": ta_frame("bbands"), "stoch": ta_frame("stoch"),
    }

    # Which standard-deviation convention does pandas_ta actually use? Compute the bands
    # both ways against the same library output and let the numbers decide.
    bb_ta = theirs_raw["bbands"]
    bb_col = next(c_ for c_ in bb_ta.columns if c_.startswith("BBU"))
    ddof_probe = {}
    for dd in (0, 1):
        cmp_ = compare(own_bbands(c, 5, 2.0, ddof=dd)["BBU"], bb_ta[bb_col].to_numpy(float))
        ddof_probe[f"ddof_{dd}"] = {
            "max_abs_diff": cmp_["max_abs_diff_overall"],
            "matches": cmp_["exact_throughout"],
            "label": "population (Bollinger's own definition)" if dd == 0 else "sample (pandas .std default)",
        }
    ddof_used = next((int(kk.split("_")[1]) for kk, vv in ddof_probe.items() if vv["matches"]), None)

    results = []
    for spec in SPECS:
        k = spec["key"]
        tf = theirs_raw[k]
        series_cmp = []
        for label, arr in mine[k].items():
            # pandas_ta names columns NAME_params, but the NAME itself can carry a
            # smoothing-mode suffix: ATR with Wilder smoothing is ATRr_14, not ATR_14.
            # Match the exact stem first, then allow a single trailing mode letter.
            stems = [(col, col.split("_")[0]) for col in tf.columns]
            match = ([col for col, stem in stems if stem == label]
                     or [col for col, stem in stems
                         if stem.startswith(label) and len(stem) == len(label) + 1])
            if not match:
                series_cmp.append({"series": label, "pandas_ta_column": None,
                                   "note": "no matching pandas_ta column"})
                continue
            col = match[0]
            series_cmp.append({"series": label, "pandas_ta_column": col,
                               **compare(arr, tf[col].to_numpy(float))})

        checked = [s for s in series_cmp if "agrees" in s]
        latest = {}
        for label, arr in mine[k].items():
            v = arr[~np.isnan(arr)]
            latest[label] = round(float(v[-1]), 6) if len(v) else None

        results.append({
            **{kk: vv for kk, vv in spec.items()},
            "series": series_cmp,
            "all_agree": bool(checked) and all(s["agrees"] for s in checked),
            "latest_values": latest,
        })

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pandas_ta_version": ta.version,
        "measured_on": {
            "symbol": args.symbol, "bars": len(df),
            "from": str(df["date"].iloc[0])[:10], "to": str(df["date"].iloc[-1])[:10],
        },
        "method":
            "Each formula is implemented independently here in plain NumPy from its "
            "definition, then computed again with pandas_ta on the same real bars, and the "
            "two are compared over every point where both are defined. Agreement is "
            "evidence the published formula is the one the library implements; "
            "disagreement is published as a finding rather than hidden.",
        "tolerance": "relative difference below 1e-6 against the series' own scale",
        "bollinger_stdev_convention": {
            "probe": ddof_probe,
            "pandas_ta_uses_ddof": ddof_used,
            "finding":
                "pandas_ta computes the bands with pandas' .std(), which defaults to ddof=1 "
                "-- the SAMPLE standard deviation. Bollinger's own definition and most "
                "charting platforms use the population form (ddof=0). Both were computed "
                "against the same library output; the match is measured, not assumed.",
        },
        "indicators": results,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1), encoding="utf-8")

    print(f"  Bollinger stdev convention: pandas_ta uses ddof={ddof_used}")
    agree = sum(1 for r in results if r["all_agree"])
    print(f"{agree}/{len(results)} indicators reproduce pandas_ta once warmed up, "
          f"on {len(df)} {args.symbol} bars -> {args.out}")
    for r in results:
        checked = [s for s in r["series"] if "agrees" in s]
        flag = "OK  " if r["all_agree"] else "DIFF"
        exact = all(s["exact_throughout"] for s in checked) if checked else False
        after = max((s["max_abs_diff_after_convergence"] or 0.0) for s in checked) \
            if checked else float("nan")
        warm = max((s["bars_before_convergence"] or 0) for s in checked) if checked else 0
        near = max((s["bars_to_within"].get("0.01") or 0) for s in checked) if checked else 0
        print(f"  {flag} {r['name']:<16} post-warm-up max abs diff {after:.2e}"
              + ("  exact throughout" if exact
                 else f"  warm-up {warm} bars ({near} to within 0.01)"))
        for s in checked:
            if not s["agrees"]:
                print(f"        DISAGREES {s['series']} vs {s['pandas_ta_column']}: "
                      f"max abs {s['max_abs_diff_overall']:.6g} over "
                      f"{s['comparable_points']} pts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
