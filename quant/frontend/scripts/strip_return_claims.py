#!/usr/bin/env python3
"""Remove fabricated performance claims from indexable blog articles.

    python scripts/strip_return_claims.py --dry-run
    python scripts/strip_return_claims.py --apply

WHY
---
A scan of the indexable corpus found 325 sentences across 111 articles asserting
specific trading returns as fact:

    "Professional day traders in 2026 earn 1-3% daily compounding to 250-500%+
     annual returns using proven indicator strategies..."
    "Successful swing traders average 5-8% per trade with 60%+ win rate,
     compounding to 150-300% annual returns."
    "Covered calls generate 12-26% annualized returns through systematic premium
     selling"

None is sourced, and several sit immediately above broker AFFILIATE LINKS
("Open account on Kraken or Binance"). A fabricated return figure next to a
referral link is the exact pattern affiliate compliance reviews reject, and
financial content is held to a higher standard by search quality raters. It is
also flatly inconsistent with a site whose entire positioning is that its numbers
are measured.

APPROACH
--------
Operate on RAW markdown, at sentence granularity, and DELETE rather than reword.
Deleting is the conservative choice here: any replacement figure would be another
unsourced number, and these sentences are pure assertion -- removing one leaves
the surrounding explanation intact and loses no information the article actually
supports.

Two guards keep this from mangling prose:

  * A sentence is only removed if the claim pattern matches AND the sentence is
    predominantly the claim (not a long paragraph that happens to contain a
    percentage). Sentences over MAX_SENTENCE characters are reported for manual
    review instead of being touched.
  * Headings, code fences and table rows are never modified. A percentage inside
    a worked example ("$3.75 premium = 5.6% for 45 days") is arithmetic on stated
    inputs, not a forward-looking promise, so those patterns are excluded.

Everything changed is printed, and --dry-run makes no writes.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "content" / "blog"
NOINDEX_TS = ROOT / "src" / "lib" / "noindex-drafts.ts"

MAX_SENTENCE = 320   # longer than this, report rather than edit

# The defect is a promise about what the READER will earn. That is the discriminator,
# and it is narrower than "a sentence containing a percentage" -- an earlier, looser
# version of this file flagged "you keep 100% of the premium" (a factual description of
# covered-call mechanics) and "Yield: 3.5-4% APY" (an observable protocol rate). Neither
# is a promise, and removing them would delete real content to fix a different problem.
PERIOD = r"(?:monthly|daily|weekly|annual(?:ly|ized)?|per\s+trade|per\s+year|per\s+month)"
ACTOR = r"(?:traders?|investors?|farmers?|scalpers?|professionals?|you|we)"
EARN = r"(?:earn|average|gain|make|generate|achieve|deliver|pocket|realiz\w+|compound\w*)"

CLAIMS = [
    # "Professional day traders earn 1-3% daily", "you make 5-15% monthly"
    re.compile(rf"\b{ACTOR}\b[^.!?]{{0,90}}?\b{EARN}\b[^.!?]{{0,50}}?"
               rf"\d{{1,4}}(?:\.\d+)?\s*[-–]\s*\d{{1,4}}(?:\.\d+)?\s*%", re.I),
    # "generate 2-5% monthly returns", "compounding to 250-500%+ annual returns"
    re.compile(rf"\b{EARN}\w*\b[^.!?]{{0,30}}?\d{{1,4}}(?:\.\d+)?\s*[-–]\s*"
               rf"\d{{1,4}}(?:\.\d+)?\s*%\+?\s*{PERIOD}", re.I),
    # a return range explicitly tied to a period AND framed as a return
    re.compile(rf"\d{{1,4}}(?:\.\d+)?\s*[-–]\s*\d{{1,4}}(?:\.\d+)?\s*%\+?\s*{PERIOD}"
               rf"[^.!?]{{0,25}}\breturns?\b", re.I),
    # "60%+ win rate", "90% success rate"
    re.compile(r"\b\d{2,3}\s*%\s*\+?\s*(?:win rate|success rate|accuracy)", re.I),
    # outright impossibility claims
    re.compile(r"\b(?:guaranteed|risk[- ]free)\s+profits?\b", re.I),
    re.compile(r"\bRealistic returns?\s*:", re.I),
]

# Contexts that are NOT promises and must be preserved.
EXEMPT = [
    re.compile(r"\bnot\s+guaranteed|no\s+guarantee|past performance|not a guarantee", re.I),
    re.compile(r"\bstop[- ]?loss|maximum loss|risk per trade|drawdown", re.I),
    # "100% of the premium" means "all of it", not a 100% return.
    re.compile(r"\b100\s*%\s*of\b", re.I),
    # A protocol's published yield is observable data, not a promise about the reader.
    re.compile(r"^\s*[-*]?\s*(?:yield|apy|apr)\s*:", re.I),
    # A figure used as the INPUT to a worked example is pedagogy, not a forecast:
    # "With a 55% win rate and 2:1 reward-to-risk:" introduces an expectancy calculation.
    # Removing these would delete the teaching and leave an orphaned list behind.
    re.compile(r"^\s*(?:\*\*)?(?:example|suppose|assume|imagine|say)\b", re.I),
    re.compile(r"^\s*(?:with|if|given)\s+(?:a|an)\b[^.!?]{0,60}"
               r"(?:win rate|profit factor|reward[- ]to[- ]risk|r:r)", re.I),
]

SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def noindex_slugs() -> set[str]:
    if not NOINDEX_TS.exists():
        return set()
    return set(re.findall(r"'([a-z0-9][a-z0-9\-]{3,})'", NOINDEX_TS.read_text(encoding="utf-8")))


def is_claim(sentence: str) -> bool:
    if any(e.search(sentence) for e in EXEMPT):
        return False
    return any(c.search(sentence) for c in CLAIMS)


def process_line(line: str) -> tuple[str, list[str]]:
    """Strip claim sentences from one prose line. Returns (new_line, removed)."""
    parts = SENT_SPLIT.split(line)
    kept, removed = [], []
    for p in parts:
        if is_claim(p) and len(p) <= MAX_SENTENCE:
            removed.append(p.strip())
        else:
            kept.append(p)
    return (" ".join(kept).strip(), removed)


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    ap.add_argument("--samples", type=int, default=25)
    args = ap.parse_args()

    skip = noindex_slugs()
    removed_all: list[tuple[str, str]] = []
    too_long: list[tuple[str, str]] = []
    files_changed = 0

    for f in sorted(BLOG.glob("*.md")):
        if f.name == "ARTICLES_COMPLETED.md":
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", text, re.S)
        if not m:
            continue
        slug = f.stem
        if slug in skip:
            continue
        head, body = text[: m.end()], text[m.end():]

        out_lines: list[str] = []
        in_fence = False
        changed = False
        for line in body.split("\n"):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_fence = not in_fence
                out_lines.append(line)
                continue
            # Never touch code, headings, or table rows.
            if in_fence or stripped.startswith("#") or stripped.startswith("|") \
                    or stripped.startswith("    ") or not stripped:
                out_lines.append(line)
                continue

            new, removed = process_line(line)
            for r in removed:
                removed_all.append((slug, r))
            for p in SENT_SPLIT.split(line):
                if is_claim(p) and len(p) > MAX_SENTENCE:
                    too_long.append((slug, p[:160]))
            if removed:
                changed = True
                # Preserve list markers and bold-lead formatting when the line had one.
                if new:
                    out_lines.append(new)
                # A line that was ENTIRELY a claim is dropped rather than left blank.
            else:
                out_lines.append(line)

        if changed:
            files_changed += 1
            if args.apply:
                f.write_text(head + "\n".join(out_lines), encoding="utf-8", newline="\n")

    print(f"claim sentences removed : {len(removed_all)}")
    print(f"articles changed        : {files_changed}")
    print(f"too long, left for review: {len(too_long)}")
    print("\n--- sample removals ---")
    for slug, s in removed_all[: args.samples]:
        print(f"  [{slug[:40]}]\n      {s[:150]}")
    if too_long:
        print("\n--- flagged, NOT edited (over length guard) ---")
        for slug, s in too_long[:8]:
            print(f"  [{slug[:40]}] {s}")
    if args.dry_run:
        print("\nDRY RUN — nothing written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
