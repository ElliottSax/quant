# Seasonality Verdict — Statistical Specification

**Status:** DRAFT v0.1, agent-authored 2026-08-18. Requires Elliott's line-by-line review
and signature before ANY implementation of story 3.2 (Sprint 2 gate, 2–3 protected hours).
**Spec version is a published field.** Every verdict rendered on the site carries the
version of this document that produced it. Changing any rule below is a version bump and
invalidates prior verdicts for recomputation.

This document exists because the product's only moat is that its verdicts are honest.
The implementation must follow this spec exactly; where the spec is ambiguous, the
implementation must stop and ask rather than choose.

---

## 1. The question being answered

For a given ticker and calendar month, the site answers exactly one question:

> Over the available history, are this ticker's returns in this calendar month
> distinguishable from its returns in other months, after correcting for the fact
> that we tested many months and many tickers?

This is a **descriptive historical question**, not a forecast. No output of this pipeline
may be phrased as a prediction, an expectation, or a recommendation. The verdict describes
what the record shows; it says nothing about what happens next, and the rendered page must
say so.

## 2. Unit of analysis and data requirements

- **Observation:** one (ticker, year, calendar month) total return, computed from adjusted
  end-of-day closes: `r = (adj_close[last trading day of month] / adj_close[last trading day of prior month]) - 1`.
- **Adjustments:** splits and dividends must be included. If the vendor's adjusted series
  is unavailable for a ticker, that ticker is excluded — never mixed.
- **Minimum history:** a (ticker, month) cell requires **n ≥ 20 observations** to be
  gradeable at all. Below that it is reported as `Insufficient history` with n shown. It is
  never given a tier and never enters the multiple-testing family (see §5).
- **Survivorship:** the universe must come from a delisted-inclusive source, or be
  restricted to index ETFs and mega-caps where survivorship distortion is negligible. The
  chosen branch is recorded per run and stated on every page. A survivorship-biased
  universe silently inflates every result; this is not a footnote, it is a validity
  condition.
- **Vendor and vintage:** each run records data vendor, retrieval timestamp, and the last
  trading day covered. Verdicts are stamped with this provenance.

## 3. The test

Monthly equity returns are fat-tailed, mildly autocorrelated, and the per-cell sample is
small (≈30 for a 30-year history). A plain one-sample t-test is therefore **not**
sufficient on its own.

**Primary test — permutation (label-shuffling):**
1. Let `M` = the set of returns for the target calendar month; `O` = returns for all other
   months of the same ticker over the same span.
2. Observed statistic: `d_obs = mean(M) - mean(O)`.
3. Under the null, calendar labels carry no information: pool `M ∪ O`, randomly reassign
   labels preserving group sizes, recompute `d`. Repeat **B = 10,000** times with a
   per-cell deterministic seed (`hash(ticker, month, spec_version)`) so results are exactly
   reproducible.
4. Two-sided p-value: `p = (1 + #{|d_perm| ≥ |d_obs|}) / (B + 1)`.

The `+1` in numerator and denominator is required — it prevents `p = 0`, which would
otherwise misrepresent a finite resampling as certainty.

**Secondary statistic (reported, never decisive):** Welch's t-statistic for the same
comparison, reported alongside so readers can see the parametric answer and its
disagreement with the permutation result when the tails matter.

**Effect size (always shown):** difference in means in percentage points, plus a
bootstrap 95% confidence interval (10,000 resamples, same seeding rule). **A verdict is
never rendered without its interval.** An interval spanning zero must be visible as such.

## 4. What is NOT tested (scope discipline)

The following are out of scope for v1 and may not be silently added, because each one
multiplies the hypothesis count and changes the correction:
- Day-of-week, turn-of-month, holiday-window, or intramonth effects.
- Conditional variants ("month X in an election year", "after a down month"). These are
  the classic route to false discovery by subgroup proliferation.
- Any strategy overlay (entry/exit rules, stops, position sizing). The pipeline describes
  return distributions; it does not simulate trading.

## 5. Multiple testing — the correction that makes the product honest

This is the heart of the spec and the single most important rule in it.

**The family is the entire run**: all gradeable (ticker, month) cells in the published
universe, tested together. If the universe is 50 tickers × 12 months, the family is up to
600 hypotheses. Correcting within a ticker (12 tests) instead of across the run is a
**specification error** — it is the exact shortcut that lets marketing-driven sites claim
discoveries — and any implementation that does it fails review.

**Procedure — Benjamini–Hochberg FDR control at q = 0.10:**
1. Collect all `m` gradeable p-values from the run, sort ascending: `p(1) ≤ … ≤ p(m)`.
2. Find the largest `k` such that `p(k) ≤ (k/m) · q`.
3. Reject (i.e. call statistically distinguishable) all hypotheses with rank ≤ `k`.
4. Report per-cell BH-adjusted values (`q-values`) for display.

FDR (not Bonferroni/FWER) is the right family-wise choice here: the goal is a roster where
a stated minority of entries are false discoveries, not near-total suppression of signal.
The chosen `q = 0.10` means **we expect roughly 1 in 10 Robust entries to be a false
positive, and the site must say that in plain words on the methodology page.**

If the universe changes between runs, `m` changes and prior q-values are no longer
comparable. Re-run the whole family; never splice results across universes.

## 6. Verdict tiers

Tiers are assigned only after §5's correction. Thresholds are fixed here so they cannot be
tuned after seeing results — tuning thresholds to produce a satisfying number of Robust
entries is p-hacking with extra steps.

| Tier | Condition |
|---|---|
| **Robust** | BH-adjusted q ≤ 0.10 **and** n ≥ 25 **and** the 95% bootstrap CI for the mean difference excludes zero **and** the sign of the effect is stable under leave-one-year-out (see below) |
| **Weak** | Raw p ≤ 0.05 but fails BH correction, or passes BH but fails the stability/CI conditions |
| **Folklore** | Raw p > 0.05 — the pattern is not distinguishable from noise in this history. Applies especially to widely-repeated named effects, which is why they are worth publishing |
| **Nothing Clears the Bar** | Page-level state when no month of a ticker reaches Robust or Weak |
| **Insufficient history** | n < 20 (§2). Not a verdict; excluded from the family |

**Leave-one-year-out stability:** recompute `d_obs` with each single year removed in turn.
If removing any one year flips the sign of the effect, the result is driven by one episode
and cannot be Robust. The dropped-year sensitivity is displayed on the page.

**Failure years are mandatory output.** Every graded cell publishes the individual years in
which the effect went the other way, with magnitudes. A tier badge without its failure
years is an incomplete render and must fail QA.

## 7. Out-of-sample discipline (the calibration clock)

The corrected in-sample verdict is a *candidate*, never a finding. From the day a verdict
is first published, the calibration logger appends an immutable dated row: ticker, month,
tier, statistics, spec version, universe hash.

- **The Survivors roster** contains only entries that remain Robust as new out-of-sample
  observations accrue. Tenure is displayed in days since first publication.
- **Demotion is published, not silently corrected.** When a Survivor stops clearing the
  bar, the demotion is dated and kept in the record.
- The out-of-sample record is never back-edited. If the spec changes, prior rows keep their
  original spec version and a new series begins.

## 8. Tolerances and cross-implementation agreement

Story 3.2 builds **two independent implementations** from this spec, in isolated worktrees,
without sharing code. They are compared by a harness:

- **Tier agreement: 100%.** Any disagreement quarantines BOTH implementations; nothing
  publishes until reconciled.
- **Numeric agreement:** means, effect sizes and CI bounds within `1e-9` relative. Permutation
  p-values must match exactly given the shared seeding rule (§3); if they do not, the seeding
  is not deterministic and that is a defect, not a tolerance question.
- The harness output is an artifact of the run, retained.

## 9. Hand-computed reference case (Elliott's check)

Before either implementation is trusted, one cell is computed by hand — spreadsheet or
paper — and must match to the stated tolerance:

- **Reference cell:** SPY, January, over the most recent 25 complete years available.
- **Hand-computed values required:** n; mean(M); mean(O); difference in means; Welch t;
  and the count of permutation draws exceeding |d_obs| for a reduced B = 1,000 run with the
  documented seed.
- Record the hand values, the implementation values, and the deltas in
  `docs/STATS_REFERENCE_CHECK.md`. **This file is the evidence that the gate was really run**
  — an unrecorded check counts as no check.

## 10. Rendering rules (bind the front end)

The statistics are only as honest as their presentation:
1. Never show a tier without: n, q-value, effect size with CI, and failure years.
2. Never round a q-value to 0. Show `< 0.001`.
3. Never sort or rank tickers by effect size in a way that reads as a recommendation list.
   Sorting within a screener is fine; a "top picks" framing is not.
4. Every page states the universe, the survivorship branch, the spec version, and the data
   vintage.
5. The false-discovery expectation from §5 (`q = 0.10` ⇒ ~1 in 10 Robust entries is expected
   to be a false positive) appears on the methodology page in plain language.
6. Null results are first-class pages, not error states.

---

## Reviewer's checklist (Elliott, Sprint 2 gate)

- [ ] §5 family definition is run-wide, not per-ticker — confirmed in code, not just here
- [ ] q = 0.10 accepted, and its plain-language consequence is on the methodology page
- [ ] Tier thresholds (§6) fixed before results were seen; no post-hoc tuning
- [ ] Permutation seeding is deterministic and reproducible from a clean clone
- [ ] Minimum-n rules enforced, and sub-threshold cells excluded from the family
- [ ] Survivorship branch chosen, recorded, and stated on-page
- [ ] Leave-one-year-out stability implemented as specified
- [ ] Failure years render on every graded cell
- [ ] Hand-computed reference case matches, and is recorded in STATS_REFERENCE_CHECK.md
- [ ] Two implementations agree 100% on tiers; harness artifact retained

Signature / date: ______________________
