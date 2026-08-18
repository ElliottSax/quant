/**
 * Quick Ticker Lookup Widget — disabled, renders nothing.
 *
 * This widget accepted any ticker, waited 800ms to look like a network request,
 * and then displayed a fixed invented quote for it: price $156.78, a 1.52% move,
 * a 45.2M volume, a $2.3T market cap, a P/E, a dividend, an RSI, a "Bullish" MACD
 * and support/resistance levels — the same numbers for AAPL, for a typo, for a
 * ticker that does not exist. It also claimed, on a coin flip via Math.random,
 * that "12 politicians traded this stock recently" with a buy/sell split.
 *
 * That last claim is the sharpest reason this renders nothing rather than a
 * trimmed version: congressional trade data on this site is real and FMP-backed
 * (see /congress-stock-trades), so a fabricated count sat next to a genuine one
 * and was indistinguishable from it.
 *
 * The lookup may return when it is backed by the market-data quote endpoint, and
 * then only for fields that endpoint actually returns — a real price does not
 * license an invented RSI beside it, and per-ticker congressional activity must
 * come from the filings service or be absent. Until then this component renders
 * nothing: no widget is honest, a plausible one is not.
 *
 * The prior implementation is preserved in git history. Do not restore it.
 */

export function QuickTickerLookup() {
  return null
}
