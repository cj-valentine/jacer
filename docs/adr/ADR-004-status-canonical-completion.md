# ADR-004 — `status` is canonical; `is_completed` is derived

- **Status:** Accepted
- **Date:** 2026-07-24

## Context

A `Task` carries both a `status` (`backlog | today | scheduled | done`) and a
separate `is_completed` boolean. Phase 2 wrote the two independently: nothing
kept them in step, `is_completed` was never read, and the board drove itself
purely off `status`. That left two representations of "done" that could
disagree.

## Decision

- **`status` is the single source of truth.** `is_completed` is a derived view
  of it: `is_completed == (status == "done")`.
- The tasks router reconciles the pair on every write, so a caller may drive
  either field:
  - On create, `is_completed` is derived from the initial `status`.
  - On update, if `is_completed` is supplied without `status`, it drives the
    status (`true → done`, `false → backlog`). When both are supplied, `status`
    wins. `is_completed` is then always re-derived from the resulting status, so
    the pair can never be left inconsistent.
- Both fields stay in every request and response — the API surface is unchanged
  (the FastAPI contract remains frozen, per [ADR-003](ADR-003-blazor-mudblazor-frontend.md)).

## Consequences

- Clients (the board, future callers) read and write `status` only and can
  ignore `is_completed`, while integrations that speak in terms of completion
  still work.
- The reconciliation lives in the router, so both repository adapters stay
  storage-only; contract tests exercise both directions on both adapters.
