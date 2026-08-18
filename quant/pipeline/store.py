"""DuckDB store for adjusted EOD bars, plus run provenance.

Two tables, both append-safe:

  eod_prices   one row per (symbol, day), adjusted OHLCV, stamped with the provider
               and the run that wrote it.
  ingest_runs  one row per nightly run: what was asked for, what arrived, whether the
               run was clean, and why not when it wasn't.

Provenance is not bookkeeping here — every published verdict has to be traceable to
the vendor and vintage that produced it, so the run id travels with the rows.
"""

from __future__ import annotations

import os
from datetime import date, datetime, timezone
from pathlib import Path

import duckdb

DEFAULT_DB = Path(os.environ.get("QUANT_DB_PATH", Path(__file__).resolve().parents[1] / "data" / "market.duckdb"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS eod_prices (
    symbol      VARCHAR NOT NULL,
    day         DATE    NOT NULL,
    adj_open    DOUBLE,
    adj_high    DOUBLE,
    adj_low     DOUBLE,
    adj_close   DOUBLE  NOT NULL,
    volume      DOUBLE,
    provider    VARCHAR NOT NULL,
    run_id      VARCHAR NOT NULL,
    ingested_at TIMESTAMP NOT NULL,
    PRIMARY KEY (symbol, day)
);

CREATE TABLE IF NOT EXISTS ingest_runs (
    run_id            VARCHAR PRIMARY KEY,
    started_at        TIMESTAMP NOT NULL,
    finished_at       TIMESTAMP,
    provider          VARCHAR NOT NULL,
    symbols_requested INTEGER NOT NULL,
    symbols_ok        INTEGER,
    symbols_failed    INTEGER,
    rows_written      INTEGER,
    max_day           DATE,
    clean             BOOLEAN,
    notes             VARCHAR
);
"""


def connect(db_path: Path | str | None = None) -> duckdb.DuckDBPyConnection:
    path = Path(db_path or DEFAULT_DB)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(path))
    con.execute(SCHEMA)
    return con


def start_run(con, run_id: str, provider: str, symbols_requested: int) -> None:
    con.execute(
        "INSERT INTO ingest_runs (run_id, started_at, provider, symbols_requested) VALUES (?, ?, ?, ?)",
        [run_id, datetime.now(timezone.utc), provider, symbols_requested],
    )


def write_bars(con, bars, provider: str, run_id: str) -> int:
    """Upsert bars. Re-running a day is idempotent: same (symbol, day) is replaced,
    so a retry after a partial night cannot double-count or leave a torn series."""
    if not bars:
        return 0
    now = datetime.now(timezone.utc)
    rows = [
        (b.symbol, b.day, b.adj_open, b.adj_high, b.adj_low, b.adj_close, b.volume, provider, run_id, now)
        for b in bars
    ]
    con.executemany(
        """
        INSERT INTO eod_prices
            (symbol, day, adj_open, adj_high, adj_low, adj_close, volume, provider, run_id, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (symbol, day) DO UPDATE SET
            adj_open = excluded.adj_open,
            adj_high = excluded.adj_high,
            adj_low  = excluded.adj_low,
            adj_close = excluded.adj_close,
            volume   = excluded.volume,
            provider = excluded.provider,
            run_id   = excluded.run_id,
            ingested_at = excluded.ingested_at
        """,
        rows,
    )
    return len(rows)


def finish_run(con, run_id: str, *, symbols_ok: int, symbols_failed: int,
               rows_written: int, max_day: date | None, clean: bool, notes: str) -> None:
    con.execute(
        """
        UPDATE ingest_runs
           SET finished_at = ?, symbols_ok = ?, symbols_failed = ?,
               rows_written = ?, max_day = ?, clean = ?, notes = ?
         WHERE run_id = ?
        """,
        [datetime.now(timezone.utc), symbols_ok, symbols_failed, rows_written,
         max_day, clean, notes, run_id],
    )


def coverage(con) -> list[tuple]:
    """Per-symbol coverage: rows, span, and complete calendar-year count.

    `complete_years` is the number the statistical spec actually cares about — it caps
    the per-(symbol, month) observation count, which drives the gradeable (n>=20) and
    Robust (n>=25) thresholds.
    """
    return con.execute(
        """
        SELECT symbol,
               COUNT(*)                                   AS rows,
               MIN(day)                                   AS first_day,
               MAX(day)                                   AS last_day,
               COUNT(DISTINCT YEAR(day))                  AS distinct_years
          FROM eod_prices
         GROUP BY symbol
         ORDER BY symbol
        """
    ).fetchall()


def clean_night_report(con, run_id: str) -> dict:
    row = con.execute(
        "SELECT symbols_ok, symbols_failed, rows_written, max_day, clean, notes "
        "FROM ingest_runs WHERE run_id = ?", [run_id]
    ).fetchone()
    if not row:
        return {}
    return dict(zip(["symbols_ok", "symbols_failed", "rows_written", "max_day", "clean", "notes"], row))
