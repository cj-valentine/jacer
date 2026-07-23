# ADR-006 — `reset-to-template` endpoint (frozen-contract escape clause)

- **Status:** Accepted
- **Date:** 2026-07-24

## Context

Editing a template-derived task sets `diverged = True`; the board surfaces this
with a subtle dot. Users need to undo that — reset a task back to its template's
definition. But the escape is circular: `update_task` re-sets `diverged = True`
on **any** PATCH to a template-origin task, so a reset cannot be expressed as a
PATCH from the client. There is no other route that can clear `diverged`.

The FastAPI backend is otherwise frozen ([ADR-003](ADR-003-blazor-mudblazor-frontend.md)).
This is the deliberate "additive endpoint only if unavoidable" case: reset is
committed Phase 3 scope and is not implementable against the existing surface.

## Decision

- Add **`POST /api/tasks/{id}/reset-to-template`**. It restores the task's
  **definition** from its originating template item — `title`,
  `duration_minutes`, `category`, `scheduled_time` — and sets `diverged = False`.
- It **does not** touch `status`, `is_completed`, `scheduled_date` or
  `instance_date`: reset is about definition, not placement or completion.
- Errors: **409** when the task has no `template_origin_id`; **404** when the
  task or its originating template item no longer exists (the UI hides Reset in
  that case and snackbars the mid-session race).
- **Additive only** — no existing route, field, or behaviour changes. The prior
  test suite is unchanged; new contract tests cover every case on both adapters.

## Consequences

- The frozen contract grew by exactly one route, recorded here so the exception
  is explicit and bounded.
- Divergence is now reversible from the board without deleting and
  re-materialising the task, preserving its placement and completion.
