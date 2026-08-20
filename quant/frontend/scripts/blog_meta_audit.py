#!/usr/bin/env python3
"""Audit blog frontmatter the way the SITE parses it, not the way YAML would.

    python scripts/blog_meta_audit.py

The site does not use a YAML library. `src/lib/frontmatter.ts` reads a key with a
line-folding regex and then collapses runs of stray quotes, because the generation
pipeline re-quoted scalars on every pass. Any audit that parses these files with real
YAML measures a different corpus than the one being served, so this mirrors the
TypeScript exactly — including its quote-run collapsing, which is what makes the
seven-quote titles render clean despite looking corrupt on disk.

Defect classes counted here, all judged on the POST-PARSE value:

  missing    no description, or too short to occupy a result snippet
  filler     restates the title or promises value without delivering any
  truncated  cut off mid-sentence at authoring time -- ends on a comma, a conjunction,
             or with no terminal punctuation at all. These render in Google as dangling
             fragments and are the worst of the three, because they look deliberate.
  long_title exceeds what a result renders once " | QuantEngines" is appended
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "content" / "blog"
NOINDEX_TS = ROOT / "src" / "lib" / "noindex-drafts.ts"

TITLE_SUFFIX = len(" | QuantEngines")
MAX_TITLE_RENDERED = 75
MIN_DESC = 60

FILLER = re.compile(
    r"valuable insights and information|comprehensive guide to|^\s*in this article", re.I)
# A description that stops on a comma, a semicolon, a dangling conjunction, or with no
# sentence-final punctuation was cut off rather than written to length.
TRUNCATED = re.compile(r"(?:[,;:]|\b(?:and|or|with|for|the|a|an|to|of|in|by)\b)\s*$", re.I)


def clean_value(raw: str) -> str:
    """Mirror of cleanFrontmatterValue() in src/lib/frontmatter.ts."""
    if not raw:
        return ""
    v = re.sub(r"\s+", " ", raw).strip()
    v = re.sub(r"'{2,}", "'", v)          # collapse quote runs (also undoes YAML '' escapes)
    v = re.sub(r'"{2,}', '"', v)
    v = re.sub(r"^['\"\s]+|['\"\s]+$", "", v)
    return v.strip()


def read_value(block: str, key: str) -> str:
    """Mirror of readFrontmatterValue(), including its line folding."""
    m = re.search(rf"^{key}:[ \t]*(.*(?:\r?\n[ \t]+\S.*)*)$", block, re.M)
    return clean_value(m.group(1)) if m else ""


def noindex_slugs() -> set[str]:
    if not NOINDEX_TS.exists():
        return set()
    return set(re.findall(r"'([a-z0-9][a-z0-9\-]{3,})'", NOINDEX_TS.read_text(encoding="utf-8")))


def audit() -> dict[str, list[tuple[str, str]]]:
    skip = noindex_slugs()
    out: dict[str, list[tuple[str, str]]] = {
        "missing": [], "filler": [], "truncated": [], "long_title": [], "ok": []}
    for f in sorted(BLOG.glob("*.md")):
        if f.name == "ARTICLES_COMPLETED.md":
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
        if not m:
            continue
        block = m.group(1)
        slug = f.stem                     # routes derive the slug from the FILE NAME
        if slug in skip or read_value(block, "status") == "template":
            continue

        desc = read_value(block, "description")
        title = read_value(block, "title")

        if len(title) + TITLE_SUFFIX > MAX_TITLE_RENDERED:
            out["long_title"].append((slug, f"{len(title) + TITLE_SUFFIX}: {title}"))

        if len(desc) < MIN_DESC:
            out["missing"].append((slug, desc))
        elif FILLER.search(desc):
            out["filler"].append((slug, desc[:70]))
        elif TRUNCATED.search(desc):
            out["truncated"].append((slug, desc[-70:]))
        else:
            out["ok"].append((slug, desc[:50]))
    return out


if __name__ == "__main__":
    res = audit()
    total = sum(len(v) for k, v in res.items() if k != "long_title")
    print(f"indexable posts: {total}\n")
    for k in ("ok", "missing", "filler", "truncated", "long_title"):
        print(f"  {k:<11} {len(res[k]):>4}")
    for k in ("truncated", "missing", "filler"):
        print(f"\n--- {k} samples ---")
        for slug, v in res[k][:5]:
            print(f"  {slug}\n      {v!r}")
