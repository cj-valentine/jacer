# Jacer — repo guide for Claude

Self-hosted, open-source task tracker built around locked weekly/fortnightly
routine templates. Ships standalone; designed to slot into a larger platform later.

## Layout

- `backend/` — FastAPI + Pydantic API, markdown-on-disk storage. **Frozen as the
  API contract**: treat the endpoints and model fields as fixed and consume them;
  don't change the API surface without an explicit decision.
- `frontend/` — Blazor Server solution (`Jacer.slnx`, .NET 10, InteractiveServer):
  - `Jacer.ApiClient` — typed `HttpClient` + `System.Text.Json` snake_case DTOs.
  - `Jacer.Components` — Razor Class Library; **all** components live here.
  - `Jacer.Web` — host; registers MudBlazor services and the typed client.
  - `Jacer.Tests` — bUnit unit tests.
- `docs/adr/` — architecture decision records. Frontend stack is set by
  [ADR-003](docs/adr/ADR-003-blazor-mudblazor-frontend.md): Blazor + MudBlazor,
  FastAPI frozen, DevExpress excluded on MIT-licence grounds.
- `legacy/` — preserved v1 codebase; historical only.

## Conventions

- **UI library:** MudBlazor (MIT). Don't introduce non-MIT component libraries.
- **API shape:** status-driven columns (`backlog | today | scheduled | done`),
  trailing-slash collection routes, flat `/api/template-items/{id}`. Duration
  totals are computed client-side; the backend has no aggregate endpoint.
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
dotnet test  Jacer.slnx
```

The frontend's backend URL is config-driven (`Jacer:ApiBaseUrl`, default
`http://localhost:8000`). CORS origins are env-driven (`JACER_CORS_ORIGINS`).
