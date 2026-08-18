# EOD data vendor — decision brief (plan story 1.1)

**For Elliott. Prepared 2026-08-18 by measuring the current FMP key directly, not by
reading vendor marketing.** The pipeline is built and proven; what it can be pointed at
is now the only open question, and it decides whether the seasonality product is
possible at all.

## The finding in one line

On the current FMP entitlement, **zero (symbol, month) cells can ever reach `Robust`** —
so The Survivors roster, the product's flagship object, would launch empty and stay empty.

## Measured facts (all verified live today)

| Property | Measured | Consequence |
|---|---|---|
| History depth | **5,000 rows per symbol, cap-limited to 2006-10-02** (~19.9 years) | 20 observations per (symbol, calendar month) maximum |
| Adjusted prices | Available via `historical-price-eod/dividend-adjusted` | Splits handled correctly — verified: AAPL Aug-2020 (4:1 split) returns +21.7%, not a −75% artefact |
| ETF coverage | **Every ETF except SPY returns HTTP 402** — QQQ, XLE, XLF, USO, UNG, GLD, IWM all gated | The plan's Survivors seeds (commodity/sector ETFs) are unreachable |
| Equity coverage | **33% of a 24-name mainstream sample gated** (PG, MRK, IBM, MCD, CAT) | The universe cannot be chosen on merit; it is chosen by what the plan happens to cover |
| Freshness | Same-day bars available | Nightly staleness gate works |

## What that does to the statistical spec

Running `python -m pipeline.readiness` against the 50,000 bars now in the store:

```
cells:            120 (10 symbols x 12 calendar months)
max observations: 20 per cell
gradeable (n>=20):       100 / 120
Robust-eligible (n>=25):   0 / 120
```

`docs/STATS_SPEC.md` sets the Robust floor at n ≥ 25 and the gradeable floor at n ≥ 20.
Twenty years of history yields exactly 20 observations per cell. So the site could publish
`Folklore` and `Nothing Clears the Bar` verdicts — which are genuinely good content and
on-thesis — but it **could never publish a single Robust verdict, and The Survivors board
would have nothing to list.**

Do not respond to this by lowering the threshold. Tuning the floor to fit the data on hand
is the exact p-hacking the spec was written to prevent, and the honesty of the tiers is the
entire moat.

## The options, with what each buys

1. **Upgrade FMP.** Cheapest path if a higher tier lifts both the 5,000-row cap and the
   ETF/equity gating — but *verify both before paying*, since today's evidence is that
   coverage, not just depth, is entitlement-limited. Consolidates one vendor for congress
   + prices, which also simplifies story 5.1.
2. **Norgate (~$60/mo, the plan's suggestion).** Delisted-inclusive, 30+ years, full ETF
   coverage. Solves history, survivorship, and ETF seeds in one purchase. Highest
   confidence, highest fixed cost, Windows-native (fits the compute plane).
3. **Tiingo / EODHD.** Mid-priced, deep history, broad ETF coverage; survivorship handling
   needs checking per vendor.
4. **Restrict the product to what SPY-only data supports.** Free, but the seasonality
   product becomes a single-symbol curiosity — not a site.

## Recommendation

**Option 2 (Norgate), unless a quick check shows FMP's next tier lifts both limits.** The
deciding factor is not price, it is that survivorship-inclusive 30-year history is a
validity condition for the verdicts, not a nice-to-have: the spec requires the survivorship
branch to be stated on every page, and "we used a survivorship-biased universe" is a
statement that undermines the one thing the site sells.

Whichever is chosen, the switch is a config change — `QUANT_EOD_PROVIDER` plus credentials.
The adapter interface in `pipeline/providers.py` was built for exactly this decision, and
the FMP adapter stays as the congress-side and fallback provider.

## What is already done and waiting

- `pipeline/` — provider adapter, DuckDB store with provenance, nightly runner with the
  clean-night gate (exit code 0/1), and the readiness check above.
- Proven end to end: **50,000 bars, 10 symbols, CLEAN NIGHT, exit 0**, split adjustment
  verified against a known corporate action.
- The moment a vendor is chosen, the same commands run against the real universe.
