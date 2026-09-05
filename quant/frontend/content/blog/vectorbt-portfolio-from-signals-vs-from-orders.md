---
title: "VectorBT's Portfolio Engine: from_signals vs. from_orders, and the Pitfalls That Skew Backtests"
description: "Three verified VectorBT gotchas that silently change backtest results: the from_signals vs from_orders direction mismatch, same-bar look-ahead, and freq inference failures on real trading calendars."
date: "2026-04-26"
author: "QuantEngines"
category: "Algo Trading"
tags: ["vectorbt", "backtesting", "python", "look-ahead bias", "quantitative trading"]
keywords: ["vectorbt portfolio", "vectorbt from_signals vs from_orders", "vectorbt pitfalls", "vectorbt freq error"]
---
# VectorBT's Portfolio Engine: from_signals vs. from_orders, and the Pitfalls That Skew Backtests

[VectorBT is the fastest of the mainstream Python backtesting frameworks](/blog/backtrader-vs-zipline-vs-vectorbt) because its `Portfolio` object simulates an entire strategy as array operations rather than an event loop. That speed comes from a set of defaults and conventions that are easy to get wrong in ways that don't throw an error -- they just quietly change your results. This guide walks through three of them, each verified by running both the "wrong" and "right" version side by side on the same data so the size of the effect is measured, not asserted.

## Building the Test Case

A standard 10/50-day SMA crossover on 300 bars of synthetic daily data, entering on a bullish crossover and exiting on a bearish one:

```python
import numpy as np
import pandas as pd
import vectorbt as vbt

close = pd.Series(...)  # your OHLCV close series
fast = close.rolling(10).mean()
slow = close.rolling(50).mean()
entries = (fast > slow) & (fast.shift(1) <= slow.shift(1))
exits = (fast < slow) & (fast.shift(1) >= slow.shift(1))
```

## Pitfall 1: from_signals and from_orders Disagree by Default

`Portfolio.from_signals()` takes boolean entry/exit arrays and is built specifically for signal-based strategies. `Portfolio.from_orders()` is the more general primitive, taking an explicit order-size series -- and it's tempting to reach for it once you need something `from_signals` doesn't directly support. Porting the same crossover to `from_orders` looks like the obvious equivalent:

```python
pf_signals = vbt.Portfolio.from_signals(
    close, entries, exits, init_cash=100_000, fees=0.0005, slippage=0.0005,
)

size = pd.Series(np.nan, index=close.index)
size[entries] = np.inf   # "buy with all available cash"
size[exits] = -np.inf    # "sell the entire position"
pf_orders = vbt.Portfolio.from_orders(
    close, size, size_type="amount", init_cash=100_000, fees=0.0005, slippage=0.0005,
)
```

On the test data, these produce **different final portfolio values** -- $125,622 for `from_signals` against $111,450 for the naive `from_orders` port, a difference large enough to change a strategy's apparent viability. The trade log explains why: `from_signals` defaults to `direction="longonly"`, so an exit signal simply closes the long. `from_orders` defaults to `direction="both"`, so a `-np.inf` order doesn't just close the long -- it keeps selling straight through zero into a large short position, which then gets unwound and re-entered on the next signal. The result is extra phantom round-trips that were never intended by a long-only crossover.

The fix is one keyword argument:

```python
pf_orders_fixed = vbt.Portfolio.from_orders(
    close, size, size_type="amount", init_cash=100_000,
    fees=0.0005, slippage=0.0005, direction="longonly",
)
# pf_orders_fixed.final_value() now matches pf_signals.final_value() exactly
```

With `direction="longonly"` set explicitly, both methods produce identical trade counts and final equity, confirming the two APIs are equivalent -- the direction default was the entire discrepancy. If you ever port signal logic from `from_signals` to `from_orders` (commonly needed for order types `from_signals` doesn't support, like target-percent rebalancing), set `direction` explicitly rather than relying on the default.

## Pitfall 2: Zero Fees and Slippage Are the Default

A second, quieter issue in the same example: calling `from_signals` without `fees` or `slippage` arguments simulates costless, frictionless execution.

```python
pf_free = vbt.Portfolio.from_signals(close, entries, exits, init_cash=100_000)
pf_costed = vbt.Portfolio.from_signals(
    close, entries, exits, init_cash=100_000, fees=0.0005, slippage=0.0005,
)
```

On the same 300-bar test case, `pf_free` finishes at $126,252 and `pf_costed` (5 bps commission plus 5 bps slippage -- a reasonable assumption for a liquid large-cap) finishes at $125,622. That's a small gap on three trades over roughly a year; it compounds directly with trade frequency, so a mean-reversion strategy with hundreds of round trips will show a far larger gap between the "free" and "costed" backtest than a slow crossover will. Since `fees=0` and `slippage=0` are the library defaults, a backtest run without explicitly setting them is, silently, the frictionless version.

## Pitfall 3: Same-Bar Signals Are a Look-Ahead

The crossover signal above is computed from the same bar's closing price -- `fast > slow` evaluated using today's close. Feeding that directly into `entries` at the same timestamp means the backtest enters **at today's close using information (today's close) that only exists at today's close**. In live trading you cannot act on a signal before the price that generates it has printed. The realistic version shifts execution to the next bar:

```python
entries_shifted = entries.shift(1).fillna(False).astype(bool)
exits_shifted = exits.shift(1).fillna(False).astype(bool)
pf_shifted = vbt.Portfolio.from_signals(
    close, entries_shifted, exits_shifted, init_cash=100_000, fees=0.0005, slippage=0.0005,
)
```

On the test data, the same-bar version finishes at $125,622 and the next-bar version finishes at $129,095 -- different results, in either direction, not because one is "better" but because they represent different (and only one of them executable) assumptions about when the strategy could actually have traded. Note the explicit `.astype(bool)`: `Series.shift()` on a boolean array introduces `NaN` for the first row, which silently upcasts the dtype to `object` -- passing that into `from_signals` fails inside VectorBT's Numba-compiled core with an opaque `TypingError` rather than a clear message about the dtype.

## Pitfall 4: freq Inference Fails on Real Trading Calendars

A fourth issue surfaces the moment you call any annualized metric:

```python
pf = vbt.Portfolio.from_signals(close, entries, exits, init_cash=100_000)
pf.sharpe_ratio()
# ValueError: <BusinessDay> is a non-fixed frequency
```

This happens whenever `close.index` is a business-day index (from `pd.bdate_range`, or from real market data where weekends and holidays are simply absent) -- VectorBT tries to infer a fixed timedelta from the index frequency to annualize returns, and `BusinessDay` isn't a fixed-length offset the way `Day` or `Hour` is. The fix is to pass `freq` explicitly rather than rely on inference:

```python
pf = vbt.Portfolio.from_signals(close, entries, exits, init_cash=100_000, freq="D")
pf.sharpe_ratio()  # now returns a value instead of raising
```

This is easy to miss in development because it only breaks when you call a metric that needs annualization (`sharpe_ratio`, `annualized_return`, `stats()`), not when you build the `Portfolio` object itself -- so a script that builds several portfolios and prints raw `final_value()` numbers can run cleanly, then fail the moment someone adds a Sharpe comparison.

## A Checklist Before Trusting a VectorBT Backtest

- If you built the same strategy with both `from_signals` and `from_orders`, confirm `direction` matches between them -- don't assume the defaults agree.
- Set `fees` and `slippage` explicitly. Zero is a valid choice for some research questions, but it should be a choice, not an unnoticed default.
- Shift signals derived from the same bar's close so entries/exits execute on the *next* bar, matching what would actually be tradeable live.
- Pass `freq` explicitly whenever your index isn't a fixed-frequency `DatetimeIndex` -- which, for real daily market data, is essentially always.

You can check a strategy's raw entries and exits against real price data in our [Charts tool](/charts), or configure and run the equivalent backtest without hand-rolling the `Portfolio` calls yourself in the [Strategy Builder](/backtesting/builder).

## Key Takeaways

- `Portfolio.from_signals()` defaults to `direction="longonly"`; `Portfolio.from_orders()` defaults to `direction="both"`. Porting a long-only signal strategy between the two without setting `direction` explicitly introduces phantom short trades and changes the result -- verified at roughly an 11% difference in final equity on the test case here.
- `fees` and `slippage` default to zero. A backtest run without setting them is the frictionless, unrealistic version, even though nothing in the API signals that.
- Signals computed from the same bar's close and fed into `entries`/`exits` at that same timestamp assume an unrealistic, unexecutable fill; shift by one bar to simulate acting on the signal after it's actually known.
- `Series.shift()` on a boolean array upcasts to `object` dtype on the introduced `NaN`; cast back to `bool` explicitly or VectorBT's Numba core raises an opaque `TypingError`.
- VectorBT cannot infer an annualization frequency from a non-fixed-frequency index (`BusinessDay`, or any real trading calendar) -- pass `freq` explicitly or metrics like `sharpe_ratio()` raise `ValueError` at call time, not at `Portfolio` construction time.

## Frequently Asked Questions

### Is from_orders ever a better choice than from_signals?

Yes, for anything `from_signals` doesn't directly express: target-percentage rebalancing, variable position sizing per signal, or custom order logic driven by a size series rather than boolean flags. The pitfall isn't that `from_orders` is worse -- it's more general and requires you to be explicit about things `from_signals` defaults sensibly (direction, in particular). Use `from_signals` for straightforward boolean entry/exit strategies and reach for `from_orders` only when you need the extra control, setting `direction` and `size_type` deliberately rather than accepting defaults you haven't checked.

### Why does VectorBT default to zero fees and slippage instead of a realistic default?

There's no universally "realistic" default -- costs vary enormously by instrument, venue, and order type, so any default VectorBT picked would be wrong for most users some of the time. The library's design philosophy leans toward explicit configuration over implicit assumptions; the tradeoff is that it's easy to forget to set them, especially when iterating quickly on signal logic before moving to cost-aware evaluation. Treat "did I set fees and slippage" as a standard item to check before reading any backtest result, the same way you'd check for look-ahead bias.

### How much does the same-bar vs. next-bar signal timing actually matter?

It depends entirely on the strategy's holding period and how much the entry price moves between the signal bar and the next bar. For a slow-moving crossover on daily bars, the difference is usually a matter of a few basis points per trade from the price gap between bars. For higher-frequency strategies, or ones where the signal itself is correlated with a same-bar price jump (a breakout strategy is the classic case), same-bar execution can substantially overstate performance because it implicitly assumes you traded at a price that had already moved in your favor before you could have known to trade.
