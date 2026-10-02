"""pytest tests for repair_blog_frontmatter.py (run: python -m pytest scripts/test_repair_blog_frontmatter.py -q)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fix_blog_meta as F  # noqa: E402
import repair_blog_frontmatter as R  # noqa: E402

TEMPLATE_BODY = (
    "\n# Collar Strategy for Options Trading 2026: Complete Guide\n\n"
    "**Meta Description**: Master the collar strategy. Learn entry/exit rules, Greeks impact, real-world examples, "
    "P&L diagrams, and FAQ.\n\n**Quick Summary**: The Collar strategy is a powerful options trading approach for Combined hedging.\n\n"
    "## Entry Rules\n\ntext\n\n## Exit Rules\n\ntext\n\n## Greeks Explained\n\ntext\n\n## Real-World Example: Complete Trade\n\ntext\n\n"
    "## P&L Diagram\n\ntext\n\n## FAQ: Collar Questions\n\n**Q1**: What is the max profit?\n\nAnswer here.\n"
)

BAD_FM = (
    "---\n"
    "title: '''''''Collar Strategy for Options Trading 2026: Complete Guide'''''''\n"
    "slug: 12_collar\n"
    "description: '''''''Collar Strategy for Options Trading 2026: Complete Guide This article'\n"
    "author: \"QuantEngines\"\n"
    "published_date: '''''''2026-03-21'''''''\n"
    "reading_time: '''6'''\n"
    "canonical_url: https://example.com/12_collar\n"
    "---"
)


def test_is_echo_equal_prefix_and_trailing_fragment():
    t = "Collar Strategy for Options Trading 2026: Complete Guide"
    assert R.is_echo(t, t)
    assert R.is_echo("Collar Strategy for Options Trading 2026: Complete Guide This article", t)
    assert R.is_echo("Collar Strategy for Options", t)
    assert not R.is_echo("Altcoin seasonality and cycle trading have gained significant attention in recent years, "
                         "particularly among quantitative traders.", "Altcoin Seasonality and Cycle Trading")


def test_meta_line_used_only_when_promises_have_headings():
    assert "Master the collar strategy" in R.choose_description("Collar Strategy", TEMPLATE_BODY)
    no_faq = TEMPLATE_BODY.replace("## FAQ: Collar Questions", "## Notes")
    assert R.choose_description("Collar Strategy", no_faq) is None or "FAQ" not in R.choose_description("Collar Strategy", no_faq)


def test_faq_fragment_never_spliced_into_prose():
    prose = R.body_prose(TEMPLATE_BODY)
    assert "max profit" not in prose and "Q1" not in prose


def test_doubled_word_rejected():
    body = TEMPLATE_BODY.replace("collar strategy.", "collar strategy strategy.")
    assert R.choose_description("Collar Strategy", body) is None


def test_repair_block_normalizes_quotes_and_canonical_and_description():
    block = BAD_FM.split("\n", 1)[1].rsplit("\n---", 1)[0]
    new, changes = R.repair_block("12-collar", block, TEMPLATE_BODY)
    assert F.read_value(new, "title") == "Collar Strategy for Options Trading 2026: Complete Guide"
    assert F.read_value(new, "published_date") == "2026-03-21"
    assert F.read_value(new, "reading_time") == "6"
    assert F.read_value(new, "description").startswith("Master the collar strategy.")
    assert 'canonical_url: "https://quantengines.com/blog/12-collar"' in new
    assert {"echo_description", "canonical_url"} <= {c.split(":")[0] for c in changes}
    assert "''" not in new


def test_parsed_values_identical_for_quote_only_changes():
    block = "title: '''''''A Good Title'''''''\npublished_date: '''''''2026-03-21'''''''\nreading_time: '''11'''"
    new, _ = R.repair_block("a-good-title", block, "Body.")
    for k in ("title", "published_date", "reading_time"):
        assert F.read_value(new, k) == F.read_value(block, k)


def test_idempotent():
    block = BAD_FM.split("\n", 1)[1].rsplit("\n---", 1)[0]
    once, _ = R.repair_block("12-collar", block, TEMPLATE_BODY)
    twice, changes = R.repair_block("12-collar", once, TEMPLATE_BODY)
    assert once == twice and changes == []


def _setup(tmp_path, monkeypatch, files):
    blog = tmp_path / "blog"
    blog.mkdir()
    for name, data in files.items():
        (blog / name).write_bytes(data)
    nx = tmp_path / "noindex.ts"
    nx.write_text("export const S = new Set(['noindexed-post'])", encoding="utf-8")
    monkeypatch.setattr(R, "BLOG", blog)
    monkeypatch.setattr(F, "BLOG", blog)
    monkeypatch.setattr(F, "NOINDEX_TS", nx)
    return blog


def test_main_apply_end_to_end_body_untouched_noindex_skipped_idempotent(tmp_path, monkeypatch):
    body_crlf = TEMPLATE_BODY.replace("\n", "\r\n")
    bad = BAD_FM.replace("\n", "\r\n") + body_crlf
    files = {"12-collar.md": bad.encode(), "noindexed-post.md": bad.encode(), "tidy.md": b"---\ntitle: Tidy\ndescription: A fine description that is long enough to be useful in a search result snippet here.\n---\nBody\n"}
    blog = _setup(tmp_path, monkeypatch, files)
    monkeypatch.setattr(sys, "argv", ["x", "--apply"])
    R.main()
    out = (blog / "12-collar.md").read_bytes()
    assert out.endswith(body_crlf.encode())                         # body byte-identical, CRLF preserved
    fm_bytes = out[: out.index(b"\r\n---\r\n") + 7]
    assert b"\n" not in fm_bytes.replace(b"\r\n", b"")              # no bare LF left inside a CRLF frontmatter
    assert (blog / "noindexed-post.md").read_bytes() == bad.encode()  # noindexed: untouched
    assert (blog / "tidy.md").read_bytes() == files["tidy.md"]        # nothing to fix: untouched
    assert b"example.com" not in out and b"'''" not in out
    monkeypatch.setattr(sys, "argv", ["x", "--apply"])
    R.main()
    assert (blog / "12-collar.md").read_bytes() == out               # second run changes nothing


def test_duplicate_replacement_across_posts_is_skipped(tmp_path, monkeypatch):
    def post(title):
        return (f'---\ntitle: "{title}"\ndescription: "{title} This article"\n---\n\n'
                "# x\n\nWe'll cover essential protocols, real yield calculations, security best practices, and tax considerations.\n").encode()
    blog = _setup(tmp_path, monkeypatch, {"a.md": post("Alpha Guide To Yield Farming"), "b.md": post("Beta Guide To Mining Pools")})
    monkeypatch.setattr(sys, "argv", ["x", "--apply"])
    R.main()
    assert (blog / "a.md").read_bytes() == post("Alpha Guide To Yield Farming")   # shared sentence: left alone
