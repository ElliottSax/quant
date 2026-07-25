import { permanentRedirect } from 'next/navigation'

// This page previously rendered DEMO (fake) trade data. It's superseded by
// /congress-stock-trades, which shows real, current House & Senate trades.
// Permanent (308) redirect consolidates any link equity onto the real page.
export default function CongressionalTradesRedirect() {
  permanentRedirect('/congress-stock-trades')
}
