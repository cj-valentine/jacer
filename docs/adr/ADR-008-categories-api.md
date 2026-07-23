# ADR-008 — Categories API (second frozen-contract escape)

- **Status:** Accepted
- **Date:** 2026-07-24

## Context

Tasks and template items have always carried a `category_id`, but there was no
way to define a category: no endpoint listed them, no colour source existed, and
the frontend never set one, so every task was effectively uncategorised. The
Phase 3.5 board needs real categories — collapsible Backlog groups with counts
and muted colour on card edges (Marvin-style).

The FastAPI backend is frozen ([ADR-003](ADR-003-blazor-mudblazor-frontend.md)),
with the single prior escape in [ADR-006](ADR-006-reset-to-template-endpoint.md).
Categories cannot be expressed against the existing surface, so this is a second,
deliberately bounded, additive escape — authorised on the same terms as ADR-006.

## Decision

- Add **`/api/categories`**: `GET` (list), `POST` (create), `GET/PATCH/DELETE
  /{id}`, plus **`GET /api/categories/palette`**. A `Category` is `id`, `name`,
  `colour`.
- **Colour is drawn from a fixed muted palette** (`CATEGORY_PALETTE`, eight tones
  that read on the charcoal dark theme). On create, an omitted colour is assigned
  round-robin so fresh categories get distinct tones; a supplied colour must be in
  the palette (**422** otherwise). The palette endpoint is the single source of
  truth the frontend renders its swatch picker from.
- **Deleting a category clears dangling references**: any task or template item
  pointing at it is reset to `category_id = null` (uncategorised). Chosen over
  "treat dangling as null on read" because it lives entirely in the new delete
  handler and leaves the frozen task/template read paths untouched.
- **Additive only** — no existing route, field, or behaviour changes. The prior
  116 tests are unchanged; new contract tests cover categories on both repository
  adapters, and router tests cover the palette, round-robin, validation, and the
  clear-on-delete cascade (proven across both adapters).

## Consequences

- The frozen contract grew by one more bounded route set, recorded here so the
  exception stays explicit.
- Category colour has one authority (the palette endpoint), so the board's card
  edges and the picker never drift apart.
- A deleted category degrades cleanly to uncategorised rather than leaving broken
  references behind.
