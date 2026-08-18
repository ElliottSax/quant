# Seasonality Verdict — Statistical Specification

**Status:** DRAFT v0.3, agent-authored 2026-08-18 (v0.2 trailing-partial-month rule §2; v0.3 Monte Carlo boundary rule §6 and cross-implementation tolerance §8 — all three found by the cross-check harness, none by review). Requires Elliott's line-by-line review
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
- **Trailing partial months are excluded.** *(Added v0.2 — this gap was found by the
  cross-check harness, not by review: the two implementations disagreed on every August
  because the store ended mid-month.)* A month counts as complete only when the symbol has
  data strictly after that month's last calendar day, so the "last trading day of month"
  named above is actually observed. Interior months always satisfy this; only the ragged
  edge of the vintage is affected. Including a part-month return is a false observation —
  an 18-day return presented as a monthly one — and it contaminates twice: once in its own
  cell, and again in every other cell through the "all other months" pool.
- **Consecutive months only.** A return is formed only from adjacent calendar months; a gap
  in the series must break the chain rather than silently span it.
- **Adjustments:** splits and dividends must be included. If the vendor's adjusted series
  is unavailable for a ticker, that ticker is excluded — never mixed.
- **Minimum history:** a (ticker, month) cell requires **n ≥ 20 observations** to be
  gradeable at all. Below that it is reported as `Insufficient history` with n shown. It is
  never given a tier and never enters the multiple-testing family (see §5).
- **What an under-powered cell reports** *(added v0.3, third harness finding — the two
  implementations disagreed on whether to report a t-statistic for ungradeable cells).*
  It reports its **deterministic** descriptive statistics (n, both means, the difference,
  Welch t) and **no resampling estimate, q-value or tier**. Descriptive numbers are honest
  and cheap; a p-value on a cell the spec refuses to grade only invites a verdict to be
  read into it.
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

**Precedence is top-down and exhaustive** *(clarified v0.3 — the original table was
genuinely contradictory, since BH can reject a p-value above 0.05 while the Folklore row
claimed every such cell. The second implementation caught this; one implementation alone
would have silently picked a reading.)* Evaluate in order and stop at the first match:

| Tier | Condition |
|---|---|
| **Robust** | BH-rejected **and** n ≥ 25 **and** the 95% bootstrap CI for the mean difference excludes zero **and** the sign of the effect is stable under leave-one-year-out (see below) |
| **Weak** | BH-rejected but failing any Robust condition, **or** raw p ≤ 0.05 |
| **Folklore** | Everything else — the pattern is not distinguishable from noise in this history. Applies especially to widely-repeated named effects, which is why they are worth publishing |
| **Nothing Clears the Bar** | Page-level state when no month of a ticker reaches Robust or Weak |
| **Insufficient history** | n < 20 (§2). Not a verdict; excluded from the family |

**Monte Carlo boundary rule (added v0.3).** A permutation p-value is an estimate with its
own error: at B = 10,000 the standard error near p = 0.05 is ≈ 0.0022, so two honest runs
can differ by ≈ 0.006 — exactly the width that flips `Weak` and `Folklore`. A tier that
depends on which side of the line the sampling noise happened to land is false precision,
and it would let a cell change verdict between runs with no new data.

Therefore: **if `|p − threshold| < 3 × SE(p)`, where `SE(p) = sqrt(p(1−p)/B)`, the cell is
assigned the more conservative tier** (`Folklore` over `Weak`; a cell may not be promoted
to `Robust` on a BH decision that is itself inside this band). Cells resolved this way must
record that the boundary rule applied, so the reason is inspectable rather than invisible.

*This rule exists because the cross-check harness caught it, not because it was foreseen:
the two implementations disagreed on exactly one cell, MSFT April, whose p-value straddled
0.05. One engine alone would have published that tier with full confidence.*

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
- **Numeric agreement:** means, effect sizes and Welch t within `1e-9` relative — these are
  deterministic functions of the data and must agree essentially exactly.
- **Resampling estimates (p-values, CI bounds) agree to Monte Carlo tolerance, not bitwise.**
  *(Corrected v0.3.)* The earlier requirement of exact agreement was wrong: it assumed a
  shared seeding rule, but two independently written implementations legitimately use
  different RNGs and hash schemes, so identical draws are neither achievable nor desirable —
  requiring them would only force the second implementation to copy the first, destroying the
  independence that makes agreement meaningful. The test is `|p_A − p_B| ≤ 4 × SE(p)` with
  `SE(p) = sqrt(p(1−p)/B)`, and CI bounds within 4 × the bootstrap standard error. What must
  agree exactly is every **tier**, which the §6 boundary rule makes robust to this noise.
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

## Open questions for the reviewer to settle

These were raised by the implementations and are NOT yet decided. Each is written down
rather than silently chosen, per the rule at the top of this document.

- **A8 — where the BH decision band sits in p-space.** §6 states the Monte Carlo band in
  p-space, but the BH half of the rule ("a BH decision itself inside this band") needs the
  procedure's effective cutoff located in p-space. Implementation B reads it as
  `p_cut = (k/m)·q` with k the number BH rejects, falling back to `(1/m)·q` when k = 0.
  Unreachable on the current data (min q = 0.60), so it costs nothing today — but a
  different mapping could change Robust eligibility once the history supports it.
- **Ratify the implementation-B readings** carried forward as written: "same span" means
  all other monthly returns with no trimming to whole years; leave-one-year-out removes the
  year from both groups and an emptied group counts as unstable; failure years are
  strictly-opposite-sign (zero is not opposite); the `|d_perm| ≥ |d_obs|` comparison carries
  1e-15 slack so float noise cannot drop a tie, which raises p and is therefore conservative.

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
