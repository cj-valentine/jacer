# ADR-005 — Obsidian-native daily logs and the stale-day sweep

- **Status:** Accepted
- **Date:** 2026-07-24

## Context

Locked templates materialise into task instances per day. Past days need to
roll over: their template tasks shouldn't linger on the board forever, but the
day's outcome is worth keeping. Jacer stores records as markdown on disk, so the
historical record should be readable in Obsidian, not just by Jacer.

## Decision

- **Stale-day sweep.** When materialisation runs (the board fires the horizon
  materialise on load), template-origin tasks whose placement (`scheduled_date`,
  else `instance_date`) is before today are rolled into that day's log and
  removed from the store. A task bumped forward is therefore not swept.
  **Manual tasks (no `template_origin_id`) are never swept.** The sweep is
  idempotent — swept tasks are deleted — and needs no new endpoint.
- **Obsidian-native daily logs.** A daily log keeps its YAML frontmatter stats
  (`date`, `total_tasks`, `completed_tasks`, `completion_pct`) and gains a native
  markdown body:

  ```
  # YYYY-MM-DD

  - [x] Title (45m) #category
  - [ ] Another task
  ```

  Completed items are `- [x]`, incomplete `- [ ]`; the duration parens and the
  `#category` tag are omitted when absent. The sweep appends to an existing log
  rather than clobbering it.
- **The task/template store format is untouched** — only the daily-log body
  becomes native. The frozen API contract ([ADR-003](ADR-003-blazor-mudblazor-frontend.md))
  is unchanged; the sweep is a side effect of existing materialisation.

## Consequences

- Days roll over cleanly: the board shows current/upcoming template tasks, and
  history lives in human- and Obsidian-readable logs.
- Frontmatter + native body means the same file serves both Jacer's stats and a
  reader's eye. Keeping the frontmatter avoids recomputing stats on read.
- The sweep boundary is the real "today", independent of the horizon start.
