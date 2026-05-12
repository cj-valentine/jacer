# Roadmap

Public-facing roadmap for Jacer. Detailed planning lives in the maintainer's project notes; this page is the version contributors and users see.

## Milestone: `v0.1.0`

The first public release. Scope is deliberately narrow.

### Phase 0 — Foundations *(in progress)*

- GitHub repository created
- MIT licence
- Governance files (`CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`)
- Continuous integration wired up
- v1 codebase preserved as `legacy/` and tagged `v1.0-legacy`

### Phase 1 — Data model + API

- Repository abstraction (`Repository` interface) — markdown adapter as default
- Task, Template, TemplateItem, DailyLog models
- Materialisation endpoint: turn template items into task instances for a given date
- pytest coverage per endpoint

### Phase 2 — Today view UX

- React + Vite + Tailwind + shadcn/ui frontend
- Three-column layout: Backlog · Today · Scheduled
- Duration estimates and day-total cap
- Drag-and-drop between columns
- Quick-add input

### Phase 3 — Templates + auto-prepopulate

- Weekly grid template editor
- Optional fortnightly cadence (week A / week B)
- Template lock / unlock
- Automatic prepopulation of the next 14 days
- "Diverged from template" indicator on edited instances

### Phase 4 — Release

- Polished README with screenshots and demo GIF
- Verified one-command install on a clean machine
- GitHub Release tagged `v0.1.0`

## Beyond `v0.1.0`

A non-binding sketch — nothing here is committed until `v0.1.0` ships.

- **v0.2.x** — import/export (Parquet, ICS, JSON), simple recurring tasks outside templates, mobile-responsive layout
- **v0.3.x** — pluggable storage backends exposed publicly (SQLite as an option)
- **v1.0.x** — stable public API, the first long-term-supported release

## Scope discipline

Jacer borrows day-planning ergonomics from [Amazing Marvin](https://amazingmarvin.com) and deliberately leaves the rest. Features outside the routine-template and day-planning loops (habits, gamification, calendar sync, plugin system, multi-user) are unlikely to ship in `v0.1.0` even if requested. They may land in a later minor or major release; they may not. Discussion welcome on GitHub Issues.
