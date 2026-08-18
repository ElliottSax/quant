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
from datetime import date
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
      * 5000-row cap per request => history begins 2006-10-02 (~19.9y)
      * ETFs other than SPY return HTTP 402
    Both are entitlement limits, not code limits; a higher tier lifts them without
    touching this class.
    """

    name = "fmp"
    BASE = "https://financialmodelingprep.com/stable"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("FMP_API_KEY", "")
        if not self.api_key:
            raise ProviderError("FMP_API_KEY is not set")

    def fetch(self, symbol: str, start: date) -> list[Bar]:
        url = (
            f"{self.BASE}/historical-price-eod/dividend-adjusted"
            f"?symbol={symbol}&from={start.isoformat()}&apikey={self.api_key}"
        )
        payload = _get(url)
        if not isinstance(payload, list) or not payload:
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
                        volume=float(row.get("volume") or 0),
                    )
                )
            except (KeyError, TypeError, ValueError):
                # A malformed row is dropped, never defaulted. Padding a series with
                # invented values is the failure mode this whole pipeline exists to avoid.
                continue

        if not bars:
            raise ProviderError("no usable rows after validation")
        bars.sort(key=lambda b: b.day)
        return bars


def get_provider(name: str | None = None) -> EodProvider:
    name = (name or os.environ.get("QUANT_EOD_PROVIDER") or "fmp").lower()
    if name == "fmp":
        return FmpProvider()
    raise ProviderError(
        f"unknown provider '{name}'. Add an adapter here rather than special-casing callers."
    )
