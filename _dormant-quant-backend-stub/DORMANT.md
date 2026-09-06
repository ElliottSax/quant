# Dormant: leftover orchestration stub

Renamed from `quant-backend/` (repo root) to `_dormant-quant-backend-stub/`
on 2026-09-06 during a dead-code/bloat audit.

## Why this is dormant, not deleted
This directory contains only a 372-byte `CLAUDE.md` — no code. It's leftover
scaffolding from an old multi-agent coordination scheme (its content
instructs updating `/mnt/e/projects/.agent-bus/status/quant-backend.md`
each cycle, an agent-bus path that has nothing to do with this repo's actual
backend). The real backend lives at `quant/backend/` and is unaffected.

Named one character apart from the real backend directory
(`quant-backend` vs `quant/backend`) — low-severity confusion risk for
anyone browsing the repo root, since there's no code inside to be
mistakenly reused, but still worth flagging rather than silently leaving in
place under a name that looks like the real thing.

## Decision still needed
- **Delete**: nothing here is used; safe to `git rm -r` whenever convenient.
- No finish-and-launch case applies — this is pure leftover scaffolding, not
  unfinished product work. Flagged as dormant rather than deleted outright
  only to follow this session's standing rule of not deleting
  naming-collision clusters without a separate confirmation pass.
