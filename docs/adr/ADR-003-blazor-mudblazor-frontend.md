# ADR-003 — Blazor + MudBlazor frontend

- **Status:** Accepted
- **Date:** 2026-06-10

## Context

The original React frontend ([ADR-002](ADR-002-original-stack.md)) was reset
before any UI shipped. The FastAPI backend is kept as-is and treated as a frozen
API contract.

## Decision

- Build the frontend in **Blazor Server (.NET 10, InteractiveServer)** using the
  **MudBlazor** component library.
- Treat the **FastAPI backend as frozen** — the frontend consumes it through a
  typed `HttpClient` and does not change the API surface.
- **Exclude DevExpress Blazor** components: they are commercially licensed and
  incompatible with shipping Jacer under MIT ([ADR-001](ADR-001-mit-licence.md)).
  MudBlazor is MIT-licensed and clears that bar.

## Consequences

- One language across the data model and UI for contributors who prefer .NET.
- A standalone deployable that can later slot into a larger platform.
- Component choices are constrained to MIT-compatible libraries.
