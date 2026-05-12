# Legacy — Jacer v1

This directory contains the original Jacer v1 codebase, preserved as a historical baseline before the v2 rewrite began.

**Do not develop in this directory.** All new work happens in the v2 tree at the repository root. See the top-level [README](../README.md) and [ROADMAP](../docs/ROADMAP.md).

## What's here

- `backend/` — FastAPI + markdown-storage backend. Functional in isolation.
- `frontend/` — Vite/React scaffolding **with the application source code missing**. Only build configuration (`Dockerfile`, `nginx.conf`, `eslint.config.js`), the entry HTML, and the Playwright E2E spec survived. The application source was lost prior to the v2 rewrite, which is partly why v2 was triggered.
- `data/templates/` — example weekday templates from v1. Personal task data (`data/tasks/`, `data/archive/`, `data/logs/`) is gitignored and not committed.
- `docker-compose.yml` — v1 deployment shape.

## Why this is preserved

For reference when porting the v1 API surface into v2, and because rewrites that delete history are dishonest about the path that got us here.

## Tag

The initial commit of this repository (tagged `v1.0-legacy`) is the v1 codebase exactly as it stood before the v2 rewrite began. To check it out:

```bash
git checkout v1.0-legacy
```

To return to the v2 tree:

```bash
git checkout main
```
