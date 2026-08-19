# EOD data vendor — decision brief (plan story 1.1)

> ## SUPERSEDED IN PART — 2026-08-18, later the same day
>
> **The history limit was not a vendor limit. It was ours.**
>
> The 5,000-row cap is **per request**, not per symbol. An open-ended request silently
> truncates to the most recent ~20 years; the same key, asked in date windows, returns
> data to inception — 1993 for SPY, 1990 for the equities. The pipeline now paginates,
> the store holds **91,461 bars spanning 1990–2026**, and readiness went from
> *0 of 120 cells Robust-eligible* to **120 of 120**.
>
> Splicing was verified before it was trusted: 440 overlapping days across two windows
> matched to 1e-9, and windowed values match the un-windowed series exactly, so the
> adjustment is absolute rather than per-request. A per-request normalisation would have
> corrupted every spliced series invisibly.
>
> **Cost of the fix: nothing.** No tier upgrade, no new vendor, same API key.
>
> What this does NOT solve, and what the decision below is now only about:
> * **ETF coverage** — every ETF except SPY still returns HTTP 402, including the
>   commodity/sector seeds the plan wants for The Survivors.
> * **Equity coverage** — 33% of a mainstream large-cap sample is still gated.
> * **Survivorship** — FMP is not delisted-inclusive, and that is a validity condition
>   for published verdicts, not a footnote.
>
> And the headline result did not change: with 36 years instead of 20, **still zero
> Robust cells**. The lowest q-value improved from 0.61 to 0.216 against a 0.10
> threshold. More history made the tests sharper and the answer stayed no — which is
> the strongest evidence yet that the product's thesis is sound and that the earlier
> "we just need more data" reading was wrong.
>
> Read the rest of this document with those corrections applied.


**For Elliott. Prepared 2026-08-18 by measuring the current FMP key directly, not by
reading vendor marketing.** The pipeline is built and proven; what it can be pointed at
is now the only open question, and it decides whether the seasonality product is
possible at all.

## The original finding (now corrected)

The brief originally concluded that zero cells could ever reach `Robust` on this
entitlement. That was true of the *code as written*, not of the vendor: the request was
open-ended and silently truncated. With windowed pagination all 120 cells are
Robust-eligible. The corrected conclusion is narrower and still real: **coverage and
survivorship are worth paying for; history is not.**

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
