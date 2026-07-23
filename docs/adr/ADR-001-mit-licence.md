# ADR-001 — MIT licence

- **Status:** Accepted
- **Date:** 2026-06-15 (backfilled stub documenting an earlier decision)

## Context

Jacer is intended to ship as a self-hosted, open-source task tracker that anyone
can run, modify, and redistribute, including alongside commercial offerings.

## Decision

Release Jacer under the [MIT licence](../../LICENSE).

## Consequences

- Maximum freedom for users and downstream integrators; minimal obligations.
- All bundled dependencies must be licence-compatible with MIT distribution.
  This constraint later shaped the frontend component-library choice — see
  [ADR-003](ADR-003-blazor-mudblazor-frontend.md).
