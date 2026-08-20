#!/usr/bin/env python3
"""Repair blog frontmatter: meta descriptions, over-long titles, fabricated bylines.

    python scripts/fix_blog_meta.py --dry-run      # show what would change
    python scripts/fix_blog_meta.py --apply

Measured defects across the 458 indexable posts (see scripts/blog_meta_audit.py):

  115 missing    no description, so Google writes its own snippet -- for these posts
                 usually from a code block, because that is most of the page.
   76 filler     "Comprehensive guide to <title>." Restates the title; tells a searcher
                 nothing they did not already read in the blue link.
   15 truncated  cut off mid-sentence at authoring time ("...Entry/exit rules,").
                 The worst of the three: it renders as a dangling fragment that looks
                 deliberate rather than missing.
  130 long_title exceeds what a result renders once " | QuantEngines" is appended.

DESCRIPTIONS ARE EXTRACTED FROM THE ARTICLE'S OWN PROSE, NEVER COMPOSED. A meta
description is a promise about the page; a generated one can promise something the page
does not contain. Using the article's own sentences makes that impossible by
construction. Where no sentence clears the quality gates the post is LEFT ALONE and
reported -- an absent description is better than a misleading one, because Google will
at least draw its snippet from the real page.

PARSING MIRRORS THE SITE, NOT YAML. src/lib/frontmatter.ts reads keys with a
line-folding regex and collapses runs of stray quotes, because the generation pipeline
re-quoted scalars on every pass (hence titles sitting on disk as
'''''''Title'''''''). Parsing these files with a real YAML library would measure a
different corpus than the one being served. Values are rewritten in clean double-quoted
single-line form, which both parsers agree on.

Only indexable posts are touched. Slugs carrying robots:noindex are skipped -- improving
the SERP presentation of a deliberately de-indexed page is wasted work.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "content" / "blog"
NOINDEX_TS = ROOT / "src" / "lib" / "noindex-drafts.ts"

# Google renders roughly 155-160 characters. 90 is comfortably a useful snippet; the
# earlier 110 floor rejected perfectly good two-sentence openings and left 111 posts
# with no description at all, which is strictly worse than a slightly short one.
MIN_DESC, MAX_DESC = 90, 158
TITLE_SUFFIX = len(" | QuantEngines")
MAX_TITLE_RENDERED = 75
MIN_TITLE = 30

FILLER_DESC = re.compile(
    r"valuable insights and information|comprehensive guide to|^\s*in this article", re.I)
TRUNCATED_DESC = re.compile(
    r"(?:[,;:]|\b(?:and|or|with|for|the|a|an|to|of|in|by)\b)\s*$", re.I)

# Sentence openings that restate the title or promise value instead of delivering it.
FILLER_SENTENCE = re.compile(
    r"^\s*(comprehensive guide to|a comprehensive guide|this article provides|"
    r"in this article|this guide (?:covers|will|explains)|this post|"
    r"everything you need to know)", re.I)

# A trailing segment that adds no search value. Dropped before any hard truncation,
# because "Complete Guide" is exactly the part nobody searches for.
FILLER_TAIL = re.compile(
    r"^(?:a |an |the )?(?:complete|ultimate|comprehensive|definitive|full|"
    r"step[- ]by[- ]step|practical|beginner'?s?|essential)?\s*"
    r"(?:guide|tutorial|handbook|overview|walkthrough|explained)$", re.I)

BODY_BYLINE = re.compile(r"^\*\*Author:\*\*[ \t]*.+?[ \t]*\r?\n", re.M)


# --------------------------------------------------------------------------- parsing
def clean_value(raw: str) -> str:
    """Mirror of cleanFrontmatterValue() in src/lib/frontmatter.ts."""
    if not raw:
        return ""
    v = re.sub(r"\s+", " ", raw).strip()
    v = re.sub(r"'{2,}", "'", v)
    v = re.sub(r'"{2,}', '"', v)
    v = re.sub(r"^['\"\s]+|['\"\s]+$", "", v)
    return v.strip()


def key_span(block: str, key: str) -> tuple[int, int, str] | None:
    """Byte span of a key's full value INCLUDING folded continuation lines."""
    m = re.search(rf"^{key}:[ \t]*(.*(?:\r?\n[ \t]+\S.*)*)$", block, re.M)
    if not m:
        return None
    return m.start(), m.end(), clean_value(m.group(1))


def read_value(block: str, key: str) -> str:
    s = key_span(block, key)
    return s[2] if s else ""


def write_value(block: str, key: str, value: str) -> str:
    """Replace a key's whole value (continuation lines included) with one clean line."""
    safe = re.sub(r"\s+", " ", value).replace('"', "'").strip()
    line = f'{key}: "{safe}"'
    span = key_span(block, key)
    if span:
        return block[: span[0]] + line + block[span[1]:]
    return block.rstrip() + "\n" + line


def noindex_slugs() -> set[str]:
    if not NOINDEX_TS.exists():
        return set()
    return set(re.findall(r"'([a-z0-9][a-z0-9\-]{3,})'", NOINDEX_TS.read_text(encoding="utf-8")))


# ----------------------------------------------------------------------- extraction
def clean_body(body: str) -> str:
    """Strip everything that is not the author's running prose."""
    b = re.sub(r"```.*?```", " ", body, flags=re.S)
    b = re.sub(r"^\s*#{1,6}\s+.*$", " ", b, flags=re.M)
    b = BODY_BYLINE.sub(" ", b)
    b = re.sub(r"^\s*\*\*(?:Author|Category|Date|Published|Last Updated|Tags):\*\*.*$",
               " ", b, flags=re.M)
    b = re.sub(r"^\s*[-*+]\s+.*$", " ", b, flags=re.M)
    b = re.sub(r"^\s*\d+\.\s+.*$", " ", b, flags=re.M)
    b = re.sub(r"^\s*[|>].*$", " ", b, flags=re.M)
    b = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", b)
    b = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", b)
    b = re.sub(r"`([^`]*)`", r"\1", b)
    b = re.sub(r"\*\*|__|\*|_", "", b)
    return re.sub(r"\s+", " ", b).strip()


def sentences(prose: str) -> list[str]:
    protected = prose
    for abbr in ("U.S.", "e.g.", "i.e.", "vs.", "Dr.", "Inc.", "etc.", "Fig.", "No."):
        protected = protected.replace(abbr, abbr.replace(".", "\x00"))
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", protected)
    return [p.replace("\x00", ".").strip() for p in parts if p.strip()]


def usable_sentence(s: str) -> bool:
    if not (25 <= len(s) <= 300):
        return False
    if FILLER_SENTENCE.match(s) or FILLER_DESC.search(s):
        return False
    if not s[0].isalnum():
        return False
    if s.count("(") != s.count(")"):
        return False
    return bool(re.search(r"[a-z]", s))       # an all-caps fragment is a label


def build_description(prose: str) -> str | None:
    """Join the article's own leading sentences until the snippet is long enough.

    Two passes. The first takes strictly consecutive sentences, which reads best. Only
    if that cannot reach the minimum does the second pass skip a sentence that is merely
    too long to fit -- an earlier version stopped dead at the first oversized sentence,
    which is why 111 posts ended up with no description despite having perfectly good
    prose one sentence further down.
    """
    candidates = [s for s in sentences(prose)[:10] if usable_sentence(s)]

    for allow_skip in (False, True):
        out: list[str] = []
        total = 0
        for s in candidates:
            projected = total + (1 if out else 0) + len(s)
            if projected > MAX_DESC:
                if allow_skip and not out:
                    continue          # nothing started yet; try a later sentence
                if allow_skip:
                    continue          # keep looking for one that fits
                break
            out.append(s)
            total = projected
            if total >= MIN_DESC:
                break
        if out and total >= MIN_DESC:
            return " ".join(out)
    return None


def shorten_title(title: str) -> str | None:
    """Cut a title to render fully, preferring to drop filler over truncating."""
    budget = MAX_TITLE_RENDERED - TITLE_SUFFIX
    if len(title) <= budget:
        return None

    # 1. Drop a trailing segment that is pure filler ("...: Complete Guide").
    for sep in (": ", " — ", " – ", " - ", " | "):
        if sep in title:
            head, _, tail = title.rpartition(sep)
            if FILLER_TAIL.match(tail.strip()) and MIN_TITLE <= len(head.strip()) <= budget:
                return head.strip()

    # 2. Otherwise keep the head before a subtitle, if that alone fits and is substantial.
    for sep in (": ", " — ", " – ", " - "):
        head = title.split(sep)[0].strip()
        if MIN_TITLE <= len(head) <= budget:
            return head

    # 3. Last resort: trim on a word boundary rather than mid-word.
    cut = title[:budget].rsplit(" ", 1)[0].rstrip(" ,;:-—–")
    return cut if len(cut) >= MIN_TITLE else None


# ---------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    ap.add_argument("--samples", type=int, default=8)
    args = ap.parse_args()

    skip = noindex_slugs()
    desc_written, title_cut, byline_cut, no_candidate, title_stuck = [], [], [], [], []
    considered = 0

    for f in sorted(BLOG.glob("*.md")):
        if f.name == "ARTICLES_COMPLETED.md":
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", text, re.S)
        if not m:
            continue
        block, body = m.group(1), text[m.end():]
        slug = f.stem                       # routes derive the slug from the FILE NAME
        if slug in skip or read_value(block, "status") == "template":
            continue
        considered += 1

        new_block, new_body = block, body

        if BODY_BYLINE.search(new_body):
            new_body = BODY_BYLINE.sub("", new_body)
            byline_cut.append(slug)

        desc = read_value(new_block, "description")
        if len(desc) < 60 or FILLER_DESC.search(desc) or TRUNCATED_DESC.search(desc):
            built = build_description(clean_body(new_body))
            if built:
                new_block = write_value(new_block, "description", built)
                desc_written.append((slug, desc, built))
            else:
                no_candidate.append(slug)

        title = read_value(new_block, "title")
        if len(title) + TITLE_SUFFIX > MAX_TITLE_RENDERED:
            short = shorten_title(title)
            if short:
                new_block = write_value(new_block, "title", short)
                title_cut.append((slug, title, short))
            else:
                title_stuck.append(slug)

        if args.apply and (new_block != block or new_body != body):
            f.write_text(f"---\n{new_block}\n---\n{new_body}", encoding="utf-8")

    print(f"indexable posts considered : {considered}")
    print(f"descriptions written       : {len(desc_written)}")
    print(f"  no usable sentence       : {len(no_candidate)}  (left unchanged)")
    print(f"titles shortened           : {len(title_cut)}")
    print(f"  could not shorten safely : {len(title_stuck)}  (left unchanged)")
    print(f"body bylines removed       : {len(byline_cut)}")

    print("\n--- sample descriptions ---")
    for slug, old, new in desc_written[: args.samples]:
        print(f"\n{slug}\n  was ({len(old)}): {old[:70]!r}\n  now ({len(new)}): {new}")
    print("\n--- sample titles ---")
    for slug, old, new in title_cut[: args.samples]:
        print(f"\n{slug}\n  was ({len(old)+TITLE_SUFFIX}): {old}\n  now ({len(new)+TITLE_SUFFIX}): {new}")

    if args.dry_run:
        print("\nDRY RUN — nothing written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
