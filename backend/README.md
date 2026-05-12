# Jacer Backend

The FastAPI backend for [Jacer](../README.md).

## Quick start

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
cd backend
uv sync --extra dev
uv run uvicorn jacer.main:app --reload
```

The API is now at <http://localhost:8000>. Interactive docs at <http://localhost:8000/docs>.

## Tests

```bash
uv run pytest
```

## Lint and format

```bash
uv run ruff check .
uv run ruff format .
```

## Layout

```
backend/
├── pyproject.toml
├── jacer/
│   ├── main.py             FastAPI app
│   ├── models.py           Domain models (Pydantic)
│   ├── deps.py             Dependency injection
│   ├── repositories/       Storage adapters behind one interface
│   ├── services/           Business logic (e.g. template materialisation)
│   └── routers/            HTTP endpoints
└── tests/
```

The `Repository` interface in `jacer/repositories/base.py` is the central architectural seam — see the project notes for why this matters (it keeps the door open for a future Iceberg adapter without rewriting the application code).
