# Reference check — SPY January (spec §9)

Spec `docs/STATS_SPEC.md` §9 requires one cell computed outside the engine and compared
to it, recorded here, because "an unrecorded check counts as no check."

**Status:** third-path check PASSED 2026-08-18 (agent), re-verified under spec v0.3. Elliott's hand-computation of the
same cell is still outstanding and remains part of the Sprint 2 gate — a check computed by
the same author who wrote the engine is weaker evidence than one computed by a person with
a spreadsheet, which is the point of §9.

## Data vintage

| | |
|---|---|
| Symbol / cell | SPY, calendar month January |
| Store | `quant/data/market.duckdb`, 50,000 adjusted bars, 10 symbols |
| Span | 2006-10-02 → 2026-08-18 (provider FMP, dividend-adjusted series) |
| Spec version | 0.3 (trailing partial month excluded, so n_other = 217) |

## Third-path computation

Computed with raw SQL plus Python's `statistics` module — no numpy, no shared code with
either engine, written separately from both.

| Statistic | Independent path | Engine A | Agreement |
|---|---|---|---|
| n (January) | 20 | 20 | exact |
| n (other months) | 217 | 217 | exact |
| mean(January) | 0.0026950351 | 0.0026950351 | to 1e-10 |
| mean(other) | 0.0103358034 | 0.0103358034 | to 1e-10 |
| difference | −0.0076407683 | −0.0076407683 | to 1e-10 |
| Welch t | −0.7175915622 | −0.7175915622 | to 1e-10 |

Engine-only statistics (no independent path — these are what Elliott's review must
scrutinise on the code rather than the number): `p_perm` 0.455854, 95% bootstrap CI
[−0.0283285814, 0.0125571507], `q_value` 0.683782, tier **Folklore**, boundary rule not
triggered. Cross-checked against independently written implementation B: 120/120 tiers agree.

## The January returns behind it

```
2007 +1.50   2008 -6.05   2009 -8.20   2010 -3.63   2011 +2.33
2012 +4.65   2013 +5.12   2014 -3.52   2015 -2.96   2016 -4.98
2017 +1.79   2018 +5.64   2019 +8.01   2020 -0.04   2021 -1.02
2022 -5.27   2023 +6.29   2024 +1.59   2025 +2.69   2026 +1.47
```

Eleven of twenty Januaries were positive, yet January's mean (+0.27%) sits *below* the
all-other-months mean (+1.03%). The famous "January effect" does not appear in this span,
and the permutation test cannot distinguish the difference from noise (p = 0.456).

This cell is a good candidate for the flagship null page: a named, widely-repeated
seasonal claim, tested, and reported as **Folklore** with its failure years on the page.

## Elliott's hand-check (outstanding)

Recompute `n`, `mean(January)`, `mean(other)`, the difference and Welch t from the January
list above plus the store's other-month returns, and record the deltas here. If they match,
sign §10 of the spec. If they do not, both engines are quarantined until reconciled.

Hand values: ______________________  Date: __________  Deltas: __________
