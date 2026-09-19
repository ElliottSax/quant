"""
Regression tests for the backtesting engine.

Each test here corresponds to a defect that was live in production on
2026-09-19 and that the existing suite did not catch. They are written against
deterministic synthetic price data (no yfinance, no network) so they stay
reproducible.
"""

import pandas as pd
import pytest

from app.services.backtesting import BacktestEngine, OrderStatus


def _ramp_frame(n: int = 60) -> pd.DataFrame:
    """Price ramps 100 -> 129 then falls back, so a buy and a later sell both fire."""
    prices = [100 + i for i in range(n // 2)] + [100 + (n // 2) - 1 - i for i in range(n // 2)]
    return pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=n, freq="D"),
        "open": prices,
        "high": [p + 1 for p in prices],
        "low": [p - 1 for p in prices],
        "close": prices,
        "volume": [1_000_000] * n,
    })


def _flat_frame(n: int = 60) -> pd.DataFrame:
    """Perfectly flat price series."""
    return pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=n, freq="D"),
        "open": [100.0] * n,
        "high": [100.0] * n,
        "low": [100.0] * n,
        "close": [100.0] * n,
        "volume": [1_000_000] * n,
    })


def _buy_then_sell(buy_at: int = 20, sell_at: int = 45, qty: float = 10):
    async def strategy(data: pd.DataFrame):
        if len(data) == buy_at:
            return {"type": "buy", "quantity": qty}
        if len(data) == sell_at:
            return {"type": "sell", "quantity": qty}
        return None
    return strategy


def _never_trades():
    async def strategy(data: pd.DataFrame):
        return None
    return strategy


def _as_dict(result):
    return result if isinstance(result, dict) else result.__dict__


@pytest.mark.asyncio
async def test_orders_are_keyed_by_ticker_not_row_number():
    """
    Regression: _process_signal used `bar.name` as the symbol. run_backtest calls
    `reset_index(drop=True)` first, so `bar.name` is the integer ROW NUMBER. Every
    order therefore got a different "symbol" (e.g. 19 and 44 for a buy and a sell),
    and orders/positions were keyed by row index instead of the ticker.
    """
    engine = BacktestEngine(initial_capital=100_000)
    await engine.run_backtest("AAPL", _ramp_frame(), _buy_then_sell())

    assert [o.symbol for o in engine.orders] == ["AAPL", "AAPL"]
    assert all(isinstance(o.symbol, str) for o in engine.orders)


@pytest.mark.asyncio
async def test_sell_closes_the_position_its_buy_opened():
    """
    Regression: because buy and sell got different row-number "symbols", the sell
    looked up a position that did not exist and was silently REJECTED. Every
    round-trip backtest dropped its exits and reported only the entry.
    """
    engine = BacktestEngine(initial_capital=100_000)
    result = _as_dict(await engine.run_backtest("AAPL", _ramp_frame(), _buy_then_sell()))

    statuses = [o.status for o in engine.orders]
    assert statuses == [OrderStatus.FILLED, OrderStatus.FILLED], (
        f"exit order did not fill: {statuses}"
    )
    assert result["total_trades"] == 2
    # Position fully closed, so nothing is left held at the end of the run.
    assert "AAPL" not in engine.positions


@pytest.mark.asyncio
async def test_flat_equity_curve_yields_zero_sharpe_not_astronomical():
    """
    Regression: the guard was `np.std(excess_returns) > 0`. When nothing ever
    fills, the equity curve is flat, every return is exactly 0.0, and np.std of
    that constant array is floating-point noise (~1e-18) rather than a clean 0.
    That passed `> 0` and divided a nonzero mean by ~1e-18 -- production returned
    sharpe_ratio = -9.296285203407621e+16 for a do-nothing backtest.
    """
    engine = BacktestEngine(initial_capital=100_000)
    result = _as_dict(await engine.run_backtest("AAPL", _flat_frame(), _never_trades()))

    assert result["total_trades"] == 0
    assert result["sharpe_ratio"] == 0.0
    assert result["sortino_ratio"] == 0.0
    assert abs(result["total_return"]) < 1e-9


@pytest.mark.asyncio
async def test_unaffordable_order_is_rejected_with_a_stated_reason():
    """
    Regression: an order too large for the cash balance was rejected by a bare
    `return`, leaving no trace. The response was indistinguishable from "the
    strategy never fired" -- both surfaced as 0 trades on a flat equity curve.
    """
    # 100 shares at ~119 needs ~11.9k; give the engine 1k so it cannot fill.
    engine = BacktestEngine(initial_capital=1_000)
    await engine.run_backtest("AAPL", _ramp_frame(), _buy_then_sell(qty=100))

    assert engine.orders[0].status == OrderStatus.REJECTED
    assert len(engine.rejected_orders) >= 1
    rejected_order, reason = engine.rejected_orders[0]
    assert rejected_order is engine.orders[0]
    assert "insufficient cash" in reason


@pytest.mark.asyncio
async def test_reset_clears_symbol_and_rejections_between_runs():
    """State must not leak from one run into the next."""
    engine = BacktestEngine(initial_capital=1_000)
    await engine.run_backtest("AAPL", _ramp_frame(), _buy_then_sell(qty=100))
    assert engine.rejected_orders

    await engine.run_backtest("MSFT", _ramp_frame(), _never_trades())
    assert engine.rejected_orders == []
    assert engine.orders == []
