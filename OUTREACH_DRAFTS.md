# Outreach drafts — Congress late-filers leaderboard

**Status: DRAFTS ONLY. Nothing has been sent.** Elliott needs to review, pick
the send channel for each (see notes), and send these himself — no
accounts/contacts are set up for any of these three yet.

## What this is pitching

`/congress-stock-trades/late-filers` on quantengines.com — a real,
data-backed STOCK Act filing-timeliness leaderboard. It's not a mockup: it's
live, built from `getCongressTrades()` in `src/lib/congress-trades.ts`, which
sources official House & Senate financial disclosures (via Financial Modeling
Prep, pulling from efdsearch.senate.gov + disclosures-clerk.house.gov). It
measures the calendar-day gap between each trade's transaction date and its
disclosure date against the STOCK Act's 45-day filing deadline.

**Verified live** (curled the production page 2026-09-07 — see the JSON
embedded in the RSC payload, not a guess):

- 199 trades in the current rolling window have usable transaction +
  disclosure dates, as of the page's last-updated date of 2026-08-28.
- 15.1% of those were filed after the 45-day deadline.
- 39 days average time-to-disclose across all trades in the window.
- Slowest individual filing: **John Boozman** (Senate), an AAXJ trade —
  transaction date 2025-11-06, not disclosed until 2026-08-24 — **291 days**,
  about 6.5x the 45-day requirement.
- Top of the "most late filings" leaderboard:
  1. **Richard Blumenthal** (Senate) — 16 of 71 trades filed late (worst: 49 days)
  2. **John Boozman** (Senate) — 7 of 7 trades filed late (worst: 291 days)
  3. **Michael Patrick Guest** (House) — 4 of 4 trades filed late (worst: 244 days)
  4. **Jared Moskowitz** (House) — 3 of 3 trades filed late (worst: 46 days)

## ⚠️ Before sending anything, re-pull fresh numbers

The page revalidates daily (`export const revalidate = 86400`) and the
underlying disclosure feed updates continuously, so the exact figures above
will drift. **Right before sending each piece below, re-check
https://quantengines.com/congress-stock-trades/late-filers and swap in
whatever the live "Trades with usable dates / % filed after 45 days / Avg.
days to disclose" numbers say that day**, and re-copy the "Share this" box
on the page itself — it's built to be pasted verbatim and already reflects
current data. Don't send the numbers in this doc without checking; they're a
snapshot from 2026-09-07, one week old already at time of review.

## Sending logistics (checked live, 2026-09-07)

- **Quantocracy**: no public submission email found. They run a contact
  form at https://quantocracy.com/contact/ with three fields — Name, Email,
  Message. Use that form; paste the blurb below into "Message."
- **PyQuant News**: no direct pitch email found either. They have a
  dedicated submission page/form at
  https://pyquantnews.com/write-for-pyquant-news/ — paste content there and
  put your email at the end per their instructions, so they can respond.
  Founder is Jason Strimpel (also active on LinkedIn/X @pyquantnews as a
  fallback contact route if the form doesn't fit a short pitch). The draft
  below is written as a short pitch email — if the form wants a full guest
  post instead of a pitch, treat this as a cover note and paste it into
  whatever intro field the form provides.
- **Quantified Strategies**: real contact email is
  **support@quantifiedstrategies.com**. Site is run by Oddmund Groette and
  Håkan Samuelsson (per their About page) — addressed the draft to them by
  name.

---

## 1. Quantocracy submission (contact form → "Message" field)

**Name:** Elliott Saxton
**Email:** [Elliott's preferred contact email — not autofilled here]
**Message:**

```
Hi Quantocracy team,

Submitting a post for the roundup — a data piece, not a strategy post, but
it's built entirely from real STOCK Act disclosure data and I think it fits
the "quantitative and empirical" bar.

Congress's Slowest Stock-Trade Filers — a STOCK Act 45-day filing-deadline
compliance check built from official House & Senate disclosure dates (via
FMP, sourced from efdsearch.senate.gov + disclosures-clerk.house.gov).
Measures the actual calendar-day gap between each trade's transaction date
and its disclosure date, not just "Congress traded X stock."

Current numbers from the live page: 15.1% of trades in the rolling
disclosure window were filed after the 45-day deadline, averaging 39 days
to disclose overall. Slowest filing on record right now is 291 days late —
about 6.5x the legal window. Full leaderboard + methodology + honest
limitations (it's a compliance-timing measure, not a legal violation
determination) here:

https://quantengines.com/congress-stock-trades/late-filers

Happy to answer anything about the data pipeline if useful for the writeup.

Thanks,
Elliott
```

---

## 2. Cold pitch — PyQuant News

**To:** via https://pyquantnews.com/write-for-pyquant-news/ (or Jason
Strimpel directly if a better contact turns up)
**Subject:** A STOCK Act compliance dataset your readers can query — 291-day-late filing on record

```
Hi Jason,

I built a small tool I think fits PyQuant News's "real code, real data"
bar better than most congressional-trading content out there, and wanted
to send it your way before pushing it anywhere else.

Most "Congress trading" content just reports what members bought. This one
measures something different and checkable: how long members actually take
to file, against the STOCK Act's hard 45-day disclosure deadline. It's
built off official House & Senate disclosure dates (via Financial Modeling
Prep, sourced from efdsearch.senate.gov + disclosures-clerk.house.gov) —
not scraped headlines, not modeled estimates.

Right now, live: 15.1% of trades in the current rolling window were filed
after the 45-day deadline, 39 days average time-to-disclose overall, and
the single slowest filing on record is 291 days — about 6.5x the legal
window (a Senate AAXJ trade: transaction 2025-11-06, disclosed 2026-08-24).
Full leaderboard, methodology, and stated limitations (it's a timing
measure, not a legal-violation determination — some delays are legitimate
extensions or amended filings) are here:

https://quantengines.com/congress-stock-trades/late-filers

If it's useful as a newsletter item, a dataset to point Python readers at,
or just interesting to riff on, happy to talk through the data pipeline or
send the underlying field list. No ask beyond that — just thought it was a
good fit for what you cover.

Thanks for your time,
Elliott
[contact info]
```

---

## 3. Cold pitch — Quantified Strategies

**To:** support@quantifiedstrategies.com
**Subject:** Real STOCK Act filing-delay data — thought this might interest you and Håkan

```
Hi Oddmund and Håkan,

Long-time reader of the strategy backtests on QuantifiedStrategies.com —
sending this along because it's adjacent to the congressional-trading
angle you've covered before, but measures something most of that content
skips: actual filing compliance, not just what got bought.

I built a leaderboard off official House & Senate STOCK Act disclosure
dates (via FMP, sourced from efdsearch.senate.gov and
disclosures-clerk.house.gov) that measures the calendar-day gap between
each trade's transaction date and its disclosure date, against the
45-day legal deadline.

Live right now: 15.1% of trades in the current rolling window were filed
after the deadline, averaging 39 days to disclose overall, with the
slowest filing on record at 291 days — about 6.5x the legal window (a
Senate AAXJ trade, transaction 2025-11-06, disclosed 2026-08-24). Full
breakdown, per-member leaderboard, and the methodology/limitations
(it's a compliance-timing measure, not a legal determination — some gaps
are legitimate extensions or amended filings) are here:

https://quantengines.com/congress-stock-trades/late-filers

If it's useful to cite, link, or riff on for your own audience, feel free
— and if you'd want the underlying data fields or a quick rundown of how
the pipeline works, happy to share.

Best,
Elliott
[contact info]
```
