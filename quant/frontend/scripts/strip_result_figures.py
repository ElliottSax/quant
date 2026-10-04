#!/usr/bin/env python3
"""Remove fabricated backtest/result figures from blog posts (fourth and fifth pass, 2026-10-04).

    python scripts/strip_result_figures.py --dry-run
    python scripts/strip_result_figures.py --apply

WHY
---
Posts that carry the "Note on figures" banner still showed specific results with no code, data
or date behind them: numeric result tables (Sharpe 1.35, Win Rate 53.2%, Max Drawdown -7.8%),
"- Win rate: 68.4%" bullets (including invented statistics about Congress), sentences such as
"generated a Sharpe ratio of 0.82", templated FAQ answers ("regime-aware strategies can achieve
20-40% Sharpe improvements", "empirical results show 34-160% ..."), and a cost block whose
numbers were internally inconsistent (1 trade/day cost 1.9%, 5 trades/week cost 0.7%).
A banner that says "illustrative" does not make a made-up table honest, so the figures go.

RULES (all deterministic, nothing is reworded except the two computed blocks below)
  * Posts that document their method under "## Sources" are never touched.
  * Code fences are never touched.
  * A markdown table whose rows name a performance metric (Sharpe, win rate, annual/total
    return, max drawdown, profit factor, CAGR, Sortino, Calmar) AND hold a numeric cell is
    replaced by one sentence saying results are not published.
  * Bullet lines that state a specific metric value are removed, as are bullets that give two
    or more.
  * Sentences claiming a specific historical result are removed (same exemptions as
    strip_return_claims.py: worked examples, hypotheticals).
  * The templated cost block is replaced by the cost-drag formula with arithmetic that is
    computed here from stated inputs; the "Impact on annual return/Sharpe" lines are replaced
    by a pointer to the formula.
  * Named template sentences are removed.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "content" / "blog"

NOTE = ("*Results for this analysis are not published here. Test any strategy on your own data with "
        "realistic costs before relying on it; past performance does not predict future results.*")

METRIC = (r"(?:sharpe(?: ratio)?|sortino(?: ratio)?|calmar(?: ratio)?|win[- ]?rate|success rate|"
          r"annuali[sz]ed return|annual return|total return|average return(?: per trade)?|"
          r"max(?:imum)? drawdown|max dd|profit factor|cagr)")
TABLE_METRIC = re.compile(METRIC, re.I)
TABLE_NUM = re.compile(r"\|\s*[-+~]?\$?\d[\d.,]*\s*(?:%|:1|x)?\s*(?:\||$)")
BULLET_ONE = re.compile(rf"^\s*[-*]\s+(?:\*\*)?{METRIC}(?:\*\*)?\s*(?:\([^)]*\))?\s*[:=]\s*(?:\*\*)?[-+~]?\$?\d", re.I)
METRIC_VAL = re.compile(rf"{METRIC}[^\n|]{{0,18}}?[-+~]?\d", re.I)

RESULT_SENTENCE = [
    re.compile(r"\b(?:generated|produced|achieved|delivered|yielded|returned|posted|reached|recorded|showed|"
               r"generates|produces|achieves|delivers|yields)\s+"
               r"(?:an?\s+)?(?:annuali[sz]ed\s+|annual\s+|average\s+|total\s+)?"
               r"(?:return|Sharpe(?: ratio)?|win rate|profit factor|drawdown)\b[^.!?]{0,40}?[-+]?\d", re.I),
    re.compile(r"\b\d(?:\.\d+)?\s+Sharpe(?: ratio)?\s+and\s+\d{2}(?:\.\d+)?%\s+win rate", re.I),
    re.compile(r"\bSharpe(?: ratio)? of \d\.\d+[^.!?]{0,60}?(?:drawdown|return)\b", re.I),
    re.compile(r"\b(?:annuali[sz]ed|annual) returns? of [-+]?\d[^.!?]{0,60}?(?:since|from|over|between)\s+(?:19|20)\d\d", re.I),
    # in-house results with no code or data behind them
    re.compile(r"\b(?:in|from) our (?:own )?back-?tests?\b[^.!?]*\d|\bour back-?tests? (?:show|shows|found|produced|indicate)[^.!?]*\d", re.I),
    re.compile(r"\bIn this example,[^.!?]{0,120}\b(?:generated|achieved|delivered)[^.!?]{0,60}\d", re.I),
    re.compile(r"\bproduced the (?:best|highest|lowest)[^.!?\n]{0,70}(?:Sharpe|drawdown|return)[^.!?\n]{0,25}\d", re.I),
    re.compile(r"\btypically (?:achieves?|produces?|delivers?|generates?)[^.!?]{0,60}Sharpe ratios? (?:of|between|from) \d", re.I),
    re.compile(r"\b(?:Win rate|Sharpe)\b[^.!?\n]{0,12}\d[^.!?\n]*\b(?:Sharpe|profit factor|average return)\b[^.!?\n]{0,12}\d", re.I),
    # fifth pass (2026-10-04): in-house results phrased in other ways, and vague "studies"
    re.compile(r"\b(?:our|my) (?:own )?back-?tests?\b[^.!?]{0,80}\d", re.I),
    re.compile(r"\d[^.!?]*\b(?:in|from|on|during) (?:our|my) (?:own )?back-?tests?\b", re.I),
    re.compile(r"\b(?:the )?results? (?:show|shows|indicate|indicates|suggest|suggests)\b[^.!?]{0,80}"
               r"(?:return|Sharpe|win rate|drawdown)[^.!?]{0,40}\d", re.I),
    re.compile(r"\b(?:a |one |the )?(?:study|survey|research|report|paper|analysis) (?:by|from|in|published in) "
               r"(?:the )?[A-Z][A-Za-z&' ]{2,50}(?:Journal|Review|Institute|Association|Society)\b[^.!?]{0,160}\d", re.I),
    re.compile(r"\b(?:empirical )?(?:studies|research|evidence) (?:show|shows|found|finds|suggests?|indicates?)\b"
               r"[^.!?]{0,100}\d+(?:\.\d+)?\s*%", re.I),
    re.compile(r"\b(?:average|mean|typical) (?:monthly |annual |annualized |annualised )?returns? of \d[^.!?]{0,40}"
               r"\b(?:historically|during|in the|over the|since|each year)\b", re.I),
    re.compile(r"\bhistorically[^.!?]{0,80}\b(?:average|mean|typical) (?:monthly |annual )?returns? of \d", re.I),
    # generic "can increase efficiency by up to 30%" filler that no study backs
    re.compile(r"\b(?:increase|improve|boost|enhance|reduce|decrease|cut|lower)\w*\b[^.!?]{0,70}"
               r"\bby up to \d+(?:\.\d+)?\s*%", re.I),
]
# a section lead-in that frames invented numbers as a measured example
EXAMPLE_LEAD = re.compile(r"^(\s*(?:[-*]\s+)?(?:\*\*)?)(Real[- ]World Example|Real Example|Example [Rr]esults?|"
                          r"Backtest(?:ed)? [Rr]esults?)(\*\*)?\s*:?\s*(.*)$")
# "For example, a study by X found ... 3.5%" is a cited statistic, not a hypothetical: "for example" does not exempt it
STUDY_STAT = re.compile(r"\b(?:study|studies|survey|research|report|paper)\b[^.!?]{0,260}\d+(?:\.\d+)?\s*%", re.I)
ILLUSTRATION = "Illustration only (not a measured result):"
HYPOTHETICAL_LABEL = "Illustration (hypothetical, not a real trade or result):"
HEADING_REAL = re.compile(r"^(#{2,4}) Real(?:[- ]World)? Example(: Complete Trade)?\s*$")
BOLD_REAL = re.compile(r"^\*\*Real Example - (.+?)\*\*:\s*$")
LEAD_ONLY = re.compile(r"^(\s*)\*\*Real(?:[- ]World)? Example:\*\*\s*$")
BULLET_IMPROVES = re.compile(rf"^\s*[-*]\s+(?:\*\*)?{METRIC}(?:\*\*)?\s*:\s*(?:improves?|increases?|rises?|boosts?|"
                             rf"reduces?|falls?|jumps?)\s+by\s+\d", re.I)
VAGUE_CITATION = re.compile(r"\b(?:study|survey|research|report|paper)s? (?:by|from|published in) (?:the )?Journal of \w+", re.I)
YEAR = re.compile(r"\b(?:19|20)\d\d\b")
RESULT_EXEMPT = re.compile(r"\b(?:for example|for instance|suppose|assume|assuming|hypothetical|illustrat\w+|"
                           r"imagine|say you|not guaranteed|no guarantee|past performance)\b", re.I)

TEMPLATE_SENTENCES = [
    re.compile(r"Regime-aware strategies can achieve 20-40% Sharpe ratio improvements[^.]*\."),
    re.compile(r"Empirical results show 34-160% Sharpe ratio improvement[^.]*\.(?:\s*Annual returns typically improve[^.]*\.)?"
               r"(?:\s*Backtested improvements typically exceed live trading results by 20-40%[^.]*\.)?"),
    re.compile(r"Daily retraining improves Sharpe ratios by 2-8%[^.]*\."),
    re.compile(r"Quarterly reoptimization on rolling 24-month windows is recommended\. If Sharpe ratio decays below 1\.2[^.]*\.[^.]*\.?"),
    re.compile(r"Transaction costs are the primary detractor from strategy returns\. A 1% annual return strategy can be erased[^.]*\."),
]
TEMPLATE_LINES = [
    re.compile(r"^\s*\d+\.\s+\*\*Risk-Return Trade-offs\*\*:.*$"),
    re.compile(r"^\s*-\s*Increase profit factor targets to 2\.5-3\.0\s*$"),
    re.compile(r"^\s*-\s*Accept lower profit factors \(1\.2-1\.5\)\s*$"),
]

COST_HEAD = re.compile(r"^### Commission Impact\s*$")
COST_BLOCK_START = re.compile(r"^- \*\*(?:2 trades/day|1 trade/day|5 trades/week) at 0\.05% commission\*\*:")
SLIP_HEAD = re.compile(r"^### Slippage Impact\s*$")
SLIP_LINE = re.compile(r"^- \*\*(?:High-liquidity assets \(top 100\)|Mid-cap stocks|Low-liquidity ETFs)\*\*:")
IMPACT_RET = re.compile(r"^Impact on annual return: [\d.]+% \(approximate net of costs\)\s*$")
IMPACT_SHARPE = re.compile(r"^Impact on Sharpe ratio: [\d.]+ \(adjusted for reduced returns\)\s*$")

# Arithmetic is computed, not typed: cost drag = round trips per year x round-trip cost x capital committed.
SIDE_COST = 0.0005
RT = 2 * SIDE_COST


def drag(trips: int) -> str:
    return f"{trips * RT * 100:.1f}%"


COST_REPLACEMENT = [
    "Cost drag grows with turnover: annual drag is about round trips per year x cost per round trip x the fraction of capital committed to each trade.",
    f"Worked example with stated assumptions (not a forecast): 0.05% commission per side is {RT * 100:.2f}% per round trip with all capital committed each time.",
    f"- 1 round trip per day (252 a year): 252 x {RT * 100:.2f}% = {drag(252)} a year",
    f"- 2 round trips per day (504 a year): 504 x {RT * 100:.2f}% = {drag(504)} a year",
    f"- 1 round trip per week (52 a year): 52 x {RT * 100:.2f}% = {drag(52)} a year",
    f"- 1 round trip per month (12 a year): 12 x {RT * 100:.2f}% = {drag(12)} a year",
]
SLIP_REPLACEMENT = ["Slippage depends on liquidity, order size and timing. Estimate it from your own fills instead of a rule of thumb."]
IMPACT_REPLACEMENT = ("Net return is gross return minus cost drag (see the formula above). Recompute the Sharpe ratio "
                      "from the net return series, not from a rule of thumb.")


# --- sixth pass (2026-10-04): triage of the "unclear" hits. A 62-hit stratified sample showed ~60% were invented
# or unsourced results, including real papers cited next to numbers they do not contain (Fama and French 1992,
# Gatev et al. 2006, Avellaneda and Lee 2010, Khandani et al. 2010, Black et al. 1972 were checked against
# the published abstracts). Educational thresholds, derived arithmetic and labelled hypotheticals are kept.
AUTHOR_YEAR = re.compile(r"[A-Z][A-Za-z'\u2019\-]+(?: (?:and|&) [A-Z][A-Za-z'\u2019\-]+| et al\.?)\s*\(?(?:19|20)\d\d\)?")
FINDING_VERB = re.compile(r"\b(?:found|finds|show|shows|showed|demonstrat\w+|report\w+|conclud\w+|estimat\w+|reveal\w+|"
                          r"document\w+|according to|can (?:generate|produce|explain|lead)|explains?)\b", re.I)
FIGURE = re.compile(r"\d+(?:\.\d+)?\s*(?:%|percent)|\bSharpe(?: ratio)?[^.!?]{0,20}\d|\b\d\.\d+\b", re.I)
SURVEY_N = re.compile(r"\bsurvey of \d+[^.!?]{0,120}\b(?:found|showed|reported|revealed|said)\b", re.I)
BACKTEST_CLAIM = [
    re.compile(r"\b(?:back-?tests?|back-?testing|backtested|empirical testing)\b[^.!?]{0,100}?"
               r"\b(?:shows?|showed|found|finds|reveal\w*|demonstrate\w*|produce\w*|yield\w*|indicate\w*)\b[^.!?]{0,160}?"
               r"(?:\d+(?:\.\d+)?\s*%|\bSharpe[^.!?]{0,20}\d|\b\d\.\d+\b)", re.I),
    re.compile(r"\bin (?:our|my) (?:own )?tests?\b[^.!?]{0,200}?(?:\d+(?:\.\d+)?\s*%|\bSharpe[^.!?]{0,20}\d|\b\d\.\d+\b)", re.I),
    re.compile(r"\bthe results show\b[^.!?]{0,200}?(?:\d+(?:\.\d+)?\s*%|\bSharpe[^.!?]{0,20}\d|\b\d\.\d+\b)", re.I),
    re.compile(r"\bempirical testing on\b[^.!?]{0,120}?\b(?:shows?|found)\b[^.!?]{0,80}?\d", re.I),
]
WINRATE_FACT = [
    re.compile(r"\bwin rates? (?:are|were|was)\s+(?:about |around |approximately |roughly |typically )?\d", re.I),
    re.compile(r"\b(?:push|raise|lift|increase|improve|boost)\w* (?:the |your )?win rate (?:to|by|from)\s+\d", re.I),
    re.compile(r"\bwin rate improvement of (?:only )?\d", re.I),
    re.compile(r"\b(?:achieved|achieves|delivered|produces?)\b[^.!?]{0,40}\b\d+%\s+(?:improvement|reduction)[^.!?]{0,30}\b(?:Sharpe|drawdown)", re.I),
]
CONDITIONAL = re.compile(r"\b(?:if|suppose|assume|assuming|when you|need(?:s|ed)? (?:a|to)|must|requires?|break-?even|"
                         r"hypothetical|illustrat\w+|imagine|say you|would|could|might)\b", re.I)
INTRO_LINE = re.compile(r"^\s*(?:\*\*)?[^|\n]{3,120}:(?:\*\*)?\s*$")
HEDGED_GENERIC = re.compile(r"^\s*(?:a|an|any) (?:strategy|model|portfolio|trader|system|backtest)\b[^.!?]*\b(?:may|might|can|could)\b", re.I)
# a bullet or bold-lead line whose label names a performance result and whose value is a number
RESULT_LABEL_LINE = re.compile(r"^\s*(?:[-*]\s+(?:\*\*)?|\*\*)(?P<label>[^:\n]{2,100}?)(?:\*\*)?\s*:\s*(?:\*\*)?\s*(?P<val>[^\n]*)$")
LABEL_KEY = re.compile(r"\b(?:returns?|sharpe|win[- ]?rate|performance|outperform\w*|alpha|cagr)\b", re.I)
LABEL_EXEMPT = re.compile(r"\b(?:required|expected|target|assumed|assumption|hypothetical|illustrat\w+|risk-free|discount|"
                          r"hurdle|cost|fee|input|initial|starting|break-?even|threshold|minimum|maximum|goal|budget|"
                          r"formula|definition|formulation|limit|stop|window|lookback|horizon|period|if|when|example[- ]only|"
                          r"per trade|position|sizing|rate of return needed|needed|volatility|vol|standard deviation|correlation)\b", re.I)
VALUE_NUM = re.compile(r"^(?:estimated |approximately |about |around )?[-+~\u2248]?\$?\d")
SECTION_EXEMPT = re.compile(r"\b(?:calculation|calculat\w+|formula|assumption|input|parameter|scenario|hypothetical|illustrat\w+|"
                            r"how to|worked|compute|computing|math|derivation|sizing|kelly|definition|what is|"
                            r"interpret\w*|rule of thumb|benchmarks?|thresholds?|explained|walk-?through|understand\w*|sample|output|reading)\b", re.I)
ARITH_CONTEXT = re.compile(r"\b(?:assum\w+|suppose|given|inputs?|parameters?|scenario|hypothetical|illustrat\w+|let'?s say|imagine|"
                           r"for example|for instance)\b", re.I)
DATED = re.compile(r"\b(?:19|20)\d\d\b")
LEAD_WORD = re.compile(r"(?:Historical|Average|Annuali[sz]ed|Typical|Backtest|Observed|Realized|Realised)\b", re.I)

SENT_SPLIT = re.compile(r"(?<!et al\.)(?<!e\.g\.)(?<!i\.e\.)(?<=[.!?])\s+")
MAX_SENTENCE = 360
MEASURED_PAGES = {"triple-barrier-labeling-meta-labeling.md", "python-backtesting-framework.md", "walk-forward-optimization.md"}

# --- seventh pass (2026-10-04): the leftovers the sixth pass listed, and their near-variants.
# Found by reading every instance in context: "Key Takeaways" bullets that state a strategy's Sharpe / win rate /
# drawdown / improvement as a result, "improved X from A to B" sentences, "Annual returns of N-M%" claims, the
# generic "Backtested improvements typically exceed live trading results by 20-40%" line, and the figures of the
# machine-generated "haiku" template (the same invented numbers on ~25 pages).
KEY_HEAD = re.compile(r"^#{2,4}\s+.*\b(?:key takeaways?|takeaways?|key points|key findings|in short|bottom line)\b", re.I)
TAKEAWAY_PERF = re.compile(
    r"\bSharpe\b[^.\n]{0,25}\d|\bwin[- ]?rates?\b[^.\n]{0,60}\d+(?:\.\d+)?\s*%|\bdrawdowns?\b[^.\n]{0,60}\d+(?:\.\d+)?\s*%|"
    r"\b(?:improv|reduc|increas|boost|cut|lower|rais)\w*\b[^.\n]{0,70}\d+(?:\.\d+)?\s*(?:-|–|to)?\s*\d*(?:\.\d+)?\s*%|"
    r"\boutperform\w*\b[^.\n]{0,80}\d|\bprofit factor\b[^.\n]{0,25}\d|\b(?:annual|annualized) returns?\b[^.\n]{0,40}\d", re.I)
# a takeaway whose number is derived from a simulation shown with its stated inputs on the same page
TAKEAWAY_VERIFIED = re.compile(r"Even a Sharpe 1\.0 strategy has a 22% chance of a -15% drawdown")
# a takeaway that is a definition, a derivation or a caution is not a result and stays
TAKEAWAY_KEEP = re.compile(
    r"\b(?:requires?|mathematically|break-?even|deflat\w+|skeptic\w*|square root|significance|acceptable|size positions|"
    r"row-by-row|if|could|would|might|may|should|treated|hypothetical|illustrat\w+)\b|\b1:\d", re.I)
IMPROVED_FROM_TO = re.compile(
    r"\b(?:improv|increas|rais|boost|reduc|cut|lower)\w*\b[^.!?\n]{0,60}?\b(?:Sharpe(?: ratio)?|win[- ]?rates?|profit factor|"
    r"drawdowns?|returns?)\b[^.!?\n]{0,40}?\bfrom\s+\*{0,2}[-+]?\d[\d.]*\s*%?\s+to\s+\*{0,2}[-+]?\d|"
    r"\b(?:Sharpe(?: ratio)?|win[- ]?rates?|profit factor|(?:max(?:imum)? )?drawdown)\s+(?:improv|increas|rose|fell|dropp|declin|reduc)\w*"
    r"\s+from\s+\*{0,2}[-+]?\d[\d.]*\s*%?\s+to\s+\*{0,2}[-+]?\d", re.I)
ANNUAL_RANGE_CLAIM = re.compile(
    r"\bannual(?:i[sz]ed)?\s+returns?\s+(?:of\s+)?\d[\d.]*\s*(?:-|–|to)\s*\d[\d.]*\s*%[^.!?\n]{0,80}?"
    r"\b(?:are|is|were|have been)\s+(?:achievable|typical|common|realistic|possible)", re.I)

QUALITATIVE_BACKTEST_GAP = ("Backtested results are usually more optimistic than live trading because of costs, slippage, "
                            "market impact and overfitting.")
# line-level replacements for the machine-generated "haiku" template and the generic filler (exact templates)
LINE_RULES = [
    (re.compile(r"\s*Achieved validation R² of 0\.84-0\.91 confirms robust generalization despite parameter complexity\."),
     " Check generalization with your own out-of-sample validation."),
    (re.compile(r"Annual returns typically improve \d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?% while maintaining or reducing maximum drawdown\.\s*"
                r"Backtested improvements typically exceed live trading results by [^.]*\."),
     "No typical improvement figure is published here: gains found in a backtest depend on the data, the costs assumed and how many "
     "variants were tried. " + QUALITATIVE_BACKTEST_GAP + " Judge a parameter change by out-of-sample and paper-trading results."),
    (re.compile(r"\s*Backtested improvements typically exceed live trading results by [^.]*\."), " " + QUALITATIVE_BACKTEST_GAP),
    (re.compile(r"Machine learning approaches to parameter tuning have demonstrated \d+-\d+% improvements in Sharpe ratios compared to "
                r"static parameter configurations\."),
     "Machine learning approaches to parameter tuning can improve on static parameter configurations, but gains are not "
     "guaranteed and have to be validated out-of-sample."),
    (re.compile(r"(\*\*Parameter Importance Distribution\*\*): ([^.\n]*?) feature importance analysis identified [^.\n]*?\(\d+% importance\)[^.\n]*?"
                r"\(\d+%\)[^.\n]*?\(\d+%\)[^.\n]*?as primary drivers of strategy performance\.[^\n]*"),
     r"\1: Feature-importance analysis can show which parameters drive a strategy's performance. Compute it on your own data "
     r"before concluding that any one parameter dominates."),
    (re.compile(r"(\*\*Regime-Dependent Optimization\*\*): Largest performance improvements occurred during volatile market regimes "
                r"\(\d+(?:\.\d+)?% in bear markets versus \d+(?:\.\d+)?% in bull markets\)\.[^\n]*"),
     r"\1: Parameter flexibility may matter most in volatile regimes, when static parameters can become suboptimal. Check "
     r"regime-dependent behaviour on your own data."),
    (re.compile(r"(\*\*Computational Efficiency\*\*): [^\n]*? training completed in [^\n]*?(?:hours|minutes)[^\n]*"),
     r"\1: Model-based search is usually much cheaper than exhaustive grid search, which can make frequent recalibration practical. "
     r"Measure the runtime on your own data."),
    (re.compile(r"(\*\*Generalization Robustness\*\*): Cross-validation R² scores of [^\n]*"),
     r"\1: Report cross-validation scores and out-of-sample degradation from your own runs; do not assume stable generalization."),
    (re.compile(r" \(typically \d+-\d+% drift per week\)"), ""),
    (re.compile(r"Asset-specific models outperform universal models by \d+-\d+% due to regime heterogeneity\."),
     "Asset-specific models can outperform universal models when assets behave differently across regimes."),
    (re.compile(r"Asset-specific models achieve \d+-\d+% higher performance than universal models due to regime variation\."),
     "Asset-specific models can outperform universal models when assets behave differently across regimes."),
    (re.compile(r"\s*These extensions typically improve R² by \d+-\d+%\."), ""),
    (re.compile(r"Constrained optimization yields \d+-\d+% lower performance but ensures compliance\."),
     "Constraints can reduce in-sample performance but keep the strategy within its limits."),
]

# file-specific rewrites for items that do not generalise: (file, regex, replacement). Each pattern must match the
# corpus at least once on the first run (checked by the test); later runs are no-ops.
EXPLICIT = [
    ("automating-bollinger-bands-using-machine-learning.md",
     re.compile(r"On a universe of S&P 500 stocks \(2018-2025\), the ML signal filter typically:\n- Reduces total trades by 40-50%\n"
                r"- Increases Sharpe ratio from 0\.65 to 0\.95\n- Reduces maximum drawdown by 25-35%"),
     "An ML signal filter aims to cut false signals and trade less often. Whether it improves risk-adjusted returns net of costs "
     "depends on the data and has to be tested out-of-sample."),
    ("automating-pairs-trading-with-high-success-rate.md",
     re.compile(r"\n# Impact: Adding 2 confirmation signals raises win rate from 62% to 75%"), ""),
    ("backtesting-macd-crossovers-using-machine-learning.md",
     re.compile(r"\*\*Key insight\*\*: ML filters out ~46% of false signals while increasing win rate from 50% to 56%\."),
     "**Key insight**: An ML filter aims to remove false signals. Whether it raises the win rate or the net return has to be "
     "measured out-of-sample with realistic costs."),
    ("market-regime-detection.md",
     re.compile(r"captured the bull run with a \[Sharpe ratio\]\(/blog/sharpe-ratio-portfolio-analysis\) of approximately 1\.2"),
     "captured the bull run"),
    ("market-regime-detection.md", re.compile(r"Multiple false signals due to shallow pullbacks, Sharpe approximately 0\.4"),
     "Multiple false signals due to shallow pullbacks"),
    ("market-regime-detection.md", re.compile(r"Inconsistent performance, Sharpe approximately 0\.6"), "Inconsistent performance"),
    ("algorithmic-trading-beginners.md",
     re.compile(r"This translates to \$4,000-7,500 per year\. (Scaling requires either more capital, leverage, or multiple "
                r"uncorrelated strategies\.) The median independent quant trader in surveys reports annual returns of 10-20% before fees\."),
     r"Returns depend on capital, strategy and costs, and no figure is guaranteed. \1"),
    ("commodity-trading-strategies.md",
     re.compile(r"Commodity carry strategies have historically delivered:\n- Annual returns of 5-8% \(cross-sectional\) or 3-6% "
                r"\(time-series\)\n- Sharpe ratios of 0\.5-0\.8\n- Low correlation with trend following \(0\.1-0\.3\), enabling strong "
                r"diversification when combined\n- Moderate drawdowns \(-15 to -20% maximum\)"),
     "Commodity carry strategies earn returns from the roll yield, and results vary widely by period and implementation. Estimate "
     "returns, the Sharpe ratio, drawdowns and the correlation with trend following on your own data, net of costs."),
    ("crypto-arbitrage-strategies.md",
     re.compile(r"Annual returns of 25-60% are achievable but require significant time investment"),
     "Returns depend heavily on capital, costs and competition and are not guaranteed, and the strategies require significant "
     "time investment"),
    ("pairs-trading-strategy-guide.md",
     re.compile(r"The ML-enhanced selection improved the Sharpe ratio from 1\.42 to 1\.61 by identifying pairs with more stable "
                r"relationships, though at the cost of a smaller trading universe \(120 pairs vs\. 200\)\."),
     "ML-enhanced selection aims to identify pairs with more stable relationships, at the cost of a smaller trading universe."),
    ("pairs-trading-strategy-guide.md", re.compile(r"can enhance pair selection, improving Sharpe from 1\.42 to 1\.61"),
     "can enhance pair selection"),
    ("crypto-exchange-rate-arbitrage-global-markets.md",
     re.compile(r",? typically ranging from \d+% to \d+% per trade"), ""),
    ("crypto-exchange-rate-arbitrage-global-markets.md",
     re.compile(r"\| (Low|Medium|High) \| \d+-\d+% \|"), r"| \1 | Varies; not guaranteed |"),
    ("automating-mean-reversion-safely.md",
     re.compile(r"The frameworks presented achieve superior risk-adjusted returns \(Sharpe 1\.94 vs\. 0\.87\) while reducing maximum "
                r"drawdowns by 81%\."),
     "The frameworks presented aim to improve risk-adjusted returns and reduce drawdowns; verify those benefits on your own data."),
    ("cerebras-backtesting-bollinger-bands-efficiently.md",
     re.compile(r"The best-performing configuration is \*\*window=10, k=2\.5\*\* \(Sharpe: 0\.38\)\. This setting increases "
                r"sensitivity to short-term price movements and reduces false signals\."),
     "Run the optimization on your own data to find the configuration that suits your market."),
    ("momentum-trading-strategy-guide.md",
     re.compile(r"Monthly rebalancing is standard, but we tested alternatives:\n\n- \*\*Weekly\*\*: Higher Sharpe \(1\.38\) but 3x higher "
                r"turnover, net worse after costs\n- \*\*Monthly\*\*: Best risk-adjusted returns after costs \(Sharpe 1\.31\)\n- "
                r"\*\*Quarterly\*\*: Lower turnover but misses intermediate signals \(Sharpe 0\.94\)"),
     "Monthly rebalancing is standard. Weekly rebalancing raises turnover and costs, and quarterly rebalancing lowers turnover but "
     "misses intermediate signals. Compare rebalancing frequencies on your own data, net of costs."),
    ("cerebras-guide-to-macd-crossovers-using-machine-learning.md",
     re.compile(r"Key findings:\n\n- The ML model \*\*reduced trade frequency by 42%\*\*[^\n]*\n- Annual return increased by \*\*[^\n]*\n"
                r"- Sharpe ratio improved from \*\*0\.38 to 0\.93\*\*[^\n]*\n- Maximum drawdown was \*\*[^\n]*\n\n"
                r"The equity curve in Figure 1 \(not shown\) demonstrates consistent outperformance, particularly during high-volatility "
                r"regimes such as Q1 2020 and Q4 2022\."),
     "An ML filter aims to cut low-probability signals and trade less often. Whether it improves the Sharpe ratio, returns or drawdowns "
     "has to be measured on your own data with realistic costs."),
    ("cerebras-guide-to-macd-crossovers-using-machine-learning.md",
     re.compile(r"The ML-augmented MACD strategy significantly outperforms both the traditional MACD and buy-and-hold benchmarks over the "
                r"2018.2023 period\."),
     "Compare the ML-augmented MACD strategy with the traditional MACD and buy-and-hold benchmarks on your own data."),
    ("tail-risk-hedging-guide.md",
     re.compile(r"but cost 1\.5-3\.0% annually; put spreads and VIX call spreads reduce costs by 40-60% while covering"),
     "but carry an ongoing premium cost; put spreads and VIX call spreads reduce costs while covering"),
    ("rebalancing-strategies-quant.md",
     re.compile(r"reducing unnecessary transactions by 30-50% versus calendar rebalancing"),
     "reducing unnecessary transactions compared with calendar rebalancing"),
    ("risk-budgeting-framework.md",
     re.compile(r"can improve risk-adjusted returns by 15-30% relative to static budgets"),
     "may improve risk-adjusted returns relative to static budgets, but test this on your own data"),
    ("smart-beta-strategies-guide.md",
     re.compile(r"produces superior risk-adjusted returns because factor premia are lowly or negatively correlated; integrated "
                r"multi-factor portfolios achieve Sharpe ratios 35-40% higher than single factors"),
     "can improve risk-adjusted returns because factor premia are imperfectly correlated; check this on your own data"),
    ("smart-beta-strategies-guide.md", re.compile(r"buffer rules reduce turnover by 30-40%, and"), "buffer rules reduce turnover, and"),
    ("tactical-asset-allocation.md",
     re.compile(r", achieving 15-25% lower volatility and 30-60% lower maximum drawdowns relative to static allocation"),
     ", aiming for lower volatility and smaller drawdowns than static allocation"),
    ("tactical-asset-allocation.md",
     re.compile(r"produces more robust TAA than any single signal category, with Sharpe ratio improvements of 0\.15-0\.25"),
     "can make TAA more robust than any single signal category"),
    ("trend-following-system-guide.md",
     re.compile(r"slow trend signals improves Sharpe from 0\.72-0\.88 to 0\.94"), "slow trend signals diversifies across horizons"),
    ("trend-following-system-guide.md",
     re.compile(r"A 20-30% allocation to trend following in a traditional portfolio reduces max drawdown by 25-35%"),
     "Adding a trend-following allocation to a traditional portfolio may reduce drawdowns, depending on the period and implementation"),
    ("options-trading-strategies-quant.md",
     re.compile(r"reduce portfolio volatility from 15\.8% to 11\.4% with minimal return sacrifice"),
     "can reduce portfolio volatility, at the cost of capping upside"),
    ("moving-average-crossover-strategy.md",
     re.compile(r"Triple MA systems reduce false signals by 42% at the cost of later entries"),
     "Triple MA systems can reduce false signals at the cost of later entries"),
    ("momentum-trading-strategy-guide.md",
     re.compile(r"essential to survive momentum crashes \(reduce max drawdown from -38\.7% to -16\.2%\)"),
     "essential to survive momentum crashes"),
    ("breakout-trading-strategy.md",
     re.compile(r"Breakout strategies have low win rates \(38-48%\) compensated by high reward-to-risk ratios \(2:1 to 4:1\)"),
     "Breakout strategies tend to have low win rates, compensated by high reward-to-risk ratios"),
]


def apply_explicit(name: str, body: str, stats: dict, samples: list) -> str:
    for fname, rx, repl in EXPLICIT:
        if fname != name:
            continue
        body, n = rx.subn(repl, body)
        if n:
            stats["explicit"] = stats.get("explicit", 0) + n
            samples.append(("explicit", f"{fname}: {rx.pattern[:100]}"))
    return body


def split_front(text: str):
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", text, re.S)
    return (text[: m.end()], text[m.end():]) if m else ("", text)


def process(body: str, stats: dict, samples: list) -> str:
    lines = body.split("\n")
    out: list[str] = []
    i = 0
    fenced = False
    n = len(lines)

    def note(kind: str, snippet: str):
        stats[kind] = stats.get(kind, 0) + 1
        if len(samples) < 2000:
            samples.append((kind, snippet.strip()[:150]))

    heading = ""
    in_key = False
    while i < n:
        line = lines[i]
        s = line.strip()
        if s.startswith("#"):
            heading = s.lstrip("#").strip()
            in_key = bool(KEY_HEAD.match(s))
        if s.startswith("```"):
            fenced = not fenced
            out.append(line)
            i += 1
            continue
        if fenced or "Note on figures" in line:
            out.append(line)
            i += 1
            continue
        # seventh pass: exact-template replacements (haiku template, generic backtest-gap filler)
        replaced = line
        for rx_t, repl_t in LINE_RULES:
            replaced = rx_t.sub(repl_t, replaced)
        if replaced != line:
            note("line-rule", line)
            line = replaced
            s = line.strip()
        # computed cost block
        if COST_HEAD.match(line):
            j = i + 1
            while j < n and COST_BLOCK_START.match(lines[j]):
                j += 1
            if j > i + 1:
                out.append("### Commission Impact")
                out.append("")
                out.extend(COST_REPLACEMENT[:2])
                out.append("")
                out.extend(COST_REPLACEMENT[2:])
                note("cost-block", lines[i + 1])
                i = j
                continue
        if SLIP_HEAD.match(line):
            j = i + 1
            while j < n and SLIP_LINE.match(lines[j]):
                j += 1
            if j > i + 1:
                out.append("### Slippage Impact")
                out.append("")
                out.extend(SLIP_REPLACEMENT)
                note("slippage-block", lines[i + 1])
                i = j
                continue
        if IMPACT_RET.match(line):
            out.append(IMPACT_REPLACEMENT)
            note("impact-lines", line)
            i += 1
            if i < n and IMPACT_SHARPE.match(lines[i]):
                i += 1
            continue
        if IMPACT_SHARPE.match(line):
            note("impact-lines", line)
            i += 1
            continue
        # "Real Example" / "Real-World Example: Complete Trade" headings introduce invented, dated price scenarios
        hm = HEADING_REAL.match(line)
        if hm:
            out.append(f"{hm.group(1)} Worked example (hypothetical numbers){hm.group(2) or ''}")
            note("heading-relabel", line)
            i += 1
            continue
        bm = BOLD_REAL.match(line)
        if bm:
            out.append(f"**Worked example (hypothetical numbers) - {bm.group(1)}**:")
            note("heading-relabel", line)
            i += 1
            continue
        # "**Real Example:**" on its own line: these are invented scenarios, so label them as such
        # and drop any outcome sentence ("Win rate: 62%.") from the line that follows
        lm = LEAD_ONLY.match(line)
        if lm:
            nxt = lines[i + 1] if i + 1 < n else ""
            out.append(f"{lm.group(1)}**{HYPOTHETICAL_LABEL}**")
            note("example-lead-relabel", line)
            if nxt.strip() and METRIC_VAL.search(nxt):
                kept_parts = [p for p in SENT_SPLIT.split(nxt) if not METRIC_VAL.search(p)]
                note("example-outcome-dropped", nxt)
                if kept_parts:
                    out.append(" ".join(kept_parts).strip())
                i += 2
            else:
                i += 1
            continue
        # tables
        if s.startswith("|"):
            j = i
            while j < n and lines[j].strip().startswith("|"):
                j += 1
            block = lines[i:j]
            joined = "\n".join(block)
            if (TABLE_METRIC.search(joined) and any(TABLE_NUM.search(b) for b in block[2:] or block)
                    and not re.search(r"required|break-?even|needed to", block[0], re.I)):
                out.append(NOTE)
                note("table", block[0])
                i = j
                continue
            out.extend(block)
            i = j
            continue
        # template lines
        if any(t.match(line) for t in TEMPLATE_LINES):
            note("template-line", line)
            i += 1
            continue
        # labelled result lines ("- Average return achieved: 24.3%", "- **Sharpe improvement**: 0.74 to 1.18")
        lm2 = RESULT_LABEL_LINE.match(line)
        is_bullet = bool(re.match(r"^\s*[-*]\s", line))
        val2 = lm2.group("val").lstrip("* ").strip() if lm2 else ""
        pct_ok = bool(lm2) and bool(
            re.search(r"\d\s*%|percent", val2, re.I)
            or (re.search(r"sharpe", lm2.group("label"), re.I) and re.search(r"\d\.\d+", val2))
        )
        lead_ok = bool(lm2) and (is_bullet or LEAD_WORD.match(lm2.group("label").strip()) or DATED.search(heading))
        derived = "=" in val2 or bool(re.search(r"[\u00d7*]\s*\d", val2))  # a worked calculation, not a reported result
        if lm2 and pct_ok and lead_ok and not derived and LABEL_KEY.search(lm2.group("label")) and VALUE_NUM.match(val2):
            ctx_ok = not LABEL_EXEMPT.search(lm2.group("label"))
            recent = " ".join(x for x in lines[max(0, i - 8):i] if x.strip())
            heading_ok = (not SECTION_EXEMPT.search(heading)) and (not re.search(r"example", heading, re.I) or DATED.search(heading))
            if ctx_ok and heading_ok and not ARITH_CONTEXT.search(recent):
                note("labelled-result", line)
                i += 1
                # if that was the last item under an intro line ("Cross-sectional momentum (1990-2025):"), drop the intro too
                j = i
                while j < n and not lines[j].strip():
                    j += 1
                if j >= n or not re.match(r"^\s*[-*]\s", lines[j]):
                    k = len(out) - 1
                    while k >= 0 and not out[k].strip():
                        k -= 1
                    if k >= 0 and INTRO_LINE.match(out[k]) and not re.match(r"^\s*[-*]\s", out[k]):
                        del out[k:]
                continue
        # seventh pass: "Key Takeaways" bullets that state a strategy result as a fact (Sharpe, win rate, drawdown, improvement)
        if (in_key and re.match(r"^\s*(?:[-*]|\d+\.)\s", line) and TAKEAWAY_PERF.search(line)
                and not TAKEAWAY_KEEP.search(line) and not TAKEAWAY_VERIFIED.search(line)):
            note("takeaway-result", line)
            i += 1
            continue
        # bullets with specific metric values
        if re.match(r"^\s*[-*]\s", line):
            if (BULLET_ONE.match(line) or BULLET_IMPROVES.match(line)
                    or len(set(m.group(0).split()[0].lower() for m in METRIC_VAL.finditer(line))) >= 2):
                note("bullet", line)
                i += 1
                continue
        # "Real Example: ... Win rate: 62%." -> keep the rule, drop the invented outcome, relabel
        em = EXAMPLE_LEAD.match(line)
        if em and METRIC_VAL.search(em.group(4)) and not RESULT_EXEMPT.search(em.group(4)):
            if em.group(2).lower().startswith("real"):
                # a described trade rule is fine as an illustration; its invented outcome is not
                kept_parts = [p for p in SENT_SPLIT.split(em.group(4)) if not METRIC_VAL.search(p)]
                note("example-relabel", line)
                if kept_parts:
                    out.append(f"{em.group(1)}{ILLUSTRATION}{em.group(3) or ''} {' '.join(kept_parts).strip()}")
            else:
                # "Backtest results: ..." / "Example results: ..." is itself a result claim
                note("example-result-dropped", line)
            i += 1
            continue
        # sentences
        if s and not s.startswith("#") and not line.startswith("    "):
            parts = SENT_SPLIT.split(line)
            kept = []
            changed = False
            for p in parts:
                drop = False
                if any(t.search(p) for t in TEMPLATE_SENTENCES):
                    p2 = p
                    for t in TEMPLATE_SENTENCES:
                        p2 = t.sub("", p2)
                    p2 = p2.strip()
                    note("template-sentence", p)
                    changed = True
                    if p2:
                        kept.append(p2)
                    continue
                if (len(p) <= MAX_SENTENCE and (not RESULT_EXEMPT.search(p) or STUDY_STAT.search(p))
                        and any(r.search(p) for r in RESULT_SENTENCE)):
                    drop = True
                if len(p) <= MAX_SENTENCE + 200 and AUTHOR_YEAR.search(p) and FINDING_VERB.search(p) and FIGURE.search(p):
                    drop = True  # a real paper cited next to a number it does not contain
                if len(p) <= MAX_SENTENCE + 200 and SURVEY_N.search(p):
                    drop = True
                if (len(p) <= MAX_SENTENCE and not CONDITIONAL.search(p) and not HEDGED_GENERIC.search(p)
                        and (any(r.search(p) for r in BACKTEST_CLAIM) or any(r.search(p) for r in WINRATE_FACT))):
                    drop = True
                if len(p) <= MAX_SENTENCE and VAGUE_CITATION.search(p) and not YEAR.search(p):
                    drop = True  # a citation with no year or author cannot be checked
                if (len(p) <= MAX_SENTENCE + 200 and not CONDITIONAL.search(p)
                        and (IMPROVED_FROM_TO.search(p) or ANNUAL_RANGE_CLAIM.search(p))):
                    drop = True  # "improved the Sharpe from A to B", "annual returns of N-M% are achievable"
                if drop:
                    note("result-sentence", p)
                    changed = True
                else:
                    kept.append(p)
            if changed:
                new = " ".join(kept).strip()
                if not new and re.match(r"^\s*(?:\*\*)?A(?:nswer)?:(?:\*\*)?", line):
                    out.append(line[: re.match(r"^\s*(?:\*\*)?A(?:nswer)?:(?:\*\*)?", line).end()] + " Specific figures are not published here; test any idea on your own data with realistic costs.")
                    note("answer-note", line)
                    i += 1
                    continue
                pm = re.match(r"^\s*(?:\*\*)?A(?:nswer)?:(?:\*\*)?\s*", line)
                if new and pm and not re.match(r"^\s*(?:\*\*)?A(?:nswer)?:", new):
                    new = pm.group(0) + new  # keep the answer label when its first sentence was the one removed
                if new:
                    prefix = re.match(r"^\s*(?:\*\*)?(?:[A-Za-z]:|Q\d*:)", line)
                    out.append(new if not prefix or len(new) > 12 else "")
                i += 1
                continue
        out.append(line)
        i += 1
    # collapse 3+ blank lines left by removals
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    ap.add_argument("--samples", type=int, default=30)
    args = ap.parse_args()

    total: dict = {}
    samples: list = []
    changed_files = []
    for f in sorted(BLOG.glob("*.md")):
        if f.name == "ARTICLES_COMPLETED.md" or f.name in MEASURED_PAGES:
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        if "## Sources" in text:
            continue
        head, body = split_front(text)
        stats: dict = {}
        new_body = process(apply_explicit(f.name, body, stats, samples), stats, samples)
        if new_body != body:
            changed_files.append(f.name)
            for k, v in stats.items():
                total[k] = total.get(k, 0) + v
            if args.apply:
                f.write_text(head + new_body, encoding="utf-8", newline="\n")
    print(f"files changed: {len(changed_files)}")
    for k, v in sorted(total.items()):
        print(f"  {k}: {v}")
    print("--- samples ---")
    for kind, s in samples[: args.samples]:
        print(f"  [{kind}] {s}")
    if args.dry_run:
        print("DRY RUN - nothing written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
