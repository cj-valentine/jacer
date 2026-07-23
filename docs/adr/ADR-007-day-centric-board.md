# ADR-007 — Day-centric board and a custom DayTimeline

- **Status:** Accepted
- **Date:** 2026-07-24

## Context

Phase 3 shipped a status-driven Kanban board (`backlog | today | scheduled |
done` columns). First real use showed the model was wrong for a daily routine:
"Scheduled" piled every future task into one undifferentiated column with no day
awareness, and a template task materialised for next week with no time slot got
`status = "today"` and appeared on the board *immediately*. The owner asked for a
**day-centric** model instead — a global backlog plus a selected day (default
today) that owns both a task list and a schedule timeline (à la Amazing Marvin).

The FastAPI backend is frozen ([ADR-003](ADR-003-blazor-mudblazor-frontend.md)),
and Phase 3.5 is expected to be almost entirely frontend over the existing PATCH
surface (`scheduled_date`, `scheduled_time`, `duration_minutes`, `status`).

## Decision

- **Placement is presentation-layer, keyed off dates, not status.** The board
  queries tasks itself; day navigation never mutates `status`.
  - **Backlog** (global, undated): active tasks with `scheduled_date == null`.
  - **Upcoming** (in Backlog): active tasks with `scheduled_date > today`, shown
    with a date chip — future tasks stay visible and fully interactive.
  - **Selected day**: tasks with `scheduled_date == selectedDay` (fallback
    `instance_date`); timed → timeline, untimed → the day list.
  - **Done** (`status == done`) is completion (ADR-004), excluded from list/timeline.
- Scheduling forward (drag or the day dropdown) PATCHes `scheduled_date`
  (+ `scheduled_time` when dropped on the timeline), optimistically. No status flip.
- **The day timeline is a custom MudBlazor component (`DayTimeline`), not an
  adopted calendar library.** A 30-minute grid with duration-proportional cards,
  drag-to-move (start time) and drag-to-resize (duration) that PATCH on drop, is
  exactly where a general calendar component fights back; and the repo's proven
  test seam is small invokable handlers (`OnMove(id, startMin)` /
  `OnResize(id, durationMin)`) that bUnit calls directly, rather than simulated
  pointer physics. Building keeps us on the existing optimistic-PATCH +
  `EventCallback` pattern, adds no non-MIT dependency ([ADR-001](ADR-001-mit-licence.md)),
  and avoids a MudBlazor 9.7 theming fight. The same component serves the board
  (one day) and the template editor (seven stacked days).

## Consequences

- Days differentiate cleanly; a future task lives in Upcoming until its day, and
  is still draggable, editable, completable and deletable from there.
- **`status` becomes vestigial for placement** — only the `done` vs not-done and
  the "in backlog" (undated) distinctions still matter. Collapsing `status` to a
  completion flag is a sensible future refactor; it is **flagged, not addressed
  here**, to keep the frozen contract and the 116 backend tests untouched.
- Owning `DayTimeline` is more up-front work than wrapping a library, repaid by
  full control of the interaction and testability, and reuse across both screens.
