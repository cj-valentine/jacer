# Jacer — repo guide for Claude

Self-hosted, open-source task tracker built around locked weekly/fortnightly
routine templates. Ships standalone; designed to slot into a larger platform later.

## Layout

- `backend/` — FastAPI + Pydantic API, markdown-on-disk storage. **Frozen as the
  API contract**: treat the endpoints and model fields as fixed and consume them;
  don't change the API surface without an explicit decision.
- `frontend/` — Blazor Server solution (`Jacer.slnx`, .NET 10, InteractiveServer):
  - `Jacer.ApiClient` — typed `HttpClient` + `System.Text.Json` snake_case DTOs.
  - `Jacer.Components` — Razor Class Library; **all** components live here. The
    board is **day-centric** (Phase 3.5, [ADR-007](docs/adr/ADR-007-day-centric-board.md)):
    a global backlog + a selected day owning a task list and a custom `DayTimeline`
    (30-min grid, drag move/resize). Placement is keyed off `scheduled_date`, not
    status; `status` is now vestigial for placement (done + backlog distinction
    only) — a flagged future refactor.
  - `Jacer.Web` — host; registers MudBlazor services and the typed clients, and
    the Crucible dark `MudTheme` (`JacerTheme`).
  - `Jacer.Tests` — bUnit unit tests.
  - `Jacer.E2E` — Playwright/NUnit end-to-end tests. Native HTML5 drag is driven
    by dispatching `dragstart`/`dragover`/`drop` with a real `DataTransfer` handle;
    `unset BROWSER` before running.
- `docs/adr/` — architecture decision records. Frontend stack is set by
  [ADR-003](docs/adr/ADR-003-blazor-mudblazor-frontend.md): Blazor + MudBlazor,
  FastAPI frozen, DevExpress excluded on MIT-licence grounds. Phase 3 adds
  [ADR-004](docs/adr/ADR-004-status-canonical-completion.md) (`status` canonical,
  `is_completed` derived), [ADR-005](docs/adr/ADR-005-obsidian-native-daily-logs.md)
  (Obsidian-native daily logs + stale-day sweep), and
  [ADR-006](docs/adr/ADR-006-reset-to-template-endpoint.md) (an additive
  route, `POST /api/tasks/{id}/reset-to-template`). Phase 3.5 adds
  [ADR-007](docs/adr/ADR-007-day-centric-board.md) (day-centric board + custom
  `DayTimeline`) and [ADR-008](docs/adr/ADR-008-categories-api.md) (the additive
  `/api/categories` route set + palette).
- `legacy/` — preserved v1 codebase; historical only.

## Conventions

- **UI library:** MudBlazor (MIT). Don't introduce non-MIT component libraries.
- **API shape:** task `status` (`backlog | today | scheduled | done`),
  trailing-slash collection routes, flat `/api/template-items/{id}`. Duration
  totals are computed client-side; the backend has no aggregate endpoint.
  `status` is canonical and `is_completed` is derived from it (ADR-004). The
  frontend board is day-centric and drives placement off `scheduled_date`
  (ADR-007), reading `status` only for done/backlog. The contract is frozen
  except the additive routes in ADR-006 (`reset-to-template`) and ADR-008
  (`/api/categories`). Clearing a nullable field via PATCH needs an explicit
  `null` (`JacerJson.WriteNulls`); an omitted field means "leave unchanged".
- **Category colour** is drawn from the backend's fixed muted palette
  (`GET /api/categories/palette`) — one source of truth for the picker and card
  edges. Deleting a category clears dangling `category_id` references.
- **`TaskStatus`:** `Jacer.ApiClient.TaskStatus` collides with
  `System.Threading.Tasks.TaskStatus`; it's aliased in `GlobalUsings.cs` and the
  Razor `_Imports.razor`. Keep both if you add files that reference it.
- **AU English** in user-facing copy. YYYY-MM-DD dates in technical docs.

## Commands

```bash
# Backend (from backend/)
uv sync --extra dev
uv run uvicorn jacer.main:app --reload --port 8000   # JACER_REPOSITORY=memory for ephemeral data
uv run ruff check . && uv run ruff format --check . && uv run pytest

# Frontend (from frontend/)
dotnet run --project Jacer.Web --launch-profile http   # http://localhost:5099
dotnet build Jacer.slnx
dotnet test  Jacer.Tests/Jacer.Tests.csproj            # bUnit units

# E2E (needs the frontend + a backend running; browsers installed once)
unset BROWSER
JACER_WEB_URL=http://localhost:5099 dotnet test Jacer.E2E/Jacer.E2E.csproj
```

The frontend's backend URL is config-driven (`Jacer:ApiBaseUrl`, default
`http://localhost:8000`). CORS origins are env-driven (`JACER_CORS_ORIGINS`).
