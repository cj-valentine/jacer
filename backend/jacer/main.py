from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from jacer import __version__
from jacer.routers import health

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
