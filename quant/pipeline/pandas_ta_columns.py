#!/usr/bin/env python3
"""Capture the column names pandas_ta actually emits, by running it.

  python -m pipeline.pandas_ta_columns --out artefact.json

Why this exists: people search for pandas_ta column names (`BBM_20_2.0`,
`MACDS_12_26_9`) because the library appends generated suffixes and documents them
nowhere central — you are expected to read the source. The names also CHANGE between
versions: 0.3.x `bbands` defaults to length 20 and emits `BBM_20_2.0`, while 0.4.x
defaults to length 5 and emits `BBM_5_2.0_2.0`, a four-part suffix. Someone following a
2023 tutorial on a fresh install gets a KeyError and no explanation.

So this does not transcribe documentation — it runs each indicator against real OHLCV
and records what came back, tagged with the version that produced it. Run it under each
version to build a comparison.

Nothing is inferred: if an indicator raises, the error is recorded rather than the entry
being guessed or dropped silently.
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# Indicators worth documenting: the ones with non-obvious generated column names.
# A single-column indicator like RSI_14 is self-explanatory; BBANDS is not.
INDICATORS = [
    "bbands", "macd", "stoch", "stochrsi", "adx", "atr", "rsi", "ema", "sma", "wma",
    "vwap", "obv", "cci", "mfi", "willr", "psar", "supertrend", "kc", "donchian",
    "aroon", "ao", "apo", "bop", "cmf", "coppock", "dm", "efi", "eom", "kdj",
    "kst", "massi", "mom", "natr", "ppo", "pvo", "qstick", "roc", "rvi", "slope",
    "squeeze", "trix", "tsi", "uo", "vortex", "zscore",
]


def load_prices(db: str, symbol: str, bars: int):
    import duckdb
    con = duckdb.connect(db, read_only=True)
    df = con.execute(
        """
        SELECT day AS date, adj_open AS open, adj_high AS high, adj_low AS low,
               adj_close AS close, volume
          FROM eod_prices WHERE symbol = ? ORDER BY day
        """, [symbol]
    ).df()
    con.close()
    if df.empty:
        raise SystemExit(f"no rows for {symbol}")
    return df.set_index("date").tail(bars)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--db", default=str(Path(__file__).resolve().parents[1] / "data" / "market.duckdb"))
    ap.add_argument("--symbol", default="AAPL")
    ap.add_argument("--bars", type=int, default=400)
    args = ap.parse_args()

    import pandas as pd
    import pandas_ta as ta

    df = load_prices(args.db, args.symbol, args.bars)

    entries = []
    for name in INDICATORS:
        fn = getattr(df.ta, name, None)
        if fn is None:
            entries.append({"indicator": name, "ok": False, "error": "not present in this version"})
            continue
        try:
            out = fn()
            if isinstance(out, pd.DataFrame):
                cols = list(out.columns)
            elif out is None:
                entries.append({"indicator": name, "ok": False, "error": "returned None"})
                continue
            else:
                cols = [out.name]
            entries.append({"indicator": name, "ok": True, "columns": [str(c) for c in cols],
                            "n_columns": len(cols)})
        except Exception as e:  # noqa: BLE001 — the failure is the finding
            entries.append({"indicator": name, "ok": False,
                            "error": f"{type(e).__name__}: {str(e)[:120]}"})

    out = {
        "pandas_ta_version": ta.version,
        "python": sys.version.split()[0],
        "measured_on": {"symbol": args.symbol, "bars": len(df),
                        "from": str(df.index[0])[:10], "to": str(df.index[-1])[:10]},
        "indicators": entries,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1), encoding="utf-8")
    ok = sum(1 for e in entries if e["ok"])
    print(f"pandas_ta {ta.version}: {ok}/{len(entries)} indicators captured -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
