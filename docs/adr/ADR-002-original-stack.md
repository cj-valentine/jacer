# ADR-002 — Original v2 stack (FastAPI + React)

- **Status:** Superseded (frontend portion) by [ADR-003](ADR-003-blazor-mudblazor-frontend.md)
- **Date:** 2026-06-15 (backfilled stub documenting an earlier decision)

## Context

The v2 rewrite needed a backend and a frontend. The team chose a Python API with
a TypeScript single-page app, matching then-current familiarity and the broader
web ecosystem.

## Decision

- **Backend:** Python 3.12 + FastAPI + Pydantic, with markdown-on-disk storage.
- **Frontend:** TypeScript + React + Vite + Tailwind + shadcn/ui.

## Consequences

- The backend decision stands and is unaffected by later ADRs.
- The frontend decision was reversed before any UI shipped: see
  [ADR-003](ADR-003-blazor-mudblazor-frontend.md). The React scaffold was never
  committed to the main tree and has been removed.
