#!/usr/bin/env python3
"""Unit tests for congress_alerts_digest.py's pure logic -- matching,
date parsing, and HTML-escaping of third-party feed data before it lands in
an email. No network, no Supabase/Resend/FMP credentials: `requests` is
imported by the module under test but never called by anything exercised
here.

Run with:  python -m unittest scripts/test_congress_alerts_digest.py -v
(from the quant/ directory, i.e. C:\\projects\\quant\\quant)
"""

from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from congress_alerts_digest import (  # noqa: E402
    build_digest_email,
    parse_date,
    trade_matches,
)


def make_trade(**overrides):
    trade = {
        "ticker": "AAPL",
        "member": "Jane Doe",
        "chamber": "House",
        "transactionDate": "2026-09-01",
        "disclosureDate": "2026-09-05",
        "assetDescription": "Apple Inc.",
        "type": "Purchase",
        "amount": "$1,001 - $15,000",
        "link": "https://example.com",
    }
    trade.update(overrides)
    return trade


class ParseDateTests(unittest.TestCase):
    def test_valid_date(self):
        self.assertEqual(parse_date("2026-09-05"), date(2026, 9, 5))

    def test_empty_string_returns_none(self):
        self.assertIsNone(parse_date(""))

    def test_none_input_returns_none(self):
        self.assertIsNone(parse_date(None))

    def test_malformed_date_returns_none_not_raise(self):
        # This is exactly the "FMP returns malformed data" case: a bad date
        # string must not crash the whole digest run for every subscriber.
        for bad in ("not-a-date", "2026/09/05", "09-05-2026", "2026-13-40"):
            with self.subTest(bad=bad):
                self.assertIsNone(parse_date(bad))


class TradeMatchesTests(unittest.TestCase):
    def test_no_filters_matches_everything(self):
        self.assertTrue(trade_matches(make_trade(), []))

    def test_ticker_filter_matches_case_insensitively(self):
        trade = make_trade(ticker="aapl")
        self.assertTrue(trade_matches(trade, [{"ticker": "AAPL"}]))

    def test_ticker_filter_rejects_non_match(self):
        trade = make_trade(ticker="MSFT")
        self.assertFalse(trade_matches(trade, [{"ticker": "AAPL"}]))

    def test_member_name_filter_is_substring_case_insensitive(self):
        trade = make_trade(member="Senator Jane Q. Doe")
        self.assertTrue(trade_matches(trade, [{"member_name": "jane"}]))

    def test_chamber_filter(self):
        trade = make_trade(chamber="Senate")
        self.assertFalse(trade_matches(trade, [{"chamber": "House"}]))
        self.assertTrue(trade_matches(trade, [{"chamber": "Senate"}]))

    def test_multiple_filters_are_ored(self):
        trade = make_trade(ticker="TSLA", chamber="Senate")
        filters = [{"ticker": "AAPL"}, {"chamber": "Senate"}]
        self.assertTrue(trade_matches(trade, filters))

    def test_single_row_requires_all_its_own_criteria(self):
        # One filter row with BOTH a ticker and a chamber set is an AND
        # within that row -- only the OR is across separate rows.
        trade = make_trade(ticker="AAPL", chamber="House")
        row = {"ticker": "AAPL", "chamber": "Senate"}
        self.assertFalse(trade_matches(trade, [row]))


class BuildDigestEmailEscapingTests(unittest.TestCase):
    """The htmlpayload interpolates FMP fields (member/office name, ticker,
    amount, dates) directly. FMP is a third-party feed, so anything it
    returns must be escaped before landing in an HTML email client renders."""

    def test_html_special_chars_in_member_name_are_escaped(self):
        trade = make_trade(member='<img src=x onerror=alert(1)> & "Someone"')
        _subject, html, _text = build_digest_email([trade], "tok123", "pro")
        self.assertNotIn("<img src=x onerror=alert(1)>", html)
        self.assertIn("&lt;img", html)
        self.assertIn("&amp;", html)

    def test_html_special_chars_in_ticker_are_escaped(self):
        trade = make_trade(ticker="<script>evil()</script>")
        _subject, html, _text = build_digest_email([trade], "tok123", "pro")
        self.assertNotIn("<script>evil()</script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_plain_text_body_is_unaffected(self):
        # The plaintext part of the email is not HTML, so it should keep the
        # raw value rather than HTML-entity-encoding it.
        trade = make_trade(member="A & B")
        _subject, _html, text = build_digest_email([trade], "tok123", "pro")
        self.assertIn("A & B", text)

    def test_manage_token_appears_in_both_bodies(self):
        _subject, html, text = build_digest_email([make_trade()], "tok-xyz", "free")
        self.assertIn("tok-xyz", html)
        self.assertIn("tok-xyz", text)


if __name__ == "__main__":
    unittest.main()
