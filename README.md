# Jacer

A self-hosted, open-source task tracker built around **locked weekly and fortnightly routine templates**. Write your routine once; Jacer prepopulates your days from it.

> **Status — v2 in active development.** Targeting `v0.1.0` as the first public release. The `legacy/` directory contains the v1 codebase, preserved as a historical baseline. New development happens in the v2 tree (landing in Phase 1 onward — see [ROADMAP](docs/ROADMAP.md)).

## What is Jacer?

Most weeks have shape. You have a Monday morning that looks much like every other Monday morning. Jacer treats that shape as data: you write a Monday template once, lock it in, and every future Monday is prepopulated for you. Edit today as much as you want — the template stays clean and keeps producing future days.

The day-planning UX is borrowed deliberately from [Amazing Marvin](https://amazingmarvin.com): a Today / Backlog / Scheduled split, duration estimates on every task, and a visible day-total cap so you can see when you've overbooked. Everything else from Marvin's 100+ feature set is left out on purpose.

## Status

| Phase | What | Status |
|---|---|---|
| 0 | Foundations — repo, licence, governance, CI | In progress |
| 1 | Data model + API | Not started |
| 2 | Today view UX | Not started |
| 3 | Templates editor + auto-prepopulate | Not started |
| 4 | `v0.1.0` release | Not started |

Until `v0.1.0` ships, the public API and data shapes are unstable. See [ROADMAP](docs/ROADMAP.md) for full detail.

## Tech stack

- **Backend:** Python 3.12 + FastAPI + Pydantic + markdown-on-disk storage
- **Frontend:** TypeScript + React + Vite + Tailwind + shadcn/ui
- **Deployment:** Docker Compose, with a `pip install jacer` path planned
- **Tests:** pytest (backend), Vitest + Playwright (frontend, once Phase 2 lands)

## Install

> Not ready yet — coming with `v0.1.0`. Watch this space.

## Develop

> Detailed development guide coming with Phase 1. The v2 backend will live in `backend/`, frontend in `frontend/`. For now, browse the [`legacy/`](legacy/) directory to see the v1 starting point.

## Contributing

PRs welcome — please read [CONTRIBUTING.md](CONTRIBUTING.md) first. The project is mid-rewrite; open an issue before doing substantial work so we can align on direction.

## Licence

[MIT](LICENSE). Use freely, modify freely, distribute freely.
