import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from jacer import __version__
from jacer.routers import categories, days, health, tasks, template_items, templates

app = FastAPI(
    title="Jacer API",
    version=__version__,
    description="Self-hosted task tracker with locked weekly/fortnightly routine templates",
)

# CORS origins are driven by the JACER_CORS_ORIGINS env var (comma-separated).
# Default covers the Blazor Server dev origin. Note: a Blazor Server frontend
# calls this API server-side, so CORS is not strictly required for it — this is
# belt-and-braces for browser-origin callers (e.g. a future WASM client).
_default_origins = "http://localhost:5099,https://localhost:7099"
_cors_origins = [
    origin.strip()
    for origin in os.environ.get("JACER_CORS_ORIGINS", _default_origins).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(template_items.router, prefix="/api", tags=["Template items"])
app.include_router(days.router, prefix="/api/days", tags=["Days"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
