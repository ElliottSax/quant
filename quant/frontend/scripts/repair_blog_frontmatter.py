#!/usr/bin/env python3
"""Repair the frontmatter defects that fix_blog_meta.py does not cover, on INDEXABLE posts only.

    python scripts/repair_blog_frontmatter.py --dry-run     # prints before/after for 10 samples, writes nothing
    python scripts/repair_blog_frontmatter.py --apply

What it fixes (each judged on the value the SITE parses, via the shared helpers in fix_blog_meta.py):

  echo_description   the description merely repeats the title (often "<Title>: Complete Guide This article"),
                     so Google's snippet tells a searcher nothing. Replaced with the post's OWN leading prose
                     (same extractor and quality gates as fix_blog_meta.py); if the prose offers nothing usable,
                     the post's own "**Meta Description**:" line is used; if neither, the post is left alone.
  quote_runs         values stored as '''''''text''''''' (the generator re-quoted scalars on every pass).
                     src/lib/frontmatter.ts already collapses these when reading, so this is hygiene: the value is
                     rewritten as one clean double-quoted line. Parsed value is identical before and after.
  canonical_url      the placeholder https://example.com/<slug>. The site never reads this key (page code builds
                     the canonical from the file name), so it is replaced with https://quantengines.com/blog/<file name>
                     purely so a future reader cannot pick up a wrong value.

Guarantees: body text is byte-identical (only the frontmatter character span is replaced, original newlines kept);
noindexed slugs and `status: template` posts are never touched; generated public/data/*.json is never touched; re-running
after --apply changes nothing (idempotent).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fix_blog_meta as F  # noqa: E402  (shared parsing + description extraction)

BLOG = F.BLOG
SCALAR_KEYS = ("title", "description", "author", "published_date", "last_updated", "reading_time")
SITE = "https://quantengines.com/blog/"
# LLM process artifacts that were published as posts (delivery summaries / manifests): not articles, so they get no
# polished description; they are reported for the owner to noindex or delete.
ARTIFACT_SLUGS = {"delivery-report", "final-manifest"}
DOUBLED_WORD = re.compile(r"\b(\w{3,})\s+\1\b", re.I)
META_LINE = re.compile(r"^\*\*Meta Description\*\*:[ \t]*(.+?)[ \t]*$", re.M)


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def is_echo(desc: str, title: str) -> bool:
    """True when the description is just the title again (equal, a prefix of it, or starting with it)."""
    nd, nt = norm(desc), norm(title)
    if not nd or not nt:
        return False
    if nd == nt or nt.startswith(nd):      # identical, or a truncated copy of the title
        return True
    # starts with the title but adds almost nothing after it ("<Title>: Complete Guide This article")
    return nd.startswith(nt) and len(nd) - len(nt) < 40


TEMPLATE_SENTENCE = re.compile(
    r"is a powerful (?:options trading )?(?:approach|strategy) for|"
    r"valuable insights and information|^\s*generate consistent profits", re.I)

# What each promise in a "**Meta Description**:" line needs to exist in the post (a matching heading).
PROMISES = (
    (re.compile(r"entry/exit|entry and exit", re.I), (r"entry", r"exit")),
    (re.compile(r"greeks", re.I), (r"greeks",)),
    (re.compile(r"real-world", re.I), (r"example",)),
    (re.compile(r"p&l|profit", re.I), (r"p&l|profit",)),
    (re.compile(r"\bfaq\b", re.I), (r"faq|frequently|q&a",)),
)


def body_prose(body: str) -> str:
    """fix_blog_meta's prose cleaner, but with label prefixes (Quick Summary etc.) removed so the label itself never
    starts a description, and FAQ question/answer lines removed so they are never spliced onto one."""
    body = re.sub(r"^\*\*Meta Description\*\*:.*$", " ", body, flags=re.M)
    body = re.sub(r"^\s*\*{0,2}(?:[QA]\d+\*{0,2}[:.]|[QA]\*{0,2}:).*$", " ", body, flags=re.M)
    body = re.sub(r"^\*\*(?:Quick Summary|Summary|TL;DR|Overview)\*\*:[ 	]*", "", body, flags=re.M)
    return F.clean_body(body)


def headings(body: str) -> list[str]:
    return [h.lower() for h in re.findall(r"^#{1,6}\s+(.+)$", body, re.M)]


def promises_supported(meta: str, body: str) -> bool:
    hs = headings(body)
    for trigger, needs in PROMISES:
        if trigger.search(meta) and not all(any(re.search(n, h) for h in hs) for n in needs):
            return False
    return True


def meta_line_fallback(body: str) -> str | None:
    m = META_LINE.search(body)
    if not m:
        return None
    s = re.sub(r"\s+", " ", m.group(1)).strip()
    if (F.MIN_DESC <= len(s) <= F.MAX_DESC and not F.FILLER_DESC.search(s) and not F.TRUNCATED_DESC.search(s)
            and promises_supported(s, body)):
        return s
    return None


def choose_description(title: str, body: str) -> str | None:
    """Prefer genuine prose; else the post's own meta line (promises verified against its headings); else None."""
    prose = F.build_description(body_prose(body))
    if prose and not TEMPLATE_SENTENCE.search(prose) and not is_echo(prose, title) and not DOUBLED_WORD.search(prose):
        return prose
    meta = meta_line_fallback(body)
    if meta and not is_echo(meta, title) and not DOUBLED_WORD.search(meta):
        return meta
    return None


def repair_block(slug: str, block: str, body: str, allowed=None) -> tuple[str, list[str]]:
    """Return (new_block, list of change tags). Never raises on odd input; leaves what it cannot fix."""
    changes: list[str] = []
    title = F.read_value(block, "title")
    desc = F.read_value(block, "description")

    if desc and is_echo(desc, title) and slug not in ARTIFACT_SLUGS:
        new = choose_description(title, body)
        if new and (allowed is None or allowed(new)):
            block = F.write_value(block, "description", new)
            changes.append("echo_description")

    for key in SCALAR_KEYS:
        span = F.key_span(block, key)
        if not span:
            continue
        raw = re.search(rf"^{key}:[ \t]*(.*(?:\r?\n[ \t]+\S.*)*)$", block, re.M).group(1)
        if "''" in raw:
            new_block = F.write_value(block, key, span[2])
            if new_block != block:
                block = new_block
                changes.append(f"quote_runs:{key}")

    if re.search(r"^canonical_url:[ \t]*.*example\.com", block, re.M):
        block = re.sub(r"^canonical_url:[ \t]*.*$", f'canonical_url: "{SITE}{slug}"', block, count=1, flags=re.M)
        changes.append("canonical_url")
    return block, changes


def process_text(slug: str, text: str, allowed=None) -> tuple[str, list[str]]:
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    if not m:
        return text, []
    block, body = m.group(1), text[m.end():]
    new_block, changes = repair_block(slug, block, body, allowed)
    if not changes:
        return text, []
    # rewritten lines must use the file's own newline style (CRLF files otherwise end up with bare LFs in the frontmatter)
    eol = "\r\n" if re.match(r"^---\r\n", text) else "\n"
    new_block = re.sub(r"\r?\n", eol, new_block)
    return text[: m.start(1)] + new_block + text[m.end(1):], changes


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    ap.add_argument("--samples", type=int, default=10)
    args = ap.parse_args()

    skip = F.noindex_slugs()
    tally: dict[str, int] = {}
    touched: list[tuple[str, list[str], str, str]] = []
    unfixed_echo: list[str] = []
    considered = 0

    def indexable():
        for f in sorted(BLOG.glob("*.md")):
            if f.name == "ARTICLES_COMPLETED.md":
                continue
            text = f.read_bytes().decode("utf-8", errors="surrogateescape")
            m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
            if m and f.stem not in skip and F.read_value(m.group(1), "status") != "template":
                yield f, text, m

    # Pre-pass: a replacement shared by several posts, or equal to a description already in use, is no better than the
    # echo it replaces (identical meta descriptions read as low value), so those posts are left alone and reported.
    existing = {norm(F.read_value(m.group(1), "description")) for _, _, m in indexable()}
    counts: dict[str, int] = {}
    for f, text, m in indexable():
        d, t = F.read_value(m.group(1), "description"), F.read_value(m.group(1), "title")
        if is_echo(d, t) and f.stem not in ARTIFACT_SLUGS:
            c = choose_description(t, text[m.end():])
            if c:
                counts[norm(c)] = counts.get(norm(c), 0) + 1

    def allowed(cand: str) -> bool:
        return counts.get(norm(cand), 0) == 1 and norm(cand) not in existing

    for f, text, m in indexable():
        slug = f.stem
        considered += 1
        new_text, changes = process_text(slug, text, allowed)
        d, t = F.read_value(m.group(1), "description"), F.read_value(m.group(1), "title")
        if is_echo(d, t) and "echo_description" not in changes:
            unfixed_echo.append(slug)
        if not changes:
            continue
        for c in changes:
            tally[c.split(":")[0]] = tally.get(c.split(":")[0], 0) + 1
        touched.append((slug, changes, m.group(1), re.match(r"^---\r?\n(.*?)\r?\n---", new_text, re.S).group(1)))
        if args.apply:
            f.write_bytes(new_text.encode("utf-8", errors="surrogateescape"))

    print(f"indexable posts considered : {considered}")
    print(f"posts changed              : {len(touched)}")
    for k, v in sorted(tally.items()):
        print(f"  {k:<18} {v}")
    print(f"echo descriptions left alone (no unique, honest replacement / process artifact): {len(unfixed_echo)}")
    for s_ in unfixed_echo:
        print(f"    {s_}")
    print("\n--- before/after samples (changed keys only) ---")
    shown = 0
    for slug, changes, old, new in touched:
        if shown >= args.samples:
            break
        print(f"\n{slug}   {sorted(set(changes))}")
        for key in (*SCALAR_KEYS, "canonical_url"):
            a, b = F.read_value(old, key) if key != "canonical_url" else _line(old, key), \
                F.read_value(new, key) if key != "canonical_url" else _line(new, key)
            if _line(old, key) != _line(new, key):
                print(f"  {key}:\n    was: {_line(old, key)[:150]}\n    now: {_line(new, key)[:150]}")
        shown += 1
    if args.dry_run:
        print("\nDRY RUN - nothing written.")
    return 0


def _line(block: str, key: str) -> str:
    m = re.search(rf"^{key}:[ \t]*(.*)$", block, re.M)
    return m.group(1) if m else ""


if __name__ == "__main__":
    sys.exit(main())
