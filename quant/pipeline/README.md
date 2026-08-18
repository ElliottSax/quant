# Pipeline — nightly EOD ingest

The compute plane. Runs on the Windows box, writes DuckDB, and never sits in the
serving path: the site reads static artefacts, not this database.

## Commands

```bash
export FMP_API_KEY=...                  # or the credentials for whichever provider
python -m pipeline.run_nightly          # incremental (last 10 days)
python -m pipeline.run_nightly --full   # full history for every symbol
python -m pipeline.readiness            # can the store support the stats spec yet?
```

`run_nightly` exits **0 only on a clean night** — every symbol returned rows and the
store is no older than the last completed trading day. Any publish step must gate on
that exit code; stale data served as current is the same class of error as inventing it.

## Files

| File | Role |
|---|---|
| `providers.py` | Vendor adapters behind one interface. Swapping vendors is config (`QUANT_EOD_PROVIDER`), never a caller change. Adjusted bars only — raw closes turn splits into fake returns. |
| `store.py` | DuckDB schema, idempotent upserts, and per-run provenance so every published number traces to a vendor and vintage. |
| `run_nightly.py` | Orchestrator, clean-night gate, loud failure. |
| `readiness.py` | Checks the store against `docs/STATS_SPEC.md` thresholds before any verdict work. |
| `universe.txt` | Provisional symbol list — see the header, it proves the pipeline rather than defining the product. |

## Current blocker

The store cannot yet support the product: on the current data entitlement no cell reaches
the spec's Robust threshold. See `docs/VENDOR_DECISION_BRIEF.md`.
