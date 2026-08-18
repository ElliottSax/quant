# Why the frontend never showed real market data

**Found 2026-08-18 during Sprint 0 story 1.3 (fabricated-data purge).** This file explains
why every market-data surface on the site fell back to invented numbers, and what must be
fixed before any page can display real prices. It is input to Sprint 1.

The site did not fall back to fabrication because the data was unavailable. It fell back
because of **three independent breakages in the request path, any one of which alone was
fatal.** They masked each other, and the synthetic fallbacks masked all three.

## 1. The production API base URL was malformed (FIXED 2026-08-18)

`NEXT_PUBLIC_API_URL` on the Vercel production environment was:

```
https://elliottsax-quant-backend.hf.space/api/v1\n
```

— with a literal backslash-n as the last two characters of the value. Every request the
frontend built therefore had a corrupt path segment and could never reach any endpoint.

**Status: fixed.** The variable was rewritten without the trailing characters and verified
by re-pulling it. **Vercel env changes do not apply to an existing build — the frontend
must be redeployed for this to take effect.**

## 2. The hooks call an API namespace that does not exist (OPEN)

`src/lib/hooks.ts` reaches for `api.market.*`:

```ts
return (await anyApi?.market?.quote?.(ticker)) ?? null;   // hooks.ts
```

but `src/lib/api-client.ts` exports the namespace as **`marketData`**. `api.market` is
`undefined`, the optional chain short-circuits, and the `safe()` wrapper converts the
silent miss into the fallback value. Because the call is written with `?.` and cast through
`as any`, TypeScript cannot catch it — it fails silently at runtime, forever.

Affected hooks: `useMarketStatus`, `useMarketQuote`, `useMarketQuotes`, `useHistoricalData`.

## 3. The endpoints the client calls are not on the deployed backend (OPEN)

`api-client.ts`'s `marketData` namespace targets:

```
/market-data/public/quote/{symbol}
/market-data/public/quotes?symbols=…
/market-data/public/historical/{symbol}
```

The deployed HuggingFace backend serves **109 endpoints and none of these**. Verified
against its own OpenAPI spec (`/api/v1/openapi.json`). Even `/health` 404s at that prefix.

The equivalent route that **does** exist and **does** return real data:

```
GET /api/v1/data/market/price/{ticker}
```

Live check, 2026-08-18:

| Request | Response |
|---|---|
| `/data/market/price/AAPL` | `{"price":310.03,"change":4.88,"change_percent":1.6,"volume":46601840,…}` — real, current |
| `/data/market/price/SPY` | all fields `null` — the provider returns nothing for this ETF |

So the backend has a working quote path with **partial coverage**: single equities resolve,
at least some ETFs return nulls.

## What this means for the plan

- The honest empty/error states shipped in story 1.3 are **correct and will be visible** on
  deploy. `/charts` and the market ticker will show "did not load" rather than prices until
  a wiring decision is made. That is the intended behaviour, not a regression.
- **Do not simply repoint the hooks at the HF space.** Story NEW-0.1 demotes that space from
  the market-data serving path deliberately, and its ETF coverage is incomplete — SPY is the
  benchmark series the seasonality work depends on. The architecture's answer is the nightly
  ingest into DuckDB/Parquet plus static JSON, and that remains the answer.
- The cheap interim option, if a live ticker is wanted before the ingest lands, is a single
  adapter mapping `marketData.quote` → `/data/market/price/{ticker}` **plus** fixing the
  `api.market` → `api.marketData` name in hooks.ts. Both fixes are required; either alone
  still fails. Any symbol returning null fields must render as absent, never as zero.
- Whatever is chosen, the `?.` + `as any` pattern in hooks.ts should go. It converted a
  typo into a permanent silent failure, and silent failure is what made fabricated
  fallbacks look acceptable in the first place.
