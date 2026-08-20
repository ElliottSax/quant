"""EOD price providers.

The vendor decision (plan story 1.1) is deliberately NOT baked into the pipeline.
Every provider implements the same tiny interface, so switching vendors is a config
change — set QUANT_EOD_PROVIDER and the credentials for that provider.

A provider returns ADJUSTED bars only. Unadjusted closes silently corrupt monthly
returns: AAPL's 4:1 split in Aug 2020 shows as a -75% "return" in raw closes, which
would then be published as a seasonal effect. If a vendor cannot supply adjusted
series for a symbol, the provider must raise rather than fall back to raw.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol


class ProviderError(RuntimeError):
    """Raised when a provider cannot supply usable data for a symbol."""


class EntitlementError(ProviderError):
    """The vendor recognised the request but the plan does not cover this symbol.

    Distinct from a transport failure on purpose: an entitlement gap is a
    purchasing decision, not a retry candidate.
    """


@dataclass(frozen=True)
class Bar:
    symbol: str
    day: date
    adj_open: float
    adj_high: float
    adj_low: float
    adj_close: float
    volume: float


class EodProvider(Protocol):
    name: str

    def fetch(self, symbol: str, start: date) -> list[Bar]:
        """Adjusted daily bars for symbol from start (inclusive), oldest first."""
        ...


def _get(url: str, timeout: int = 60):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code in (401, 402, 403):
            raise EntitlementError(f"HTTP {e.code} — symbol not covered by the current plan")
        raise ProviderError(f"HTTP {e.code}")
    except Exception as e:  # noqa: BLE001 - surfaced verbatim to the runner
        raise ProviderError(str(e))


class FmpProvider:
    """Financial Modeling Prep, dividend-adjusted EOD series.

    Measured limits on the key in use (2026-08-18), which the vendor brief records:
      * the 5000-row cap is PER REQUEST — windowed fetches reach inception (1993 for
        SPY), so history is NOT vendor-limited; only an open-ended request is
      * ETFs other than SPY return HTTP 402 (a genuine entitlement limit)
    Both are entitlement limits, not code limits; a higher tier lifts them without
    touching this class.
    """

    name = "fmp"
    BASE = "https://financialmodelingprep.com/stable"
    WINDOW_YEARS = 5  # comfortably inside the ~5000-row response cap (~1260 rows/5y)

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("FMP_API_KEY", "")
        if not self.api_key:
            raise ProviderError("FMP_API_KEY is not set")

    def fetch(self, symbol: str, start: date) -> list[Bar]:
        """Adjusted bars from `start` to today, paginated by date window.

        The 5,000-row response cap is PER REQUEST, not per symbol: an open-ended
        request silently truncates to the most recent ~20 years, while windowed
        requests reach inception (verified to 1993 for SPY). Splicing is safe because
        the adjustment is absolute, not relative to the requested range — 440
        overlapping days across two windows matched to 1e-9, and windowed values match
        the un-windowed series exactly. Both were checked before this was written,
        because a per-request normalisation would have corrupted every spliced series
        invisibly.
        """
        rows: dict[str, dict] = {}
        today = date.today()
        cursor = start
        dropped = 0

        while cursor <= today:
            window_end = min(date(cursor.year + self.WINDOW_YEARS, 1, 1) - timedelta(days=1), today)
            url = (
                f"{self.BASE}/historical-price-eod/dividend-adjusted"
                f"?symbol={symbol}&from={cursor.isoformat()}&to={window_end.isoformat()}"
                f"&apikey={self.api_key}"
            )
            try:
                payload = _get(url)
            except EntitlementError as e:
                # The plan does not cover this symbol at all; no window will succeed.
                raise e
            except ProviderError as e:
                # One bad window must not silently truncate the history. Surface it.
                raise ProviderError(f"window {cursor}..{window_end}: {e}")

            if isinstance(payload, list):
                for row in payload:
                    d = row.get("date")
                    if d:
                        rows[d] = row  # dedupe across overlapping window edges
            cursor = window_end + timedelta(days=1)

        payload = list(rows.values())
        if not payload:
            raise ProviderError("empty response")

        bars: list[Bar] = []
        for row in payload:
            try:
                bars.append(
                    Bar(
                        symbol=symbol,
                        day=date.fromisoformat(row["date"]),
                        adj_open=float(row["adjOpen"]),
                        adj_high=float(row["adjHigh"]),
                        adj_low=float(row["adjLow"]),
                        adj_close=float(row["adjClose"]),
                        # Volume is not used in any published statistic, so a missing
                        # value is recorded as 0 rather than dropping an otherwise-valid
                        # price bar. Every field that DOES feed a statistic is required
                        # above and raises here if absent.
                        volume=float(row.get("volume") or 0),
                    )
                )
            except (KeyError, TypeError, ValueError):
                # A malformed row is dropped, never defaulted. Padding a series with
                # invented values is the failure mode this whole pipeline exists to avoid.
                dropped += 1
                continue

        if not bars:
            raise ProviderError("no usable rows after validation")
        # Silent thinning is its own failure mode: a vendor that nulls adjClose on halted
        # days would quietly shorten the series while every gate still passed.
        if dropped and dropped > 0.01 * (len(bars) + dropped):
            raise ProviderError(
                f"{dropped} of {len(bars) + dropped} rows unusable (>1%) — refusing a thinned series"
            )
        if dropped:
            print(f"    note: {symbol} dropped {dropped} malformed row(s)")
        bars.sort(key=lambda b: b.day)
        return bars


class YFinanceProvider:
    """Yahoo Finance via the yfinance library.

    Keyless, and returns split/dividend-adjusted bars to inception in a single request
    (SPY: 8,446 rows back to 1993-01-29, measured) — so unlike the FMP adapter it needs
    no date-window pagination.

    NOT FOR PUBLISHED DATA. Yahoo has no public API — this is an internal endpoint —
    and Yahoo's terms prohibit automated collection and any commercial use outright.
    They are also actively locking it down (/v7/finance/quote now returns 401). It is
    kept for local development and for the vendor bench, where the point is to MEASURE
    a source rather than to redistribute it.

    Ingesting through it into the published store requires QUANT_ALLOW_YFINANCE_INGEST=1,
    an explicit opt-in, so it cannot become a published data source by accident.
    """

    name = "yfinance"

    def fetch(self, symbol: str, start: date) -> list[Bar]:
        if os.environ.get("QUANT_ALLOW_YFINANCE_INGEST") != "1":
            raise ProviderError(
                "yfinance is not licensed for published data (Yahoo prohibits automated "
                "and commercial use). Set QUANT_ALLOW_YFINANCE_INGEST=1 only for local "
                "development or bench measurement."
            )
        try:
            import yfinance as yf
        except ImportError:
            raise ProviderError("yfinance is not installed")

        try:
            # auto_adjust=True returns split- AND dividend-adjusted OHLC, matching the
            # series every published statistic is computed from.
            df = yf.Ticker(symbol).history(
                start=start.isoformat(), interval="1d", auto_adjust=True
            )
        except Exception as e:  # noqa: BLE001
            raise ProviderError(f"yfinance error: {e}")

        if df is None or df.empty:
            # Yahoo answers an unknown symbol with an empty frame rather than an error,
            # so emptiness is the only signal that the ticker is not covered.
            raise ProviderError("no rows returned (unknown symbol or no coverage)")

        bars: list[Bar] = []
        for ts, row in df.iterrows():
            try:
                bars.append(
                    Bar(
                        symbol=symbol,
                        day=ts.date(),
                        adj_open=float(row["Open"]),
                        adj_high=float(row["High"]),
                        adj_low=float(row["Low"]),
                        adj_close=float(row["Close"]),
                        volume=float(row.get("Volume") or 0),
                    )
                )
            except (KeyError, TypeError, ValueError):
                continue

        if not bars:
            raise ProviderError("no usable rows after validation")
        bars.sort(key=lambda b: b.day)
        return bars


def get_provider(name: str | None = None) -> EodProvider:
    name = (name or os.environ.get("QUANT_EOD_PROVIDER") or "fmp").lower()
    if name == "fmp":
        return FmpProvider()
    if name in ("yfinance", "yahoo"):
        return YFinanceProvider()
    raise ProviderError(
        f"unknown provider '{name}'. Add an adapter here rather than special-casing callers."
    )
