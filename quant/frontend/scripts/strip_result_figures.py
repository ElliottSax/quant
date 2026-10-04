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

SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
MAX_SENTENCE = 360


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

    while i < n:
        line = lines[i]
        s = line.strip()
        if s.startswith("```"):
            fenced = not fenced
            out.append(line)
            i += 1
            continue
        if fenced or "Note on figures" in line:
            out.append(line)
            i += 1
            continue
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
                if len(p) <= MAX_SENTENCE and VAGUE_CITATION.search(p) and not YEAR.search(p):
                    drop = True  # a citation with no year or author cannot be checked
                if drop:
                    note("result-sentence", p)
                    changed = True
                else:
                    kept.append(p)
            if changed:
                new = " ".join(kept).strip()
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
        if f.name == "ARTICLES_COMPLETED.md":
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        if "## Sources" in text:
            continue
        head, body = split_front(text)
        stats: dict = {}
        new_body = process(body, stats, samples)
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
