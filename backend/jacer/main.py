from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from jacer import __version__
from jacer.routers import days, health, tasks, template_items, templates

app = FastAPI(
    title="Jacer API",
    version=__version__,
    description="Self-hosted task tracker with locked weekly/fortnightly routine templates",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(template_items.router, prefix="/api", tags=["Template items"])
app.include_router(days.router, prefix="/api/days", tags=["Days"])
