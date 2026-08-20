#!/usr/bin/env python3
"""Measure which statsmodels import paths actually work, by importing them.

    python -m pipeline.statsmodels_imports --out ../frontend/public/data/statsmodels-imports.json

Why this exists: Search Console shows this site surfacing around position 8-10 for
`from statsmodels.tsa.api import arima` on 132 impressions with ZERO clicks. That query
is a person with an ImportError traceback open. They need one line: the path that works.
The same pattern covers `coint_johansen`, whose import path is genuinely obscure and
which almost every tutorial gets wrong or writes from an older layout.

So this does not transcribe documentation -- it ATTEMPTS each import and records what
happened, tagged with the version that produced it. A path that raises is recorded with
its real exception text, because "this one fails and here is the error you are seeing"
is the answer the searcher needs in order to recognise their own problem.

Return shapes are captured the same way: by calling the thing on real data and recording
what came back. `coint_johansen` in particular returns an object whose attributes
(`lr1`, `cvt`, `evec`) are undocumented in any obvious place and are the actual reason
people search for it.
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
import warnings
from datetime import datetime, timezone
from pathlib import Path

warnings.filterwarnings("ignore")

# (label, module, symbol). Both the paths people TRY and the paths that WORK -- a
# reference that omits the failing form cannot be matched against a traceback.
CANDIDATES = [
    ("ARIMA", "statsmodels.tsa.api", "ARIMA"),
    ("ARIMA", "statsmodels.tsa.arima.model", "ARIMA"),
    ("ARIMA", "statsmodels.tsa.arima_model", "ARIMA"),
    ("SARIMAX", "statsmodels.tsa.statespace.sarimax", "SARIMAX"),
    ("SARIMAX", "statsmodels.tsa.api", "SARIMAX"),
    ("coint_johansen", "statsmodels.tsa.vector_ar.vecm", "coint_johansen"),
    ("coint_johansen", "statsmodels.tsa.johansen", "coint_johansen"),
    ("coint_johansen", "statsmodels.tsa.api", "coint_johansen"),
    ("coint (Engle-Granger)", "statsmodels.tsa.stattools", "coint"),
    ("adfuller", "statsmodels.tsa.stattools", "adfuller"),
    ("kpss", "statsmodels.tsa.stattools", "kpss"),
    ("acf / pacf", "statsmodels.tsa.stattools", "acf"),
    ("grangercausalitytests", "statsmodels.tsa.stattools", "grangercausalitytests"),
    ("VECM", "statsmodels.tsa.vector_ar.vecm", "VECM"),
    ("VAR", "statsmodels.tsa.api", "VAR"),
    ("seasonal_decompose", "statsmodels.tsa.seasonal", "seasonal_decompose"),
    ("STL", "statsmodels.tsa.seasonal", "STL"),
    ("OLS", "statsmodels.api", "OLS"),
    ("add_constant", "statsmodels.api", "add_constant"),
    ("het_breuschpagan", "statsmodels.stats.diagnostic", "het_breuschpagan"),
    ("acorr_ljungbox", "statsmodels.stats.diagnostic", "acorr_ljungbox"),
    ("variance_inflation_factor", "statsmodels.stats.outliers_influence", "variance_inflation_factor"),
    ("ExponentialSmoothing", "statsmodels.tsa.holtwinters", "ExponentialSmoothing"),
    ("multipletests (FDR)", "statsmodels.stats.multitest", "multipletests"),
]


def try_import(module: str, symbol: str) -> dict:
    entry = {"statement": f"from {module} import {symbol}", "module": module, "symbol": symbol}
    try:
        mod = __import__(module, fromlist=[symbol])
    except Exception as e:  # noqa: BLE001 -- the failure IS the finding
        entry.update(ok=False, error=f"{type(e).__name__}: {str(e).splitlines()[0][:200]}")
        return entry
    if not hasattr(mod, symbol):
        entry.update(
            ok=False,
            error=f"ImportError: cannot import name '{symbol}' from '{module}'",
        )
        return entry
    obj = getattr(mod, symbol)
    entry.update(ok=True, kind=type(obj).__name__,
                 qualname=getattr(obj, "__module__", "") + "." + getattr(obj, "__qualname__", symbol))
    return entry


# Import statements that SUCCEED but hand back the wrong object, so the traceback
# appears further down where nothing looks wrong. This is the actual reason people
# search for the ARIMA import error, and no reference documents it, because a reference
# built from documentation cannot see it -- only running the code can.
DEFERRED_FAILURES = [
    ("from statsmodels.tsa.arima.model import ARIMA",
     "statsmodels.tsa.arima.model", "ARIMA", "instantiate"),
    ("from statsmodels.tsa.api import ARIMA",
     "statsmodels.tsa.api", "ARIMA", "instantiate"),
    ("from statsmodels.tsa.api import arima",
     "statsmodels.tsa.api", "arima", "call"),
    ("from statsmodels.tsa.arima_model import ARIMA",
     "statsmodels.tsa.arima_model", "ARIMA", "instantiate"),
]


def probe_deferred() -> list[dict]:
    """Import each form, then USE it, and record where it actually breaks."""
    import numpy as np

    y = np.cumsum(np.ones(120)) + np.linspace(0, 1, 120)
    out = []
    for stmt, module, symbol, how in DEFERRED_FAILURES:
        rec = {"statement": stmt, "used_by": how}
        try:
            mod = __import__(module, fromlist=[symbol])
            obj = getattr(mod, symbol)
        except Exception as e:  # noqa: BLE001
            out.append(rec | {"imports": False, "usable": False,
                              "object": None,
                              "error": f"{type(e).__name__}: {str(e).splitlines()[0][:200]}"})
            continue
        rec["imports"] = True
        rec["object"] = ("module" if type(obj).__name__ == "module"
                         else f"{type(obj).__name__} {getattr(obj, '__module__', '')}."
                              f"{getattr(obj, '__qualname__', symbol)}")
        try:
            obj(y, order=(1, 1, 1))
            out.append(rec | {"usable": True, "error": None})
        except Exception as e:  # noqa: BLE001
            msg = " ".join(str(e).split())
            out.append(rec | {"usable": False,
                              "error": f"{type(e).__name__}: {msg[:260]}"})
    return out


def load_prices(db: str, symbols: list[str], bars: int):
    import duckdb
    con = duckdb.connect(db, read_only=True)
    out = {}
    for s in symbols:
        df = con.execute(
            "SELECT day AS date, adj_close AS close FROM eod_prices WHERE symbol = ? ORDER BY day",
            [s],
        ).df()
        if not df.empty:
            out[s] = df.set_index("date")["close"].tail(bars)
    con.close()
    return out


def measure_johansen(series: dict) -> dict:
    """Run coint_johansen on real prices and record the object it returns."""
    import numpy as np
    from statsmodels.tsa.vector_ar.vecm import coint_johansen

    names = [s for s in series if len(series[s]) > 100][:2]
    if len(names) < 2:
        return {"ok": False, "error": "needs two price series with enough history"}
    a, b = series[names[0]], series[names[1]]
    idx = a.index.intersection(b.index)
    data = np.column_stack([a.loc[idx].to_numpy(float), b.loc[idx].to_numpy(float)])

    res = coint_johansen(data, det_order=0, k_ar_diff=1)
    attrs = sorted(x for x in dir(res) if not x.startswith("_"))
    return {
        "ok": True,
        "pair": names,
        "observations": int(data.shape[0]),
        "from": str(idx[0])[:10],
        "to": str(idx[-1])[:10],
        "call": "coint_johansen(data, det_order=0, k_ar_diff=1)",
        "returns_type": type(res).__name__,
        "attributes": attrs,
        "trace_stat_lr1": [round(float(v), 4) for v in res.lr1],
        "trace_crit_cvt": [[round(float(c), 4) for c in row] for row in res.cvt],
        "max_eig_lr2": [round(float(v), 4) for v in res.lr2],
        "max_eig_crit_cvm": [[round(float(c), 4) for c in row] for row in res.cvm],
        "eigenvalues": [round(float(v), 6) for v in res.eig],
        "crit_columns": ["90%", "95%", "99%"],
        "reading":
            "lr1 holds the TRACE statistic for r=0, r<=1, ... and cvt the matching critical "
            "values at 90/95/99%. Reject the null of at most r cointegrating relations when "
            "lr1[r] exceeds cvt[r][1] for the 95% level. lr2/cvm are the maximum-eigenvalue "
            "form of the same test. There are no p-values -- only these critical values, "
            "which is the single most common source of confusion with this function.",
    }


def measure_arima(series: dict) -> dict:
    from statsmodels.tsa.arima.model import ARIMA

    name = next((s for s in series if len(series[s]) > 200), None)
    if name is None:
        return {"ok": False, "error": "no series with enough history"}
    y = series[name].to_numpy(float)[-300:]
    fit = ARIMA(y, order=(1, 1, 1)).fit()
    return {
        "ok": True,
        "symbol": name,
        "observations": len(y),
        "call": "ARIMA(y, order=(1, 1, 1)).fit()",
        "returns_type": type(fit).__name__,
        "aic": round(float(fit.aic), 4),
        "bic": round(float(fit.bic), 4),
        "params": {k: round(float(v), 6) for k, v in zip(fit.param_names, fit.params)},
        "forecast_3": [round(float(v), 4) for v in fit.forecast(3)],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--db", default=str(Path(__file__).resolve().parents[1] / "data" / "market.duckdb"))
    ap.add_argument("--symbols", default="AAPL,MSFT")
    ap.add_argument("--bars", type=int, default=1000)
    args = ap.parse_args()

    import statsmodels

    results = [try_import(m, s) | {"label": label} for label, m, s in CANDIDATES]
    ok = sum(1 for r in results if r["ok"])

    series = load_prices(args.db, args.symbols.split(","), args.bars)
    measured: dict[str, dict] = {}
    for name, fn in (("coint_johansen", measure_johansen), ("arima", measure_arima)):
        try:
            measured[name] = fn(series)
        except Exception as e:  # noqa: BLE001
            measured[name] = {"ok": False,
                              "error": f"{type(e).__name__}: {str(e)[:200]}",
                              "traceback_tail": traceback.format_exc().splitlines()[-1]}

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "statsmodels_version": statsmodels.__version__,
        "python": sys.version.split()[0],
        "imports": results,
        "deferred_failures": probe_deferred(),
        "measured": measured,
        "method":
            "Each import statement was executed in this interpreter and its outcome recorded. "
            "Failing paths are kept with their real exception text so a reader can match the "
            "traceback they are looking at. Return shapes come from calling the function on "
            "real daily price data, not from documentation.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"statsmodels {statsmodels.__version__}: {ok}/{len(results)} import paths work "
          f"-> {args.out}")
    for r in results:
        if not r["ok"]:
            print(f"  FAILS: {r['statement']}\n         {r['error']}")
    for k, v in measured.items():
        print(f"  measured {k}: ok={v.get('ok')}" + ("" if v.get("ok") else f" ({v.get('error')})"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
